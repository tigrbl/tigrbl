export type ThemeId =
  | 'nocturne'
  | 'paper'
  | 'porcelain'
  | 'parchment'
  | 'ink'
  | 'graphite';

export interface ThemeSpec {
  id: ThemeId;
  name: string;
  isDark: boolean;
  canvas: string;
  panel: string;
  panelElevated: string;
  panelHover: string;
  text: string;
  textSecondary: string;
  textMuted: string;
  accent: string;
  accentMuted: string;
  accentText: string;
  borderRule: string;
  borderStrong: string;
  gridLine: string;
  statusOk: string;
  statusWarn: string;
  statusErr: string;
  statusInfo: string;
  protoRest: string;
  protoRpc: string;
  protoWs: string;
  protoWt: string;
}

export const THEMES: Record<ThemeId, ThemeSpec> = {
  nocturne: {
    id: 'nocturne',
    name: 'Nocturne',
    isDark: true,
    canvas: '#11151D',
    panel: '#181E2A',
    panelElevated: '#1F2736',
    panelHover: '#242E40',
    text: '#F3F0EA',
    textSecondary: '#B8BECB',
    textMuted: '#8891A3',
    accent: '#F0A454',
    accentMuted: 'rgba(240, 164, 84, 0.16)',
    accentText: '#11151D',
    borderRule: 'rgba(243, 240, 234, 0.11)',
    borderStrong: 'rgba(243, 240, 234, 0.22)',
    gridLine: 'rgba(243, 240, 234, 0.06)',
    statusOk: '#59B98C',
    statusWarn: '#E6A84C',
    statusErr: '#E56B6F',
    statusInfo: '#6CA6DB',
    protoRest: '#6CA6DB',
    protoRpc: '#A88BE0',
    protoWs: '#59B98C',
    protoWt: '#F0A454',
  },
  paper: {
    id: 'paper',
    name: 'Paper',
    isDark: false,
    canvas: '#FAF9F6',
    panel: '#FFFFFF',
    panelElevated: '#F3F1EC',
    panelHover: '#EDEAE3',
    text: '#202326',
    textSecondary: '#4E545C',
    textMuted: '#6D747E',
    accent: '#B94438',
    accentMuted: 'rgba(185, 68, 56, 0.12)',
    accentText: '#FFFFFF',
    borderRule: 'rgba(32, 35, 38, 0.11)',
    borderStrong: 'rgba(32, 35, 38, 0.24)',
    gridLine: 'rgba(32, 35, 38, 0.06)',
    statusOk: '#1E7A50',
    statusWarn: '#A66314',
    statusErr: '#B94438',
    statusInfo: '#25649C',
    protoRest: '#25649C',
    protoRpc: '#6B48B8',
    protoWs: '#1E7A50',
    protoWt: '#B94438',
  },
  porcelain: {
    id: 'porcelain',
    name: 'Porcelain',
    isDark: false,
    canvas: '#F3F7F8',
    panel: '#FFFFFF',
    panelElevated: '#EBF2F4',
    panelHover: '#E2ECEF',
    text: '#172A36',
    textSecondary: '#405866',
    textMuted: '#627987',
    accent: '#087C91',
    accentMuted: 'rgba(8, 124, 145, 0.12)',
    accentText: '#FFFFFF',
    borderRule: 'rgba(23, 42, 54, 0.11)',
    borderStrong: 'rgba(23, 42, 54, 0.24)',
    gridLine: 'rgba(23, 42, 54, 0.06)',
    statusOk: '#1A7B64',
    statusWarn: '#A66A14',
    statusErr: '#B83F4B',
    statusInfo: '#087C91',
    protoRest: '#1E6699',
    protoRpc: '#5E53A8',
    protoWs: '#1A7B64',
    protoWt: '#087C91',
  },
  parchment: {
    id: 'parchment',
    name: 'Parchment',
    isDark: false,
    canvas: '#F6F1E7',
    panel: '#FFFDF8',
    panelElevated: '#EFE8DB',
    panelHover: '#E7DEC9',
    text: '#342D28',
    textSecondary: '#5D534B',
    textMuted: '#7C7066',
    accent: '#A3532C',
    accentMuted: 'rgba(163, 83, 44, 0.13)',
    accentText: '#FFFDF8',
    borderRule: 'rgba(52, 45, 40, 0.12)',
    borderStrong: 'rgba(52, 45, 40, 0.26)',
    gridLine: 'rgba(52, 45, 40, 0.06)',
    statusOk: '#2A7350',
    statusWarn: '#9F5C16',
    statusErr: '#AE3D35',
    statusInfo: '#2E6288',
    protoRest: '#2E6288',
    protoRpc: '#734F91',
    protoWs: '#2A7350',
    protoWt: '#A3532C',
  },
  ink: {
    id: 'ink',
    name: 'Ink',
    isDark: true,
    canvas: '#101317',
    panel: '#1A1E23',
    panelElevated: '#21272E',
    panelHover: '#283038',
    text: '#F0F1F2',
    textSecondary: '#B3B9C0',
    textMuted: '#828A94',
    accent: '#E06A5D',
    accentMuted: 'rgba(224, 106, 93, 0.16)',
    accentText: '#101317',
    borderRule: 'rgba(240, 241, 242, 0.11)',
    borderStrong: 'rgba(240, 241, 242, 0.22)',
    gridLine: 'rgba(240, 241, 242, 0.06)',
    statusOk: '#59B88B',
    statusWarn: '#E3A44B',
    statusErr: '#E06A5D',
    statusInfo: '#6BA7DC',
    protoRest: '#6BA7DC',
    protoRpc: '#A88EE0',
    protoWs: '#59B88B',
    protoWt: '#E06A5D',
  },
  graphite: {
    id: 'graphite',
    name: 'Graphite',
    isDark: true,
    canvas: '#17191B',
    panel: '#222528',
    panelElevated: '#2A2E32',
    panelHover: '#32373C',
    text: '#F2EEE8',
    textSecondary: '#BCB7AF',
    textMuted: '#8C877F',
    accent: '#D4A35D',
    accentMuted: 'rgba(212, 163, 93, 0.17)',
    accentText: '#17191B',
    borderRule: 'rgba(242, 238, 232, 0.11)',
    borderStrong: 'rgba(242, 238, 232, 0.22)',
    gridLine: 'rgba(242, 238, 232, 0.06)',
    statusOk: '#65B88E',
    statusWarn: '#D4A35D',
    statusErr: '#DE6E68',
    statusInfo: '#78A6CC',
    protoRest: '#78A6CC',
    protoRpc: '#AE93D8',
    protoWs: '#65B88E',
    protoWt: '#D4A35D',
  },
};

export function applyCorrelationTheme(root: HTMLElement, themeId: ThemeId): void {
  const spec = THEMES[themeId] ?? THEMES.paper;
  root.style.setProperty('--bg-canvas', spec.canvas);
  root.style.setProperty('--bg-panel', spec.panel);
  root.style.setProperty('--bg-panel-elevated', spec.panelElevated);
  root.style.setProperty('--bg-panel-hover', spec.panelHover);
  root.style.setProperty('--text-primary', spec.text);
  root.style.setProperty('--text-secondary', spec.textSecondary);
  root.style.setProperty('--text-muted', spec.textMuted);
  root.style.setProperty('--accent', spec.accent);
  root.style.setProperty('--accent-muted', spec.accentMuted);
  root.style.setProperty('--accent-text', spec.accentText);
  root.style.setProperty('--border-rule', spec.borderRule);
  root.style.setProperty('--border-strong', spec.borderStrong);
  root.style.setProperty('--grid-line', spec.gridLine);
  root.style.setProperty('--status-ok', spec.statusOk);
  root.style.setProperty('--status-warn', spec.statusWarn);
  root.style.setProperty('--status-err', spec.statusErr);
  root.style.setProperty('--status-info', spec.statusInfo);
  root.style.setProperty('--proto-rest', spec.protoRest);
  root.style.setProperty('--proto-rpc', spec.protoRpc);
  root.style.setProperty('--proto-ws', spec.protoWs);
  root.style.setProperty('--proto-wt', spec.protoWt);
}
