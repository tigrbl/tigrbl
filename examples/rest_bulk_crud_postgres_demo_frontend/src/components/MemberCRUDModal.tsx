import { useState, useEffect } from "react";
import { X, CheckCircle, AlertCircle, Trash2, ArrowUpRight, RefreshCw, Layers } from "lucide-react";
import { Order } from "../types";

interface MemberCRUDModalProps {
  order: Order;
  onClose: () => void;
  onExecuteRequest: (
    method: "GET" | "POST" | "PATCH" | "PUT" | "DELETE",
    path: string,
    payload: any,
    type: "collection" | "bulk" | "member" | "system"
  ) => Promise<any>;
}

type ModalTab = "get" | "patch" | "put" | "delete";

export default function MemberCRUDModal({ order, onClose, onExecuteRequest }: MemberCRUDModalProps) {
  const [activeTab, setActiveTab] = useState<ModalTab>("get");
  const [liveOrder, setLiveOrder] = useState<Order>(order);
  const [loading, setLoading] = useState(false);
  const [feedback, setFeedback] = useState<{ success: boolean; msg: string } | null>(null);

  const [sku, setSku] = useState(order.sku);
  const [quantity, setQuantity] = useState(order.quantity);
  const [status, setStatus] = useState(order.status);

  // Sync state if order changes
  useEffect(() => {
    setLiveOrder(order);
    setSku(order.sku);
    setQuantity(order.quantity);
    setStatus(order.status);
    setFeedback(null);
  }, [order]);

  // GET Operation
  const fetchLatest = async () => {
    setLoading(true);
    setFeedback(null);
    try {
      const res = await onExecuteRequest("GET", `/orders/${order.id}`, null, "member");
      setLiveOrder(res);
      setSku(res.sku);
      setQuantity(res.quantity);
      setStatus(res.status);
      setFeedback({ success: true, msg: "FETCHED_LATEST: Successfully retrieved state from PostgreSQL database." });
    } catch (err: any) {
      setFeedback({ success: false, msg: err.message || "Failed to retrieve member." });
    } finally {
      setLoading(false);
    }
  };

  // Trigger initial GET on load
  useEffect(() => {
    fetchLatest();
  }, [order.id]);

  // PATCH Operation (Partial changes)
  const handlePatch = async () => {
    setLoading(true);
    setFeedback(null);
    
    const updates: any = {};
    if (sku !== liveOrder.sku) updates.sku = sku;
    if (quantity !== liveOrder.quantity) updates.quantity = quantity;
    if (status !== liveOrder.status) updates.status = status;

    if (Object.keys(updates).length === 0) {
      setFeedback({ success: false, msg: "No fields modified. Please make a change first." });
      setLoading(false);
      return;
    }

    try {
      const res = await onExecuteRequest("PATCH", `/orders/${order.id}`, updates, "member");
      setLiveOrder(res);
      setFeedback({ success: true, msg: "ROW_PATCHED: Column(s) partially updated successfully." });
      window.dispatchEvent(new CustomEvent("orders-db-mutated"));
    } catch (err: any) {
      setFeedback({ success: false, msg: err.message || "Failed to patch record." });
    } finally {
      setLoading(false);
    }
  };

  // PUT Operation (Full replacement)
  const handlePut = async () => {
    setLoading(true);
    setFeedback(null);

    const fullPayload = {
      id: order.id,
      sku,
      quantity,
      status
    };

    try {
      const res = await onExecuteRequest("PUT", `/orders/${order.id}`, fullPayload, "member");
      setLiveOrder(res);
      setFeedback({ success: true, msg: "ROW_REPLACED: Entire record fully updated successfully." });
      window.dispatchEvent(new CustomEvent("orders-db-mutated"));
    } catch (err: any) {
      setFeedback({ success: false, msg: err.message || "Failed to replace record." });
    } finally {
      setLoading(false);
    }
  };

  // DELETE Operation
  const handleDelete = async () => {
    if (!window.confirm(`Are you sure you want to permanently delete Order #${order.id} from PostgreSQL?`)) {
      return;
    }
    
    setLoading(true);
    setFeedback(null);

    try {
      await onExecuteRequest("DELETE", `/orders/${order.id}`, null, "member");
      setFeedback({ success: true, msg: "ROW_PURGED: Record successfully deleted from PG table." });
      window.dispatchEvent(new CustomEvent("orders-db-mutated"));
      setTimeout(() => {
        onClose();
      }, 1000);
    } catch (err: any) {
      setFeedback({ success: false, msg: err.message || "Failed to delete record." });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-xs animate-fadeIn" id="member-crud-overlay">
      <div className="bg-[#111216] border border-white/10 rounded-lg max-w-lg w-full overflow-hidden shadow-2xl flex flex-col max-h-[90vh]">
        
        {/* Modal Header */}
        <div className="bg-[#16181c] px-4 py-3.5 border-b border-white/5 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Layers className="w-4 h-4 text-cyan-400" />
            <h3 className="text-xs font-bold text-white tracking-widest uppercase font-mono">
              Member Endpoint Inspector
            </h3>
          </div>
          <button
            onClick={onClose}
            className="text-slate-500 hover:text-white transition-all p-1 hover:bg-white/5 rounded cursor-pointer"
            id="btn-close-modal"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Target Endpoint Callout */}
        <div className="bg-[#0c0d0f] px-4 py-2 border-b border-white/5 flex items-center justify-between font-mono text-[11px]">
          <div className="flex items-center gap-2">
            <span className="text-slate-500 uppercase">Route:</span>
            <span className="text-cyan-400 font-bold">/api/orders/{order.id}</span>
          </div>
          <span className="text-slate-500 uppercase">PG ROW_ID: {order.id}</span>
        </div>

        {/* Member Action Tabs */}
        <div className="grid grid-cols-4 border-b border-white/5 font-mono text-[10px] bg-[#0c0d0f] select-none">
          {(["get", "patch", "put", "delete"] as ModalTab[]).map((tab) => {
            const isSelected = activeTab === tab;
            const colors: Record<ModalTab, string> = {
              get: "border-blue-500 text-blue-400 bg-[#111216]",
              patch: "border-purple-500 text-purple-400 bg-[#111216]",
              put: "border-amber-500 text-amber-400 bg-[#111216]",
              delete: "border-red-500 text-red-400 bg-[#111216]"
            };
            return (
              <button
                key={tab}
                onClick={() => { setActiveTab(tab); setFeedback(null); }}
                className={`py-3 text-center uppercase tracking-widest font-bold transition-all border-b ${
                  isSelected ? `${colors[tab]}` : "border-transparent text-slate-500 hover:text-slate-300"
                }`}
                id={`modal-tab-${tab}`}
              >
                {tab}
              </button>
            );
          })}
        </div>

        {/* Modal Body / Tab View Panels */}
        <div className="p-5 overflow-y-auto flex-1 flex flex-col gap-4 text-xs text-slate-300 bg-[#111216]">
          
          {activeTab === "get" && (
            <div className="flex flex-col gap-3 animate-fadeIn font-mono">
              <p className="text-slate-500 leading-normal uppercase text-[10px] tracking-wide">
                Execute GET to poll current database state for Order ID {order.id}.
              </p>
              
              <div className="bg-[#0c0d0f] rounded p-3.5 border border-white/5">
                <div className="flex items-center justify-between text-slate-600 font-mono text-[9px] border-b border-white/5 pb-1.5 mb-2.5">
                  <span className="uppercase font-bold tracking-wider">DATABASE STATE STREAM</span>
                  <button
                    onClick={fetchLatest}
                    disabled={loading}
                    className="flex items-center gap-1 text-[10px] text-cyan-400 hover:text-cyan-300 font-bold uppercase cursor-pointer"
                  >
                    <RefreshCw className={`w-3 h-3 ${loading ? "animate-spin" : ""}`} />
                    <span>REFRESH_GET</span>
                  </button>
                </div>
                
                <pre className="text-amber-400 font-mono text-[11px] overflow-auto max-h-[180px] custom-scrollbar leading-relaxed">
                  {JSON.stringify(liveOrder, null, 2)}
                </pre>
              </div>
            </div>
          )}

          {(activeTab === "patch" || activeTab === "put") && (
            <div className="flex flex-col gap-3.5 animate-fadeIn font-mono">
              <p className="text-slate-500 leading-normal uppercase text-[10px] tracking-wide">
                {activeTab === "patch" ? (
                  <span>Submit a partial PATCH request. Changes are applied dynamically to modified attributes.</span>
                ) : (
                  <span>Submit a full PUT replacement. Blank fields will reset to database defaults.</span>
                )}
              </p>

              {/* Form inputs */}
              <div className="grid grid-cols-2 gap-3 bg-[#0c0d0f] p-4 rounded border border-white/5 uppercase">
                {/* SKU */}
                <div className="flex flex-col gap-1">
                  <label className="text-[9px] font-bold text-slate-600 tracking-widest">SKU Code</label>
                  <input
                    type="text"
                    value={sku}
                    onChange={(e) => setSku(e.target.value)}
                    className="bg-[#111216] border border-white/10 focus:border-cyan-500 px-3 py-1.5 rounded text-[11px] text-slate-200 font-mono focus:outline-none"
                    id="member-input-sku"
                  />
                </div>

                {/* Status selection */}
                <div className="flex flex-col gap-1">
                  <label className="text-[9px] font-bold text-slate-600 tracking-widest">Status</label>
                  <select
                    value={status}
                    onChange={(e) => setStatus(e.target.value)}
                    className="bg-[#111216] border border-white/10 focus:border-cyan-500 px-2.5 py-1.5 rounded text-[11px] text-slate-200 focus:outline-none"
                    id="member-input-status"
                  >
                    <option value="pending">PENDING</option>
                    <option value="allocated">ALLOCATED</option>
                    <option value="ready">READY</option>
                    <option value="packed">PACKED</option>
                  </select>
                </div>

                {/* Quantity */}
                <div className="flex flex-col gap-1">
                  <label className="text-[9px] font-bold text-slate-600 tracking-widest">Quantity</label>
                  <input
                    type="number"
                    value={quantity}
                    onChange={(e) => setQuantity(parseInt(e.target.value, 10) || 0)}
                    className="bg-[#111216] border border-white/10 focus:border-cyan-500 px-3 py-1.5 rounded text-[11px] text-slate-200 font-mono focus:outline-none"
                    id="member-input-quantity"
                  />
                </div>
              </div>

              {/* Submit Buttons */}
              <div className="flex justify-end pt-1">
                {activeTab === "patch" ? (
                  <button
                    onClick={handlePatch}
                    disabled={loading}
                    className="px-4 py-2 bg-purple-600 hover:bg-purple-500 disabled:opacity-50 text-white font-bold text-[10px] tracking-widest uppercase rounded flex items-center gap-1.5 transition-all cursor-pointer shadow-[0_0_15px_rgba(168,85,247,0.3)]"
                    id="btn-modal-patch"
                  >
                    <span>COMMIT_PATCH</span>
                    <ArrowUpRight className="w-3.5 h-3.5" />
                  </button>
                ) : (
                  <button
                    onClick={handlePut}
                    disabled={loading}
                    className="px-4 py-2 bg-amber-600 hover:bg-amber-500 disabled:opacity-50 text-white font-bold text-[10px] tracking-widest uppercase rounded flex items-center gap-1.5 transition-all cursor-pointer shadow-[0_0_15px_rgba(245,158,11,0.3)]"
                    id="btn-modal-put"
                  >
                    <span>COMMIT_PUT_REPLACE</span>
                    <ArrowUpRight className="w-3.5 h-3.5" />
                  </button>
                )}
              </div>
            </div>
          )}

          {activeTab === "delete" && (
            <div className="flex flex-col gap-4 py-2 animate-fadeIn font-mono">
              <div className="p-4 bg-red-950/20 border border-red-500/20 rounded text-red-300">
                <div className="flex items-center gap-2 mb-1.5 uppercase font-bold text-xs tracking-wider">
                  <AlertCircle className="w-4 h-4 text-red-400" />
                  <span>DANGEROUS OPERATIONAL DIRECTIVE</span>
                </div>
                <p className="leading-normal text-[10px] uppercase tracking-wide">
                  Invoking DELETE will execute an immediate SQL purge query on PostgreSQL row matching ID {order.id}. This transactional change is permanent and un-recoverable.
                </p>
              </div>

              <div className="flex justify-center py-2">
                <button
                  onClick={handleDelete}
                  disabled={loading}
                  className="px-5 py-2.5 bg-red-600 hover:bg-red-500 disabled:opacity-50 text-white font-bold text-[11px] tracking-widest uppercase rounded flex items-center gap-2 transition-all cursor-pointer shadow-[0_0_20px_rgba(239,68,68,0.4)]"
                  id="btn-modal-delete"
                >
                  <Trash2 className="w-4 h-4" />
                  <span>EXECUTE_ROW_PURGE</span>
                </button>
              </div>
            </div>
          )}

          {/* Feedback messages */}
          {feedback && (
            <div
              className={`p-3 rounded border text-[11px] font-mono flex items-start gap-2.5 mt-2 animate-fadeIn uppercase ${
                feedback.success
                  ? "bg-green-950/20 border-green-500/20 text-green-300"
                  : "bg-red-950/20 border-red-500/20 text-red-300"
              }`}
              id="member-modal-feedback"
            >
              <div className="flex-1 leading-normal">
                <span className="font-bold block mb-0.5">{feedback.success ? "TRANSACTION VERIFIED" : "SECTOR ERROR RESPONSE"}</span>
                <span>{feedback.msg}</span>
              </div>
            </div>
          )}

        </div>

        {/* Modal Footer */}
        <div className="bg-[#0c0d0f] px-5 py-3 border-t border-white/5 text-[9px] text-slate-600 flex items-center justify-between font-mono uppercase tracking-wider">
          <span>Engine version: V1.4.2</span>
          <span>Compliance check guaranteed</span>
        </div>

      </div>
    </div>
  );
}
