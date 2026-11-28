export function CollectorControls({ nextBefore }: { nextBefore: number | null }) {
  const { pathname, search } = window.location;
  const query = new URLSearchParams(search);
  const onOlderPage = query.has('before');
  if (!onOlderPage && nextBefore === null) return null;
  query.delete('before');
  const latest = query.size ? `${pathname}?${query}` : pathname;
  if (nextBefore !== null) query.set('before', String(nextBefore));

  return (
    <div className="border-b px-4 py-2" style={{ borderColor: 'var(--border)' }}>
      <nav aria-label="Timeline pages" className="flex gap-3 text-sm">
        {onOlderPage && <a href={latest} className="underline">Latest</a>}
        {nextBefore !== null && <a href={`${pathname}?${query}`} className="underline">Older</a>}
      </nav>
    </div>
  );
}
