export type DatasetMode = 'live' | 'recorded';

export type TransportProtocol = 'rest' | 'jsonrpc' | 'websocket' | 'webtransport' | 'unknown';

export type CorrelationScope =
  | 'http_request'
  | 'rpc_request'
  | 'ws_logical'
  | 'wt_session'
  | 'wt_stream';

export type SearchIdType =
  | 'correlation_id'
  | 'request_id'
  | 'rpc_id'
  | 'stream_correlation_id'
  | 'quic_connection_id'
  | 'transport_session_id'
  | 'transaction_id'
  | 'invocation_id';

export type TimeBasis =
  | 'recorded_at'
  | 'measured_monotonic'
  | 'partial_mixed'
  | 'clock_skewed';

export type DirectionLabel =
  | 'Observed at server'
  | 'Ingress'
  | 'Egress'
  | 'Direction unavailable';

export type ProvenanceLabel = 'Reported correlation' | 'Linked by evidence';

export type OutcomeStatus =
  | 'ok'
  | 'error'
  | 'no_reply_expected'
  | 'reply_not_observed'
  | 'incomplete'
  | 'observed'
  | 'partial';

export type CoverageLabel =
  | 'Complete'
  | 'Partial (Reply not observed)'
  | 'Partial (Observed-at only)'
  | 'Notification (No reply expected)'
  | 'Skewed clocks'
  | 'Evicted endpoint'
  | 'Bounded evidence'
  | 'Observed only';

export type KnownEventKind =
  | 'http.request.received'
  | 'http.response.sent'
  | 'rpc.document.received'
  | 'rpc.batch.item.invoked'
  | 'rpc.batch.item.completed'
  | 'rpc.notification.received'
  | 'rpc.response.sent'
  | 'invocation.started'
  | 'invocation.completed'
  | 'hook.completed'
  | 'atom.completed'
  | 'atom.failed'
  | 'db.tx.participant'
  | 'db.tx.begin'
  | 'db.tx.query'
  | 'db.tx.commit'
  | 'db.tx.rollback'
  | 'db.flush.completed'
  | 'db.flush.failed'
  | 'ws.session.opened'
  | 'ws.frame.received'
  | 'ws.frame.sent'
  | 'ws.broker.publish'
  | 'ws.broker.delivery'
  | 'ws.subscription.attached'
  | 'wt.quic.connected'
  | 'wt.session.opened'
  | 'wt.stream.opened'
  | 'wt.stream.frame.received'
  | 'wt.stream.frame.sent'
  | 'wt.stream.closed'
  | 'wt.datagram.received'
  | 'wt.datagram.sent';

export interface RawTraceEventInput {
  seq: number;
  at: string; // ISO-8601 UTC recorded-at timestamp
  kind: string;
  protocol: TransportProtocol;
  direction?: 'inbound' | 'outbound' | 'internal' | 'unknown';
  observer?: string;
  op_model?: string;
  op_alias?: string;
  hook_name?: string;
  hook_phase?: string;
  service?: string;
  environment?: string;
  // Opaque IDs (may arrive as number or string at adapter boundary)
  correlation_id?: string | number | null;
  origin_correlation_id?: string | number | null;
  origin_invocation_id?: string | number | null;
  receiving_correlation_id?: string | number | null;
  request_id?: string | number | null;
  rpc_id?: string | number | null;
  rpc_item_index?: number | null;
  rpc_is_notification?: boolean;
  invocation_id?: string | number | null;
  transport_session_id?: string | number | null;
  requester_session_id?: string | number | null;
  quic_connection_id?: string | number | null;
  stream_id?: string | number | null;
  stream_correlation_id?: string | number | null;
  datagram_id?: string | number | null;
  subscription_id?: string | number | null;
  attachment_generation?: string | number | null;
  destination_id?: string | number | null;
  engine_session_id?: string | number | null;
  transaction_id?: string | number | null;
  flush_id?: string | null;
  atom_label?: string | null;
  atom_phase?: string | null;
  atom_ordinal?: number | null;
  atom_trace_dropped?: number | null;
  // Timing & measurement fields
  source_started_at?: string | null;
  source_ended_at?: string | null;
  measured_duration_ms?: number | null;
  timing_boundary?: string | null;
  clock_domain?: string | null;
  // Outcome & metadata
  outcome?: 'ok' | 'error' | 'incomplete' | 'unknown' | null;
  status_code?: number | null;
  method?: string | null;
  route?: string | null;
  topic?: string | null;
  bytes?: number | null;
  note?: string | null;
  // Explicit linkage hints
  linked_from_seq?: number | null;
  external_endpoint_label?: string | null;
  evicted_endpoint_id?: string | null;
  // Arbitrary extra keys (must be stripped by allowlist)
  [key: string]: unknown;
}

export interface NormalizedTraceEvent {
  seq: number;
  at: string;
  atMs: number;
  kind: string;
  isKnownKind: boolean;
  protocol: TransportProtocol;
  directionLabel: DirectionLabel;
  rawDirection: 'inbound' | 'outbound' | 'internal' | 'unknown';
  observer: string;
  service?: string;
  environment?: string;
  // Losslessly stringified opaque IDs
  correlationId?: string;
  originCorrelationId?: string;
  originInvocationId?: string;
  receivingCorrelationId?: string;
  requestId?: string;
  rpcId?: string;
  rpcItemIndex?: number;
  rpcIsNotification: boolean;
  invocationId?: string;
  transportSessionId?: string;
  requesterSessionId?: string;
  quicConnectionId?: string;
  streamId?: string;
  streamCorrelationId?: string;
  datagramId?: string;
  subscriptionId?: string;
  attachmentGeneration?: string;
  destinationId?: string;
  engineSessionId?: string;
  transactionId?: string;
  transactionKey?: string; // engine_session_id + transaction_id
  // Timing
  sourceStartedAt?: string;
  sourceStartedAtMs?: number;
  sourceEndedAt?: string;
  sourceEndedAtMs?: number;
  measuredDurationMs?: number;
  timingBoundary?: string;
  clockDomain?: string;
  timeBasis: TimeBasis;
  // Outcomes & allowlisted metadata
  outcome: 'ok' | 'error' | 'incomplete' | 'unknown';
  statusCode?: number;
  allowlistedMeta: Record<string, string | number | boolean>;
  linkedFromSeq?: number;
  externalEndpointLabel?: string;
  evictedEndpointId?: string;
}

export interface TraceSnapshotInput {
  capture_id: string;
  adapter_version?: string;
  mode: DatasetMode;
  synthetic_label?: string;
  fixture_id?: string;
  sequence_floor: number;
  sequence_ceiling: number;
  retained_count: number;
  evicted_count: number;
  generated_at: string;
  bounded?: boolean;
  events: RawTraceEventInput[];
}

export interface NormalizedSnapshot {
  captureId: string;
  adapterVersion: string;
  mode: DatasetMode;
  syntheticLabel?: string;
  fixtureId?: string;
  sequenceFloor: number;
  sequenceCeiling: number;
  retainedCount: number;
  evictedCount: number;
  generatedAt: string;
  bounded?: boolean;
  events: NormalizedTraceEvent[];
  unknownKindCount: number;
}

export interface OwnedEventRecord {
  event: NormalizedTraceEvent;
  provenance: ProvenanceLabel;
  linkageBasis: string;
}

export interface RelatedCorrelationEdge {
  id: string;
  targetGroupKey: string;
  targetShortId: string;
  targetScope: CorrelationScope;
  targetProtocol: TransportProtocol;
  relationKind:
    | 'publish_to_delivery'
    | 'delivery_from_origin'
    | 'shared_transaction'
    | 'quic_sibling_session'
    | 'child_stream'
    | 'parent_session';
  direction: 'outbound' | 'inbound' | 'peer';
  label: string;
  evidenceSequences: number[];
  attachmentGeneration?: string;
  destinationId?: string;
  subscriptionId?: string;
  transactionKey?: string;
  quicConnectionId?: string;
}

export interface DeliveryOutcomeBreakdown {
  ok: number;
  error: number;
  noReplyExpected: number;
  replyNotObserved: number;
  incomplete: number;
}

export interface GroupMetrics {
  observedEvents: number;
  invocations: number;
  transactions: number;
  deliveryOutcomes: DeliveryOutcomeBreakdown;
  coverage: CoverageLabel;
  streams?: number;
  datagrams?: number;
}

export interface CorrelationGroup {
  groupKey: string; // capture-qualified opaque key
  captureId: string;
  scope: CorrelationScope;
  protocol: TransportProtocol;
  scopeIdentity: string;
  discriminator?: string;
  discriminatorLabel?: string;
  shortId: string;
  displayTitle: string;
  service?: string;
  environment?: string;
  httpStatus?: number;
  committedTransactions: number;
  rolledBackTransactions: number;
  firstRecordedAt: string;
  firstRecordedAtMs: number;
  lastRecordedAt: string;
  lastRecordedAtMs: number;
  recordedSpanMs: number;
  events: OwnedEventRecord[];
  relatedCorrelations: RelatedCorrelationEdge[];
  metrics: GroupMetrics;
  outcomeSummary: OutcomeStatus;
  hasClockSkew: boolean;
  hasEvictedEndpoint: boolean;
  // Secondary indexed IDs for explicit typed search
  requestIds: string[];
  rpcIds: string[];
  streamCorrelationIds: string[];
  quicConnectionId?: string;
  transportSessionId?: string;
  requesterSessionId?: string;
  transactionKeys: string[];
  invocationIds: string[];
}

export interface UnassignedEventRecord {
  event: NormalizedTraceEvent;
  reason: string;
  ambiguousCandidateKeys: string[];
}

export interface CorrelationIndex {
  captureId: string;
  adapterVersion: string;
  mode: DatasetMode;
  syntheticLabel?: string;
  fixtureId?: string;
  sequenceFloor: number;
  sequenceCeiling: number;
  retainedCount: number;
  evictedCount: number;
  generatedAt: string;
  bounded?: boolean;
  minRecordedAtMs: number;
  maxRecordedAtMs: number;
  groups: CorrelationGroup[];
  groupsByKey: Map<string, CorrelationGroup>;
  unassignedEvents: UnassignedEventRecord[];
  transactionParticipants: Map<string, string[]>; // transactionKey -> groupKeys
  quicSiblings: Map<string, string[]>; // quicConnectionId -> groupKeys
  unknownKindCount: number;
}

export interface SearchCandidate {
  groupKey: string;
  group: CorrelationGroup;
  matchedField: SearchIdType;
  matchedValue: string;
  disambiguationLabel: string;
}

export type WaterfallLaneKind =
  | 'round_trip'
  | 'requester'
  | 'session_transport'
  | 'ingress'
  | 'invocation'
  | 'batch_group'
  | 'batch_item'
  | 'streams_group'
  | 'stream_lane'
  | 'datagrams_lane'
  | 'subscriptions_group'
  | 'subscription_lane'
  | 'transactions_group'
  | 'transaction_lane'
  | 'egress'
  | 'related_context_group'
  | 'related_context_lane';

export interface WaterfallMark {
  id: string;
  seq: number;
  laneKey: string;
  at: string;
  atMs: number;
  endAtMs?: number;
  measuredDurationMs?: number;
  timeBasis: TimeBasis;
  kind: string;
  label: string;
  glyph: 'point' | 'interval' | 'datagram' | 'tx' | 'open_ended' | 'unknown';
  outcome: OutcomeStatus;
  directionLabel: DirectionLabel;
  provenance: ProvenanceLabel;
  linkageBasis: string;
  stackOffset: number; // px offset for same-time marks
  timelineNodeOffset?: number; // vertical offset from a collapsed timeline bar
  isLinkedContext: boolean;
  clockOrderUncertain: boolean;
  evidenceSequences?: number[];
  transactionBoundaries?: WaterfallMark[];
  reason?: string;
  event: NormalizedTraceEvent;
}

export interface WaterfallEdge {
  id: string;
  fromKey: string;
  toKey: string;
  fromLabel: string;
  toLabel: string;
  kind:
    | 'request_ingress'
    | 'response_egress'
    | 'invocation_dispatch'
    | 'tx_participation'
    | 'stream_handoff'
    | 'publish_fanout'
    | 'related_link'
    | 'missing_endpoint';
  direction: DirectionLabel;
  evidenceSequences: number[];
  coverage: 'complete' | 'partial' | 'evicted' | 'hidden' | 'external' | 'clock_uncertain';
  timeBasis: TimeBasis;
  startAtMs: number;
  endAtMs: number;
  measuredDurationMs?: number;
  clockOrderUncertain: boolean;
  dashed: boolean;
  endpointChip?: string;
  relatedGroupKey?: string;
  reason?: string;
  outcome: OutcomeStatus;
  textSummary: string;
}

export interface WaterfallLane {
  collapseToTimeline?: boolean;
  laneKey: string;
  parentKey?: string;
  depth: number;
  label: string;
  sublabel?: string;
  kind: WaterfallLaneKind;
  defaultExpanded: boolean;
  collapsible: boolean;
  isLinkedContext: boolean;
  relatedGroupKey?: string;
  markCount: number;
  marks: WaterfallMark[];
  childrenKeys: string[];
}

export interface WaterfallModel {
  groupKey: string;
  minTimeMs: number;
  maxTimeMs: number;
  lanes: WaterfallLane[];
  marks: WaterfallMark[];
  edges: WaterfallEdge[];
  hasLinkedContext: boolean;
  timeBasisSummary: string;
}

export interface KaryogramBucket {
  index: number;
  startMs: number;
  endMs: number;
  count: number;
  groupKeys: string[];
}

export interface KaryogramRow {
  rowKey: string;
  protocol: TransportProtocol;
  scope: CorrelationScope;
  label: string;
  groupCount: number;
  eventCount: number;
  buckets: KaryogramBucket[];
}

export interface KaryogramData {
  minTimeMs: number;
  maxTimeMs: number;
  bucketCount: number;
  maxBucketCount: number;
  rows: KaryogramRow[];
}

export type CompareMeasureId =
  | 'measured_request_latency'
  | 'engine_transaction_duration'
  | 'stream_invocation_duration';

export interface MeasureObservation {
  id: string;
  entityKey: string; // deduplicated by typed key (e.g., txKey)
  groupKey: string;
  groupShortId: string;
  protocol: TransportProtocol;
  valueMs: number;
  timingBoundary: string;
  clockSource: string;
  label: string;
}

export interface ExcludedObservation {
  groupKey: string;
  groupShortId: string;
  protocol: TransportProtocol;
  reason: string;
}

export interface HistogramBin {
  binIndex: number;
  startMs: number;
  endMs: number;
  count: number;
  empiricalProbability: number;
  contributors: MeasureObservation[];
}

export interface EcdfPoint {
  valueMs: number;
  cumulativeProbability: number;
  observation: MeasureObservation;
}

export interface CohortDistribution {
  protocol: TransportProtocol;
  measureId: CompareMeasureId;
  measureLabel: string;
  units: 'ms';
  timingBoundary: string;
  clockSource: string;
  eligibleCount: number;
  excludedCount: number;
  excludedReasons: Record<string, number>;
  excludedSamples: ExcludedObservation[];
  minMs: number | null;
  maxMs: number | null;
  medianMs: number | null;
  p95Ms: number | null; // null if eligibleCount < 20
  p95SuppressedReason?: string;
  p99Ms: number | null; // null if eligibleCount < 100
  p99SuppressedReason?: string;
  bins: HistogramBin[];
  ecdf: EcdfPoint[];
  observations: MeasureObservation[];
}
