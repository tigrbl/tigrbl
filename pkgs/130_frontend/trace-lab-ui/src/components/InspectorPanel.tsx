import React, { useEffect, useState } from 'react';
import {
  Check,
  ChevronRight,
  Copy,
  Database,
  Link2,
  X,
} from 'lucide-react';
import {
  EntityGraph,
  formatOutcomeLabel,
  formatUtcTime,
  truncateId,
  TYPED_ID_KEYS,
} from '../adapter/traceAdapter';
import { PROTOCOL_LABELS } from '../theme/tokens';
import {
  NormalizedEvent,
  SelectionState,
  TypedEntity,
} from '../types/trace';
import { RoleMark } from './RoleMark';
import { CorrelationLink } from './CorrelationLink';

interface InspectorPanelProps {
  selection: SelectionState | null;
  selectionStatus:
    | { state: 'none' }
    | { state: 'found'; event?: NormalizedEvent; entity?: TypedEntity }
    | { state: 'evicted'; id: string };
  graph: EntityGraph;
  onSelect: (sel: SelectionState | null) => void;
  onClose: () => void;
  onFollowCorrelation?: (href: string) => void;
}

export const InspectorPanel: React.FC<InspectorPanelProps> = ({
  selection,
  selectionStatus,
  graph,
  onSelect,
  onClose,
  onFollowCorrelation,
}) => {
  const [copiedKey, setCopiedKey] = useState<string | null>(null);
  const [metadataOpen, setMetadataOpen] = useState(false);
  const [txAccordionOpen, setTxAccordionOpen] = useState(true);
  const [subAccordionOpen, setSubAccordionOpen] = useState(true);

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && selection) {
        onClose();
      }
    };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [selection, onClose]);

  if (!selection || selectionStatus.state === 'none') return null;

  const copyText = (key: string, value: string) => {
    navigator.clipboard?.writeText(value).catch(() => {});
    setCopiedKey(key);
    window.setTimeout(() => setCopiedKey(null), 1500);
  };

  // Evicted selection state: retain link & explain expiry
  if (selectionStatus.state === 'evicted') {
    return (
      <aside
        aria-label="Event inspector"
        className="w-full xl:w-[368px] shrink-0 rounded-[5px] border flex flex-col overflow-hidden"
        style={{
          backgroundColor: 'var(--panel)',
          borderColor: 'var(--border)',
          boxShadow: 'var(--overlay-shadow)',
        }}
      >
        <div
          className="px-4 py-3 border-b flex items-center justify-between gap-2"
          style={{ borderColor: 'var(--border)' }}
        >
          <h2 className="text-[15px] font-semibold" style={{ color: 'var(--text-primary)' }}>
            Selection no longer retained
          </h2>
          <button
            type="button"
            onClick={onClose}
            aria-label="Close inspector"
            className="p-1 rounded-[4px] cursor-pointer"
            style={{ color: 'var(--text-muted)' }}
          >
            <X size={16} aria-hidden="true" />
          </button>
        </div>
        <div className="p-4 space-y-3 text-[13px]">
          <div className="font-mono-data text-[12px] break-all p-2 rounded-[4px] border" style={{ backgroundColor: 'var(--canvas)', borderColor: 'var(--border)' }}>
            {selectionStatus.id}
          </div>
          <p style={{ color: 'var(--text-muted)' }}>
            This record was evicted by the server retention limit (750 events) or belongs to a
            previous capture session. Your active filter and time window remain preserved.
          </p>
          <button
            type="button"
            onClick={onClose}
            className="h-8 px-3 rounded-[4px] border text-[13px] cursor-pointer"
            style={{
              backgroundColor: 'var(--canvas)',
              borderColor: 'var(--border)',
              color: 'var(--text-primary)',
            }}
          >
            Dismiss selection
          </button>
        </div>
      </aside>
    );
  }

  const ev = selectionStatus.event;
  const entity = selectionStatus.entity;

  // Derive associated entity when inspecting an event
  const associatedEntities: TypedEntity[] = ev
    ? (graph.eventToEntityIds.get(ev.id) ?? [])
        .map((id) => graph.entities.get(id))
        .filter((e): e is TypedEntity => e !== undefined && e.entityKind !== 'protocol')
    : entity
      ? [entity]
      : [];

  // Gather typed IDs strictly as opaque strings
  const idEntries: Array<{ key: string; label: string; value: string }> = [];
  const seenIdKey = new Set<string>();
  for (const { key, label } of TYPED_ID_KEYS) {
    const val = ev ? ev[key] : entity?.typedIds[key];
    if (val && !seenIdKey.has(key)) {
      seenIdKey.add(key);
      idEntries.push({ key, label, value: val });
    }
  }
  if (ev?.rpc_item_index !== undefined) {
    idEntries.push({ key: 'rpc_item_index', label: 'RPC batch index', value: String(ev.rpc_item_index) });
  }
  if (ev?.attachment_generation !== undefined) {
    idEntries.push({
      key: 'attachment_generation',
      label: 'Attachment generation',
      value: String(ev.attachment_generation),
    });
  }
  if (ev?.note_id) {
    idEntries.push({ key: 'note_id', label: 'Shared note (scenario)', value: ev.note_id });
  }

  // Find linked DB transactions
  const linkedTransactions: TypedEntity[] = [];
  const seenTx = new Set<string>();
  const addTxIfFound = (txEntityId: string) => {
    if (seenTx.has(txEntityId)) return;
    const t = graph.entities.get(txEntityId);
    if (t && t.entityKind === 'transaction') {
      seenTx.add(txEntityId);
      linkedTransactions.push(t);
    }
  };

  if (entity?.entityKind === 'transaction') {
    addTxIfFound(entity.id);
  } else if (ev?.scopedTransactionKey) {
    addTxIfFound(`transaction:${ev.scopedTransactionKey}`);
  }
  const invId = ev?.invocation_id || (entity?.entityKind === 'invocation' ? entity.fullId : undefined);
  if (invId) {
    const txSet = graph.invocationToTxIds.get(`invocation:${invId}`);
    if (txSet) txSet.forEach(addTxIfFound);
  }

  // Find linked WS subscription if any
  const subEntity =
    (entity?.entityKind === 'subscription' ? entity : null) ||
    (ev?.subscription_id ? graph.entities.get(`subscription:${ev.subscription_id}`) ?? null : null);

  // Collect related entities (placed ABOVE raw metadata accordion per spec)
  const relatedLinks: Array<{
    key: string;
    label: string;
    relationship: string;
    target: SelectionState;
    unretained?: boolean;
  }> = [];
  const seenRel = new Set<string>();

  for (const ae of associatedEntities) {
    if (ev) {
      const k = `ent:${ae.id}`;
      if (!seenRel.has(k)) {
        seenRel.add(k);
        relatedLinks.push({
          key: k,
          label: `${ae.label} (${ae.shortId})`,
          relationship: ae.entityKind.replace('_', ' '),
          target: { type: 'entity', id: ae.id },
        });
      }
    }
    for (const l of ae.links) {
      const k = `link:${l.targetId}:${l.relationship}`;
      if (seenRel.has(k)) continue;
      seenRel.add(k);
      relatedLinks.push({
        key: k,
        label: l.label,
        relationship: l.relationship,
        target: { type: l.targetType === 'event' ? 'event' : 'entity', id: l.targetId },
        unretained: l.unretained,
      });
    }
  }

  // If entity has child entities or events, expose quick jump links
  const entityEvents = entity
    ? entity.eventSequences
        .map((s) => graph.eventBySequence.get(s))
        .filter((x): x is NormalizedEvent => Boolean(x))
    : [];

  return (
    <aside
      aria-label="Trace record inspector"
      className="w-full xl:w-[368px] shrink-0 rounded-[5px] border flex flex-col max-h-[82vh] xl:max-h-[calc(100vh-140px)] overflow-hidden xl:sticky xl:top-[64px]"
      style={{
        backgroundColor: 'var(--panel)',
        borderColor: 'var(--border)',
        boxShadow: 'var(--overlay-shadow)',
      }}
    >
      {/* Inspector Header */}
      <div
        className="px-4 py-3 border-b flex items-start justify-between gap-2 shrink-0"
        style={{ borderColor: 'var(--border)' }}
      >
        <div className="min-w-0 space-y-1">
          <div className="flex items-center gap-2 text-[12px]" style={{ color: 'var(--text-muted)' }}>
            <span>{PROTOCOL_LABELS[(ev?.transport ?? entity?.transport) || 'rest']}</span>
            <span aria-hidden="true">·</span>
            <span>{ev ? `Event #${ev.sequence}` : entity?.entityKind.replace('_', ' ')}</span>
          </div>
          <h2
            className="text-[15px] leading-[20px] font-semibold break-words"
            style={{ color: 'var(--text-primary)' }}
          >
            {ev ? ev.displayLabel : entity?.label}
          </h2>
          <div className="flex items-center gap-2 text-[12px]">
            <RoleMark
              role={ev ? ev.role : entity!.role}
              kind={ev?.kind}
              label={
                ev
                  ? ev.outcomeLabel
                  : entity?.isOpen
                    ? 'Open / still in flight'
                    : formatOutcomeLabel(entity?.outcome)
              }
            />
            {ev?.framing && (
              <>
                <span aria-hidden="true" style={{ color: 'var(--text-muted)' }}>·</span>
                <span className="font-mono-data" style={{ color: 'var(--text-muted)' }}>
                  {ev.framing}
                </span>
              </>
            )}
          </div>
        </div>

        <button
          type="button"
          onClick={onClose}
          aria-label="Close inspector (Escape)"
          className="p-1.5 rounded-[4px] cursor-pointer row-hover shrink-0"
          style={{ color: 'var(--text-muted)' }}
        >
          <X size={16} aria-hidden="true" />
        </button>
      </div>

      {/* Scrollable Inspector Body */}
      <div className="flex-1 overflow-y-auto divide-y" style={{ borderColor: 'var(--border)' }}>
        {/* Timing & Provenance Section */}
        <div className="px-4 py-3 space-y-1.5 text-[12px]">
          <div className="font-semibold text-[12px]" style={{ color: 'var(--text-primary)' }}>
            Timing &amp; provenance
          </div>
          {ev ? (
            <>
              <div className="flex justify-between gap-2">
                <span style={{ color: 'var(--text-muted)' }}>Recorded at (sink)</span>
                <span className="font-mono-data" style={{ color: 'var(--text-primary)' }}>
                  {ev.at}
                </span>
              </div>
              <div className="flex justify-between gap-2">
                <span style={{ color: 'var(--text-muted)' }}>Source / Kind</span>
                <span className="font-mono-data truncate" style={{ color: 'var(--text-primary)' }}>
                  {ev.source} · {ev.kind}
                </span>
              </div>
              {ev.observation || ev.duration_ms !== undefined ? (
                <>
                  <div className="flex justify-between gap-2">
                    <span style={{ color: 'var(--text-muted)' }}>Measured duration</span>
                    <span className="font-mono-data font-medium" style={{ color: 'var(--accent)' }}>
                      {(ev.observation?.value ?? ev.duration_ms)?.toFixed(2)} ms
                    </span>
                  </div>
                  <div className="flex justify-between gap-2">
                    <span style={{ color: 'var(--text-muted)' }}>Clock domain</span>
                    <span className="font-mono-data" style={{ color: 'var(--text-primary)' }}>
                      {ev.observation?.clock_domain ?? ev.clock_domain ?? 'server.monotonic_ns'}
                    </span>
                  </div>
                  <div className="text-[11px] font-mono-data" style={{ color: 'var(--text-muted)' }}>
                    Boundary: {ev.observation?.timing_boundary ?? ev.timing_boundary}
                  </div>
                </>
              ) : (
                <div className="text-[11px]" style={{ color: 'var(--text-muted)' }}>
                  Sink capture timestamp only — no producer-measured duration on this record.
                </div>
              )}
            </>
          ) : entity ? (
            <>
              <div className="flex justify-between gap-2">
                <span style={{ color: 'var(--text-muted)' }}>First recorded</span>
                <span className="font-mono-data" style={{ color: 'var(--text-primary)' }}>
                  {entity.startMs !== null ? formatUtcTime(entity.startMs) : '—'}
                </span>
              </div>
              <div className="flex justify-between gap-2">
                <span style={{ color: 'var(--text-muted)' }}>Last recorded</span>
                <span className="font-mono-data" style={{ color: 'var(--text-primary)' }}>
                  {entity.endMs !== null ? formatUtcTime(entity.endMs) : '—'}
                </span>
              </div>
              <div className="flex justify-between gap-2">
                <span style={{ color: 'var(--text-muted)' }}>Retained records</span>
                <span className="font-mono-data" style={{ color: 'var(--text-primary)' }}>
                  {entity.eventSequences.length}
                </span>
              </div>
            </>
          ) : null}
        </div>

        {/* Typed Identifiers with Full Opaque Values & Copy Actions */}
        {idEntries.length > 0 && (
          <div className="px-4 py-3 space-y-2">
            <div className="font-semibold text-[12px]" style={{ color: 'var(--text-primary)' }}>
              Typed identifiers
            </div>
            <dl className="space-y-1.5">
              {idEntries.map((item) => (
                <div
                  key={item.key}
                  className="flex items-center justify-between gap-2 text-[12px]"
                >
                  <dt className="shrink-0" style={{ color: 'var(--text-muted)' }}>
                    {item.label}
                  </dt>
                  <dd className="flex items-center gap-1 min-w-0">
                    {item.key === 'correlation_id' && onFollowCorrelation ? (
                      <CorrelationLink id={item.value} sequence={ev?.sequence} onFollowCorrelation={onFollowCorrelation} />
                    ) : (
                      <span className="font-mono-data truncate" style={{ color: 'var(--text-primary)' }} title={item.value}>
                        {item.value}
                      </span>
                    )}
                    <button
                      type="button"
                      onClick={() => copyText(item.key, item.value)}
                      aria-label={`Copy ${item.label} ${item.value}`}
                      className="p-1 rounded-[3px] shrink-0 cursor-pointer row-hover"
                      style={{ color: copiedKey === item.key ? 'var(--role-success)' : 'var(--text-muted)' }}
                    >
                      {copiedKey === item.key ? (
                        <Check size={12} aria-hidden="true" />
                      ) : (
                        <Copy size={12} aria-hidden="true" />
                      )}
                    </button>
                  </dd>
                </div>
              ))}
            </dl>
          </div>
        )}

        {/* Database Transaction Lifecycle Accordion */}
        {linkedTransactions.length > 0 && (
          <div className="px-4 py-3">
            <button
              type="button"
              onClick={() => setTxAccordionOpen((o) => !o)}
              aria-expanded={txAccordionOpen}
              className="w-full flex items-center justify-between text-[12px] font-semibold cursor-pointer"
              style={{ color: 'var(--text-primary)' }}
            >
              <span className="inline-flex items-center gap-1.5">
                <Database size={14} aria-hidden="true" style={{ color: 'var(--role-invocation)' }} />
                Database transactions ({linkedTransactions.length})
              </span>
              <ChevronRight
                size={14}
                className="lab-transition"
                style={{
                  transform: txAccordionOpen ? 'rotate(90deg)' : 'rotate(0deg)',
                  color: 'var(--text-muted)',
                }}
                aria-hidden="true"
              />
            </button>

            {txAccordionOpen && (
              <div className="mt-2.5 space-y-2.5">
                {linkedTransactions.map((tx) => {
                  const lc = tx.txLifecycle!;
                  const beginEv = lc.beginSequence ? graph.eventBySequence.get(lc.beginSequence) : undefined;
                  const termEv = lc.terminalSequence
                    ? graph.eventBySequence.get(lc.terminalSequence)
                    : undefined;

                  return (
                    <div
                      key={tx.id}
                      className="p-2.5 rounded-[4px] border space-y-1.5 text-[12px]"
                      style={{ backgroundColor: 'var(--canvas)', borderColor: 'var(--border)' }}
                    >
                      <div className="flex items-center justify-between gap-2">
                        <button
                          type="button"
                          onClick={() => onSelect({ type: 'entity', id: tx.id })}
                          className="font-mono-data font-medium hover:underline cursor-pointer truncate"
                          style={{ color: 'var(--accent)' }}
                        >
                          {lc.transaction_id}
                        </button>
                        <RoleMark
                          role={tx.role}
                          size={10}
                          label={formatOutcomeLabel(lc.terminalOutcome)}
                        />
                      </div>
                      <div className="font-mono-data text-[11px]" style={{ color: 'var(--text-muted)' }}>
                        Engine session: {lc.engine_session_id}
                      </div>

                      {/* Begin -> Terminal step links */}
                      <div className="flex flex-wrap items-center gap-2 pt-1">
                        {beginEv && (
                          <button
                            type="button"
                            onClick={() => onSelect({ type: 'event', id: beginEv.id })}
                            className="font-mono-data text-[11px] px-1.5 py-0.5 rounded-[3px] border cursor-pointer row-hover"
                            style={{ borderColor: 'var(--border)', color: 'var(--text-primary)' }}
                          >
                            Begin #{beginEv.sequence}
                          </button>
                        )}
                        {termEv ? (
                          <button
                            type="button"
                            onClick={() => onSelect({ type: 'event', id: termEv.id })}
                            className="font-mono-data text-[11px] px-1.5 py-0.5 rounded-[3px] border cursor-pointer row-hover"
                            style={{ borderColor: 'var(--border)', color: 'var(--text-primary)' }}
                          >
                            {formatOutcomeLabel(lc.terminalOutcome)} #{termEv.sequence}
                            {lc.durationMs !== undefined ? ` (${lc.durationMs}ms)` : ''}
                          </button>
                        ) : (
                          <span className="text-[11px]" style={{ color: 'var(--role-partial)' }}>
                            No terminal commit/rollback observed
                          </span>
                        )}
                      </div>

                      {/* Many-to-many participating invocations */}
                      {lc.participantInvocationIds.length > 0 && (
                        <div className="pt-1 border-t space-y-1" style={{ borderColor: 'var(--border)' }}>
                          <div className="text-[11px]" style={{ color: 'var(--text-muted)' }}>
                            Participants ({lc.participantInvocationIds.length}):
                          </div>
                          <div className="flex flex-wrap gap-1.5">
                            {lc.participantInvocationIds.map((pid) => (
                              <button
                                key={pid}
                                type="button"
                                onClick={() => onSelect({ type: 'entity', id: `invocation:${pid}` })}
                                className="font-mono-data text-[11px] hover:underline cursor-pointer"
                                style={{ color: 'var(--accent)' }}
                              >
                                {truncateId(pid, 18)}
                              </button>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        )}

        {/* WebSocket Subscription Attachment Accordion */}
        {subEntity && subEntity.attachmentGenerations && subEntity.attachmentGenerations.length > 0 && (
          <div className="px-4 py-3">
            <button
              type="button"
              onClick={() => setSubAccordionOpen((o) => !o)}
              aria-expanded={subAccordionOpen}
              className="w-full flex items-center justify-between text-[12px] font-semibold cursor-pointer"
              style={{ color: 'var(--text-primary)' }}
            >
              <span>Subscription attachments ({subEntity.attachmentGenerations.length})</span>
              <ChevronRight
                size={14}
                className="lab-transition"
                style={{
                  transform: subAccordionOpen ? 'rotate(90deg)' : 'rotate(0deg)',
                  color: 'var(--text-muted)',
                }}
                aria-hidden="true"
              />
            </button>

            {subAccordionOpen && (
              <div className="mt-2 space-y-1.5 text-[12px]">
                {subEntity.attachmentGenerations.map((g) => (
                  <div
                    key={`${g.generation}-${g.sequence}`}
                    className="p-2 rounded-[4px] border space-y-0.5"
                    style={{ backgroundColor: 'var(--canvas)', borderColor: 'var(--border)' }}
                  >
                    <div className="flex items-center justify-between">
                      <span className="font-medium" style={{ color: 'var(--text-primary)' }}>
                        Generation {g.generation}
                      </span>
                      <span className="font-mono-data text-[11px]" style={{ color: 'var(--text-muted)' }}>
                        seq #{g.sequence}
                      </span>
                    </div>
                    <div className="text-[11px]" style={{ color: 'var(--text-muted)' }}>
                      {g.status}
                    </div>
                    {g.transport_session_id && (
                      <button
                        type="button"
                        onClick={() =>
                          onSelect({
                            type: 'entity',
                            id: `transport_session:${g.transport_session_id}`,
                          })
                        }
                        className="font-mono-data text-[11px] hover:underline cursor-pointer"
                        style={{ color: 'var(--accent)' }}
                      >
                        Session: {g.transport_session_id}
                      </button>
                    )}
                    {g.lease_id && (
                      <div className="font-mono-data text-[11px]" style={{ color: 'var(--text-muted)' }}>
                        Lease: {g.lease_id}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Related Entities (explicitly positioned ABOVE Raw Metadata) */}
        {relatedLinks.length > 0 && (
          <div className="px-4 py-3 space-y-2">
            <div className="font-semibold text-[12px] flex items-center gap-1.5" style={{ color: 'var(--text-primary)' }}>
              <Link2 size={13} aria-hidden="true" />
              Related entities
            </div>
            <ul className="space-y-1">
              {relatedLinks.map((rel) => (
                <li key={rel.key} className="flex items-center justify-between gap-2 text-[12px]">
                  <button
                    type="button"
                    onClick={() => !rel.unretained && onSelect(rel.target)}
                    disabled={rel.unretained}
                    className="truncate text-left hover:underline cursor-pointer disabled:cursor-default disabled:no-underline"
                    style={{
                      color: rel.unretained ? 'var(--role-partial)' : 'var(--accent)',
                    }}
                  >
                    {rel.label}
                  </button>
                  <span className="text-[11px] font-mono-data shrink-0" style={{ color: 'var(--text-muted)' }}>
                    {rel.unretained ? 'unretained endpoint' : rel.relationship}
                  </span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Entity Event List when inspecting a group/entity */}
        {entity && entityEvents.length > 0 && (
          <div className="px-4 py-3 space-y-2">
            <div className="font-semibold text-[12px]" style={{ color: 'var(--text-primary)' }}>
              Timeline records ({entityEvents.length})
            </div>
            <div className="space-y-1 max-h-48 overflow-y-auto pr-1">
              {entityEvents.slice(0, 40).map((item) => (
                <button
                  key={item.id}
                  type="button"
                  onClick={() => onSelect({ type: 'event', id: item.id })}
                  className="w-full text-left px-2 py-1.5 rounded-[4px] flex items-center justify-between gap-2 text-[12px] cursor-pointer row-hover"
                >
                  <span className="truncate flex items-center gap-1.5" style={{ color: 'var(--text-primary)' }}>
                    <RoleMark role={item.role} kind={item.kind} size={10} />
                    <span className="truncate">{item.displayLabel}</span>
                  </span>
                  <span className="font-mono-data text-[11px] shrink-0" style={{ color: 'var(--text-muted)' }}>
                    #{item.sequence}
                  </span>
                </button>
              ))}
              {entityEvents.length > 40 && (
                <div className="text-[11px] px-2" style={{ color: 'var(--text-muted)' }}>
                  Showing first 40 of {entityEvents.length} records. Use Event table for full list.
                </div>
              )}
            </div>
          </div>
        )}

        {/* Raw Allowlisted Metadata Accordion (below Related Entities) */}
        <div className="px-4 py-3">
          <button
            type="button"
            onClick={() => setMetadataOpen((o) => !o)}
            aria-expanded={metadataOpen}
            className="w-full flex items-center justify-between text-[12px] font-semibold cursor-pointer"
            style={{ color: 'var(--text-primary)' }}
          >
            <span>Raw allowlisted metadata</span>
            <ChevronRight
              size={14}
              className="lab-transition"
              style={{
                transform: metadataOpen ? 'rotate(90deg)' : 'rotate(0deg)',
                color: 'var(--text-muted)',
              }}
              aria-hidden="true"
            />
          </button>

          {metadataOpen && (
            <pre
              className="mt-2 p-2.5 rounded-[4px] border font-mono-data text-[11px] leading-[16px] overflow-x-auto"
              style={{
                backgroundColor: 'var(--canvas)',
                borderColor: 'var(--border)',
                color: 'var(--text-muted)',
              }}
            >
              {JSON.stringify(
                ev
                  ? {
                      sequence: ev.sequence,
                      recorded_at: ev.at,
                      kind: ev.kind,
                      transport: ev.transport,
                      source: ev.source,
                      outcome: ev.outcome,
                      metadata: ev.metadata ?? {},
                    }
                  : {
                      entity_id: entity?.id,
                      entity_kind: entity?.entityKind,
                      typed_ids: entity?.typedIds,
                    },
                null,
                2
              )}
            </pre>
          )}
        </div>
      </div>
    </aside>
  );
};
