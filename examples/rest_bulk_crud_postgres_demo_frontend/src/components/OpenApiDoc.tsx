import { useState, useEffect } from "react";
import { Code, Copy, FileText, CheckCircle2, ChevronRight, ChevronDown, RefreshCw } from "lucide-react";

type ComposerTemplate =
  | "collectionList"
  | "collectionCreate"
  | "memberRead"
  | "memberUpdate"
  | "memberReplace"
  | "memberDelete"
  | "bulkCreate"
  | "bulkUpdate"
  | "bulkReplace"
  | "bulkDelete";

interface OpenApiDocProps {
  onLoadTemplate: (templateName: ComposerTemplate) => void;
}

export default function OpenApiDoc({ onLoadTemplate }: OpenApiDocProps) {
  const [showRaw, setShowRaw] = useState(false);
  const [rawSpec, setRawSpec] = useState<any>(null);
  const [copied, setCopied] = useState(false);
  const [loading, setLoading] = useState(false);
  const [activeRoute, setActiveRoute] = useState<string | null>("/orders-GET");

  const fetchOpenApi = async () => {
    setLoading(true);
    try {
      const res = await fetch("/api/openapi.json");
      if (res.ok) {
        const data = await res.json();
        setRawSpec(data);
      }
    } catch (err) {
      console.error("Failed to load OpenAPI Spec", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchOpenApi();
  }, []);

  const copySpec = () => {
    if (!rawSpec) return;
    navigator.clipboard.writeText(JSON.stringify(rawSpec, null, 2));
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const routes: Array<{
    path: string;
    method: "GET" | "POST" | "PATCH" | "PUT" | "DELETE";
    summary: string;
    desc: string;
    params: Array<{ name: string; type: string; desc: string }>;
    payloadType: string;
    sampleType: ComposerTemplate;
  }> = [
    {
      path: "/orders",
      method: "GET",
      summary: "List all orders",
      desc: "Fetches the live order collection from the PostgreSQL-backed Tigrbl table. Rows contain id, sku, quantity, and status.",
      params: [
        { name: "id", type: "string", desc: "Optional generated query parameter from the table schema" },
        { name: "sku", type: "string", desc: "Optional generated query parameter from the table schema" }
      ],
      payloadType: "None",
      sampleType: "collectionList"
    },
    {
      path: "/orders",
      method: "POST",
      summary: "Create order(s) [Bulk Support]",
      desc: "Creates one or more orders by sending an array of row objects. Each row uses id, sku, quantity, and status.",
      params: [],
      payloadType: "Array of order records",
      sampleType: "collectionCreate"
    },
    {
      path: "/orders",
      method: "PATCH",
      summary: "Bulk Update orders",
      desc: "Processes a list of updates. Every object includes the string primary key id and the row fields to update.",
      params: [],
      payloadType: "Array of partial records",
      sampleType: "bulkUpdate"
    },
    {
      path: "/orders",
      method: "PUT",
      summary: "Bulk Replace orders",
      desc: "Overwrites entire records for specified string IDs. Requires a full array of order rows.",
      params: [],
      payloadType: "Array of full records",
      sampleType: "bulkReplace"
    },
    {
      path: "/orders",
      method: "DELETE",
      summary: "Bulk Delete orders",
      desc: "Removes multiple order records from PostgreSQL. The live endpoint accepts an array of string IDs.",
      params: [],
      payloadType: "Array of string IDs",
      sampleType: "bulkDelete"
    },
    {
      path: "/orders/{item_id}",
      method: "GET",
      summary: "Retrieve a member order",
      desc: "Get full column schema attributes for a single primary-key matched row.",
      params: [{ name: "item_id", type: "string", desc: "The unique order ID" }],
      payloadType: "None",
      sampleType: "memberRead"
    },
    {
      path: "/orders/{item_id}",
      method: "PATCH",
      summary: "Partially update member order",
      desc: "Standard member PATCH. Relational partial column update for the specified primary key ID.",
      params: [{ name: "item_id", type: "string", desc: "The unique order ID" }],
      payloadType: "Object (subset)",
      sampleType: "memberUpdate"
    },
    {
      path: "/orders/{item_id}",
      method: "PUT",
      summary: "Full replace member order",
      desc: "Standard member PUT. Replaces the complete table row with the provided payload.",
      params: [{ name: "item_id", type: "string", desc: "The unique order ID" }],
      payloadType: "Full order row",
      sampleType: "memberReplace"
    },
    {
      path: "/orders/{item_id}",
      method: "DELETE",
      summary: "Delete member order",
      desc: "Purges the single record from the PostgreSQL table.",
      params: [{ name: "item_id", type: "string", desc: "The unique order ID" }],
      payloadType: "None",
      sampleType: "memberDelete"
    }
  ];

  return (
    <div className="bg-[#111216] border border-white/10 rounded-lg overflow-hidden" id="openapi-teaching-panel">
      {/* Tab bar header */}
      <div className="h-11 bg-[#16181c] border-b border-white/5 flex items-center px-4 justify-between">
        <div className="flex items-center gap-2">
          <FileText className="w-4 h-4 text-cyan-400" />
          <h3 className="text-xs font-bold uppercase tracking-widest text-slate-400">
            OpenAPI Inspector
          </h3>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => setShowRaw(!showRaw)}
            className={`flex items-center gap-1.5 px-2.5 py-1 text-[10px] font-bold uppercase tracking-wider rounded border cursor-pointer transition-all ${
              showRaw
                ? "bg-cyan-500/15 text-cyan-400 border-cyan-500/30"
                : "text-slate-400 border-white/10 hover:bg-white/5"
            }`}
            id="btn-toggle-raw-openapi"
          >
            <Code className="w-3.5 h-3.5" />
            <span>{showRaw ? "VISUAL_DOCS" : "RAW_SPEC_JSON"}</span>
          </button>
        </div>
      </div>

      {!showRaw ? (
        /* Visual Contract */
        <div className="p-4 flex flex-col gap-3.5 bg-[#111216]">
          <div className="text-[11px] text-slate-500 leading-normal bg-[#0c0d0f] p-3 rounded border border-white/5 uppercase tracking-wide">
            Spec version V3.0. Documents the standard relational mapping interface. Select any endpoint to inspect request syntax.
          </div>

          <div className="flex flex-col gap-2 font-mono text-[11px]">
            {routes.map((route, i) => {
              const uniqueRouteKey = `${route.path}-${route.method}`;
              const isSelected = activeRoute === uniqueRouteKey;
              
              // Custom method colors matching mockup
              const methodColors: Record<string, string> = {
                GET: "bg-blue-500 text-black",
                POST: "bg-green-500 text-black",
                PATCH: "bg-purple-500 text-black",
                PUT: "bg-amber-500 text-black",
                DELETE: "bg-rose-500 text-black"
              };

              return (
                <div
                  key={i}
                  className={`border rounded overflow-hidden transition-all ${
                    isSelected ? "border-white/15 bg-[#0c0d0f]" : "border-white/5 bg-[#0c0d0f]/60 hover:bg-[#0c0d0f]"
                  }`}
                >
                  <div
                    onClick={() => setActiveRoute(isSelected ? null : uniqueRouteKey)}
                    className="px-3 py-2 flex items-center justify-between gap-2 cursor-pointer select-none"
                  >
                    <div className="flex items-center gap-2.5 min-w-0">
                      <span className={`px-1.5 py-0.2 text-[9px] font-black rounded uppercase shrink-0 ${methodColors[route.method]}`}>
                        {route.method}
                      </span>
                      <span className="text-[11px] font-semibold text-slate-200 truncate">
                        {route.path}
                      </span>
                    </div>
                    <div className="flex items-center gap-2 shrink-0">
                      {isSelected ? <ChevronDown className="w-3.5 h-3.5 text-slate-500" /> : <ChevronRight className="w-3.5 h-3.5 text-slate-500" />}
                    </div>
                  </div>

                  {isSelected && (
                    <div className="px-3 pb-3 pt-2 border-t border-white/5 text-[11px] text-slate-400 bg-[#111216]/50 flex flex-col gap-2.5">
                      <div>
                        <div className="text-[9px] uppercase font-bold tracking-widest text-slate-600 mb-0.5">Semantics</div>
                        <p className="leading-relaxed text-slate-300 font-sans uppercase text-[10px]">{route.desc}</p>
                      </div>

                      {route.params.length > 0 && (
                        <div>
                          <div className="text-[9px] uppercase font-bold tracking-widest text-slate-600 mb-1">Parameters</div>
                          <div className="flex flex-col gap-1 text-[10px] tracking-wide">
                            {route.params.map((p, pi) => (
                              <div key={pi} className="flex items-baseline gap-2">
                                <span className="text-cyan-400 font-bold">{p.name}</span>
                                <span className="text-slate-500 text-[9px]">({p.type})</span>
                                <span className="text-slate-400">&mdash; {p.desc}</span>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}

                      <div className="flex items-center justify-between mt-1 pt-2 border-t border-white/5">
                        <div>
                          <span className="text-slate-600 uppercase text-[9px]">Payload: </span>
                          <span className="text-emerald-400 font-bold text-[10px]">{route.payloadType}</span>
                        </div>

                        <button
                          onClick={() => onLoadTemplate(route.sampleType)}
                          className="px-2 py-0.5 bg-cyan-600/20 text-cyan-400 border border-cyan-500/20 hover:border-cyan-500/40 rounded text-[9px] font-bold uppercase tracking-wider cursor-pointer transition-all"
                        >
                          Load Template
                        </button>
                      </div>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      ) : (
        /* Raw Spec */
        <div className="p-4 flex flex-col gap-3 bg-[#111216]">
          <div className="flex items-center justify-between text-[11px]">
            <span className="font-mono text-slate-500">openapi.json spec file</span>
            <div className="flex items-center gap-3">
              <button
                onClick={fetchOpenApi}
                className="text-[10px] text-slate-400 hover:text-white flex items-center gap-1 uppercase bg-white/5 px-2 py-0.5 rounded border border-white/10 hover:bg-white/10"
              >
                <RefreshCw className="w-2.5 h-2.5" />
                <span>Sync</span>
              </button>
              <button
                onClick={copySpec}
                className="text-[10px] text-cyan-400 hover:text-cyan-300 flex items-center gap-1 uppercase bg-cyan-600/20 px-2 py-0.5 rounded border border-cyan-500/30 font-bold"
                id="btn-copy-openapi-raw"
              >
                <span>{copied ? "COPIED" : "COPY_SPEC"}</span>
              </button>
            </div>
          </div>

          {loading ? (
            <div className="py-20 text-center text-slate-500 font-mono text-xs flex items-center justify-center gap-2">
              <RefreshCw className="w-4 h-4 animate-spin text-cyan-400" />
              <span>FETCHING SPEC CONTRACT...</span>
            </div>
          ) : rawSpec ? (
            <div className="relative">
              <pre className="p-3 bg-[#0c0d0f] text-amber-400 font-mono text-[10px] rounded border border-white/5 overflow-auto max-h-[300px] custom-scrollbar leading-relaxed">
                {JSON.stringify(rawSpec, null, 2)}
              </pre>
            </div>
          ) : (
            <div className="py-12 text-center text-rose-400 font-mono text-[10px] border border-dashed border-rose-900 bg-rose-950/10 rounded uppercase">
              Connection lost to OpenAPI specification publisher.
            </div>
          )}
        </div>
      )}
    </div>
  );
}
