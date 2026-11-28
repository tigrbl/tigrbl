import {createRoot} from 'react-dom/client';
import { TraceLabShell } from './TraceLabShell';
import { TraceThemeProvider } from './theme/TraceTheme';
import './index.css';

const root = document.getElementById('root')!;
const collector = root.hasAttribute('data-trace-monitor');
createRoot(root).render(
  <TraceThemeProvider>
    <TraceLabShell
      collector={collector}
      backendVersion={root.dataset.traceBackendVersion}
      imageVersion={root.dataset.traceImageVersion}
    />
  </TraceThemeProvider>
);
