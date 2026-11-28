import { createContext, useContext, useLayoutEffect, useState, type ReactNode } from 'react';
import { THEME_ORDER } from './tokens';
import type { ThemeId } from '../types/trace';

const STORAGE_KEY = 'tigrbl.tracelab.theme';
const TraceTheme = createContext<{ theme: ThemeId; setTheme: (theme: ThemeId) => void } | null>(null);

export function TraceThemeProvider({ children }: { children: ReactNode }) {
  const [theme, setTheme] = useState<ThemeId>(() => {
    try {
      const stored = localStorage.getItem(STORAGE_KEY) as ThemeId | null;
      if (stored && THEME_ORDER.includes(stored)) return stored;
    } catch {
      // Storage can be disabled in the browser.
    }
    return 'paper';
  });

  useLayoutEffect(() => {
    document.documentElement.dataset.theme = theme;
    try {
      localStorage.setItem(STORAGE_KEY, theme);
    } catch {
      // The current theme still applies when storage is unavailable.
    }
  }, [theme]);

  return <TraceTheme.Provider value={{ theme, setTheme }}>{children}</TraceTheme.Provider>;
}

export function useTraceTheme() {
  const selection = useContext(TraceTheme);
  if (!selection) throw new Error('TraceThemeProvider is required');
  return selection;
}
