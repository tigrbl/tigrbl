import { formatUtcTime, httpStatusLabel, protocolLabel, scopedIdentity, shortenId } from './correlationEngine';
import type {
  CorrelationGroup,
  CorrelationIndex,
  NormalizedTraceEvent,
  OutcomeStatus,
  OwnedEventRecord,
  WaterfallEdge,
  WaterfallLane,
  WaterfallLaneKind,
  WaterfallMark,
  WaterfallModel,
} from './types';

function operationLabel(ev: NormalizedTraceEvent): string | undefined {
  const { op_model: model, op_alias: alias } = ev.allowlistedMeta;
  return typeof model === 'string' && typeof alias === 'string' ? `${model}.${alias}` : undefined;
}

const EXECUTION_PHASES = [
  'INGRESS_BEGIN', 'INGRESS_PARSE', 'INGRESS_DISPATCH',
  'SECURITY', 'DEPENDENCIES', 'PRE_TX_BEGIN', 'START_TX', 'PRE_HANDLER', 'HANDLER',
  'POST_HANDLER', 'PRE_COMMIT', 'TX_COMMIT', 'POST_COMMIT', 'EGRESS_SHAPE',
  'EGRESS_FINALIZE', 'POST_RESPONSE',
];

const LEGACY_COMPILED_PHASES = new Map([
  ['fused:compiled_dispatch_prelude', 'INGRESS_DISPATCH'],
  ['fused:compiled_input_prepare', 'INGRESS_PARSE'],
  ['fused:compiled_validate_and_assemble', 'PRE_HANDLER'],
]);
const TRANSACTION_PHASES = new Set(['PRE_HANDLER', 'HANDLER', 'POST_HANDLER', 'PRE_COMMIT']);

function executionPhase(ev: NormalizedTraceEvent): string | undefined {
  if (ev.kind === 'hook.completed') return String(ev.allowlistedMeta.hook_phase ?? 'Hooks');
  if (ev.kind.startsWith('atom.')) {
    const label = ev.allowlistedMeta.atom_label;
    const phase = ev.allowlistedMeta.atom_phase;
    if (phase === 'COMPILED_INPUT_PRELUDE' && typeof label === 'string') {
      return LEGACY_COMPILED_PHASES.get(label) ?? 'Atoms';
    }
    return String(phase ?? 'Atoms');
  }
}

function isStartTxAtom(event: NormalizedTraceEvent): boolean {
  const label = event.allowlistedMeta.atom_label;
  return event.kind === 'atom.completed' && executionPhase(event) === 'START_TX' &&
    typeof label === 'string' && (label === 'sys.start_tx' || label.startsWith('atom:sys:start_tx@'));
}

function isCommitAtom(event: NormalizedTraceEvent): boolean {
  const label = event.allowlistedMeta.atom_label;
  return event.kind.startsWith('atom.') && executionPhase(event) === 'TX_COMMIT' &&
    typeof label === 'string' && (
      label === 'sys.commit_tx' || label.startsWith('atom:sys:commit_tx@')
    );
}

function ownsDatabaseEvent(step: NormalizedTraceEvent, event: NormalizedTraceEvent): boolean {
  if (!event.invocationId || !step.invocationId ||
      scopedIdentity(step, step.invocationId) !== scopedIdentity(event, event.invocationId) ||
      (step.transactionKey && step.transactionKey !== event.transactionKey) ||
      step.timeBasis !== 'measured_monotonic' ||
      step.sourceStartedAtMs === undefined || step.sourceEndedAtMs === undefined) return false;

  // A commit record starts at transaction begin. Only its completion belongs to the atom.
  const end = event.kind === 'db.tx.begin' ? event.sourceStartedAtMs : event.sourceEndedAtMs;
  const start = event.kind === 'db.tx.commit' ? end : event.sourceStartedAtMs;
  return (event.kind === 'db.tx.begin' || event.timeBasis === 'measured_monotonic') &&
    start !== undefined && end !== undefined && step.sourceStartedAtMs <= start &&
    end <= step.sourceEndedAtMs;
}

function eventLabel(ev: NormalizedTraceEvent): string {
  switch (ev.kind) {
    case 'http.request.received':
      return `${ev.allowlistedMeta.method ?? 'HTTP'} ${ev.allowlistedMeta.route ?? ''} received`.trim();
    case 'http.response.sent':
      return ev.statusCode === undefined ? 'HTTP response' : httpStatusLabel(ev.statusCode);
    case 'rpc.document.received':
      return `RPC document received${ev.rpcId ? ` (rpc ${ev.rpcId})` : ''}`;
    case 'rpc.batch.item.invoked':
      return `Batch item #${ev.rpcItemIndex ?? '?'} invoked${ev.rpcId ? ` (${ev.rpcId})` : ''}`;
    case 'rpc.batch.item.completed':
      return `Batch item #${ev.rpcItemIndex ?? '?'} completed`;
    case 'rpc.notification.received':
      return `RPC notification (no reply expected)`;
    case 'rpc.response.sent':
      return `RPC response sent${ev.statusCode ? ` (${ev.statusCode})` : ''}`;
    case 'invocation.started':
      return `Invocation start ${ev.invocationId ? shortenId(ev.invocationId, 10) : ''}`.trim();
    case 'invocation.completed':
      return operationLabel(ev) ?? `Invocation end ${ev.invocationId ? shortenId(ev.invocationId, 10) : ''}`.trim();
    case 'hook.completed':
      return `${ev.allowlistedMeta.hook_phase ?? 'Hook'} · ${ev.allowlistedMeta.hook_name ?? 'Unnamed hook'}`;
    case 'atom.completed':
    case 'atom.failed':
      return String(ev.allowlistedMeta.atom_label ?? ev.kind);
    case 'db.tx.begin':
      return `TX begin ${ev.transactionId ?? ''}`.trim();
    case 'db.tx.participant':
      return 'Invocation used transaction';
    case 'db.tx.query':
      return `TX query ${ev.allowlistedMeta.note ?? ''}`.trim();
    case 'db.tx.commit':
      return `TX commit ${ev.transactionId ?? ''}`.trim();
    case 'db.tx.rollback':
      return `TX rollback ${ev.transactionId ?? ''}`.trim();
    case 'db.flush.completed':
      return 'Flush completed';
    case 'db.flush.failed':
      return 'Flush failed';
    case 'ws.session.opened':
      return `WS session ${ev.transportSessionId ?? ''}`.trim();
    case 'ws.frame.received':
      return `WS frame received${ev.allowlistedMeta.topic ? ` (${ev.allowlistedMeta.topic})` : ''}`;
    case 'ws.frame.sent':
      return `WS frame sent`;
    case 'ws.broker.publish':
      return `Broker publish${ev.allowlistedMeta.topic ? ` · ${ev.allowlistedMeta.topic}` : ''}`;
    case 'ws.broker.delivery':
      return `Delivery · sub ${ev.subscriptionId ?? '?'} (gen ${ev.attachmentGeneration ?? '?'})`;
    case 'ws.subscription.attached':
      return `Subscription attached ${ev.subscriptionId ?? ''}`.trim();
    case 'wt.quic.connected':
      return `QUIC connected ${ev.quicConnectionId ?? ''}`.trim();
    case 'wt.session.opened':
      return `WT session opened ${ev.transportSessionId ?? ''}`.trim();
    case 'wt.stream.opened':
      return `Stream opened ${ev.streamId ?? ''}`.trim();
    case 'wt.stream.frame.received':
      return `Stream frame ingress ${ev.streamId ?? ''}`.trim();
    case 'wt.stream.frame.sent':
      return `Stream frame egress ${ev.streamId ?? ''}`.trim();
    case 'wt.stream.closed':
      return `Stream closed ${ev.streamId ?? ''}`.trim();
    case 'wt.datagram.received':
      return `Datagram received ${ev.datagramId ?? ''}`.trim();
    case 'wt.datagram.sent':
      return `Datagram sent ${ev.datagramId ?? ''}`.trim();
    default:
      return `Observed (${ev.kind})`;
  }
}

function resolveOutcome(ev: NormalizedTraceEvent): OutcomeStatus {
  if (ev.rpcIsNotification) return 'no_reply_expected';
  if (ev.outcome === 'error' || (ev.statusCode && ev.statusCode >= 400)) return 'error';
  if (ev.outcome === 'incomplete') return 'incomplete';
  if (ev.timeBasis === 'clock_skewed') return 'partial';
  return ev.outcome === 'ok' || (ev.statusCode !== undefined && ev.statusCode < 400) ? 'ok' : 'observed';
}

const REQUEST_BOUNDARIES = new Set([
  'http.request.received', 'rpc.document.received', 'ws.frame.received', 'wt.stream.frame.received',
]);
const REPLY_BOUNDARIES = new Set([
  'http.response.sent', 'rpc.response.sent', 'ws.frame.sent', 'wt.stream.frame.sent',
]);

function classifyLaneForEvent(
  ev: NormalizedTraceEvent,
  group: CorrelationGroup,
  namedInvocations: Set<string>,
): {
  laneKey: string;
  label: string;
  sublabel?: string;
  kind: WaterfallLaneKind;
  parentKey?: string;
  depth: number;
  defaultExpanded: boolean;
} {
  if (ev.invocationId && namedInvocations.has(ev.invocationId) && ev.kind.startsWith('invocation.')) {
    return {
      laneKey: `invocation:${ev.invocationId}`,
      label: operationLabel(ev) ?? 'Runtime invocation',
      sublabel: ev.measuredDurationMs === undefined
        ? shortenId(ev.invocationId, 14)
        : `${ev.measuredDurationMs.toPrecision(3)} ms`,
      kind: 'invocation',
      parentKey: 'lane:invocation',
      depth: 2,
      defaultExpanded: true,
    };
  }
  const phase = executionPhase(ev);
  if (phase) {
    const parent = ev.invocationId && namedInvocations.has(ev.invocationId)
      ? `invocation:${ev.invocationId}` : 'lane:invocation';
    return {
      laneKey: `${parent}:hooks:${phase}`,
      label: phase,
      kind: 'invocation',
      parentKey: parent,
      depth: parent === 'lane:invocation' ? 2 : 3,
      defaultExpanded: true,
    };
  }
  if (ev.kind.startsWith('db.flush.')) {
    const parent = ev.invocationId && namedInvocations.has(ev.invocationId)
      ? `invocation:${ev.invocationId}` : 'lane:requester';
    return {
      laneKey: `${parent}:flushes`,
      label: 'Database flushes',
      kind: 'transaction_lane',
      parentKey: parent,
      depth: parent === 'lane:requester' ? 1 : 3,
      defaultExpanded: true,
    };
  }
  // WebTransport specialized hierarchy
  if (group.protocol === 'webtransport') {
    if (ev.kind === 'wt.datagram.received' || ev.kind === 'wt.datagram.sent') {
      // Attach datagram to stream ONLY when record explicitly supplies stream_correlation_id or stream_id
      if (ev.streamCorrelationId || ev.streamId) {
        const sId = ev.streamCorrelationId ?? ev.streamId!;
        return {
          laneKey: `stream:${sId}`,
          label: `Stream ${shortenId(sId, 14)}`,
          sublabel: ev.streamId ? `stream_id ${ev.streamId} (attached datagram)` : 'attached datagram',
          kind: 'stream_lane',
          parentKey: 'group:streams',
          depth: 2,
          defaultExpanded: false,
        };
      }
      return {
        laneKey: 'lane:datagrams',
        label: 'Datagrams',
        sublabel: `Session ${group.transportSessionId ?? 'scoped'}`,
        kind: 'datagrams_lane',
        parentKey: 'lane:session_transport',
        depth: 1,
        defaultExpanded: false,
      };
    }

    if (
      ev.kind.startsWith('wt.stream.') ||
      ev.streamCorrelationId ||
      ev.streamId
    ) {
      const sId = ev.streamCorrelationId ?? ev.streamId ?? 'unknown-stream';
      return {
        laneKey: `stream:${sId}`,
        label: `Stream ${shortenId(sId, 14)}`,
        sublabel: ev.streamCorrelationId ? `stream_corr ${ev.streamCorrelationId}` : `stream ${ev.streamId}`,
        kind: 'stream_lane',
        parentKey: 'group:streams',
        depth: 2,
        defaultExpanded: false,
      };
    }

    if (ev.kind === 'wt.quic.connected' || ev.kind === 'wt.session.opened') {
      return {
        laneKey: 'lane:session_transport',
        label: 'Session transport',
        sublabel: group.transportSessionId
          ? `${group.transportSessionId}${group.quicConnectionId ? ` · ${group.quicConnectionId}` : ''}`
          : undefined,
        kind: 'session_transport',
        parentKey: 'lane:requester',
        depth: 1,
        defaultExpanded: true,
      };
    }
  }

  // HTTP JSON-RPC batch items
  if (group.protocol === 'jsonrpc' && ev.rpcItemIndex !== undefined) {
    return {
      laneKey: `batch:${ev.rpcItemIndex}`,
      label: `Batch item #${ev.rpcItemIndex}`,
      sublabel: ev.rpcId ? `rpc_id ${ev.rpcId}` : ev.rpcIsNotification ? 'notification' : undefined,
      kind: 'batch_item',
      parentKey: 'group:batch',
      depth: 2,
      defaultExpanded: false,
    };
  }

  // WebSocket broker publish / subscriptions / delivery
  if (
    ev.kind === 'ws.broker.publish' ||
    ev.kind === 'ws.broker.delivery' ||
    ev.kind === 'ws.subscription.attached'
  ) {
    const subKey = ev.subscriptionId ?? ev.allowlistedMeta.topic?.toString() ?? 'broker';
    return {
      laneKey: `sub:${subKey}`,
      label: ev.subscriptionId ? `Subscription ${shortenId(ev.subscriptionId, 12)}` : 'Broker pub/sub',
      sublabel: ev.attachmentGeneration
        ? `gen ${ev.attachmentGeneration}${ev.destinationId ? ` → ${ev.destinationId}` : ''}`
        : ev.allowlistedMeta.topic
        ? `topic ${ev.allowlistedMeta.topic}`
        : undefined,
      kind: 'subscription_lane',
      parentKey: 'group:subscriptions',
      depth: 2,
      defaultExpanded: true,
    };
  }

  // Invocations
  if (ev.kind.startsWith('invocation.')) {
    return {
      laneKey: 'lane:invocation',
      label: 'Runtime invocation',
      sublabel: ev.invocationId ? shortenId(ev.invocationId, 14) : 'handler',
      kind: 'invocation',
      parentKey: 'lane:ingress',
      depth: 1,
      defaultExpanded: true,
    };
  }

  // Egress responses / frames
  if (
    ev.kind === 'http.response.sent' ||
    ev.kind === 'rpc.response.sent' ||
    ev.kind === 'ws.frame.sent'
  ) {
    return {
      laneKey: 'lane:egress',
      label: 'Egress / reply',
      sublabel: ev.statusCode ? `status ${ev.statusCode}` : 'outbound',
      kind: 'egress',
      parentKey: 'lane:requester',
      depth: 1,
      defaultExpanded: true,
    };
  }

  // Ingress / session transport
  if (ev.kind === 'ws.session.opened') {
    return {
      laneKey: 'lane:session_transport',
      label: 'Carrier socket',
      sublabel: ev.transportSessionId
        ? `${ev.transportSessionId}${
            ev.requesterSessionId ? ` · req ${ev.requesterSessionId}` : ''
          }`
        : undefined,
      kind: 'session_transport',
      parentKey: 'lane:requester',
      depth: 1,
      defaultExpanded: true,
    };
  }

  if (!ev.isKnownKind) {
    return {
      laneKey: 'lane:observed_unknown',
      label: 'Observed records',
      sublabel: 'Unrecognized event kind',
      kind: 'ingress',
      parentKey:
        group.protocol === 'webtransport' ? 'lane:session_transport' : 'lane:requester',
      depth: group.protocol === 'webtransport' ? 2 : 1,
      defaultExpanded: true,
    };
  }

  return {
    laneKey: 'lane:ingress',
    label: group.protocol === 'websocket' ? 'Session ingress' : 'Server ingress',
    sublabel: protocolLabel(group.protocol),
    kind: 'ingress',
    parentKey: 'lane:requester',
    depth: 1,
    defaultExpanded: true,
  };
}

export function buildWaterfallModel(
  group: CorrelationGroup,
  index: CorrelationIndex,
  options: {
    showLinkedContext?: boolean;
    collapsedLaneKeys?: Set<string>;
    windowStartMs?: number;
    windowEndMs?: number;
  } = {}
): WaterfallModel {
  const showLinkedContext = Boolean(options.showLinkedContext);
  const collapsed = options.collapsedLaneKeys ?? new Set<string>();
  const request = group.events.find(({ event }) => REQUEST_BOUNDARIES.has(event.kind));
  const replies = group.events.filter(({ event }) => REPLY_BOUNDARIES.has(event.kind));
  const singleExchange = group.scope === 'http_request' || group.scope === 'rpc_request' ||
    (group.scope !== 'wt_session' && replies.length <= 1 &&
      group.events.filter(({ event }) => REQUEST_BOUNDARIES.has(event.kind)).length <= 1);
  const measuredReply = singleExchange ? replies.find(({ event }) =>
    event.timingBoundary === 'ingress_to_egress_monotonic' &&
    event.timeBasis === 'measured_monotonic' && event.measuredDurationMs !== undefined
  ) : undefined;
  const reply = singleExchange ? measuredReply ?? replies[0] : undefined;
  const duration = measuredReply?.event.measuredDurationMs;
  const replyAt = reply?.event.sourceEndedAtMs ?? reply?.event.atMs;
  const roundTripStart = duration !== undefined && replyAt !== undefined
    ? measuredReply?.event.sourceStartedAtMs ?? replyAt - duration
    : request?.event.atMs;
  const roundTripEnd = duration !== undefined && roundTripStart !== undefined
    ? roundTripStart + duration : replyAt;
  const hasRoundTrip = singleExchange && (measuredReply || request) &&
    group.outcomeSummary !== 'no_reply_expected';
  const timelineLabel = hasRoundTrip ? 'Round trip'
    : group.scope === 'wt_session' ? 'Session timeline' : 'Correlation timeline';

  const laneMap = new Map<string, WaterfallLane>();
  const ensureLane = (spec: {
    laneKey: string;
    label: string;
    sublabel?: string;
    kind: WaterfallLaneKind;
    parentKey?: string;
    depth: number;
    defaultExpanded: boolean;
    collapsible?: boolean;
    collapseToTimeline?: boolean;
    isLinkedContext?: boolean;
    relatedGroupKey?: string;
  }) => {
    let lane = laneMap.get(spec.laneKey);
    if (!lane) {
      const parentKey = spec.laneKey === 'lane:round_trip' ? undefined
        : !spec.parentKey || spec.parentKey === 'lane:requester' ? 'lane:round_trip' : spec.parentKey;
      lane = {
        laneKey: spec.laneKey,
        parentKey,
        depth: spec.depth,
        label: spec.label,
        sublabel: spec.sublabel,
        kind: spec.kind,
        defaultExpanded: spec.defaultExpanded,
        collapsible: spec.collapsible ?? false,
        collapseToTimeline: spec.collapseToTimeline,
        isLinkedContext: spec.isLinkedContext ?? false,
        relatedGroupKey: spec.relatedGroupKey,
        markCount: 0,
        marks: [],
        childrenKeys: [],
      };
      laneMap.set(spec.laneKey, lane);
      if (parentKey) {
        const parent = laneMap.get(parentKey);
        if (parent) {
          parent.collapsible = true;
          if (!parent.childrenKeys.includes(spec.laneKey)) {
            parent.childrenKeys.push(spec.laneKey);
          }
        }
      }
    }
    return lane;
  };

  const timelineLane = ensureLane({
    laneKey: 'lane:round_trip',
    label: timelineLabel,
    sublabel: duration !== undefined ? `${duration.toPrecision(3)} ms measured at server`
      : hasRoundTrip && !reply ? 'Reply not observed' : 'Recorded evidence',
    kind: 'round_trip',
    depth: 0,
    defaultExpanded: true,
    collapsible: true,
  });

  // Keep the requester as an endpoint for ingress and return arrows.
  ensureLane({
    laneKey: 'lane:requester',
    label: 'Requester / peer',
    sublabel: group.requesterSessionId
      ? `requester ${group.requesterSessionId}`
      : `${protocolLabel(group.protocol)} client`,
    kind: 'requester',
    depth: 0,
    defaultExpanded: true,
  });

  if (group.protocol === 'webtransport') {
    ensureLane({
      laneKey: 'lane:session_transport',
      label: 'Session transport',
      sublabel: group.transportSessionId
        ? `${group.transportSessionId}${group.quicConnectionId ? ` · ${group.quicConnectionId}` : ''}`
        : 'QUIC session',
      kind: 'session_transport',
      parentKey: 'lane:requester',
      depth: 1,
      defaultExpanded: true,
      collapsible: true,
    });
  } else {
    ensureLane({
      laneKey: 'lane:ingress',
      label: group.protocol === 'websocket' ? 'Session ingress' : 'Server ingress',
      sublabel: protocolLabel(group.protocol),
      kind: 'ingress',
      parentKey: 'lane:requester',
      depth: 1,
      defaultExpanded: true,
      collapsible: true,
    });
  }

  // Group events into lanes & build marks
  const marks: WaterfallMark[] = [];
  const laneTimeCounts = new Map<string, number>();

  const addMarkForRecord = (
    rec: OwnedEventRecord,
    laneKey: string,
    isLinkedContext: boolean,
    attach = true,
  ): WaterfallMark => {
    const ev = rec.event;
    const replyDuration = REPLY_BOUNDARIES.has(ev.kind) && ev.timingBoundary === 'ingress_to_egress_monotonic';
    const startMs = replyDuration ? ev.sourceEndedAtMs ?? ev.atMs
      : ev.timeBasis === 'measured_monotonic' &&
      (ev.timingBoundary === 'invocation_monotonic' || ev.timingBoundary === 'hook_monotonic' ||
        ev.timingBoundary === 'db_flush_monotonic' || ev.timingBoundary === 'atom_monotonic')
      ? ev.sourceStartedAtMs ?? ev.atMs
      : ev.atMs;
    const bucketKey = `${laneKey}:${startMs}`;
    const stackIdx = laneTimeCounts.get(bucketKey) ?? 0;
    if (attach) laneTimeCounts.set(bucketKey, stackIdx + 1);

    let glyph: WaterfallMark['glyph'] = 'point';
    if (!ev.isKnownKind) glyph = 'unknown';
    else if (ev.kind.startsWith('wt.datagram.')) glyph = 'datagram';
    else if (ev.kind.startsWith('db.tx.')) glyph = 'tx';
    else if (
      !replyDuration && ev.timeBasis === 'measured_monotonic' &&
      typeof ev.measuredDurationMs === 'number' &&
      ev.measuredDurationMs > 0
    ) {
      glyph = 'interval';
    } else if (ev.outcome === 'incomplete') {
      glyph = 'open_ended';
    }

    const endAtMs =
      glyph === 'interval' && ev.measuredDurationMs !== undefined
        ? startMs + ev.measuredDurationMs
        : undefined;

    const mark: WaterfallMark = {
      id: `mark-${ev.seq}`,
      seq: ev.seq,
      laneKey,
      at: ev.at,
      atMs: startMs,
      endAtMs,
      measuredDurationMs: replyDuration ? undefined : ev.measuredDurationMs,
      timeBasis: replyDuration && ev.timeBasis === 'measured_monotonic' ? 'recorded_at' : ev.timeBasis,
      kind: ev.kind,
      label: eventLabel(ev),
      glyph,
      outcome: resolveOutcome(ev),
      directionLabel: ev.directionLabel,
      provenance: rec.provenance,
      linkageBasis: rec.linkageBasis,
      stackOffset: stackIdx * 8,
      isLinkedContext,
      clockOrderUncertain: ev.timeBasis === 'clock_skewed',
      reason:
        ev.timeBasis === 'clock_skewed'
          ? 'Source end timestamp precedes start across clocks'
          : !ev.isKnownKind
          ? `Unknown event kind "${ev.kind}" shown as observed record`
          : ev.outcome === 'incomplete'
          ? 'Missing closing boundary record'
          : undefined,
      event: ev,
    };

    if (!attach) return mark;
    marks.push(mark);
    const lane = laneMap.get(laneKey);
    if (lane) {
      lane.marks.push(mark);
      lane.markCount = lane.marks.length;
    }
    return mark;
  };

  // Pre-create optional accordion groups only when data is present
  const hasBatch = group.events.some((r) => r.event.rpcItemIndex !== undefined);
  const hasStreams =
    group.protocol === 'webtransport' &&
    group.events.some(
      (r) =>
        r.event.kind.startsWith('wt.stream.') ||
        r.event.streamCorrelationId ||
        r.event.streamId
    );
  const hasSubs = group.events.some(
    (r) =>
      r.event.kind === 'ws.broker.publish' ||
      r.event.kind === 'ws.broker.delivery' ||
      r.event.kind === 'ws.subscription.attached'
  );

  if (hasBatch) {
    ensureLane({
      laneKey: 'group:batch',
      label: 'Batch items',
      sublabel: 'JSON-RPC batch',
      kind: 'batch_group',
      parentKey: 'lane:ingress',
      depth: 1,
      defaultExpanded: true,
      collapsible: true,
    });
  }
  if (hasStreams) {
    ensureLane({
      laneKey: 'group:streams',
      label: 'Streams',
      sublabel: 'Session-scoped streams',
      kind: 'streams_group',
      parentKey: 'lane:session_transport',
      depth: 1,
      defaultExpanded: true,
      collapsible: true,
    });
  }
  if (hasSubs) {
    ensureLane({
      laneKey: 'group:subscriptions',
      label: 'Subscriptions & broker',
      sublabel: 'Pub/sub handoffs',
      kind: 'subscriptions_group',
      parentKey: 'lane:ingress',
      depth: 1,
      defaultExpanded: true,
      collapsible: true,
    });
  }
  const markBySeq = new Map<number, WaterfallMark>();
  const namedInvocations = new Set<string>();
  for (const { event } of group.events) {
    if (event.kind === 'invocation.completed' && event.invocationId && operationLabel(event)) {
      namedInvocations.add(event.invocationId);
    }
  }
  if (namedInvocations.size || group.events.some(({ event }) => executionPhase(event))) {
    ensureLane({
      laneKey: 'lane:invocation',
      label: 'Operations',
      kind: 'invocation',
      parentKey: group.protocol === 'webtransport' ? 'lane:session_transport' : 'lane:ingress',
      depth: 1,
      defaultExpanded: true,
    });
    for (const { event } of group.events) {
      if (event.kind === 'invocation.completed' && event.invocationId && namedInvocations.has(event.invocationId)) {
        ensureLane(classifyLaneForEvent(event, group, namedInvocations));
      }
    }
  }

  const isTransactionPhase = (event: NormalizedTraceEvent) =>
    TRANSACTION_PHASES.has(executionPhase(event) ?? '');
  const phaseCounts = new Map<string, number>();
  for (const { event } of group.events) {
    if (!executionPhase(event) || isTransactionPhase(event)) continue;
    const { laneKey } = classifyLaneForEvent(event, group, namedInvocations);
    phaseCounts.set(laneKey, (phaseCounts.get(laneKey) ?? 0) + 1);
  }
  const isTransactionEvent = (ev: NormalizedTraceEvent) =>
    ev.kind.startsWith('db.tx.') || ev.kind.startsWith('db.flush.');
  const stepsByInvocation = new Map<string, OwnedEventRecord[]>();
  const databaseOwners = new Map<number, OwnedEventRecord>();
  const flushesByStep = new Map<number, OwnedEventRecord[]>();
  const commitByTransaction = new Map<string, OwnedEventRecord>();
  const flushIds = new Set<string>();
  const transactionsWithBoundary = new Set<string>();
  for (const record of group.events) {
    const event = record.event;
    if (event.transactionKey && ['db.tx.begin', 'db.tx.commit', 'db.tx.rollback'].includes(event.kind)) {
      transactionsWithBoundary.add(scopedIdentity(event, event.transactionKey));
    }
    if (!event.invocationId || !executionPhase(event)) continue;
    const key = scopedIdentity(event, event.invocationId);
    const steps = stepsByInvocation.get(key) ?? [];
    steps.push(record);
    stepsByInvocation.set(key, steps);
  }
  for (const record of group.events) {
    const event = record.event;
    const flush = event.kind.startsWith('db.flush.');
    if (!event.invocationId || (!flush && event.kind !== 'db.tx.commit')) continue;
    const steps = stepsByInvocation.get(scopedIdentity(event, event.invocationId)) ?? [];
    const matches = steps.filter(({ event: step }) => (
      isCommitAtom(step) || (flush && (step.kind === 'hook.completed' || executionPhase(step) === 'HANDLER'))
    ) && ownsDatabaseEvent(step, event));
    if (matches.length !== 1) continue;
    const [owner] = matches;
    if (isCommitAtom(owner.event) && event.transactionKey) {
      const key = scopedIdentity(event, event.transactionKey);
      if (!transactionsWithBoundary.has(key)) continue;
      const existing = commitByTransaction.get(key);
      if (existing && existing.event.seq !== owner.event.seq) continue;
      commitByTransaction.set(key, owner);
    } else if (flush && !isCommitAtom(owner.event)) {
      const flushId = event.allowlistedMeta.flush_id;
      if (typeof flushId === 'string') {
        const key = scopedIdentity(event, flushId);
        if (flushIds.has(key)) continue;
        flushIds.add(key);
      }
      const owned = flushesByStep.get(owner.event.seq) ?? [];
      owned.push(record);
      flushesByStep.set(owner.event.seq, owned);
    } else continue;
    databaseOwners.set(event.seq, owner);
  }
  const transactionCommitSteps = new Set([...commitByTransaction.values()].map(({ event }) => event.seq));

  const addFlushLane = (record: OwnedEventRecord, parent: WaterfallLane) => {
    if (collapsed.has(parent.laneKey)) {
      const detail = addMarkForRecord(record, parent.laneKey, false);
      detail.atMs = record.event.sourceEndedAtMs ?? detail.endAtMs ?? detail.atMs;
      detail.glyph = 'point';
      detail.endAtMs = undefined;
      detail.timelineNodeOffset = parent.markCount % 2 === 0 ? -7 : 7;
      markBySeq.set(record.event.seq, detail);
      return;
    }
    const detailLane = ensureLane({
      laneKey: `${parent.laneKey}:event:${record.event.seq}`,
      parentKey: parent.laneKey,
      depth: parent.depth + 1,
      label: eventLabel(record.event),
      kind: 'transaction_lane',
      defaultExpanded: true,
    });
    markBySeq.set(record.event.seq, addMarkForRecord(record, detailLane.laneKey, false));
  };

  const addPhaseEvent = (
    record: OwnedEventRecord,
    spec: ReturnType<typeof classifyLaneForEvent>,
    multiple: boolean,
  ) => {
    const ev = record.event;
    const phase = ensureLane({ ...spec, collapsible: multiple, collapseToTimeline: multiple });
    const lane = multiple && !collapsed.has(phase.laneKey)
      ? ensureLane({
          ...spec,
          laneKey: `${phase.laneKey}:${ev.seq}`,
          parentKey: phase.laneKey,
          depth: phase.depth + 1,
          label: String(ev.allowlistedMeta.hook_name ?? ev.allowlistedMeta.atom_label ?? 'Step'),
        })
      : phase;
    markBySeq.set(ev.seq, addMarkForRecord(record, lane.laneKey, false));
    for (const flush of flushesByStep.get(ev.seq) ?? []) addFlushLane(flush, lane);
  };
  const txRecords = new Map<string, OwnedEventRecord[]>();
  const transactionPhaseRecords: OwnedEventRecord[] = [];
  for (const rec of group.events) {
    const ev = rec.event;
    if (transactionCommitSteps.has(ev.seq)) continue;
    if (isTransactionPhase(ev)) {
      transactionPhaseRecords.push(rec);
      continue;
    }
    if (isTransactionEvent(ev) && ev.transactionKey) {
      const key = scopedIdentity(ev, ev.transactionKey);
      const records = txRecords.get(key) ?? [];
      records.push(rec);
      txRecords.set(key, records);
      continue;
    }
    if (ev.kind === 'db.tx.participant') continue;
    const laneSpec = classifyLaneForEvent(ev, group, namedInvocations);
    addPhaseEvent(rec, laneSpec, (phaseCounts.get(laneSpec.laneKey) ?? 0) > 1);
  }

  const invocationMarks = new Map<string, WaterfallMark>();
  for (const mark of marks) {
    const id = mark.event.invocationId;
    if (!id || (!mark.kind.startsWith('invocation.') && !mark.kind.startsWith('rpc.batch.item.'))) continue;
    if (mark.kind === 'invocation.completed' || !invocationMarks.has(id)) invocationMarks.set(id, mark);
  }

  const sharedTransactions: Array<{ mark: WaterfallMark; invocations: WaterfallMark[] }> = [];
  type TransactionLane = {
    lane: WaterfallLane;
    participants: Set<string>;
    openedInStartPhase: boolean;
    sourceStart?: number;
    sourceEnd?: number;
    detailCount: number;
  };
  const transactions = new Map<string, TransactionLane>();
  for (const [key, records] of txRecords) {
    const relatedGroups = index.transactionParticipants.get(key) ?? [];
    const evidence = new Map(records.map((record) => [record.event.seq, record]));
    for (const groupKey of relatedGroups) {
      if (groupKey === group.groupKey) continue;
      for (const record of index.groupsByKey.get(groupKey)?.events ?? []) {
        const ev = record.event;
        if (isTransactionEvent(ev) && ev.transactionKey && scopedIdentity(ev, ev.transactionKey) === key) {
          evidence.set(ev.seq, record);
        }
      }
    }
    const rows = [...evidence.values()];
    const begin = rows.find(({ event }) => event.kind === 'db.tx.begin');
    const terminals = rows.filter(({ event }) =>
      event.kind === 'db.tx.commit' || event.kind === 'db.tx.rollback');
    const terminal = terminals.find(({ event }) => event.timeBasis === 'measured_monotonic') ?? terminals[0];
    const boundary = terminal ?? begin;
    if (!boundary) {
      for (const record of records) {
        if (!record.event.kind.startsWith('db.flush.') || databaseOwners.has(record.event.seq)) continue;
        const lane = ensureLane(classifyLaneForEvent(record.event, group, namedInvocations));
        markBySeq.set(record.event.seq, addMarkForRecord(record, lane.laneKey, false));
      }
      continue;
    }

    const participants = new Set(rows.flatMap(({ event }) => event.invocationId ? [event.invocationId] : []));
    const invocations = [...participants].flatMap((id) => invocationMarks.get(id) ?? []);
    const shared = participants.size > 1 || relatedGroups.length > 1;
    const invocationLane = !shared && invocations.length === 1 ? laneMap.get(invocations[0].laneKey) : undefined;
    const batchLane = shared && hasBatch ? laneMap.get('group:batch') : undefined;
    const beginEvent = begin?.event;
    const beginSteps = !shared && beginEvent?.invocationId
      ? (stepsByInvocation.get(scopedIdentity(beginEvent, beginEvent.invocationId)) ?? [])
        .filter(({ event }) => isStartTxAtom(event) && ownsDatabaseEvent(event, beginEvent))
      : [];
    const beginPhase = beginSteps.length === 1
      ? laneMap.get(classifyLaneForEvent(beginSteps[0].event, group, namedInvocations).laneKey)
      : undefined;
    const parent = beginPhase ?? invocationLane ?? batchLane ?? ensureLane({
      laneKey: 'group:transactions',
      label: 'Database transactions',
      kind: 'transactions_group',
      parentKey: 'lane:requester',
      depth: 1,
      defaultExpanded: true,
    });
    const id = shortenId(boundary.event.transactionId ?? key, 12);
    const elapsed = terminal?.event.timeBasis === 'measured_monotonic'
      ? terminal.event.measuredDurationMs
      : undefined;
    const lane = ensureLane({
      laneKey: `tx:${key}`,
      label: `Transaction ${id}`,
      sublabel: elapsed !== undefined ? `${elapsed.toPrecision(3)} ms` : undefined,
      kind: 'transaction_lane',
      parentKey: parent.laneKey,
      depth: parent.depth + 1,
      defaultExpanded: true,
    });

    const end = terminal?.event.sourceEndedAtMs ?? terminal?.event.atMs;
    const start = terminal?.event.sourceStartedAtMs ?? begin?.event.sourceStartedAtMs ?? begin?.event.atMs ??
      (end !== undefined && elapsed !== undefined ? end - elapsed : end);
    const measuredEnd = start !== undefined && elapsed !== undefined ? start + elapsed : end;
    const mark = addMarkForRecord(boundary, lane.laneKey, false);
    const hasSpan = start !== undefined && measuredEnd !== undefined && measuredEnd >= start &&
      (elapsed !== undefined || begin !== undefined || terminal?.event.sourceStartedAtMs !== undefined);
    mark.label = `Transaction ${id} · ${terminal?.event.kind === 'db.tx.commit' ? 'Committed' : terminal ? 'Rolled back' : 'End not observed'}`;
    mark.id = `transaction-${boundary.event.seq}`;
    mark.atMs = start ?? mark.atMs;
    mark.endAtMs = hasSpan ? measuredEnd : undefined;
    mark.glyph = hasSpan ? 'interval' : terminal ? 'tx' : 'open_ended';
    mark.measuredDurationMs = elapsed;
    mark.outcome = terminal ? resolveOutcome(terminal.event) : 'incomplete';
    mark.evidenceSequences = [...evidence.keys()].sort((a, b) => a - b);
    mark.transactionBoundaries = [];
    const compact = collapsed.has(lane.laneKey);
    lane.collapsible = true;
    const addBoundary = (record: OwnedEventRecord, atMs: number, parent = lane) => {
      const event = record.event;
      const node = addMarkForRecord(record, lane.laneKey, false, false);
      node.atMs = atMs;
      node.label = event.kind;
      const isCommitPoint = event.kind === 'db.tx.commit' && databaseOwners.has(event.seq);
      if (isCommitPoint) {
        node.measuredDurationMs = undefined;
        node.timeBasis = 'recorded_at';
      }
      mark.transactionBoundaries?.push(node);
      if (compact) return;

      const collapsePhase = parent !== lane && collapsed.has(parent.laneKey);
      const rowLane = collapsePhase ? parent : ensureLane({
        laneKey: `${parent.laneKey}:boundary:${event.seq}`,
        label: event.kind,
        sublabel: event.kind === 'db.tx.begin' ? 'Transaction start'
          : parent !== lane ? 'Commit completed'
          : elapsed !== undefined ? `${elapsed.toPrecision(3)} ms transaction total` : 'Duration unavailable',
        kind: 'transaction_lane',
        parentKey: parent.laneKey,
        depth: parent.depth + 1,
        defaultExpanded: true,
      });
      const row = addMarkForRecord(record, rowLane.laneKey, false);
      row.id = `transaction-boundary-row-${event.seq}`;
      row.atMs = atMs;
      row.label = event.kind;
      if (isCommitPoint) {
        row.glyph = 'point';
        row.measuredDurationMs = undefined;
        row.timeBasis = 'recorded_at';
        if (collapsePhase) row.timelineNodeOffset = rowLane.markCount % 2 === 0 ? -7 : 7;
      }
    };
    if (begin) addBoundary(begin, mark.atMs);
    mark.reason = !terminal ? 'Transaction end was not observed'
      : elapsed === undefined ? 'Transaction duration was not measured'
      : undefined;

    for (const { event } of rows) markBySeq.set(event.seq, mark);
    const commitStep = commitByTransaction.get(key);
    const commitLane = commitStep && !compact ? ensureLane({
      laneKey: `${lane.laneKey}:TX_COMMIT`,
      label: 'TX_COMMIT',
      kind: 'transaction_lane',
      parentKey: lane.laneKey,
      depth: lane.depth + 1,
      defaultExpanded: true,
      collapsible: true,
    }) : undefined;
    if (commitStep) {
      const step = addMarkForRecord(commitStep, (commitLane ?? lane).laneKey, false, !compact);
      if (compact) {
        step.atMs = step.endAtMs ?? step.atMs;
        step.endAtMs = undefined;
        step.glyph = 'point';
        mark.transactionBoundaries?.push(step);
      }
      markBySeq.set(step.seq, step);
    }
    const seenFlushes = new Set<string>();
    let detailCount = 0;
    const details = rows.filter(({ event }) =>
      event.kind.startsWith('db.flush.') || event.kind === 'db.tx.query');
    details.sort((a, b) =>
      (a.event.sourceStartedAtMs ?? a.event.atMs) - (b.event.sourceStartedAtMs ?? b.event.atMs));
    for (const record of details) {
      const event = record.event;
      const flush = event.kind.startsWith('db.flush.');
      if (flush && typeof event.allowlistedMeta.flush_id === 'string') {
        if (seenFlushes.has(event.allowlistedMeta.flush_id)) continue;
        seenFlushes.add(event.allowlistedMeta.flush_id);
      }
      const owner = databaseOwners.get(event.seq);
      if (owner && !isCommitAtom(owner.event)) continue;
      if (flush && commitLane && owner?.event.seq === commitStep?.event.seq) {
        addFlushLane(record, commitLane);
        continue;
      }
      if (flush && commitStep && !owner && event.invocationId && commitStep.event.invocationId &&
          scopedIdentity(event, event.invocationId) === scopedIdentity(commitStep.event, commitStep.event.invocationId) &&
          event.sourceEndedAtMs !== undefined && commitStep.event.sourceStartedAtMs !== undefined &&
          event.sourceEndedAtMs < commitStep.event.sourceStartedAtMs) {
        const spec = classifyLaneForEvent(event, group, namedInvocations);
        addFlushLane(record, ensureLane(spec));
        continue;
      }
      const detailLane = compact ? lane : ensureLane({
        laneKey: `${lane.laneKey}:event:${event.seq}`,
        parentKey: lane.laneKey,
        depth: lane.depth + 1,
        label: flush ? eventLabel(event) : 'Query',
        kind: 'transaction_lane',
        defaultExpanded: true,
      });
      const detail = addMarkForRecord(record, detailLane.laneKey, false);
      if (compact) {
        detail.atMs = event.sourceEndedAtMs ?? detail.endAtMs ?? detail.atMs;
        detail.glyph = 'point';
        detail.endAtMs = undefined;
        detail.timelineNodeOffset = detailCount % 2 === 0 ? -7 : 7;
      }
      detailCount += 1;
      markBySeq.set(event.seq, detail);
    }
    if (terminal) {
      const owner = databaseOwners.get(terminal.event.seq);
      const phase = owner && owner.event.seq === commitStep?.event.seq ? commitLane : undefined;
      addBoundary(terminal, phase ? terminal.event.sourceEndedAtMs ?? mark.endAtMs ?? mark.atMs
        : mark.endAtMs ?? mark.atMs, phase);
    }
    transactions.set(key, {
      lane,
      participants: new Set(rows.flatMap(({ event }) =>
        event.invocationId ? [scopedIdentity(event, event.invocationId)] : [])),
      openedInStartPhase: beginPhase !== undefined,
      sourceStart: terminal?.event.sourceStartedAtMs ?? begin?.event.sourceStartedAtMs,
      sourceEnd: terminal?.event.sourceEndedAtMs,
      detailCount,
    });
    if (shared) sharedTransactions.push({ mark, invocations });
  }

  const transactionPhases = new Map<string, {
    spec: ReturnType<typeof classifyLaneForEvent>;
    records: OwnedEventRecord[];
    transaction?: TransactionLane;
  }>();
  for (const record of transactionPhaseRecords) {
    const event = record.event;
    const phaseName = executionPhase(event)!;
    const invocationLane = classifyLaneForEvent(event, group, namedInvocations);
    let transaction = event.transactionKey
      ? transactions.get(scopedIdentity(event, event.transactionKey)) : undefined;
    if (!event.transactionKey && event.invocationId &&
      event.sourceStartedAtMs !== undefined && event.sourceEndedAtMs !== undefined) {
      // Some steps lack a transaction ID. Require one matching invocation and source interval.
      const invocation = scopedIdentity(event, event.invocationId);
      const candidates = [...transactions.values()].filter((tx) =>
        tx.participants.has(invocation) &&
        tx.sourceStart !== undefined && tx.sourceEnd !== undefined &&
        tx.sourceStart <= event.sourceStartedAtMs! && event.sourceEndedAtMs! <= tx.sourceEnd);
      if (candidates.length === 1) [transaction] = candidates;
    }
    if (phaseName !== 'PRE_COMMIT' && !transaction?.openedInStartPhase) transaction = undefined;
    const spec = transaction ? {
      ...invocationLane,
      laneKey: `${transaction.lane.laneKey}:hooks:${phaseName}`,
      parentKey: transaction.lane.laneKey,
      depth: transaction.lane.depth + 1,
    } : invocationLane;
    const phase = transactionPhases.get(spec.laneKey) ?? { spec, records: [], transaction };
    phase.records.push(record);
    transactionPhases.set(spec.laneKey, phase);
  }
  for (const { spec, records, transaction } of transactionPhases.values()) {
    if (transaction && collapsed.has(transaction.lane.laneKey)) {
      for (const record of records.flatMap((step) => [step, ...(flushesByStep.get(step.event.seq) ?? [])])) {
        const node = addMarkForRecord(record, transaction.lane.laneKey, false);
        node.atMs = record.event.sourceEndedAtMs ?? node.endAtMs ?? node.atMs;
        node.glyph = 'point';
        node.endAtMs = undefined;
        node.timelineNodeOffset = transaction.detailCount % 2 === 0 ? -7 : 7;
        transaction.detailCount += 1;
        markBySeq.set(node.seq, node);
      }
    } else {
      for (const record of records) addPhaseEvent(record, spec, records.length > 1);
    }
  }

  // Optional muted counterpart lanes when "Show linked context" is enabled
  const hasLinkedContext = group.relatedCorrelations.length > 0;
  if (showLinkedContext && hasLinkedContext) {
    ensureLane({
      laneKey: 'group:related_context',
      label: 'Linked context (muted)',
      sublabel: 'Excluded from group metrics',
      kind: 'related_context_group',
      depth: 0,
      defaultExpanded: true,
      collapsible: true,
      isLinkedContext: true,
    });

    for (const rel of group.relatedCorrelations) {
      const targetGroup = index.groupsByKey.get(rel.targetGroupKey);
      if (!targetGroup) continue;
      const laneKey = `related:${targetGroup.groupKey}`;
      ensureLane({
        laneKey,
        parentKey: 'group:related_context',
        depth: 1,
        label: `${targetGroup.shortId}`,
        sublabel: rel.label,
        kind: 'related_context_lane',
        defaultExpanded: true,
        collapsible: false,
        isLinkedContext: true,
        relatedGroupKey: targetGroup.groupKey,
      });

      // Add up to 12 representative marks from linked counterpart so performance stays crisp
      for (const rec of targetGroup.events.filter(({ event }) => !isTransactionEvent(event)).slice(0, 12)) {
        addMarkForRecord(rec, laneKey, true);
      }
    }
  }

  // Build evidence-backed directional edges (From -> To)
  const edges: WaterfallEdge[] = [];
  const primaryMarks = marks.filter((m) => !m.isLinkedContext);

  const evidence = (hasRoundTrip ? reply ?? request : undefined) ?? group.events[0];
  if (evidence) {
    const mark = addMarkForRecord(evidence, timelineLane.laneKey, false);
    const start = (hasRoundTrip ? roundTripStart : undefined) ?? group.firstRecordedAtMs;
    const end = hasRoundTrip ? roundTripEnd : group.lastRecordedAtMs;
    mark.id = `round-trip-${evidence.event.seq}`;
    mark.kind = 'round_trip';
    mark.label = timelineLabel;
    mark.atMs = start;
    mark.endAtMs = end !== undefined && end >= start ? end : undefined;
    mark.measuredDurationMs = duration;
    mark.timeBasis = duration !== undefined ? 'measured_monotonic' : 'recorded_at';
    mark.glyph = mark.endAtMs !== undefined ? 'interval' : 'open_ended';
    mark.outcome = group.outcomeSummary;
    mark.evidenceSequences = [...new Set(
      (hasRoundTrip ? [request, reply] : [group.events[0], group.events.at(-1)])
        .flatMap((row) => row ? [row.event.seq] : [])
    )];
    mark.clockOrderUncertain = end !== undefined && end < start;
    mark.reason = hasRoundTrip && !reply ? 'Reply not observed' : undefined;
    if (duration !== undefined) mark.linkageBasis = 'Monotonic timing from server ingress to reply';
  }

  const isLaneHidden = (laneKey: string): boolean => {
    const lane = laneMap.get(laneKey);
    if (!lane) return true;
    let curr = lane.parentKey;
    while (curr) {
      if (collapsed.has(curr)) return true;
      curr = laneMap.get(curr)?.parentKey;
    }
    return false;
  };

  const isOutsideWindow = (ms: number): boolean => {
    if (options.windowStartMs !== undefined && ms < options.windowStartMs) return true;
    if (options.windowEndMs !== undefined && ms > options.windowEndMs) return true;
    return false;
  };

  // 1. Ingress edges (Requester -> Server ingress / Session transport / Stream)
  for (const m of primaryMarks) {
    const ev = m.event;
    if (
      ev.kind === 'http.request.received' ||
      ev.kind === 'rpc.document.received' ||
      ev.kind === 'rpc.notification.received' ||
      ev.kind === 'ws.frame.received' ||
      ev.kind === 'wt.stream.frame.received'
    ) {
      const toLane = laneMap.get(m.laneKey);
      const toLabel = toLane?.label ?? m.laneKey;
      const startMs = ev.sourceStartedAtMs ?? ev.atMs;
      const clockUncertain = ev.atMs < startMs || ev.timeBasis === 'clock_skewed';
      edges.push({
        id: `edge-in-${ev.seq}`,
        fromKey: 'lane:requester',
        toKey: m.laneKey,
        fromLabel: 'Requester / peer',
        toLabel,
        kind: 'request_ingress',
        direction: 'Ingress',
        evidenceSequences: [ev.seq],
        coverage: clockUncertain ? 'clock_uncertain' : 'complete',
        timeBasis: ev.timeBasis,
        startAtMs: startMs,
        endAtMs: ev.atMs,
        measuredDurationMs: clockUncertain ? undefined : ev.measuredDurationMs,
        clockOrderUncertain: clockUncertain,
        dashed: false,
        outcome: m.outcome,
        reason: ev.rpcIsNotification ? 'Notification — No reply expected' : undefined,
        textSummary: `Requester / peer → ${toLabel} (${m.label} at ${formatUtcTime(ev.atMs)})`,
      });
    }
  }

  // 2. Dispatch edges (Ingress / Session -> Invocation / Batch item / Stream)
  const firstIngress = primaryMarks.find(
    (m) =>
      m.laneKey === 'lane:ingress' ||
      m.laneKey === 'lane:session_transport'
  );

  for (const m of primaryMarks) {
    const ev = m.event;
    if (
      ev.kind === 'invocation.started' ||
      ev.kind === 'rpc.batch.item.invoked' ||
      ev.kind === 'wt.stream.opened'
    ) {
      const fromMark = (ev.linkedFromSeq ? markBySeq.get(ev.linkedFromSeq) : undefined) ??
        (index.mode === 'recorded' ? firstIngress : undefined);
      if (!fromMark || fromMark.laneKey === m.laneKey) continue;
      const fromLane = laneMap.get(fromMark.laneKey);
      const toLane = laneMap.get(m.laneKey);
      const clockUncertain = ev.atMs < fromMark.atMs || ev.timeBasis === 'clock_skewed';
      const targetHidden = isLaneHidden(m.laneKey);
      const outside = isOutsideWindow(ev.atMs);
      edges.push({
        id: `edge-disp-${fromMark.seq}-${ev.seq}`,
        fromKey: fromMark.laneKey,
        toKey: m.laneKey,
        fromLabel: fromLane?.label ?? fromMark.laneKey,
        toLabel: toLane?.label ?? m.laneKey,
        kind: ev.kind === 'wt.stream.opened' ? 'stream_handoff' : 'invocation_dispatch',
        direction: 'Observed at server',
        evidenceSequences: [fromMark.seq, ev.seq],
        coverage: clockUncertain
          ? 'clock_uncertain'
          : targetHidden
          ? 'hidden'
          : outside
          ? 'partial'
          : 'complete',
        timeBasis: ev.timeBasis,
        startAtMs: fromMark.atMs,
        endAtMs: ev.atMs,
        measuredDurationMs: clockUncertain ? undefined : ev.measuredDurationMs,
        clockOrderUncertain: clockUncertain,
        dashed: targetHidden || outside,
        endpointChip: targetHidden
          ? `${toLane?.label ?? 'Collapsed'} (collapsed)`
          : outside
          ? `${toLane?.label ?? 'Off-window'} (outside window)`
          : undefined,
        outcome: m.outcome,
        textSummary: `${fromLane?.label ?? fromMark.laneKey} → ${toLane?.label ?? m.laneKey} (${m.label})`,
      });
    }
  }

  // Shared transactions link to each visible invocation without duplicating the transaction bar.
  for (const { mark, invocations } of sharedTransactions) {
    for (const invocation of invocations) {
      const fromLabel = laneMap.get(invocation.laneKey)?.label ?? invocation.label;
      const toLabel = laneMap.get(mark.laneKey)?.label ?? mark.label;
      const hidden = isLaneHidden(mark.laneKey);
      const anchor = Math.max(mark.atMs, Math.min(invocation.atMs, mark.endAtMs ?? mark.atMs));
      edges.push({
        id: `edge-tx-${invocation.seq}-${mark.seq}`,
        fromKey: invocation.laneKey,
        toKey: mark.laneKey,
        fromLabel,
        toLabel,
        kind: 'tx_participation',
        direction: 'Observed at server',
        evidenceSequences: [...new Set([invocation.seq, ...(mark.evidenceSequences ?? [])])],
        coverage: hidden ? 'hidden' : 'complete',
        timeBasis: 'recorded_at',
        startAtMs: anchor,
        endAtMs: anchor,
        clockOrderUncertain: false,
        dashed: hidden,
        endpointChip: hidden ? `${toLabel} (collapsed)` : undefined,
        outcome: 'observed',
        textSummary: `${invocation.label} → ${toLabel} (shared transaction)`,
      });
    }
  }

  // 4. Egress return arrows (Egress / Stream -> Requester / peer)
  for (const m of primaryMarks) {
    const ev = m.event;
    if (
      ev.kind === 'http.response.sent' ||
      ev.kind === 'rpc.response.sent' ||
      ev.kind === 'ws.frame.sent' ||
      ev.kind === 'wt.stream.frame.sent'
    ) {
      const fromLane = laneMap.get(m.laneKey);
      const clockUncertain = ev.timeBasis === 'clock_skewed';
      edges.push({
        id: `edge-out-${ev.seq}`,
        fromKey: m.laneKey,
        toKey: 'lane:requester',
        fromLabel: fromLane?.label ?? m.laneKey,
        toLabel: 'Requester / peer',
        kind: 'response_egress',
        direction: 'Egress',
        evidenceSequences: [ev.seq],
        coverage: clockUncertain ? 'clock_uncertain' : 'complete',
        timeBasis: m.timeBasis,
        startAtMs: m.atMs,
        endAtMs: m.atMs,
        measuredDurationMs: clockUncertain ? undefined : m.measuredDurationMs,
        clockOrderUncertain: clockUncertain,
        dashed: false,
        outcome: m.outcome,
        textSummary: `${fromLane?.label ?? m.laneKey} → Requester / peer (${m.label} at ${formatUtcTime(ev.atMs)})`,
      });
    }
  }

  // 5. Missing reply or evicted / external endpoint dashed edges
  if (group.outcomeSummary === 'reply_not_observed') {
    const lastMark = primaryMarks[primaryMarks.length - 1];
    if (lastMark) {
      const fromLane = laneMap.get(lastMark.laneKey);
      edges.push({
        id: `edge-missing-reply-${group.groupKey}`,
        fromKey: lastMark.laneKey,
        toKey: 'lane:requester',
        fromLabel: fromLane?.label ?? lastMark.laneKey,
        toLabel: 'Requester / peer (Reply not observed)',
        kind: 'missing_endpoint',
        direction: 'Direction unavailable',
        evidenceSequences: [lastMark.seq],
        coverage: 'partial',
        timeBasis: 'recorded_at',
        startAtMs: lastMark.atMs,
        endAtMs: lastMark.atMs,
        clockOrderUncertain: false,
        dashed: true,
        endpointChip: 'Reply not observed',
        outcome: 'reply_not_observed',
        reason: 'Ingress recorded without a matching outbound response in capture window',
        textSummary: `${fromLane?.label ?? lastMark.laneKey} ⇢ Requester / peer (Reply not observed)`,
      });
    }
  }

  for (const m of primaryMarks) {
    if (m.event.evictedEndpointId || m.event.externalEndpointLabel) {
      const fromLane = laneMap.get(m.laneKey);
      const chip = m.event.evictedEndpointId
        ? `Evicted ${shortenId(m.event.evictedEndpointId, 12)}`
        : `External: ${m.event.externalEndpointLabel}`;
      edges.push({
        id: `edge-ext-${m.seq}`,
        fromKey: m.laneKey,
        toKey: m.laneKey,
        fromLabel: fromLane?.label ?? m.laneKey,
        toLabel: chip,
        kind: 'missing_endpoint',
        direction: m.directionLabel,
        evidenceSequences: [m.seq],
        coverage: m.event.evictedEndpointId ? 'evicted' : 'external',
        timeBasis: m.timeBasis,
        startAtMs: m.atMs,
        endAtMs: m.atMs,
        clockOrderUncertain: false,
        dashed: true,
        endpointChip: chip,
        outcome: 'partial',
        reason: m.event.evictedEndpointId
          ? `Endpoint ${m.event.evictedEndpointId} fell below sequence floor ${index.sequenceFloor}`
          : `Crosses boundary to external peer ${m.event.externalEndpointLabel}`,
        textSummary: `${fromLane?.label ?? m.laneKey} ⇢ ${chip}`,
      });
    }
  }

  // 6. Related correlation edges (Publish fan-out -> delivery, shared TX, QUIC sibling)
  for (const rel of group.relatedCorrelations) {
    const pubMark =
      primaryMarks.find((m) => m.event.kind === 'ws.broker.publish') ??
      primaryMarks.find((m) => rel.evidenceSequences.includes(m.seq)) ??
      primaryMarks[primaryMarks.length - 1];
    if (!pubMark) continue;

    const targetGroup = index.groupsByKey.get(rel.targetGroupKey);
    const linkedLaneKey = `related:${rel.targetGroupKey}`;
    const hasRenderedCounterpart = showLinkedContext && laneMap.has(linkedLaneKey);
    const fromLane = laneMap.get(pubMark.laneKey);
    const targetStartMs = targetGroup ? targetGroup.firstRecordedAtMs : pubMark.atMs + 4;
    const clockUncertain =
      rel.relationKind === 'publish_to_delivery' && targetStartMs < pubMark.atMs;

    edges.push({
      id: `edge-rel-${rel.id}`,
      fromKey: pubMark.laneKey,
      toKey: hasRenderedCounterpart ? linkedLaneKey : pubMark.laneKey,
      fromLabel: fromLane?.label ?? pubMark.laneKey,
      toLabel: `${rel.targetShortId} (${rel.relationKind.replace(/_/g, ' ')})`,
      kind: rel.relationKind === 'publish_to_delivery' ? 'publish_fanout' : 'related_link',
      direction: rel.direction === 'outbound' ? 'Egress' : rel.direction === 'inbound' ? 'Ingress' : 'Observed at server',
      evidenceSequences: rel.evidenceSequences,
      coverage: clockUncertain
        ? 'clock_uncertain'
        : hasRenderedCounterpart
        ? 'complete'
        : 'hidden',
      timeBasis: clockUncertain ? 'clock_skewed' : 'recorded_at',
      startAtMs: pubMark.atMs,
      endAtMs: targetStartMs,
      clockOrderUncertain: clockUncertain,
      dashed: !hasRenderedCounterpart,
      endpointChip: !hasRenderedCounterpart ? `Open ${rel.targetShortId}` : undefined,
      relatedGroupKey: rel.targetGroupKey,
      outcome: 'ok',
      reason: rel.attachmentGeneration
        ? `Subscription ${rel.subscriptionId ?? '?'} · attachment gen ${rel.attachmentGeneration}${
            rel.destinationId ? ` · dest ${rel.destinationId}` : ''
          }`
        : rel.label,
      textSummary: `${fromLane?.label ?? pubMark.laneKey} → ${rel.targetShortId} (${rel.label})`,
    });
  }

  // Order lanes hierarchically (DFS) so accordions nest predictably
  for (const lane of laneMap.values()) {
    if (lane === timelineLane) continue;
    const parent = (lane.parentKey && laneMap.get(lane.parentKey)) || timelineLane;
    lane.parentKey = parent.laneKey;
    if (!parent.childrenKeys.includes(lane.laneKey)) parent.childrenKeys.push(lane.laneKey);
    parent.collapsible = true;
  }
  const firstMarkAt = (key: string): number => {
    const lane = laneMap.get(key);
    if (!lane) return Infinity;
    return Math.min(...lane.marks.map((mark) => mark.atMs), ...lane.childrenKeys.map(firstMarkAt));
  };
  for (const lane of laneMap.values()) {
    if (lane.kind !== 'invocation' && lane.kind !== 'transaction_lane') continue;
    const starts = new Map(lane.childrenKeys.map((key) => [key, firstMarkAt(key)]));
    lane.childrenKeys.sort((a, b) => (starts.get(a) ?? Infinity) - (starts.get(b) ?? Infinity));
    // Order lifecycle siblings by phase while retaining timestamps for other evidence rows.
    const phaseRank = (key: string) => EXECUTION_PHASES.indexOf(laneMap.get(key)?.label ?? '');
    const phases = lane.childrenKeys.filter((key) => phaseRank(key) !== -1)
      .sort((a, b) => phaseRank(a) - phaseRank(b));
    let nextPhase = 0;
    lane.childrenKeys = lane.childrenKeys.map((key) => phaseRank(key) === -1 ? key : phases[nextPhase++]);
  }
  const orderedLanes: WaterfallLane[] = [];
  const visited = new Set<string>();
  const visit = (laneKey: string, depth: number) => {
    if (visited.has(laneKey)) return;
    const lane = laneMap.get(laneKey);
    if (!lane) return;
    visited.add(laneKey);
    lane.depth = depth;
    orderedLanes.push(lane);
    for (const childKey of lane.childrenKeys) {
      visit(childKey, depth + 1);
    }
  };

  visit(timelineLane.laneKey, 0);
  for (const lane of laneMap.values()) {
    if (!lane.parentKey) visit(lane.laneKey, 0);
  }
  for (const lane of laneMap.values()) {
    visit(lane.laneKey, lane.depth);
  }

  // Compute time bounds across plotted marks
  const allTimes: number[] = [];
  for (const m of marks) {
    allTimes.push(m.atMs);
    if (m.endAtMs !== undefined) allTimes.push(m.endAtMs);
  }
  for (const e of edges) {
    allTimes.push(e.startAtMs, e.endAtMs);
  }
  const rawMin = allTimes.length > 0 ? Math.min(...allTimes) : group.firstRecordedAtMs;
  const rawMax = allTimes.length > 0 ? Math.max(...allTimes) : group.lastRecordedAtMs;
  const pad = Math.max(2, Math.round((rawMax - rawMin) * 0.06));

  const hasMeasured = marks.some((m) => !m.isLinkedContext && m.timeBasis === 'measured_monotonic');
  const hasSkew = primaryMarks.some((m) => m.clockOrderUncertain) || edges.some((e) => e.clockOrderUncertain);
  const timeBasisSummary = hasSkew
    ? 'Clock order uncertain on ≥1 link · Recorded-at axis'
    : hasMeasured
    ? 'Recorded-at axis + measured monotonic boundaries'
    : 'Recorded-at axis (sink timestamps only)';

  return {
    groupKey: group.groupKey,
    minTimeMs: rawMin - pad,
    maxTimeMs: rawMax + pad,
    lanes: orderedLanes,
    marks,
    edges,
    hasLinkedContext,
    timeBasisSummary,
  };
}
