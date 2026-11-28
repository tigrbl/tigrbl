import { DensityId, EventRole, ThemeId } from '../types/trace';

export interface ThemePalette {
  id: ThemeId;
  name: string;
  isDark: boolean;
  canvas: string;
  panel: string;
  surfaceAlt: string;
  textPrimary: string;
  textMuted: string;
  border: string;
  accent: string;
  accentContrast: string;
  selectedBg: string;
  gridMinor: string;
  gridMajor: string;
  roles: Record<EventRole, string>;
}

const LIGHT_ROLES: Record<EventRole, string> = {
  success: '#087F69',
  rejected: '#C43D45',
  partial: '#9C6A16',
  carrier: '#246EAB',
  invocation: '#7357B7',
  neutral: '#5B6670',
};

const DARK_ROLES: Record<EventRole, string> = {
  success: '#36C6A7',
  rejected: '#F07178',
  partial: '#E9BE66',
  carrier: '#68B6F1',
  invocation: '#B29AF4',
  neutral: '#A0ABB6',
};

export const THEMES: Record<ThemeId, ThemePalette> = {
  nocturne: {
    id: 'nocturne',
    name: 'Nocturne',
    isDark: true,
    canvas: '#11151D',
    panel: '#181E2A',
    surfaceAlt: '#222A3B',
    textPrimary: '#F3F0EA',
    textMuted: '#B0B8C8',
    border: '#334057',
    accent: '#F0A454',
    accentContrast: '#14100B',
    selectedBg: 'rgba(240, 164, 84, 0.14)',
    gridMinor: 'rgba(243, 240, 234, 0.07)',
    gridMajor: 'rgba(243, 240, 234, 0.14)',
    roles: DARK_ROLES,
  },
  paper: {
    id: 'paper',
    name: 'Paper',
    isDark: false,
    canvas: '#FAF9F6',
    panel: '#FFFFFF',
    surfaceAlt: '#F1EFEB',
    textPrimary: '#202326',
    textMuted: '#5C6166',
    border: '#DCD9D3',
    accent: '#B94438',
    accentContrast: '#FFFFFF',
    selectedBg: 'rgba(185, 68, 56, 0.08)',
    gridMinor: 'rgba(32, 35, 38, 0.07)',
    gridMajor: 'rgba(32, 35, 38, 0.14)',
    roles: LIGHT_ROLES,
  },
  porcelain: {
    id: 'porcelain',
    name: 'Porcelain',
    isDark: false,
    canvas: '#F3F7F8',
    panel: '#FFFFFF',
    surfaceAlt: '#E6EFF2',
    textPrimary: '#172A36',
    textMuted: '#4C6370',
    border: '#CBDCE2',
    accent: '#087C91',
    accentContrast: '#FFFFFF',
    selectedBg: 'rgba(8, 124, 145, 0.08)',
    gridMinor: 'rgba(23, 42, 54, 0.07)',
    gridMajor: 'rgba(23, 42, 54, 0.14)',
    roles: LIGHT_ROLES,
  },
  parchment: {
    id: 'parchment',
    name: 'Parchment',
    isDark: false,
    canvas: '#F6F1E7',
    panel: '#FFFDF8',
    surfaceAlt: '#ECE3D3',
    textPrimary: '#342D28',
    textMuted: '#65584E',
    border: '#D8CCBA',
    accent: '#A3532C',
    accentContrast: '#FFFDF8',
    selectedBg: 'rgba(163, 83, 44, 0.08)',
    gridMinor: 'rgba(52, 45, 40, 0.07)',
    gridMajor: 'rgba(52, 45, 40, 0.14)',
    roles: LIGHT_ROLES,
  },
  ink: {
    id: 'ink',
    name: 'Ink',
    isDark: true,
    canvas: '#101317',
    panel: '#1A1E23',
    surfaceAlt: '#252A30',
    textPrimary: '#F0F1F2',
    textMuted: '#A9B4BF',
    border: '#343B43',
    accent: '#E06A5D',
    accentContrast: '#101317',
    selectedBg: 'rgba(224, 106, 93, 0.14)',
    gridMinor: 'rgba(240, 241, 242, 0.07)',
    gridMajor: 'rgba(240, 241, 242, 0.14)',
    roles: DARK_ROLES,
  },
  graphite: {
    id: 'graphite',
    name: 'Graphite',
    isDark: true,
    canvas: '#17191B',
    panel: '#222528',
    surfaceAlt: '#2C3033',
    textPrimary: '#F2EEE8',
    textMuted: '#BBB5AC',
    border: '#414548',
    accent: '#D4A35D',
    accentContrast: '#17191B',
    selectedBg: 'rgba(212, 163, 93, 0.14)',
    gridMinor: 'rgba(242, 238, 232, 0.07)',
    gridMajor: 'rgba(242, 238, 232, 0.14)',
    roles: DARK_ROLES,
  },
};

export const THEME_ORDER: ThemeId[] = [
  'nocturne',
  'paper',
  'porcelain',
  'parchment',
  'ink',
  'graphite',
];

export const DENSITY_ROW_HEIGHT: Record<DensityId, number> = {
  dense: 28,
  compact: 32,
  comfortable: 40,
};

export const PROTOCOL_LABELS: Record<string, string> = {
  realtime: 'Realtime',
  unknown: 'Unknown',
  rest: 'REST',
  http_jsonrpc: 'HTTP JSON-RPC',
  websocket: 'WebSocket',
  webtransport: 'WebTransport',
  database: 'Database',
};

export const ROLE_DESCRIPTIONS: Record<EventRole, string> = {
  success: 'Successful terminal event',
  rejected: 'Rejected, failed, or rolled back',
  partial: 'Partial or still open',
  carrier: 'Connection, session, or stream',
  invocation: 'Invocation, attachment, or transaction',
  neutral: 'Datagram or neutral observation',
};

// Contrast verification utility (WCAG 2.2 AA check against actual plot surface)
function hexToLuminance(hex: string): number {
  const clean = hex.replace('#', '');
  const r = parseInt(clean.slice(0, 2), 16) / 255;
  const g = parseInt(clean.slice(2, 4), 16) / 255;
  const b = parseInt(clean.slice(4, 6), 16) / 255;
  const toLinear = (c: number) => (c <= 0.03928 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4));
  return 0.2126 * toLinear(r) + 0.7152 * toLinear(g) + 0.0722 * toLinear(b);
}

export function contrastRatio(hexA: string, hexB: string): number {
  const l1 = hexToLuminance(hexA);
  const l2 = hexToLuminance(hexB);
  const bright = Math.max(l1, l2);
  const dark = Math.min(l1, l2);
  return (bright + 0.05) / (dark + 0.05);
}

export function isThemeVerified(theme: ThemePalette): boolean {
  const textOnPanel = contrastRatio(theme.textPrimary, theme.panel) >= 4.5;
  const mutedOnPanel = contrastRatio(theme.textMuted, theme.panel) >= 4.2;
  const marksOnPanel = Object.values(theme.roles).every(
    (c) => contrastRatio(c, theme.panel) >= 3.0
  );
  return textOnPanel && mutedOnPanel && marksOnPanel;
}
