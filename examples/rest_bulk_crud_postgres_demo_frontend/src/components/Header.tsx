import { useState } from "react";
import { Cpu, Layers, RefreshCw } from "lucide-react";
import { HealthStatus, DemoConfig } from "../types";

interface HeaderProps {
  health: HealthStatus | null;
  config: DemoConfig | null;
  loadingHealth: boolean;
  onRefreshHealth: () => void;
}

export default function Header({ health, config, loadingHealth, onRefreshHealth }: HeaderProps) {
  const [copiedUrl, setCopiedUrl] = useState(false);
  const backendStatus = health?.status === "ok" ? "Healthy" : "Checking";

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    setCopiedUrl(true);
    setTimeout(() => setCopiedUrl(false), 2000);
  };

  return (
    <header className="header-gradient technical-border border-x-0 border-t-0 text-slate-100 py-3.5 px-6 shrink-0" id="app-header">
      <div className="max-w-7xl mx-auto flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        {/* Brand Identity */}
        <div className="flex items-center gap-4">
          <div className="w-8 h-8 bg-cyan-500 rounded flex items-center justify-center text-black font-black italic shadow-[0_0_12px_rgba(6,182,212,0.4)]">
            T
          </div>
          <div className="flex flex-col">
            <h1 className="text-sm font-bold tracking-tight text-white uppercase">
              TIGRBL <span className="text-slate-500 font-normal">/</span> ORDER_SERVICE
            </h1>
            <p className="text-[10px] text-cyan-500 uppercase tracking-widest font-semibold">
              Postgres-Backed RestBulkCrudTable
            </p>
          </div>
        </div>

        {/* Health & Connection Stats Banner */}
        <div className="flex items-center gap-6">
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 rounded-full bg-green-500 shadow-[0_0_8px_rgba(34,197,94,0.6)] animate-pulse"></div>
            <span className="text-[11px] font-medium text-slate-400">
              BACKEND: <span className="text-green-400 font-bold uppercase">{backendStatus}</span>
            </span>
          </div>

          <div className="hidden lg:flex items-center gap-4 text-[11px] font-medium text-slate-400">
            <div className="flex items-center gap-1.5 border-l border-white/10 pl-4">
              <Cpu className="w-3.5 h-3.5 text-cyan-500" />
              <span>ENGINE: <strong className="text-slate-300 font-mono">{config?.engine_kind || "postgres"}</strong></span>
            </div>
            <div className="flex items-center gap-1.5 border-l border-white/10 pl-4">
              <Layers className="w-3.5 h-3.5 text-cyan-500" />
              <span>TABLE: <strong className="text-slate-300 font-mono">{config?.resource || "orders"}</strong></span>
            </div>
          </div>

          <div className="flex items-center gap-2 border-l border-white/10 pl-6">
            <span className="text-[11px] font-medium text-slate-400">
              API_STYLE: <span className="text-white font-bold">REST_OPENAPI</span>
            </span>
          </div>

          <button
            onClick={onRefreshHealth}
            disabled={loadingHealth}
            className={`px-3 py-1 bg-white/5 border border-white/10 rounded text-[11px] text-white hover:bg-white/10 hover:border-white/20 transition-all flex items-center gap-1 cursor-pointer font-bold ${loadingHealth ? "animate-pulse" : ""}`}
            id="btn-refresh-health"
          >
            {loadingHealth && <RefreshCw className="w-3 h-3 animate-spin text-cyan-400" />}
            REFRESH
          </button>
        </div>
      </div>

      {/* Extra environmental context ribbon */}
      <div className="max-w-7xl mx-auto mt-2 pt-2 border-t border-white/5 flex flex-wrap items-center justify-between gap-2 text-[10px] text-slate-500 font-mono">
        <div className="flex items-center gap-4">
          <span>STORAGE: <strong className="text-slate-300 font-bold">{config?.db || "tigrbl_rest_bulk_crud_demo"}</strong></span>
          <span className="text-white/10">|</span>
          <span>GATEWAY: <strong className="text-slate-300">{config ? `${config.host}:${config.port}` : "REST PROXY"}</strong></span>
        </div>
        <div className="flex items-center gap-1">
          <span className="text-slate-600">URL PATH PROXY:</span>
          <span className="text-cyan-400 font-semibold cursor-pointer hover:text-cyan-300" onClick={() => copyToClipboard("/api/*")}>
            /api/*
          </span>
          <span>{copiedUrl ? "(Copied!)" : "(Click to Copy)"}</span>
        </div>
      </div>
    </header>
  );
}
