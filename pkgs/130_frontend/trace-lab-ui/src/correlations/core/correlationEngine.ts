import { adaptSnapshot } from './adapter';
import { parseTraceLookup } from './liveFeed';
import type {
  CorrelationGroup,
  CorrelationIndex,
  CorrelationScope,
  CoverageLabel,
  DeliveryOutcomeBreakdown,
  NormalizedSnapshot,
  NormalizedTraceEvent,
  OutcomeStatus,
  OwnedEventRecord,
  RelatedCorrelationEdge,
  SearchCandidate,
  SearchIdType,
  TraceSnapshotInput,
  TransportProtocol,
  UnassignedEventRecord,
} from './types';

export function buildGroupKey(
  captureId: string,
  scope: CorrelationScope,
  scopeIdentity: string,
  discriminator?: string,
  namespace?: string
): string {
  const parts = [captureId, scope, scopeIdentity];
  if (discriminator || namespace) parts.push(discriminator ?? '');
  if (namespace) parts.push(namespace);
  return parts.map(encodeURIComponent).join('|');
}

function sourceNamespace(event: NormalizedTraceEvent): string | undefined {
  return event.service ? `${event.environment ?? ''}/${event.service}` : undefined;
}

export function scopedIdentity(event: NormalizedTraceEvent, id: string): string {
  const namespace = sourceNamespace(event);
  return namespace ? JSON.stringify([namespace, id]) : id;
}

export function parseGroupKeyCaptureId(groupKey: string): string | undefined {
  const idx = groupKey.indexOf('|');
  return idx > 0 ? groupKey.slice(0, idx) : undefined;
}

export function shortenId(id: string, maxLen = 14): string {
  if (id.length <= maxLen) return id;
  return `${id.slice(0, maxLen - 4)}…${id.slice(-3)}`;
}

export function formatUtcTime(ms: number): string {
  if (!Number.isFinite(ms)) return '—';
  const d = new Date(ms);
  const hh = String(d.getUTCHours()).padStart(2, '0');
  const mm = String(d.getUTCMinutes()).padStart(2, '0');
  const ss = String(d.getUTCSeconds()).padStart(2, '0');
  const msPart = String(d.getUTCMilliseconds()).padStart(3, '0');
  return `${hh}:${mm}:${ss}.${msPart}`;
}

const httpReasons: Record<number, string> = {
  200: 'OK', 201: 'Created', 202: 'Accepted', 204: 'No Content',
  301: 'Moved Permanently', 304: 'Not Modified',
  400: 'Bad Request', 401: 'Unauthorized', 403: 'Forbidden', 404: 'Not Found',
  409: 'Conflict', 413: 'Content Too Large', 422: 'Unprocessable Content',
  429: 'Too Many Requests', 500: 'Internal Server Error', 502: 'Bad Gateway',
  503: 'Service Unavailable',
};

export function httpStatusLabel(status: number): string {
  return httpReasons[status] ? `HTTP ${status} ${httpReasons[status]}` : `HTTP ${status}`;
}

export function protocolLabel(p: TransportProtocol): string {
  switch (p) {
    case 'rest':
      return 'REST';
    case 'jsonrpc':
      return 'HTTP JSON-RPC';
    case 'websocket':
      return 'WebSocket';
    case 'webtransport':
      return 'WebTransport';
    case 'unknown':
      return 'Unclassified';
  }
}

export function scopeLabel(s: CorrelationScope): string {
  switch (s) {
    case 'http_request':
      return 'HTTP Request';
    case 'rpc_request':
      return 'RPC Exchange';
    case 'ws_logical':
      return 'WS Logical';
    case 'wt_session':
      return 'WT Session';
    case 'wt_stream':
      return 'WT Stream';
  }
}

interface PrimaryIdentity {
  scope: CorrelationScope;
  scopeIdentity: string;
  discriminator?: string;
  discriminatorLabel?: string;
  provenance: 'Reported correlation' | 'Linked by evidence';
  linkageBasis: string;
}

function resolvePrimaryIdentity(ev: NormalizedTraceEvent): PrimaryIdentity | null {
  // WebSocket delivery with receiving_correlation_id goes under receiving scope
  if (ev.protocol === 'websocket' && ev.receivingCorrelationId) {
    return {
      scope: 'ws_logical',
      scopeIdentity: ev.receivingCorrelationId,
      discriminator: ev.transportSessionId,
      discriminatorLabel: ev.transportSessionId ? `ws:${ev.transportSessionId}` : undefined,
      provenance: 'Reported correlation',
      linkageBasis: 'receiving_correlation_id on delivery record',
    };
  }

  // Standard reported correlation_id
  if (ev.correlationId) {
    if (ev.protocol === 'rest') {
      return {
        scope: 'http_request',
        scopeIdentity: ev.correlationId,
        discriminator: ev.requestId,
        discriminatorLabel: ev.requestId ? `req:${ev.requestId}` : undefined,
        provenance: 'Reported correlation',
        linkageBasis: ev.requestId
          ? 'correlation_id discriminated by request_id'
          : 'correlation_id',
      };
    }
    if (ev.protocol === 'jsonrpc') {
      return {
        scope: 'rpc_request',
        scopeIdentity: ev.correlationId,
        discriminator: ev.requestId,
        discriminatorLabel: ev.requestId ? `req:${ev.requestId}` : undefined,
        provenance: 'Reported correlation',
        linkageBasis: ev.requestId
          ? 'outer RPC correlation_id discriminated by request_id'
          : 'outer RPC correlation_id',
      };
    }
    if (ev.protocol === 'websocket') {
      return {
        scope: 'ws_logical',
        scopeIdentity: ev.correlationId,
        discriminator: ev.transportSessionId,
        discriminatorLabel: ev.transportSessionId ? `sess:${ev.transportSessionId}` : undefined,
        provenance: 'Reported correlation',
        linkageBasis: ev.transportSessionId
          ? 'logical correlation_id scoped to carrier transport_session_id'
          : 'logical correlation_id',
      };
    }
    if (ev.protocol === 'webtransport') {
      return {
        scope: 'wt_session',
        scopeIdentity: ev.correlationId,
        discriminator: ev.transportSessionId,
        discriminatorLabel: ev.transportSessionId ? `sess:${ev.transportSessionId}` : undefined,
        provenance: 'Reported correlation',
        linkageBasis: ev.transportSessionId
          ? 'WT session correlation_id within transport_session_id'
          : 'WT session correlation_id',
      };
    }
  }

  return null;
}

export function buildCorrelationIndex(
  input: TraceSnapshotInput | NormalizedSnapshot
): CorrelationIndex {
  const snapshot: NormalizedSnapshot =
    'captureId' in input ? input : adaptSnapshot(input);

  const captureId = snapshot.captureId;
  const groupEventsMap = new Map<
    string,
    {
      scope: CorrelationScope;
      protocol: TransportProtocol;
      scopeIdentity: string;
      discriminator?: string;
      discriminatorLabel?: string;
      records: OwnedEventRecord[];
    }
  >();

  // Secondary lookup tables to resolve explicit typed evidence (never replacing correlation IDs)
  const invocationToGroupKeys = new Map<string, Set<string>>();
  const scopeIdToGroupKeys = new Map<string, Set<string>>(); // `${protocol}:${scopeIdentity}` -> groupKeys
  const pendingEvents: NormalizedTraceEvent[] = [];

  const registerGroupRecord = (
    groupKey: string,
    meta: {
      scope: CorrelationScope;
      protocol: TransportProtocol;
      scopeIdentity: string;
      discriminator?: string;
      discriminatorLabel?: string;
    },
    record: OwnedEventRecord
  ) => {
    let entry = groupEventsMap.get(groupKey);
    if (!entry) {
      entry = { ...meta, records: [] };
      groupEventsMap.set(groupKey, entry);
    }
    entry.records.push(record);

    const sidKey = scopedIdentity(record.event, `${meta.protocol}:${meta.scopeIdentity}`);
    let sidSet = scopeIdToGroupKeys.get(sidKey);
    if (!sidSet) {
      sidSet = new Set();
      scopeIdToGroupKeys.set(sidKey, sidSet);
    }
    sidSet.add(groupKey);

    if (record.event.invocationId) {
      const invocationKey = scopedIdentity(record.event, record.event.invocationId);
      let invSet = invocationToGroupKeys.get(invocationKey);
      if (!invSet) {
        invSet = new Set();
        invocationToGroupKeys.set(invocationKey, invSet);
      }
      invSet.add(groupKey);
    }
  };

  // Pass 1: Assign events with explicit primary correlation identity (including discriminator)
  for (const ev of snapshot.events) {
    const primary = resolvePrimaryIdentity(ev);
    if (primary) {
      // If event has correlationId but lacks discriminator (e.g., DB row or downstream invocation),
      // defer to Pass 2 so we can check if it unambiguously joins a discriminated group.
      const needsDiscriminatorCheck = !primary.discriminator;

      if (needsDiscriminatorCheck) {
        pendingEvents.push(ev);
        continue;
      }

      const groupKey = buildGroupKey(
        captureId,
        primary.scope,
        primary.scopeIdentity,
        primary.discriminator,
        sourceNamespace(ev)
      );
      registerGroupRecord(
        groupKey,
        {
          scope: primary.scope,
          protocol: ev.protocol,
          scopeIdentity: primary.scopeIdentity,
          discriminator: primary.discriminator,
          discriminatorLabel: primary.discriminatorLabel,
        },
        {
          event: ev,
          provenance: primary.provenance,
          linkageBasis: primary.linkageBasis,
        }
      );
    } else {
      pendingEvents.push(ev);
    }
  }

  // Pass 2: Resolve deferred events by explicit typed relationship ONLY (never invent by time)
  const unassignedEvents: UnassignedEventRecord[] = [];

  for (const ev of pendingEvents) {
    // Case A: Broker publication carrying origin_correlation_id without top-level correlation_id
    if (ev.kind === 'ws.broker.publish' && !ev.correlationId && ev.originCorrelationId) {
      // Resolve via invocationId first, then scoped origin correlation
      const byInv = ev.originInvocationId || ev.invocationId;
      const byInvocation = byInv ? invocationToGroupKeys.get(scopedIdentity(ev, byInv)) : undefined;
      if (byInvocation?.size === 1) {
        const targetKey = Array.from(byInvocation)[0];
        const grp = groupEventsMap.get(targetKey)!;
        grp.records.push({
          event: ev,
          provenance: 'Linked by evidence',
            linkageBasis: `broker publish linked to origin via invocation_id=${byInv}`,
        });
        continue;
      }
      const byOrigin = scopeIdToGroupKeys.get(scopedIdentity(ev, `websocket:${ev.originCorrelationId}`));
      if (byOrigin && byOrigin.size === 1) {
        const targetKey = Array.from(byOrigin)[0];
        const grp = groupEventsMap.get(targetKey)!;
        grp.records.push({
          event: ev,
          provenance: 'Linked by evidence',
          linkageBasis: `broker publish resolved to origin_correlation_id=${ev.originCorrelationId}`,
        });
        continue;
      }
      unassignedEvents.push({
        event: ev,
        reason: byOrigin && byOrigin.size > 1
          ? `Ambiguous origin_correlation_id (${ev.originCorrelationId}) matches ${byOrigin.size} groups without discriminator`
          : `Unresolved origin_correlation_id (${ev.originCorrelationId})`,
        ambiguousCandidateKeys: byOrigin ? Array.from(byOrigin) : [],
      });
      continue;
    }

    // Case B: Event carrying invocation_id that uniquely resolves to one group
    if (ev.invocationId) {
      const byInv = invocationToGroupKeys.get(scopedIdentity(ev, ev.invocationId));
      if (byInv && byInv.size === 1) {
        const targetKey = Array.from(byInv)[0];
        const grp = groupEventsMap.get(targetKey)!;
        grp.records.push({
          event: ev,
          provenance: ev.correlationId ? 'Reported correlation' : 'Linked by evidence',
          linkageBasis: ev.correlationId
            ? `correlation_id + invocation_id=${ev.invocationId}`
            : `explicit invocation_id=${ev.invocationId}`,
        });
        continue;
      }
      if (byInv && byInv.size > 1) {
        unassignedEvents.push({
          event: ev,
          reason: `Ambiguous invocation_id=${ev.invocationId} matches ${byInv.size} correlation groups`,
          ambiguousCandidateKeys: Array.from(byInv),
        });
        continue;
      }
    }

    // Case C: Event has correlationId without discriminator — join ONLY if uniquely resolved, else keep separate or flag ambiguity
    const primary = resolvePrimaryIdentity(ev);
    if (ev.correlationId && primary) {
      const sidKey = scopedIdentity(ev, `${ev.protocol}:${ev.correlationId}`);
      const existing = scopeIdToGroupKeys.get(sidKey);
      if (existing && existing.size === 1) {
        const targetKey = Array.from(existing)[0];
        const grp = groupEventsMap.get(targetKey)!;
        grp.records.push({
          event: ev,
          provenance: 'Linked by evidence',
          linkageBasis: `correlation_id=${ev.correlationId} uniquely resolved to single group`,
        });
        continue;
      }
      if (existing && existing.size > 1) {
        unassignedEvents.push({
          event: ev,
          reason: `Missing discriminator for correlation_id=${ev.correlationId}; ${existing.size} candidate groups exist`,
          ambiguousCandidateKeys: Array.from(existing),
        });
        continue;
      }
      // No discriminated group exists for this correlation_id — create its own group
      const groupKey = buildGroupKey(captureId, primary.scope, primary.scopeIdentity, undefined, sourceNamespace(ev));
      registerGroupRecord(
        groupKey,
        {
          scope: primary.scope,
          protocol: ev.protocol,
          scopeIdentity: primary.scopeIdentity,
        },
        {
          event: ev,
          provenance: 'Reported correlation',
          linkageBasis: primary.linkageBasis,
        }
      );
      continue;
    }

    // Case D: No correlation_id and no resolvable typed link -> Unassigned (never invent from request/stream/rpc IDs)
    const hints: string[] = [];
    if (ev.requestId) hints.push(`request_id=${ev.requestId}`);
    if (ev.rpcId) hints.push(`rpc_id=${ev.rpcId}`);
    if (ev.streamId) hints.push(`stream_id=${ev.streamId}`);
    if (ev.transportSessionId) hints.push(`session=${ev.transportSessionId}`);
    unassignedEvents.push({
      event: ev,
      reason:
        hints.length > 0
          ? `No correlation_id present (${hints.join(', ')} kept as wire/carrier ID only)`
          : 'No correlation_id or resolvable typed relationship in record',
      ambiguousCandidateKeys: [],
    });
  }

  // Pass 3: Construct CorrelationGroup objects with distinct typed metrics
  const groups: CorrelationGroup[] = [];
  const groupsByKey = new Map<string, CorrelationGroup>();
  const transactionParticipants = new Map<string, Set<string>>();
  const quicSiblings = new Map<string, Set<string>>();

  for (const [groupKey, entry] of groupEventsMap.entries()) {
    entry.records.sort((a, b) =>
      a.event.atMs !== b.event.atMs
        ? a.event.atMs - b.event.atMs
        : a.event.seq - b.event.seq
    );

    const first = entry.records[0].event;
    const last = entry.records[entry.records.length - 1].event;

    const invocationSet = new Set<string>();
    const txSet = new Set<string>();
    const requestSet = new Set<string>();
    const rpcSet = new Set<string>();
    const streamCorrSet = new Set<string>();
    const streamEntitySet = new Set<string>();
    const datagramSet = new Set<string>();

    let quicConnId: string | undefined;
    let transportSessId: string | undefined;
    let requesterSessId: string | undefined;
    let hasClockSkew = false;
    let hasEvictedEndpoint = false;
    let hasNotification = false;
    let hasIngress = false;
    let hasEgressReply = false;
    let hasMeasuredTiming = false;
    let hasError = false;
    let httpStatus: number | undefined;
    const commits = new Set<string>();
    const rollbacks = new Set<string>();

    const outcomes: DeliveryOutcomeBreakdown = {
      ok: 0,
      error: 0,
      noReplyExpected: 0,
      replyNotObserved: 0,
      incomplete: 0,
    };

    for (const rec of entry.records) {
      const ev = rec.event;
      if (ev.kind === 'http.response.sent' || ev.kind === 'rpc.response.sent') {
        httpStatus = ev.statusCode ?? httpStatus;
      }
      if (ev.invocationId) invocationSet.add(ev.invocationId);
      if (ev.transactionKey) {
        txSet.add(ev.transactionKey);
        if (ev.kind === 'db.tx.commit') commits.add(ev.transactionKey);
        if (ev.kind === 'db.tx.rollback') rollbacks.add(ev.transactionKey);
        if (ev.engineSessionId && (ev.kind === 'db.tx.participant' || ev.invocationId)) {
          const scopedTx = scopedIdentity(ev, ev.transactionKey);
          let pSet = transactionParticipants.get(scopedTx);
          if (!pSet) {
            pSet = new Set();
            transactionParticipants.set(scopedTx, pSet);
          }
          pSet.add(groupKey);
        }
      }
      if (ev.requestId) requestSet.add(ev.requestId);
      if (ev.rpcId) rpcSet.add(ev.rpcId);
      if (ev.streamCorrelationId) streamCorrSet.add(ev.streamCorrelationId);
      if (ev.streamId || ev.streamCorrelationId) {
        streamEntitySet.add(ev.streamCorrelationId ?? ev.streamId!);
      }
      if (ev.datagramId || ev.kind.startsWith('wt.datagram.')) {
        datagramSet.add(ev.datagramId ?? `dgram-seq-${ev.seq}`);
      }
      if (ev.quicConnectionId) {
        quicConnId = ev.quicConnectionId;
        const scopedQuic = scopedIdentity(ev, ev.quicConnectionId);
        let qSet = quicSiblings.get(scopedQuic);
        if (!qSet) {
          qSet = new Set();
          quicSiblings.set(scopedQuic, qSet);
        }
        qSet.add(groupKey);
      }
      if (ev.transportSessionId && !transportSessId) {
        transportSessId = ev.transportSessionId;
      }
      if (ev.requesterSessionId && !requesterSessId) {
        requesterSessId = ev.requesterSessionId;
      }
      if (ev.timeBasis === 'clock_skewed') hasClockSkew = true;
      if (ev.timeBasis === 'measured_monotonic') hasMeasuredTiming = true;
      if (ev.evictedEndpointId) hasEvictedEndpoint = true;
      if (ev.rpcIsNotification) hasNotification = true;

      if (
        ev.kind === 'http.request.received' ||
        ev.kind === 'rpc.document.received' ||
        ev.kind === 'rpc.notification.received' ||
        ev.kind === 'ws.frame.received' ||
        ev.kind === 'wt.stream.frame.received'
      ) {
        hasIngress = true;
      }
      if (
        ev.kind === 'http.response.sent' ||
        ev.kind === 'rpc.response.sent' ||
        ev.kind === 'ws.frame.sent' ||
        ev.kind === 'ws.broker.delivery' ||
        ev.kind === 'wt.stream.frame.sent'
      ) {
        hasEgressReply = true;
      }

      if (ev.outcome === 'error' || (ev.statusCode && ev.statusCode >= 400)) {
        hasError = true;
        outcomes.error++;
      } else if (ev.rpcIsNotification) {
        outcomes.noReplyExpected++;
      } else if (ev.outcome === 'incomplete') {
        outcomes.incomplete++;
      } else if (ev.outcome === 'ok') {
        outcomes.ok++;
      }
    }

    // Detect missing reply on request/response protocols (when not a notification)
    const expectsReply =
      (entry.protocol === 'rest' || entry.protocol === 'jsonrpc') &&
      hasIngress &&
      !hasNotification;
    if (expectsReply && !hasEgressReply) {
      outcomes.replyNotObserved++;
    }

    // Determine explicit coverage & outcome summary
    let coverage: CoverageLabel = 'Complete';
    let outcomeSummary: OutcomeStatus = 'ok';

    if (hasClockSkew) {
      coverage = 'Skewed clocks';
      outcomeSummary = hasError ? 'error' : 'partial';
    } else if (hasEvictedEndpoint) {
      coverage = 'Evicted endpoint';
      outcomeSummary = 'partial';
    } else if (expectsReply && !hasEgressReply) {
      coverage = 'Partial (Reply not observed)';
      outcomeSummary = 'reply_not_observed';
    } else if (hasNotification && !hasEgressReply && entry.protocol === 'jsonrpc') {
      coverage = 'Notification (No reply expected)';
      outcomeSummary = 'no_reply_expected';
    } else if (outcomes.incomplete > 0) {
      coverage = 'Partial (Observed-at only)';
      outcomeSummary = 'incomplete';
    } else if (snapshot.bounded) {
      coverage = 'Bounded evidence';
      outcomeSummary = hasError ? 'error' : hasEgressReply ? 'ok' : 'observed';
    } else if (!hasMeasuredTiming) {
      coverage = hasIngress && hasEgressReply ? 'Complete' : 'Observed only';
      outcomeSummary = hasError ? 'error' : hasEgressReply || outcomes.ok > 0 ? 'ok' : 'observed';
    } else if (hasError) {
      coverage = 'Complete';
      outcomeSummary = 'error';
    }

    const shortId = shortenId(entry.scopeIdentity, 16);
    const displayTitle = entry.discriminatorLabel
      ? `${shortId} (${entry.discriminatorLabel})`
      : shortId;

    const group: CorrelationGroup = {
      groupKey,
      captureId,
      scope: entry.scope,
      protocol: entry.protocol,
      scopeIdentity: entry.scopeIdentity,
      discriminator: entry.discriminator,
      discriminatorLabel: entry.discriminatorLabel,
      shortId,
      displayTitle,
      service: first.service,
      environment: first.environment,
      httpStatus,
      committedTransactions: commits.size,
      rolledBackTransactions: rollbacks.size,
      firstRecordedAt: first.at,
      firstRecordedAtMs: first.atMs,
      lastRecordedAt: last.at,
      lastRecordedAtMs: last.atMs,
      recordedSpanMs: Math.max(0, last.atMs - first.atMs),
      events: entry.records,
      relatedCorrelations: [],
      metrics: {
        observedEvents: entry.records.length,
        invocations: invocationSet.size,
        transactions: txSet.size,
        deliveryOutcomes: outcomes,
        coverage,
        ...(entry.protocol === 'webtransport'
          ? {
              streams: streamEntitySet.size,
              datagrams: datagramSet.size,
            }
          : {}),
      },
      outcomeSummary,
      hasClockSkew,
      hasEvictedEndpoint,
      requestIds: Array.from(requestSet),
      rpcIds: Array.from(rpcSet),
      streamCorrelationIds: Array.from(streamCorrSet),
      quicConnectionId: quicConnId,
      transportSessionId: transportSessId,
      requesterSessionId: requesterSessId,
      transactionKeys: Array.from(txSet),
      invocationIds: Array.from(invocationSet),
    };

    groups.push(group);
    groupsByKey.set(groupKey, group);
  }

  // Pass 4: Build Related Correlation edges across groups (never merging groups)
  const relSeenMap = new Map<string, Set<string>>();
  const addRelatedEdge = (source: CorrelationGroup, edge: RelatedCorrelationEdge) => {
    if (source.groupKey === edge.targetGroupKey) return;
    let seen = relSeenMap.get(source.groupKey);
    if (!seen) {
      seen = new Set();
      relSeenMap.set(source.groupKey, seen);
    }
    const dedupeKey = `${edge.targetGroupKey}|${edge.relationKind}|${edge.transactionKey ?? ''}|${edge.subscriptionId ?? ''}`;
    if (!seen.has(dedupeKey)) {
      seen.add(dedupeKey);
      source.relatedCorrelations.push(edge);
    }
  };

  // 4a. WebSocket publication -> delivery edges
  for (const destGroup of groups) {
    for (const rec of destGroup.events) {
      const ev = rec.event;
      if (ev.kind === 'ws.broker.delivery' && ev.originCorrelationId) {
        const originKeys = ev.originInvocationId
          ? invocationToGroupKeys.get(scopedIdentity(ev, ev.originInvocationId))
          : scopeIdToGroupKeys.get(scopedIdentity(ev, `websocket:${ev.originCorrelationId}`));
        if (originKeys?.size !== 1) continue;
        for (const originKey of originKeys) {
          const originGroup = groupsByKey.get(originKey);
          if (!originGroup || originGroup.groupKey === destGroup.groupKey) continue;

          // Edge on publisher pointing to receiving subscription group
          addRelatedEdge(originGroup, {
            id: `rel-pub-${originGroup.groupKey}-${destGroup.groupKey}-${ev.seq}`,
            targetGroupKey: destGroup.groupKey,
            targetShortId: destGroup.shortId,
            targetScope: destGroup.scope,
            targetProtocol: destGroup.protocol,
            relationKind: 'publish_to_delivery',
            direction: 'outbound',
            label: `Delivery to ${destGroup.shortId}${
              ev.subscriptionId ? ` · sub ${ev.subscriptionId}` : ''
            }`,
            evidenceSequences: [ev.seq],
            attachmentGeneration: ev.attachmentGeneration,
            destinationId: ev.destinationId,
            subscriptionId: ev.subscriptionId,
          });

          // Back-reference on receiving group pointing to origin publisher
          addRelatedEdge(destGroup, {
            id: `rel-orig-${destGroup.groupKey}-${originGroup.groupKey}-${ev.seq}`,
            targetGroupKey: originGroup.groupKey,
            targetShortId: originGroup.shortId,
            targetScope: originGroup.scope,
            targetProtocol: originGroup.protocol,
            relationKind: 'delivery_from_origin',
            direction: 'inbound',
            label: `Published by ${originGroup.shortId}`,
            evidenceSequences: [ev.seq],
            attachmentGeneration: ev.attachmentGeneration,
            destinationId: ev.destinationId,
            subscriptionId: ev.subscriptionId,
          });
        }
      }
    }
  }

  // 4b. Shared DB transaction participation
  const MAX_PEER_EDGES = 16;
  const txParticipantsPlain = new Map<string, string[]>();
  for (const [scopedTx, keySet] of transactionParticipants.entries()) {
    const participants = Array.from(keySet);
    txParticipantsPlain.set(scopedTx, participants);
    if (participants.length > 1) {
      for (const sourceKey of participants) {
        const src = groupsByKey.get(sourceKey)!;
        const evidence = src.events
          .filter((r) => r.event.transactionKey && scopedIdentity(r.event, r.event.transactionKey) === scopedTx);
        const txKey = evidence[0]?.event.transactionKey;
        const evSeqs = evidence.map((r) => r.event.seq);
        let added = 0;
        for (const targetKey of participants) {
          if (sourceKey === targetKey) continue;
          if (added >= MAX_PEER_EDGES) break;
          const dst = groupsByKey.get(targetKey)!;
          addRelatedEdge(src, {
            id: `rel-tx-${sourceKey}-${targetKey}-${txKey}`,
            targetGroupKey: targetKey,
            targetShortId: dst.shortId,
            targetScope: dst.scope,
            targetProtocol: dst.protocol,
            relationKind: 'shared_transaction',
            direction: 'peer',
            label: `Shared tx ${txKey} with ${dst.shortId}`,
            evidenceSequences: evSeqs,
            transactionKey: txKey,
          });
          added++;
        }
      }
    }
  }

  // 4c. WebTransport QUIC sibling sessions
  const quicSiblingsPlain = new Map<string, string[]>();
  for (const [scopedQuic, keySet] of quicSiblings.entries()) {
    const siblings = Array.from(keySet);
    quicSiblingsPlain.set(scopedQuic, siblings);
    if (siblings.length > 1) {
      for (const sourceKey of siblings) {
        const src = groupsByKey.get(sourceKey)!;
        const evidence = src.events
          .filter((r) => r.event.quicConnectionId && scopedIdentity(r.event, r.event.quicConnectionId) === scopedQuic);
        const quicId = evidence[0]?.event.quicConnectionId;
        const evSeqs = evidence.map((r) => r.event.seq);
        let added = 0;
        for (const targetKey of siblings) {
          if (sourceKey === targetKey) continue;
          if (added >= MAX_PEER_EDGES) break;
          const dst = groupsByKey.get(targetKey)!;
          addRelatedEdge(src, {
            id: `rel-quic-${sourceKey}-${targetKey}-${quicId}`,
            targetGroupKey: targetKey,
            targetShortId: dst.shortId,
            targetScope: dst.scope,
            targetProtocol: dst.protocol,
            relationKind: 'quic_sibling_session',
            direction: 'peer',
            label: `QUIC sibling ${dst.shortId} (${quicId})`,
            evidenceSequences: evSeqs,
            quicConnectionId: quicId,
          });
          added++;
        }
      }
    }
  }

  // Sort groups by most recent first, deterministic tiebreak by groupKey
  groups.sort((a, b) =>
    b.lastRecordedAtMs !== a.lastRecordedAtMs
      ? b.lastRecordedAtMs - a.lastRecordedAtMs
      : a.groupKey.localeCompare(b.groupKey)
  );

  const minRecordedAtMs =
    snapshot.events.length > 0 ? snapshot.events[0].atMs : Date.now();
  const maxRecordedAtMs =
    snapshot.events.length > 0
      ? snapshot.events[snapshot.events.length - 1].atMs
      : minRecordedAtMs + 1000;

  return {
    captureId: snapshot.captureId,
    adapterVersion: snapshot.adapterVersion,
    mode: snapshot.mode,
    syntheticLabel: snapshot.syntheticLabel,
    fixtureId: snapshot.fixtureId,
    sequenceFloor: snapshot.sequenceFloor,
    sequenceCeiling: snapshot.sequenceCeiling,
    retainedCount: snapshot.retainedCount,
    evictedCount: snapshot.evictedCount,
    generatedAt: snapshot.generatedAt,
    bounded: snapshot.bounded,
    minRecordedAtMs,
    maxRecordedAtMs,
    groups,
    groupsByKey,
    unassignedEvents,
    transactionParticipants: txParticipantsPlain,
    quicSiblings: quicSiblingsPlain,
    unknownKindCount: snapshot.unknownKindCount,
  };
}

/**
 * Searches retained correlations.
 * Rule from brief:
 * - Bare ID searches primary correlation IDs and returns disambiguated candidates when multiple scopes/requests/captures match.
 * - Secondary IDs are searched ONLY when the query specifies a prefix (e.g. `req:`, `rpc:`, `stream:`, `quic:`, `sess:`, `tx:`, `inv:`)
 *   OR the caller explicitly selects `idType !== 'correlation_id'`.
 */
export function searchCorrelations(
  index: CorrelationIndex,
  rawQuery: string,
  explicitIdType: SearchIdType = 'correlation_id'
): {
  effectiveIdType: SearchIdType;
  normalizedQuery: string;
  candidates: SearchCandidate[];
  needsDisambiguation: boolean;
} {
  const lookup = parseTraceLookup(rawQuery, explicitIdType);
  if (!lookup) {
    return {
      effectiveIdType: explicitIdType,
      normalizedQuery: '',
      candidates: [],
      needsDisambiguation: false,
    };
  }
  const { field: idType, value: queryVal } = lookup;

  const needle = queryVal.toLowerCase();
  const candidates: SearchCandidate[] = [];

  for (const group of index.groups) {
    let matchedValue: string | undefined;

    switch (idType) {
      case 'correlation_id': {
        if (
          group.scopeIdentity.toLowerCase().includes(needle) ||
          group.groupKey.toLowerCase() === needle
        ) {
          matchedValue = group.scopeIdentity;
        }
        break;
      }
      case 'request_id': {
        matchedValue = group.requestIds.find((v) => v.toLowerCase().includes(needle));
        break;
      }
      case 'rpc_id': {
        matchedValue = group.rpcIds.find((v) => v.toLowerCase().includes(needle));
        break;
      }
      case 'stream_correlation_id': {
        matchedValue = group.streamCorrelationIds.find((v) =>
          v.toLowerCase().includes(needle)
        );
        break;
      }
      case 'quic_connection_id': {
        if (group.quicConnectionId?.toLowerCase().includes(needle)) {
          matchedValue = group.quicConnectionId;
        }
        break;
      }
      case 'transport_session_id': {
        if (group.transportSessionId?.toLowerCase().includes(needle)) {
          matchedValue = group.transportSessionId;
        }
        break;
      }
      case 'transaction_id': {
        matchedValue = group.transactionKeys.find((v) => v.toLowerCase().includes(needle));
        break;
      }
      case 'invocation_id': {
        matchedValue = group.invocationIds.find((v) => v.toLowerCase().includes(needle));
        break;
      }
    }

    if (matchedValue) {
      const disambigParts = [
        protocolLabel(group.protocol),
        scopeLabel(group.scope),
        group.discriminatorLabel ?? 'no discriminator',
        group.service ? `${group.environment} / ${group.service}` : `capture ${group.captureId}`,
      ];
      candidates.push({
        groupKey: group.groupKey,
        group,
        matchedField: idType,
        matchedValue,
        disambiguationLabel: disambigParts.join(' · '),
      });
    }
  }

  // Exact matches rank first
  candidates.sort((a, b) => {
    const aExact = a.matchedValue.toLowerCase() === needle ? 0 : 1;
    const bExact = b.matchedValue.toLowerCase() === needle ? 0 : 1;
    if (aExact !== bExact) return aExact - bExact;
    return b.group.lastRecordedAtMs - a.group.lastRecordedAtMs;
  });

  const exactIdCount = candidates.filter(
    (c) => c.matchedValue.toLowerCase() === needle
  ).length;

  return {
    effectiveIdType: idType,
    normalizedQuery: queryVal,
    candidates,
    needsDisambiguation: candidates.length > 1 && (exactIdCount > 1 || idType === 'correlation_id'),
  };
}
