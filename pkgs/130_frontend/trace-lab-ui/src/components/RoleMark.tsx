import React from 'react';
import { EventRole } from '../types/trace';

interface RoleMarkProps {
  role: EventRole;
  kind?: string;
  size?: number;
  label?: string;
  className?: string;
}

export const RoleMark: React.FC<RoleMarkProps> = ({
  role,
  kind,
  size = 12,
  label,
  className = '',
}) => {
  const colorVar = `var(--role-${role})`;
  const isDatagram = kind?.startsWith('wt.datagram');
  const half = size / 2;

  return (
    <span
      className={`inline-flex items-center gap-1.5 shrink-0 ${className}`}
      aria-label={label}
    >
      <svg
        width={size}
        height={size}
        viewBox={`0 0 ${size} ${size}`}
        aria-hidden="true"
        className="shrink-0"
      >
        {role === 'success' && (
          <circle cx={half} cy={half} r={half - 2} fill={colorVar} />
        )}
        {role === 'rejected' && (
          <g stroke={colorVar} strokeWidth={1.75} strokeLinecap="round">
            <line x1={2.5} y1={2.5} x2={size - 2.5} y2={size - 2.5} />
            <line x1={size - 2.5} y1={2.5} x2={2.5} y2={size - 2.5} />
          </g>
        )}
        {role === 'partial' && (
          <circle
            cx={half}
            cy={half}
            r={half - 2}
            fill="none"
            stroke={colorVar}
            strokeWidth={1.5}
            strokeDasharray="2 2"
          />
        )}
        {role === 'carrier' && (
          <g stroke={colorVar} strokeWidth={1.6} strokeLinecap="round">
            <line x1={1.5} y1={half} x2={size - 1.5} y2={half} />
            <line x1={1.5} y1={2.5} x2={1.5} y2={size - 2.5} />
            <line x1={size - 1.5} y1={2.5} x2={size - 1.5} y2={size - 2.5} />
          </g>
        )}
        {role === 'invocation' && (
          <rect
            x={2}
            y={3}
            width={size - 4}
            height={size - 6}
            rx={1.5}
            fill="none"
            stroke={colorVar}
            strokeWidth={1.6}
          />
        )}
        {role === 'neutral' && isDatagram && (
          <polygon
            points={`${half},1.5 ${size - 1.5},${half} ${half},${size - 1.5} 1.5,${half}`}
            fill="none"
            stroke={colorVar}
            strokeWidth={1.5}
          />
        )}
        {role === 'neutral' && !isDatagram && (
          <rect
            x={2.5}
            y={2.5}
            width={size - 5}
            height={size - 5}
            fill="none"
            stroke={colorVar}
            strokeWidth={1.5}
          />
        )}
      </svg>
      {label && <span className="truncate">{label}</span>}
    </span>
  );
};
