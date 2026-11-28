export type TransportProtocol = 'rest' | 'http_jsonrpc' | 'websocket' | 'webtransport' | 'database' | 'realtime' | 'unknown';

export type PrimaryProtocol = 'rest' | 'http_jsonrpc' | 'websocket' | 'webtransport';

export type EventOutcome =
  | 'ok'
  | 'committed'
  | 'delivered'
  | 'rejected'
  | 'failed'
  | 'rolled_back'
  | 'open'
  | 'partial'
  | 'unknown';

export type EventRole =
  | 'success'
  | 'rejected'
  | 'partial'
  | 'carrier'
  | 'invocation'
  | 'neutral';

export type EventSource = 'app' | 'runtime' | 'kernel' | 'broker' | 'database' | 'unknown';

export type DatasetMode = 'live' | 'recorded';

export type RecordedDatasetId = 'recorded-v1.2-synthetic' | 'recorded-stress-10k';

export type ThemeId = 'nocturne' | 'paper' | 'porcelain' | 'parchment' | 'ink' | 'graphite';

export type DensityId = 'dense' | 'compact' | 'comfortable';

export type RouteId = 'explore' | 'distributions';

export type ExploreViewMode = 'karyogram' | 'event-table';

export type DistributionMeasure =
  | 'invocation_latency'
  | 'transaction_latency'
  | 'delivery_latency'
  | 'outcome_breakdown'
  | 'wt_lane_mix';

export type DistributionChartMode = 'histogram' | 'cdf';
export type DistributionYMode = 'count' | 'probability';

export type TypedIdKey =
  | 'session_id'
  | 'transport_session_id'
  | 'connection_id'
  | 'request_id'
  | 'correlation_id'
  | 'stream_id'
  | 'stream_correlation_id'
  | 'invocation_id'
  | 'rpc_id'
  | 'datagram_id'
  | 'subscription_id'
  | 'lease_id'
  | 'publication_id'
  | 'delivery_id'
  | 'origin_invocation_id'
  | 'origin_correlation_id'
  | 'engine_session_id'
  | 'transaction_id';

export interface TimingObservation {
  measure: 'invocation_latency' | 'transaction_latency' | 'delivery_latency';
  unit: 'ms';
  value: number;
  clock_domain: string;
  timing_boundary: string;
  provenance: string;
}

export interface RawTraceEvent {
  sequence: number;
  at: string; // Sink capture timestamp (UTC ISO-8601) — always labeled "Recorded at"
  kind: string;
  transport: TransportProtocol;
  source?: EventSource;
  framing?: string;
  outcome?: EventOutcome;
  http_status?: number;
  direction?: 'inbound' | 'outbound' | 'bidirectional' | 'unidirectional';
  label?: string;
  scenario_run_id?: string;
  capture_id?: string;

  // Strictly typed opaque string identifiers (never coerced to unsafe JS numbers)
  session_id?: string;
  transport_session_id?: string;
  connection_id?: string;
  request_id?: string;
  correlation_id?: string;
  stream_id?: string;
  stream_correlation_id?: string;
  invocation_id?: string;
  rpc_id?: string;
  rpc_item_index?: number;
  datagram_id?: string;
  subscription_id?: string;
  attachment_generation?: number;
  lease_id?: string;
  publication_id?: string;
  delivery_id?: string;
  origin_invocation_id?: string;
  origin_correlation_id?: string;
  engine_session_id?: string;
  transaction_id?: string;
  flush_id?: string;
  atom_label?: string;
  atom_phase?: string;
  atom_ordinal?: number;
  atom_trace_dropped?: number;
  note_id?: string;

  // Producer-measured timing observation (additive timing contract)
  observation?: TimingObservation;
  duration_ms?: number;
  measured_duration_ms?: number;
  op_model?: string;
  op_alias?: string;
  hook_name?: string;
  hook_phase?: string;
  source_started_at?: string;
  source_ended_at?: string;
  timing_boundary?: string;
  clock_domain?: string;

  // Allowlisted, redacted metadata only
  metadata?: Record<string, string | number | boolean | null>;
}

export interface TraceRollup {
  connections: number;
  transport_sessions: number;
  invocations: number;
  subscriptions: number;
  publications: number;
  deliveries: number;
  transactions: number;
  by_protocol: Record<PrimaryProtocol, {
    events: number;
    connections: number;
    sessions: number;
    invocations: number;
    errors: number;
  }>;
}

export interface ScenarioRunSummary {
  run_id: string;
  status: 'completed' | 'partial' | 'failed';
  started_at: string;
  completed_at: string;
  duration_ms: number;
  emitted_events: number;
  note_id: string;
  transports: Record<PrimaryProtocol, string>;
  error?: string;
}

export interface TraceSnapshot {
  revision: number;
  capture_id: string;
  captured_at: string;
  dataset_label?: string;
  is_synthetic?: boolean;
  retention_limit: number;
  retained_range: {
    min_sequence: number;
    max_sequence: number;
    total_emitted: number;
    evicted_count: number;
  };
  running: boolean;
  active_run_id: string | null;
  last_run_summary: ScenarioRunSummary | null;
  events: RawTraceEvent[];
  rollup?: TraceRollup;
  next_before?: number | null;
}

export interface NormalizedEvent extends RawTraceEvent {
  id: string; // Stable synthetic key: `${capture_id}:${sequence}`
  atMs: number;
  normalizedKind: string;
  knownKind: boolean;
  role: EventRole;
  displayLabel: string;
  outcomeLabel: string;
  source: EventSource;
  scopedStreamKey?: string; // `${transport_session_id}::${stream_id}`
  scopedTransactionKey?: string; // `${engine_session_id}::${transaction_id}`
  scopedRpcKey?: string; // `${correlation_id || request_id || invocation_id}::${rpc_id}${rpc_item_index != null ? `#${rpc_item_index}` : ''}`
}

export type EntityKind =
  | 'protocol'
  | 'connection'
  | 'transport_session'
  | 'request'
  | 'stream'
  | 'datagrams'
  | 'invocation'
  | 'subscription'
  | 'engine_session'
  | 'transaction';

export interface EntityLink {
  targetType: EntityKind | 'event';
  targetId: string;
  label: string;
  relationship: string;
  unretained?: boolean;
  evidenceSequences: number[];
}

export interface TypedEntity {
  id: string; // e.g. `connection:quic-conn-01`, `tx:eng-1::tx-101`
  entityKind: EntityKind;
  transport: TransportProtocol;
  label: string;
  shortId: string;
  fullId: string;
  idField: TypedIdKey | 'composite';
  parentId: string | null;
  eventSequences: number[];
  startMs: number | null;
  endMs: number | null;
  isOpen: boolean;
  outcome: EventOutcome;
  role: EventRole;
  links: EntityLink[];
  childrenIds: string[];
  extraCaption?: string;
  typedIds: Partial<Record<TypedIdKey, string>>;
  attachmentGenerations?: Array<{
    generation: number;
    transport_session_id?: string;
    lease_id?: string;
    at: string;
    sequence: number;
    status: string;
  }>;
  txLifecycle?: {
    engine_session_id: string;
    transaction_id: string;
    beginSequence?: number;
    terminalSequence?: number;
    terminalOutcome: EventOutcome;
    participantInvocationIds: string[];
    durationMs?: number;
  };
}

export interface RelationshipArc {
  id: string;
  fromRowId: string;
  fromMs: number;
  toRowId: string;
  toMs: number;
  label: string;
  role: EventRole;
  dashed: boolean;
}

export interface KaryogramRow {
  rowId: string;
  entityId: string;
  entityKind: EntityKind;
  transport: TransportProtocol;
  depth: number;
  label: string;
  shortId: string;
  hasChildren: boolean;
  isExpanded: boolean;
  events: NormalizedEvent[];
  startMs: number | null;
  endMs: number | null;
  isOpen: boolean;
  role: EventRole;
  countLabel: string;
  measuredLatencyMedianMs?: number | null;
  isGroupBoundary?: boolean;
}

export interface FilterState {
  protocols: PrimaryProtocol[];
  includeDatabase: boolean;
  kind: string;
  outcome: string;
  source: string;
  searchQuery: string;
  fromMs: number | null;
  toMs: number | null;
  cohortEventIds: string[] | null;
  cohortLabel: string | null;
  bucketFilter: {
    rowId: string;
    startMs: number;
    endMs: number;
    count: number;
  } | null;
}

export interface SelectionState {
  type: 'event' | 'entity';
  id: string;
  labelHint?: string;
}

export interface DistributionBin {
  index: number;
  low: number;
  high: number;
  inclusiveUpper: boolean;
  count: number;
  probability: number;
  cumulativeProbability: number;
  eventIds: string[];
}

export interface QuantileSummary {
  n: number;
  p50: number | null;
  p90: number | null;
  p95: number | null;
  p99: number | null;
  max: number | null;
  limitedSample: boolean;
}

export interface DistributionLaneResult {
  key: string;
  label: string;
  protocol: TransportProtocol;
  unit: string;
  timingBoundary: string;
  scope: string;
  eligibleCount: number;
  excludedCount: number;
  excludedReasons: Record<string, number>;
  bins: DistributionBin[];
  quantiles: QuantileSummary;
  observations: Array<{
    eventId: string;
    sequence: number;
    atMs: number;
    value: number;
    label: string;
    outcome: EventOutcome;
    role: EventRole;
  }>;
}
