import { useLayoutEffect, useRef, useState, type CSSProperties, type ReactNode } from 'react';
import { createPortal } from 'react-dom';

type Bounds = { x: number; y: number; w: number; h: number };
export type TooltipAnchor =
  | { x: number; y: number }
  | { element: Element; bounds?: Bounds };

const MARGIN = 8;
const OFFSET = 14;

export function EventTooltip({ id, anchor, container, className, style, children }: {
  id: string;
  anchor: TooltipAnchor;
  container?: Element;
  className?: string;
  style?: CSSProperties;
  children: ReactNode;
}) {
  const tooltip = useRef<HTMLDivElement>(null);
  const [geometry, setGeometry] = useState({ width: 0, height: 0, right: 0, bottom: 0 });
  const [focusedPoint, setFocusedPoint] = useState<{ x: number; y: number; top: number } | null>(null);
  const element = 'element' in anchor ? anchor.element : undefined;
  const bounds = 'element' in anchor ? anchor.bounds : undefined;

  useLayoutEffect(() => {
    const box = tooltip.current;
    if (!box) return;
    const measure = () => {
      setGeometry({
        width: box.offsetWidth,
        height: box.offsetHeight,
        right: window.innerWidth,
        bottom: window.innerHeight,
      });
    };
    measure();
    const observer = new ResizeObserver(measure);
    observer.observe(box);
    window.addEventListener('resize', measure);
    return () => {
      observer.disconnect();
      window.removeEventListener('resize', measure);
    };
  }, []);

  useLayoutEffect(() => {
    if (!element) return;
    const measure = () => {
      const rect = element.getBoundingClientRect();
      const x = rect.left + (bounds ? bounds.x + bounds.w / 2 : 0);
      const top = rect.top + (bounds?.y ?? 0);
      const y = bounds ? top + bounds.h : rect.bottom;
      setFocusedPoint(element.isConnected && x >= 0 && x < window.innerWidth &&
        y > 0 && top < window.innerHeight ? { x, y, top } : null);
    };
    measure();
    window.addEventListener('scroll', measure, true);
    window.addEventListener('resize', measure);
    return () => {
      window.removeEventListener('scroll', measure, true);
      window.removeEventListener('resize', measure);
    };
  }, [element, bounds]);

  const point = 'element' in anchor ? focusedPoint : { ...anchor, top: anchor.y };
  let left = MARGIN;
  let top = MARGIN;
  if (point && geometry.width) {
    const availableRight = geometry.right - point.x;
    const availableBelow = geometry.bottom - point.y;
    const desiredLeft = availableRight >= geometry.width + OFFSET + MARGIN
      ? point.x + OFFSET : point.x - OFFSET - geometry.width;
    const horizontalLimit = geometry.right - geometry.width - MARGIN;
    left = Math.max(MARGIN, Math.min(horizontalLimit, desiredLeft));
    const desiredTop = availableBelow >= geometry.height + OFFSET + MARGIN
      ? point.y + OFFSET : point.top - OFFSET - geometry.height;
    const verticalLimit = geometry.bottom - geometry.height - MARGIN;
    top = Math.max(MARGIN, Math.min(verticalLimit, desiredTop));
  }

  return createPortal(
    <div
      ref={tooltip}
      id={id}
      role="tooltip"
      className={`pointer-events-none fixed z-50 w-max break-words ${className ?? ''}`}
      style={{
        ...style,
        left,
        top,
        maxWidth: 'min(18rem, calc(100vw - 16px))',
        visibility: point && geometry.width ? 'visible' : 'hidden',
      }}
    >
      {children}
    </div>,
    container ?? document.body,
  );
}
