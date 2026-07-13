import { useState } from "react";
import { Terminal, Trash2, ChevronDown, ChevronRight, CheckCircle2, AlertTriangle, Copy } from "lucide-react";
import { ApiTrace } from "../types";

interface TraceConsoleProps {
  traces: ApiTrace[];
  onClearTraces: () => void;
}

export default function TraceConsole({ traces, onClearTraces }: TraceConsoleProps) {
  const [selectedTraceId, setSelectedTraceId] = useState<string | null>(null);
  const [copiedPayloadId, setCopiedPayloadId] = useState<string | null>(null);

  const getMethodBadgeColor = (method: string) => {
    switch (method) {
      case "GET":
        return "text-blue-400 font-bold";
      case "POST":
        return "text-green-400 font-bold";
      case "PATCH":
        return "text-purple-400 font-bold";
      case "PUT":
        return "text-yellow-400 font-bold";
      case "DELETE":
        return "text-red-500 font-bold";
      default:
        return "text-slate-400 font-bold";
    }
  };

  const getStatusClass = (status?: number) => {
    if (!status) return "text-slate-500";
    if (status >= 200 && status < 300) return "text-green-500 underline";
    if (status >= 400) return "text-red-500 underline";
    return "text-amber-500 underline";
  };

  const toggleExpand = (id: string) => {
    setSelectedTraceId(selectedTraceId === id ? null : id);
  };

  const copyPayload = (id: string, text: string) => {
    navigator.clipboard.writeText(text);
    setCopiedPayloadId(id);
    setTimeout(() => setCopiedPayloadId(null), 2000);
  };

  return (
    <div className="bg-[#08090b] border border-white/10 rounded-lg overflow-hidden flex flex-col shrink-0" id="trace-console">
      {/* Console Header */}
      <div className="h-9 flex items-center px-4 justify-between bg-white/[0.03] border-b border-white/5">
        <div className="flex items-center gap-2">
          <div className="w-1.5 h-1.5 rounded-full bg-cyan-400 shadow-[0_0_8px_rgba(6,182,212,0.8)] animate-pulse"></div>
          <span className="text-[10px] font-bold uppercase tracking-wider text-slate-500">
            Network Trace Console
          </span>
          <span className="text-[9px] font-mono px-1 bg-white/5 border border-white/15 text-slate-400 rounded">
            {traces.length} Logs
          </span>
        </div>
        
        {traces.length > 0 && (
          <button
            onClick={onClearTraces}
            className="text-[9px] text-slate-500 hover:text-white uppercase tracking-wider font-bold cursor-pointer"
            id="btn-clear-traces"
          >
            Clear History
          </button>
        )}
      </div>

      {/* Trace Log stream list */}
      <div className="max-h-[300px] overflow-y-auto font-mono text-[11px] leading-relaxed divide-y divide-white/[0.03] custom-scrollbar bg-[#08090b] p-2">
        {traces.length === 0 ? (
          <div className="py-12 text-center text-slate-600 flex flex-col items-center justify-center gap-2">
            <Terminal className="w-6 h-6 text-slate-800" />
            <p className="text-[10px] uppercase tracking-widest">Console pipeline listening...</p>
            <p className="text-[9px] text-slate-600 uppercase tracking-wide max-w-xs leading-normal">
              Perform SQL operations, grid filters, or bulk creations to stream immediate transaction network metrics.
            </p>
          </div>
        ) : (
          [...traces].reverse().map((trace) => {
            const isExpanded = selectedTraceId === trace.id;
            
            // Check if response contains an error to draw the special mock subline
            let errorMsg = "";
            if (trace.status && trace.status >= 400 && trace.responseBody) {
              try {
                const parsed = JSON.parse(trace.responseBody);
                if (parsed.error) {
                  errorMsg = parsed.error;
                }
              } catch {
                if (trace.responseBody.includes("error")) {
                  errorMsg = "API exception occurred. Bad parameters.";
                }
              }
            }

            return (
              <div key={trace.id} className="py-1.5 px-2 hover:bg-white/[0.02] transition-colors rounded">
                {/* Log Line */}
                <div
                  onClick={() => toggleExpand(trace.id)}
                  className="flex items-center justify-between gap-4 cursor-pointer select-none"
                >
                  <div className="flex items-center gap-2 min-w-0">
                    <span className="text-slate-600 text-[10px]">[{trace.timestamp}]</span>
                    <span className={getMethodBadgeColor(trace.method)}>{trace.method}</span>
                    <span className="text-slate-300 truncate max-w-[200px] md:max-w-xs">{trace.url}</span>
                  </div>

                  <div className="flex items-center gap-2 shrink-0">
                    {trace.latencyMs !== undefined && (
                      <span className="text-slate-600 text-[10px]">{trace.latencyMs}ms</span>
                    )}
                    <span className={getStatusClass(trace.status)}>
                      {trace.status ? `${trace.status} ${trace.status === 200 || trace.status === 201 ? "OK" : trace.status === 204 ? "NO_CONTENT" : "BAD_REQUEST"}` : "PENDING..."}
                    </span>
                    <span className="text-slate-600">
                      {isExpanded ? <ChevronDown className="w-3 h-3" /> : <ChevronRight className="w-3 h-3" />}
                    </span>
                  </div>
                </div>

                {/* Sub error log line if applicable */}
                {errorMsg && !isExpanded && (
                  <div className="pl-16 text-rose-400 opacity-70 italic text-[10px] animate-fadeIn">
                    → Error: {errorMsg}
                  </div>
                )}

                {/* Expanded Payloads */}
                {isExpanded && (
                  <div className="mt-2 flex flex-col gap-4 border-t border-white/5 pt-2 text-[10px] animate-fadeIn">
                    {/* Request Payload */}
                    <div className="flex flex-col gap-1">
                      <div className="flex items-center justify-between text-slate-500 border-b border-white/5 pb-1 uppercase font-bold text-[9px] tracking-wider">
                        <span>Payload Request Spec</span>
                        {trace.requestBody && (
                          <button
                            onClick={(e) => { e.stopPropagation(); copyPayload(`${trace.id}-req`, trace.requestBody || ""); }}
                            className="text-[9px] text-cyan-400 hover:text-cyan-300 uppercase tracking-wider font-bold bg-white/5 px-1.5 py-0.5 rounded cursor-pointer"
                          >
                            {copiedPayloadId === `${trace.id}-req` ? "Copied" : "Copy"}
                          </button>
                        )}
                      </div>
                      {trace.requestBody ? (
                        <pre className="p-2 bg-[#0c0d0f] rounded text-amber-400 overflow-x-auto max-h-[140px] custom-scrollbar border border-white/5">
                          {trace.requestBody}
                        </pre>
                      ) : (
                        <div className="p-2 bg-[#0c0d0f] rounded text-slate-600 text-center italic border border-white/5 uppercase text-[9px]">
                          No payload sent (Empty query parameter)
                        </div>
                      )}
                    </div>

                    {/* Response Payload */}
                    <div className="flex flex-col gap-1">
                      <div className="flex items-center justify-between text-slate-500 border-b border-white/5 pb-1 uppercase font-bold text-[9px] tracking-wider">
                        <span>Response Body payload</span>
                        {trace.responseBody && (
                          <button
                            onClick={(e) => { e.stopPropagation(); copyPayload(`${trace.id}-res`, trace.responseBody || ""); }}
                            className="text-[9px] text-cyan-400 hover:text-cyan-300 uppercase tracking-wider font-bold bg-white/5 px-1.5 py-0.5 rounded cursor-pointer"
                          >
                            {copiedPayloadId === `${trace.id}-res` ? "Copied" : "Copy"}
                          </button>
                        )}
                      </div>
                      {trace.responseBody ? (
                        <pre className="p-2 bg-[#0c0d0f] rounded text-green-400 overflow-x-auto max-h-[140px] custom-scrollbar border border-white/5">
                          {trace.responseBody}
                        </pre>
                      ) : (
                        <div className="p-2 bg-[#0c0d0f] rounded text-slate-600 text-center italic border border-white/5 uppercase text-[9px]">
                          No content returned
                        </div>
                      )}
                    </div>
                  </div>
                )}
              </div>
            );
          })
        )}
      </div>

      {/* Semantics disclaimer footer */}
      <div className="bg-[#08090b] px-4 py-2 border-t border-white/5 flex items-center justify-between text-[9px] text-slate-600 font-mono uppercase tracking-wider">
        <span>Rest Protocol mapping: PostgreSQL raw state validation active</span>
        <span>Secure proxy loopback</span>
      </div>
    </div>
  );
}
