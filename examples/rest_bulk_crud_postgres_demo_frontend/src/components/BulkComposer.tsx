import { useEffect, useMemo, useState } from "react";
import { ArrowUpRight, AlertCircle, Sparkles, Code, Target } from "lucide-react";
import { ApiTrace } from "../types";

interface BulkComposerProps {
  selectedIds: string[];
  onExecuteRequest: (
    method: "GET" | "POST" | "PATCH" | "PUT" | "DELETE",
    path: string,
    payload: any,
    type: ApiTrace["type"]
  ) => Promise<any>;
}

type ComposerMode =
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

const ORDER_STATUSES = ["pending", "allocated", "ready", "packed"];

const modeGroups: Array<{
  label: string;
  modes: ComposerMode[];
}> = [
  { label: "Collection", modes: ["collectionList", "collectionCreate"] },
  { label: "Member", modes: ["memberRead", "memberUpdate", "memberReplace", "memberDelete"] },
  { label: "Bulk", modes: ["bulkCreate", "bulkUpdate", "bulkReplace", "bulkDelete"] }
];

const modeLabels: Record<ComposerMode, string> = {
  collectionList: "List",
  collectionCreate: "Create",
  memberRead: "Read",
  memberUpdate: "Patch",
  memberReplace: "Put",
  memberDelete: "Delete",
  bulkCreate: "Bulk Post",
  bulkUpdate: "Bulk Patch",
  bulkReplace: "Bulk Put",
  bulkDelete: "Bulk Delete"
};

const modeMeta: Record<ComposerMode, {
  method: "GET" | "POST" | "PATCH" | "PUT" | "DELETE";
  traceType: ApiTrace["type"];
  needsPayload: boolean;
  needsMemberId: boolean;
  successLabel: string;
}> = {
  collectionList: {
    method: "GET",
    traceType: "collection",
    needsPayload: false,
    needsMemberId: false,
    successLabel: "Collection GET request complete. Live rows refreshed from PostgreSQL."
  },
  collectionCreate: {
    method: "POST",
    traceType: "collection",
    needsPayload: true,
    needsMemberId: false,
    successLabel: "Collection POST request complete. Relational rows inserted successfully."
  },
  memberRead: {
    method: "GET",
    traceType: "member",
    needsPayload: false,
    needsMemberId: true,
    successLabel: "Member GET request complete. Single row returned from PostgreSQL."
  },
  memberUpdate: {
    method: "PATCH",
    traceType: "member",
    needsPayload: true,
    needsMemberId: true,
    successLabel: "Member PATCH request complete. Target row updated successfully."
  },
  memberReplace: {
    method: "PUT",
    traceType: "member",
    needsPayload: true,
    needsMemberId: true,
    successLabel: "Member PUT request complete. Target row replaced successfully."
  },
  memberDelete: {
    method: "DELETE",
    traceType: "member",
    needsPayload: false,
    needsMemberId: true,
    successLabel: "Member DELETE request complete. Target row removed successfully."
  },
  bulkCreate: {
    method: "POST",
    traceType: "bulk",
    needsPayload: true,
    needsMemberId: false,
    successLabel: "Bulk POST request complete. Rows inserted in one request."
  },
  bulkUpdate: {
    method: "PATCH",
    traceType: "bulk",
    needsPayload: true,
    needsMemberId: false,
    successLabel: "Bulk PATCH request complete. Rows updated in one request."
  },
  bulkReplace: {
    method: "PUT",
    traceType: "bulk",
    needsPayload: true,
    needsMemberId: false,
    successLabel: "Bulk PUT request complete. Rows replaced in one request."
  },
  bulkDelete: {
    method: "DELETE",
    traceType: "bulk",
    needsPayload: true,
    needsMemberId: false,
    successLabel: "Bulk DELETE request complete. Rows removed in one request."
  }
};

const methodColors: Record<string, string> = {
  GET: "bg-blue-500/10 text-blue-300 border-blue-500/20",
  POST: "bg-green-500/10 text-green-400 border-green-500/20",
  PATCH: "bg-amber-500/10 text-amber-400 border-amber-500/20",
  PUT: "bg-purple-500/10 text-purple-400 border-purple-500/20",
  DELETE: "bg-rose-500/10 text-rose-400 border-rose-500/20"
};

const makeOrder = (id: string, index = 0) => ({
  id,
  sku: `sku-${id}`,
  quantity: index === 0 ? 12 : 24,
  status: ORDER_STATUSES[index % ORDER_STATUSES.length]
});

const getTemplate = (mode: ComposerMode, ids: string[], memberId: string) => {
  const targetIds = ids.length > 0 ? ids : ["ord-live-1", "ord-live-2"];

  switch (mode) {
    case "collectionList":
    case "memberRead":
    case "memberDelete":
      return null;
    case "collectionCreate":
      return [makeOrder("ord-demo-401", 0)];
    case "memberUpdate":
      return {
        id: memberId || "ord-live-1",
        sku: `sku-${memberId || "ord-live-1"}`,
        quantity: 99,
        status: "allocated"
      };
    case "memberReplace":
      return {
        id: memberId || "ord-live-1",
        sku: `sku-${memberId || "ord-live-1"}-replaced`,
        quantity: 1,
        status: "ready"
      };
    case "bulkCreate":
      return [
        makeOrder("ord-demo-401", 0),
        makeOrder("ord-demo-402", 1),
        makeOrder("ord-demo-403", 2)
      ];
    case "bulkUpdate":
      return targetIds.map((id) => ({
        id,
        sku: `sku-${id}`,
        status: "allocated",
        quantity: 99
      }));
    case "bulkReplace":
      return targetIds.map((id) => ({
        id,
        sku: `sku-${id}-replaced`,
        quantity: 1,
        status: "ready"
      }));
    case "bulkDelete":
      return targetIds;
  }
};

export default function BulkComposer({ selectedIds, onExecuteRequest }: BulkComposerProps) {
  const [activeTab, setActiveTab] = useState<ComposerMode>("collectionList");
  const [memberId, setMemberId] = useState(selectedIds[0] || "ord-live-1");
  const [jsonValue, setJsonValue] = useState("");
  const [jsonError, setJsonError] = useState<string | null>(null);
  const [isExecuting, setIsExecuting] = useState(false);
  const [executionResult, setExecutionResult] = useState<{ success: boolean; msg: string } | null>(null);

  const activeMeta = modeMeta[activeTab];
  const activePath = activeMeta.needsMemberId ? `/orders/${encodeURIComponent(memberId)}` : "/orders";
  const editorDisabled = !activeMeta.needsPayload;

  const selectedTargetLabel = useMemo(() => {
    if (activeMeta.needsMemberId) return `Member target: ${memberId || "missing id"}`;
    if (selectedIds.length > 0) return `${selectedIds.length} selected table row${selectedIds.length === 1 ? "" : "s"}`;
    return "Default demo targets";
  }, [activeMeta.needsMemberId, memberId, selectedIds.length]);

  useEffect(() => {
    if (selectedIds[0]) {
      setMemberId(selectedIds[0]);
    }
  }, [selectedIds]);

  useEffect(() => {
    const templateObj = getTemplate(activeTab, selectedIds, memberId);
    setJsonValue(templateObj ? JSON.stringify(templateObj, null, 2) : "");
    setJsonError(null);
    setExecutionResult(null);
  }, [activeTab, selectedIds, memberId]);

  useEffect(() => {
    const handleLoadTemplate = (e: CustomEvent<{ mode: ComposerMode }>) => {
      const nextMode = e.detail.mode;
      setActiveTab(nextMode);
      const templateObj = getTemplate(nextMode, selectedIds, memberId);
      setJsonValue(templateObj ? JSON.stringify(templateObj, null, 2) : "");
      setJsonError(null);
      setExecutionResult(null);
    };

    window.addEventListener("load-openapi-template" as any, handleLoadTemplate as any);
    return () => {
      window.removeEventListener("load-openapi-template" as any, handleLoadTemplate as any);
    };
  }, [selectedIds, memberId]);

  const handleTextChange = (val: string) => {
    setJsonValue(val);
    if (!activeMeta.needsPayload) {
      setJsonError(null);
      return;
    }
    if (!val.trim()) {
      setJsonError("Payload is empty");
      return;
    }
    try {
      JSON.parse(val);
      setJsonError(null);
    } catch (err: any) {
      setJsonError(err.message || "Invalid JSON syntax");
    }
  };

  const formatJson = () => {
    if (!activeMeta.needsPayload) return;
    try {
      const parsed = JSON.parse(jsonValue);
      setJsonValue(JSON.stringify(parsed, null, 2));
      setJsonError(null);
    } catch (err: any) {
      setJsonError("Cannot format: " + (err.message || "Invalid JSON"));
    }
  };

  const handleExecute = async () => {
    if (jsonError) return;
    if (activeMeta.needsMemberId && !memberId.trim()) {
      setExecutionResult({ success: false, msg: "Member operations require a target order ID." });
      return;
    }

    let parsedPayload: any = null;
    if (activeMeta.needsPayload) {
      try {
        parsedPayload = JSON.parse(jsonValue);
      } catch {
        setJsonError("Invalid JSON syntax. Cannot parse payload.");
        return;
      }
    }

    setIsExecuting(true);
    setExecutionResult(null);

    try {
      await onExecuteRequest(activeMeta.method, activePath, parsedPayload, activeMeta.traceType);
      setExecutionResult({ success: true, msg: activeMeta.successLabel });
      window.dispatchEvent(new CustomEvent("orders-db-mutated"));
    } catch (err: any) {
      setExecutionResult({
        success: false,
        msg: err.message || "Operation failed. Review API traces console."
      });
    } finally {
      setIsExecuting(false);
    }
  };

  const loadPreset = (presetName: string) => {
    if (presetName === "collection-create") {
      setActiveTab("collectionCreate");
      setJsonValue(JSON.stringify([makeOrder("ord-demo-501", 1)], null, 2));
    } else if (presetName === "member-patch-selected") {
      const id = selectedIds[0] || memberId || "ord-live-1";
      setMemberId(id);
      setActiveTab("memberUpdate");
      setJsonValue(JSON.stringify({ id, sku: `sku-${id}`, quantity: 6, status: "allocated" }, null, 2));
    } else if (presetName === "bulk-patch-selected") {
      const ids = selectedIds.length > 0 ? selectedIds : ["ord-live-1", "ord-live-2"];
      setActiveTab("bulkUpdate");
      setJsonValue(JSON.stringify(ids.map((id) => ({ id, sku: `sku-${id}`, quantity: 6, status: "allocated" })), null, 2));
    } else if (presetName === "bulk-delete-selected") {
      setActiveTab("bulkDelete");
      setJsonValue(JSON.stringify(selectedIds.length > 0 ? selectedIds : ["ord-live-1"], null, 2));
    }
    setJsonError(null);
    setExecutionResult(null);
  };

  return (
    <div className="bg-[#111216] border border-white/10 rounded-lg overflow-hidden" id="bulk-payload-composer">
      <div className="h-11 bg-[#16181c] border-b border-white/5 flex items-center px-4 justify-between">
        <div className="flex items-center gap-2">
          <h2 className="text-xs font-bold uppercase tracking-widest text-cyan-500 glow-cyan">
            Payload Composer
          </h2>
        </div>

        <span className="text-[10px] text-slate-500 uppercase font-mono">
          {selectedTargetLabel}
        </span>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-3 border-b border-white/5 text-[11px] bg-[#0c0d0f]">
        {modeGroups.map((group) => (
          <div key={group.label} className="border-b sm:border-b-0 sm:border-r border-white/5 last:border-r-0">
            <div className="px-3 py-2 text-[9px] text-slate-600 uppercase tracking-widest font-black bg-black/10">
              {group.label}
            </div>
            <div className="grid grid-cols-2">
              {group.modes.map((mode) => {
                const isSelected = activeTab === mode;
                return (
                  <button
                    key={mode}
                    onClick={() => {
                      setActiveTab(mode);
                      setExecutionResult(null);
                    }}
                    className={`py-2.5 text-center uppercase tracking-wider font-bold transition-all border-b ${
                      isSelected
                        ? "border-cyan-500 text-cyan-400 bg-[#111216] font-bold"
                        : "border-transparent text-slate-500 hover:text-slate-300 hover:bg-white/[0.02]"
                    }`}
                    id={`tab-${mode}`}
                  >
                    {modeLabels[mode]}
                  </button>
                );
              })}
            </div>
          </div>
        ))}
      </div>

      <div className="p-4 flex flex-col gap-4 bg-[#111216]">
        <div className="flex flex-col gap-3 text-[11px]">
          <div className="flex items-center justify-between gap-3">
            <div className="flex items-center gap-2 font-mono min-w-0">
              <span className={`px-1.5 py-0.5 border rounded font-black ${methodColors[activeMeta.method]}`}>
                {activeMeta.method}
              </span>
              <span className="text-slate-300 truncate">/api{activePath}</span>
            </div>

            <button
              onClick={formatJson}
              disabled={editorDisabled}
              className={`text-[10px] uppercase tracking-wider font-bold bg-white/5 border border-white/10 px-2 py-1 rounded flex items-center gap-1 transition-all ${
                editorDisabled ? "text-slate-700 cursor-not-allowed" : "text-slate-400 hover:text-white hover:bg-white/10"
              }`}
              id="btn-format-json"
            >
              <Code className="w-3 h-3 text-slate-500" />
              <span>Format</span>
            </button>
          </div>

          {activeMeta.needsMemberId && (
            <label className="flex items-center gap-2 bg-[#0c0d0f] border border-white/10 rounded px-3 py-2 font-mono">
              <Target className="w-3.5 h-3.5 text-cyan-400" />
              <span className="text-[9px] text-slate-600 uppercase tracking-widest font-black">item_id</span>
              <input
                value={memberId}
                onChange={(event) => setMemberId(event.target.value)}
                className="min-w-0 flex-1 bg-transparent text-slate-200 outline-none text-[11px]"
                placeholder="ord-live-1"
                id="member-id-input"
              />
            </label>
          )}
        </div>

        <div className="relative">
          <textarea
            value={editorDisabled ? "// This endpoint sends no JSON request body." : jsonValue}
            onChange={(e) => handleTextChange(e.target.value)}
            disabled={editorDisabled}
            className={`w-full min-h-[160px] p-3 bg-[#0c0d0f] font-mono text-[12px] border border-white/10 rounded focus:outline-none focus:border-cyan-500 leading-relaxed custom-scrollbar tracking-wider ${
              editorDisabled ? "text-slate-600 cursor-not-allowed" : "text-amber-400"
            }`}
            id="bulk-json-input"
            spellCheck={false}
          />
          {jsonError ? (
            <div className="absolute bottom-3 left-3 right-3 py-1.5 px-3 bg-red-950/95 border border-red-500/30 rounded text-red-400 font-sans text-xs flex items-center gap-1.5">
              <AlertCircle className="w-4 h-4 shrink-0" />
              <span className="truncate">{jsonError}</span>
            </div>
          ) : (
            <div className="absolute bottom-3 right-3 px-2 py-0.5 bg-green-950/80 border border-green-500/20 text-green-400 font-mono text-[9px] rounded flex items-center gap-1 uppercase">
              <span>{editorDisabled ? "No Body" : "JSON Valid"}</span>
            </div>
          )}
        </div>

        <div className="flex flex-col gap-2 bg-[#0c0d0f] p-3 rounded border border-white/5">
          <span className="text-[9px] font-bold uppercase tracking-widest text-slate-600 flex items-center gap-1">
            <Sparkles className="w-3 h-3 text-amber-400" />
            <span>Operational Templates</span>
          </span>
          <div className="flex flex-wrap gap-2 text-[10px] font-mono">
            <button
              onClick={() => loadPreset("collection-create")}
              className="px-2.5 py-1 rounded bg-white/5 text-slate-300 hover:text-white border border-white/10 hover:bg-white/10 transition-all font-bold uppercase tracking-wider cursor-pointer"
            >
              + Single Create
            </button>
            <button
              onClick={() => loadPreset("member-patch-selected")}
              className="px-2.5 py-1 rounded bg-white/5 text-slate-300 hover:text-white border border-white/10 hover:bg-white/10 transition-all font-bold uppercase tracking-wider cursor-pointer"
            >
              Patch Member
            </button>
            <button
              onClick={() => loadPreset("bulk-patch-selected")}
              className="px-2.5 py-1 rounded bg-white/5 text-slate-300 hover:text-white border border-white/10 hover:bg-white/10 transition-all font-bold uppercase tracking-wider cursor-pointer"
            >
              Bulk Allocated
            </button>
            <button
              onClick={() => loadPreset("bulk-delete-selected")}
              className="px-2.5 py-1 rounded bg-white/5 text-slate-300 hover:text-white border border-white/10 hover:bg-white/10 transition-all font-bold uppercase tracking-wider cursor-pointer"
            >
              Purge Selected
            </button>
          </div>
        </div>

        <div className="pt-2 border-t border-white/5 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 font-mono">
          <div className="text-[10px] text-slate-500 uppercase">
            <span>
              {activeMeta.traceType.toUpperCase()} route: {activeMeta.needsPayload ? "editable JSON payload" : "request body omitted"}
            </span>
          </div>

          <button
            onClick={handleExecute}
            disabled={isExecuting || !!jsonError}
            className={`w-full sm:w-auto px-5 h-9 bg-cyan-600 hover:bg-cyan-500 text-white font-bold text-xs rounded transition-all flex items-center justify-center gap-2 uppercase cursor-pointer shadow-[0_0_15px_rgba(6,182,212,0.2)] ${
              !!jsonError ? "opacity-50 cursor-not-allowed" : ""
            }`}
            id="btn-execute-bulk"
          >
            <span>{isExecuting ? "COMMITTING" : "COMMIT_REQUEST"}</span>
            <ArrowUpRight className="w-3.5 h-3.5" />
          </button>
        </div>

        {executionResult && (
          <div
            className={`p-3 rounded border text-[11px] font-mono flex items-start gap-2.5 animate-fadeIn ${
              executionResult.success
                ? "bg-green-950/20 border-green-500/20 text-green-300"
                : "bg-red-950/20 border-red-500/20 text-red-300"
            }`}
            id="bulk-execution-feedback"
          >
            <div className="flex-1 leading-normal uppercase">
              <span className="font-bold block mb-0.5">
                {executionResult.success ? "HTTP REQUEST COMMITTED" : "OPERATION SEMANTIC FAILED"}
              </span>
              <span>{executionResult.msg}</span>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
