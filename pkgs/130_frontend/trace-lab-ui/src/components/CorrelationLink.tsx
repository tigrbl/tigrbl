import type { ReactNode } from 'react';

export function CorrelationLink({
  id,
  sequence,
  onFollowCorrelation,
  children,
}: {
  id: string;
  sequence?: number;
  onFollowCorrelation: (href: string) => void;
  children?: ReactNode;
}) {
  const query = new URLSearchParams({ correlation_id: id });
  if (sequence !== undefined) query.set('correlation_event', String(sequence));
  const href = `/correlations?${query}`;

  return (
    <a
      href={href}
      className="font-mono-data text-[12px] truncate underline"
      style={{ color: 'var(--accent)' }}
      aria-label={`Open waterfall for correlation ${id}`}
      title={id}
      onClick={(event) => {
        event.stopPropagation();
        if (event.button !== 0 || event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
        event.preventDefault();
        onFollowCorrelation(href);
      }}
    >
      {children ?? id}
    </a>
  );
}
