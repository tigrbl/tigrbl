import { protocolLabel, scopeLabel } from './correlationEngine';
import type {
  CohortDistribution,
  CompareMeasureId,
  CorrelationGroup,
  CorrelationIndex,
  EcdfPoint,
  ExcludedObservation,
  HistogramBin,
  KaryogramBucket,
  KaryogramData,
  KaryogramRow,
  MeasureObservation,
  TransportProtocol,
} from './types';

export function buildKaryogram(
  groups: CorrelationGroup[],
  minTimeMs: number,
  maxTimeMs: number,
  bucketCount = 32
): KaryogramData {
  const safeSpan = Math.max(1, maxTimeMs - minTimeMs);
  const bucketWidth = safeSpan / bucketCount;

  const rowMap = new Map<
    string,
    {
      protocol: TransportProtocol;
      scope: CorrelationGroup['scope'];
      label: string;
      groupCount: number;
      eventCount: number;
      buckets: KaryogramBucket[];
      bucketGroupSets: Set<string>[];
    }
  >();

  for (const g of groups) {
    const rowKey = `${g.protocol}:${g.scope}`;
    let row = rowMap.get(rowKey);
    if (!row) {
      const buckets: KaryogramBucket[] = [];
      const bucketGroupSets: Set<string>[] = [];
      for (let i = 0; i < bucketCount; i++) {
        buckets.push({
          index: i,
          startMs: minTimeMs + i * bucketWidth,
          endMs: minTimeMs + (i + 1) * bucketWidth,
          count: 0,
          groupKeys: [],
        });
        bucketGroupSets.push(new Set());
      }
      row = {
        protocol: g.protocol,
        scope: g.scope,
        label: `${protocolLabel(g.protocol)} · ${scopeLabel(g.scope)}`,
        groupCount: 0,
        eventCount: 0,
        buckets,
        bucketGroupSets,
      };
      rowMap.set(rowKey, row);
    }

    row.groupCount++;
    for (const rec of g.events) {
      row.eventCount++;
      const rawIdx = Math.floor((rec.event.atMs - minTimeMs) / bucketWidth);
      const idx = Math.max(0, Math.min(bucketCount - 1, rawIdx));
      row.buckets[idx].count++;
      row.bucketGroupSets[idx].add(g.groupKey);
    }
  }

  let maxBucketCount = 1;
  const rows: KaryogramRow[] = [];
  for (const [rowKey, r] of rowMap.entries()) {
    for (let i = 0; i < bucketCount; i++) {
      r.buckets[i].groupKeys = Array.from(r.bucketGroupSets[i]);
      if (r.buckets[i].count > maxBucketCount) {
        maxBucketCount = r.buckets[i].count;
      }
    }
    rows.push({
      rowKey,
      protocol: r.protocol,
      scope: r.scope,
      label: r.label,
      groupCount: r.groupCount,
      eventCount: r.eventCount,
      buckets: r.buckets,
    });
  }

  const protoOrder: Record<TransportProtocol, number> = {
    rest: 0,
    jsonrpc: 1,
    websocket: 2,
    webtransport: 3,
    unknown: 4,
  };
  rows.sort((a, b) =>
    protoOrder[a.protocol] !== protoOrder[b.protocol]
      ? protoOrder[a.protocol] - protoOrder[b.protocol]
      : a.label.localeCompare(b.label)
  );

  return {
    minTimeMs,
    maxTimeMs,
    bucketCount,
    maxBucketCount,
    rows,
  };
}

function percentile(sorted: number[], p: number): number | null {
  if (sorted.length === 0) return null;
  const idx = Math.ceil((p / 100) * sorted.length) - 1;
  return sorted[Math.max(0, Math.min(sorted.length - 1, idx))];
}

export const COMPARE_MEASURES: Record<
  CompareMeasureId,
  { label: string; timingBoundary: string; description: string }
> = {
  measured_request_latency: {
    label: 'Measured Request / Exchange Latency',
    timingBoundary: 'ingress_to_egress_monotonic',
    description: 'Producer-measured monotonic latency from inbound frame/request to outbound reply.',
  },
  engine_transaction_duration: {
    label: 'Engine Transaction Duration',
    timingBoundary: 'db_tx_begin_to_commit',
    description:
      'Engine begin to commit or rollback. Shared transactions are counted once by engine session and transaction ID.',
  },
  stream_invocation_duration: {
    label: 'Invocation / Stream Execution Duration',
    timingBoundary: 'invocation_monotonic',
    description: 'Measured handler or stream invocation duration with single-clock boundary.',
  },
};

export function computeCohortDistributions(
  index: CorrelationIndex,
  cohortGroups: CorrelationGroup[],
  measureId: CompareMeasureId,
  binCount = 12
): CohortDistribution[] {
  const protocols: TransportProtocol[] = ['rest', 'jsonrpc', 'websocket', 'webtransport'];
  const measureMeta = COMPARE_MEASURES[measureId];
  const results: CohortDistribution[] = [];

  // Deduplicate shared transactions globally across the selected cohort
  const seenTxKeys = new Set<string>();

  for (const protocol of protocols) {
    const protoGroups = cohortGroups.filter((g) => g.protocol === protocol);
    if (protoGroups.length === 0) continue;

    const observations: MeasureObservation[] = [];
    const excludedSamples: ExcludedObservation[] = [];
    const excludedReasons: Record<string, number> = {};
    const addExclusion = (g: CorrelationGroup, reason: string) => {
      excludedReasons[reason] = (excludedReasons[reason] ?? 0) + 1;
      excludedSamples.push({
        groupKey: g.groupKey,
        groupShortId: g.shortId,
        protocol: g.protocol,
        reason,
      });
    };

    const clockSources = new Set<string>();

    for (const g of protoGroups) {
      if (g.hasClockSkew) {
        addExclusion(g, 'Clock order uncertain (skewed clocks)');
        continue;
      }

      if (measureId === 'measured_request_latency') {
        if (g.outcomeSummary === 'no_reply_expected') {
          addExclusion(g, 'Notification (no reply expected)');
          continue;
        }
        if (g.outcomeSummary === 'reply_not_observed') {
          addExclusion(g, 'Reply not observed');
          continue;
        }
        const measuredReply = g.events.find(
          (r) =>
            (r.event.kind === 'http.response.sent' ||
              r.event.kind === 'rpc.response.sent' ||
              r.event.kind === 'ws.frame.sent' ||
              r.event.kind === 'ws.broker.delivery' ||
              r.event.kind === 'wt.stream.frame.sent') &&
            r.event.timeBasis === 'measured_monotonic' &&
            r.event.timingBoundary === measureMeta.timingBoundary &&
            typeof r.event.measuredDurationMs === 'number'
        );
        if (!measuredReply) {
          addExclusion(g, 'No measured ingress-to-reply boundary');
          continue;
        }
        const clk = measuredReply.event.clockDomain ?? 'server_monotonic';
        clockSources.add(clk);
        observations.push({
          id: `obs-${g.groupKey}-${measuredReply.event.seq}`,
          entityKey: g.groupKey,
          groupKey: g.groupKey,
          groupShortId: g.shortId,
          protocol: g.protocol,
          valueMs: measuredReply.event.measuredDurationMs!,
          timingBoundary: measuredReply.event.timingBoundary ?? measureMeta.timingBoundary,
          clockSource: clk,
          label: g.displayTitle,
        });
      } else if (measureId === 'engine_transaction_duration') {
        const txEvents = g.events.filter(
          (r) => r.event.kind.startsWith('db.tx.') && r.event.transactionKey
        );
        if (txEvents.length === 0) {
          addExclusion(g, 'No database transaction recorded');
          continue;
        }
        const localTxKeys = new Set(txEvents.map((t) => t.event.transactionKey!));
        for (const txKey of localTxKeys) {
          const firstEvidence = g.events.find(({ event }) => event.transactionKey === txKey);
          const scopedTx = firstEvidence ? scopedIdentity(firstEvidence.event, txKey) : txKey;
          if (seenTxKeys.has(scopedTx)) {
            // Shared transaction already counted once in this cohort
            continue;
          }
        const terminal = txEvents.find(
            (r) =>
              r.event.transactionKey === txKey &&
              ((r.event.kind === 'db.tx.commit' && r.event.timingBoundary === measureMeta.timingBoundary) ||
                (r.event.kind === 'db.tx.rollback' && r.event.timingBoundary === 'db_tx_begin_to_rollback')) &&
              r.event.timeBasis === 'measured_monotonic' &&
              typeof r.event.measuredDurationMs === 'number'
          );
          if (!terminal) {
            addExclusion(g, 'Transaction missing monotonic commit/rollback timing');
            continue;
          }
          seenTxKeys.add(scopedTx);
          const clk = terminal.event.clockDomain ?? 'engine_monotonic';
          clockSources.add(clk);
          const participants = index.transactionParticipants.get(scopedTx) ?? [g.groupKey];
          observations.push({
            id: `obs-tx-${txKey}`,
            entityKey: txKey,
            groupKey: g.groupKey,
            groupShortId: g.shortId,
            protocol: g.protocol,
            valueMs: terminal.event.measuredDurationMs!,
            timingBoundary: terminal.event.timingBoundary ?? measureMeta.timingBoundary,
            clockSource: clk,
            label: `${txKey}${participants.length > 1 ? ` (shared ×${participants.length})` : ''}`,
          });
        }
      } else if (measureId === 'stream_invocation_duration') {
        const invEvs = g.events.filter(
          (r) =>
            (r.event.kind === 'invocation.completed' ||
              r.event.kind === 'rpc.batch.item.completed' ||
              r.event.kind === 'wt.stream.closed') &&
            r.event.timeBasis === 'measured_monotonic' &&
            typeof r.event.measuredDurationMs === 'number'
        );
        if (invEvs.length === 0) {
          addExclusion(g, 'No monotonic invocation/stream completion recorded');
          continue;
        }
        for (const rec of invEvs) {
          const clk = rec.event.clockDomain ?? 'runtime_monotonic';
          clockSources.add(clk);
          const entity =
            rec.event.invocationId ??
            rec.event.streamCorrelationId ??
            `${g.groupKey}:${rec.event.seq}`;
          observations.push({
            id: `obs-inv-${rec.event.seq}`,
            entityKey: entity,
            groupKey: g.groupKey,
            groupShortId: g.shortId,
            protocol: g.protocol,
            valueMs: rec.event.measuredDurationMs!,
            timingBoundary: rec.event.timingBoundary ?? measureMeta.timingBoundary,
            clockSource: clk,
            label: `${g.shortId} · ${entity}`,
          });
        }
      }
    }

    observations.sort((a, b) => a.valueMs - b.valueMs);
    const values = observations.map((o) => o.valueMs);
    const n = observations.length;

    const minMs = n > 0 ? values[0] : null;
    const maxMs = n > 0 ? values[n - 1] : null;
    const medianMs = n > 0 ? percentile(values, 50) : null;

    // Brief rule: suppress p95 below 20 and p99 below 100 eligible observations
    const p95Ms = n >= 20 ? percentile(values, 95) : null;
    const p95SuppressedReason =
      n < 20 ? `Suppressed (n=${n} < 20 eligible)` : undefined;

    const p99Ms = n >= 100 ? percentile(values, 99) : null;
    const p99SuppressedReason =
      n < 100 ? `Suppressed (n=${n} < 100 eligible)` : undefined;

    // Histogram bins
    const bins: HistogramBin[] = [];
    if (n > 0 && minMs !== null && maxMs !== null) {
      const span = Math.max(0.5, maxMs - minMs);
      const effectiveBins = Math.max(4, Math.min(binCount, 24));
      const step = span / effectiveBins;

      for (let i = 0; i < effectiveBins; i++) {
        bins.push({
          binIndex: i,
          startMs: minMs + i * step,
          endMs: minMs + (i + 1) * step,
          count: 0,
          empiricalProbability: 0,
          contributors: [],
        });
      }

      for (const obs of observations) {
        const rawIdx = Math.floor((obs.valueMs - minMs) / step);
        const idx = Math.max(0, Math.min(effectiveBins - 1, rawIdx));
        bins[idx].count++;
        bins[idx].contributors.push(obs);
      }

      for (const b of bins) {
        b.empiricalProbability = n > 0 ? b.count / n : 0;
      }
    }

    // Empirical CDF points
    const ecdf: EcdfPoint[] = observations.map((obs, idx) => ({
      valueMs: obs.valueMs,
      cumulativeProbability: (idx + 1) / n,
      observation: obs,
    }));

    results.push({
      protocol,
      measureId,
      measureLabel: measureMeta.label,
      units: 'ms',
      timingBoundary: [...new Set(observations.map((item) => item.timingBoundary))].join(', ') || measureMeta.timingBoundary,
      clockSource: clockSources.size > 0 ? Array.from(clockSources).join(', ') : 'none observed',
      eligibleCount: n,
      excludedCount: excludedSamples.length,
      excludedReasons,
      excludedSamples,
      minMs,
      maxMs,
      medianMs,
      p95Ms,
      p95SuppressedReason,
      p99Ms,
      p99SuppressedReason,
      bins,
      ecdf,
      observations,
    });
  }

  return results;
}
import { scopedIdentity } from './correlationEngine';
