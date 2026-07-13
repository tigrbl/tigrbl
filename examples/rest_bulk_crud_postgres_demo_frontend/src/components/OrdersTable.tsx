import { useState } from "react";
import { Search, Eye, Trash2, RefreshCw, CheckSquare, Square, AlertCircle, Sparkles } from "lucide-react";
import { Order } from "../types";

interface OrdersTableProps {
  orders: Order[];
  loading: boolean;
  selectedIds: string[];
  onSelectionChange: (ids: string[]) => void;
  onOpenMemberModal: (order: Order) => void;
  onRefreshOrders: () => void;
  onBulkDelete: (ids: string[]) => Promise<void>;
  onTriggerSeed: () => Promise<void>;
}

export default function OrdersTable({
  orders,
  loading,
  selectedIds,
  onSelectionChange,
  onOpenMemberModal,
  onRefreshOrders,
  onBulkDelete,
  onTriggerSeed
}: OrdersTableProps) {
  const [searchTerm, setSearchTerm] = useState("");
  const [statusFilter, setStatusFilter] = useState<string>("all");
  const [deletingBulk, setDeletingBulk] = useState(false);

  // Filter orders based on user inputs
  const filteredOrders = orders.filter((order) => {
    const query = searchTerm.toLowerCase();
    const matchesSearch = order.id.toLowerCase().includes(query) ||
                          order.sku.toLowerCase().includes(query) ||
                          order.status.toLowerCase().includes(query);
    const matchesStatus = statusFilter === "all" || order.status === statusFilter;
    return matchesSearch && matchesStatus;
  });

  const handleSelectAll = () => {
    if (selectedIds.length === filteredOrders.length) {
      onSelectionChange([]);
    } else {
      onSelectionChange(filteredOrders.map((o) => o.id));
    }
  };

  const handleSelectRow = (id: string) => {
    if (selectedIds.includes(id)) {
      onSelectionChange(selectedIds.filter((x) => x !== id));
    } else {
      onSelectionChange([...selectedIds, id]);
    }
  };

  const getStatusBadge = (status: Order["status"]) => {
    switch (status) {
      case "pending":
        return "bg-amber-900/30 text-amber-400 border-amber-500/20";
      case "allocated":
        return "bg-green-900/30 text-green-400 border-green-500/20";
      case "ready":
      case "packed":
        return "bg-blue-900/30 text-blue-400 border-blue-500/20";
      default:
        return "bg-slate-900/30 text-slate-400 border-white/10";
    }
  };

  const executeBulkDelete = async () => {
    if (window.confirm(`Are you sure you want to bulk delete the ${selectedIds.length} selected orders?`)) {
      setDeletingBulk(true);
      try {
        await onBulkDelete(selectedIds);
        onSelectionChange([]);
      } finally {
        setDeletingBulk(false);
      }
    }
  };

  // Stats calculation
  const totalQuantity = filteredOrders.reduce((sum, o) => sum + o.quantity, 0);
  const totalCount = filteredOrders.length;
  const selectedVisibleCount = filteredOrders.filter(o => selectedIds.includes(o.id)).length;
  const statusOptions = ["all", ...Array.from(new Set(orders.map((order) => order.status)))];

  return (
    <div className="bg-[#111216] border border-white/10 rounded-lg overflow-hidden" id="orders-database-grid">
      {/* Immersive Header section */}
      <div className="h-11 bg-[#16181c] border-b border-white/5 flex items-center px-4 justify-between">
        <span className="text-xs font-bold uppercase tracking-widest text-slate-400">
          Collection: Orders Table
        </span>
        <div className="flex gap-2">
          {orders.length === 0 && (
            <button
              onClick={onTriggerSeed}
              className="text-[10px] bg-cyan-600/20 text-cyan-400 px-2.5 py-1 border border-cyan-500/30 rounded uppercase font-bold tracking-wider hover:bg-cyan-600/30 cursor-pointer"
              id="btn-table-seed-direct"
            >
              + Seed Demo Data
            </button>
          )}
          <button
            onClick={onRefreshOrders}
            className="text-[10px] bg-slate-800/80 text-slate-300 px-2.5 py-1 border border-white/10 rounded uppercase font-bold tracking-wider hover:bg-slate-700/80 cursor-pointer flex items-center gap-1"
            title="Reload orders from DB"
            id="btn-reload-grid"
          >
            <RefreshCw className={`w-3 h-3 ${loading ? "animate-spin text-cyan-400" : ""}`} />
            <span>SYNC TABLE</span>
          </button>
        </div>
      </div>

      {/* Search, Filter Toolbar */}
      <div className="p-3.5 bg-[#0c0d0f] border-b border-white/5 flex flex-col md:flex-row md:items-center justify-between gap-4">
        {/* Search Input */}
        <div className="relative flex-1 max-w-sm">
          <Search className="absolute left-3 top-2.5 h-3.5 w-3.5 text-slate-500" />
          <input
            type="text"
            placeholder="FILTER BY ID, SKU, STATUS..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-9 pr-4 py-1.5 text-[11px] bg-[#111216] border border-white/10 rounded text-white placeholder-slate-600 focus:outline-none focus:border-cyan-500 uppercase tracking-wider"
            id="orders-search-input"
          />
        </div>

        {/* Status Filters */}
        <div className="flex items-center gap-2">
          <span className="text-[10px] font-mono text-slate-600 uppercase tracking-widest hidden sm:inline">STATE:</span>
          <div className="inline-flex bg-[#111216] p-0.5 rounded border border-white/5 text-[11px]">
            {statusOptions.map((st) => {
              const isActive = statusFilter === st;
              return (
                <button
                  key={st}
                  onClick={() => setStatusFilter(st)}
                  className={`px-2.5 py-1 rounded text-[10px] font-bold uppercase transition-all cursor-pointer tracking-wider ${
                    isActive
                      ? "bg-cyan-600/20 text-cyan-400 border border-cyan-500/30"
                      : "text-slate-500 hover:text-slate-300"
                  }`}
                  id={`filter-status-${st}`}
                >
                  {st}
                </button>
              );
            })}
          </div>
        </div>
      </div>

      {/* Grid Quick Summary Dashboard Cards */}
      <div className="grid grid-cols-3 border-b border-white/5 bg-[#08090b] font-mono text-[11px]">
        <div className="p-3 border-r border-white/5 text-center flex flex-col justify-center">
          <span className="text-slate-600 text-[9px] uppercase tracking-widest block mb-0.5">Rows Matching</span>
          <span className="text-white font-bold text-xs">{totalCount} RECORD(S)</span>
        </div>
        <div className="p-3 border-r border-white/5 text-center flex flex-col justify-center">
          <span className="text-slate-600 text-[9px] uppercase tracking-widest block mb-0.5">Total Quantity</span>
          <span className="text-cyan-400 font-bold text-xs">{totalQuantity} UNIT(S)</span>
        </div>
        <div className="p-3 text-center flex flex-col justify-center">
          <span className="text-slate-600 text-[9px] uppercase tracking-widest block mb-0.5">Visible Selected</span>
          <span className="text-white font-bold text-xs">
            {selectedVisibleCount} QUEUED
          </span>
        </div>
      </div>

      {/* Bulk action helper */}
      {selectedIds.length > 0 && (
        <div className="bg-cyan-950/20 border-b border-cyan-500/20 px-4 py-2 flex items-center justify-between text-[11px] text-cyan-400 animate-fadeIn" id="bulk-selection-bar">
          <div className="flex items-center gap-2">
            <CheckSquare className="w-3.5 h-3.5 text-cyan-400" />
            <span>
              QUEUE_TARGET: <strong className="text-white font-mono">[{selectedIds.join(", ")}]</strong> selected.
            </span>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={() => onSelectionChange([])}
              className="text-slate-500 hover:text-slate-300 px-2 py-1 uppercase tracking-wider font-bold cursor-pointer"
            >
              CLEAR_QUEUE
            </button>
            <button
              onClick={executeBulkDelete}
              disabled={deletingBulk}
              className="flex items-center gap-1.5 bg-rose-950/50 hover:bg-rose-900 border border-rose-500/30 text-rose-300 px-3 py-1 rounded text-[10px] font-bold tracking-wider uppercase transition-all cursor-pointer"
              id="btn-bulk-delete-action"
            >
              <Trash2 className="w-3 h-3 text-rose-400" />
              <span>{deletingBulk ? "DELETING..." : "COMMIT_BULK_DELETE"}</span>
            </button>
          </div>
        </div>
      )}

      {/* Main Table Content */}
      <div className="overflow-x-auto custom-scrollbar">
        {loading ? (
          <div className="py-20 text-center text-slate-500 flex flex-col items-center justify-center gap-3">
            <RefreshCw className="w-6 h-6 animate-spin text-cyan-400" />
            <p className="font-mono text-[10px] uppercase tracking-widest">Executing PostgreSQL relational lookup...</p>
          </div>
        ) : filteredOrders.length === 0 ? (
          <div className="py-16 px-4 text-center">
            <div className="max-w-md mx-auto flex flex-col items-center justify-center gap-3">
              <AlertCircle className="w-8 h-8 text-slate-600" />
              <h4 className="text-slate-300 font-bold text-xs uppercase tracking-widest">No matching order entries</h4>
              <p className="text-slate-500 text-[11px] leading-relaxed">
                {orders.length === 0
                  ? "The PostgreSQL database table is empty. Press below to create real demo rows through POST /orders."
                  : "Zero rows matched your filter requirements. Refine your query."}
              </p>
              
              {orders.length === 0 && (
                <button
                  onClick={onTriggerSeed}
                  className="mt-2 flex items-center gap-1.5 px-4 py-2 bg-cyan-600 hover:bg-cyan-500 text-white text-[11px] font-bold rounded uppercase tracking-widest transition-all cursor-pointer"
                  id="btn-seed-data"
                >
                  <Sparkles className="w-3.5 h-3.5 text-cyan-200" />
                  <span>Seed Relational Demo Data</span>
                </button>
              )}
            </div>
          </div>
        ) : (
          <table className="w-full text-left border-collapse text-xs">
            <thead>
              <tr className="bg-[#111216] border-b border-white/10 text-slate-500 font-mono text-[10px] uppercase tracking-widest select-none">
                <th className="p-3 w-12 text-center">
                  <button
                    onClick={handleSelectAll}
                    className="text-slate-500 hover:text-slate-300 transition-colors focus:outline-none cursor-pointer"
                    title="Toggle all rows"
                    id="btn-table-toggle-all"
                  >
                    {selectedIds.length === filteredOrders.length ? (
                      <CheckSquare className="w-4 h-4 text-cyan-400 mx-auto" />
                    ) : (
                      <Square className="w-4 h-4 mx-auto" />
                    )}
                  </button>
                </th>
                <th className="p-3">Resource ID</th>
                <th className="p-3 hidden sm:table-cell">SKU Code</th>
                <th className="p-3 text-center">Qty</th>
                <th className="p-3 text-center w-24">Status</th>
                <th className="p-3 text-right pr-4">Action</th>
              </tr>
            </thead>
            <tbody className="text-[13px] font-mono divide-y divide-white/[0.04]">
              {filteredOrders.map((order) => {
                const isSelected = selectedIds.includes(order.id);
                return (
                  <tr
                    key={order.id}
                    className={`border-b border-white/5 hover:bg-white/[0.03] transition-colors cursor-pointer ${
                      isSelected ? "bg-white/[0.02]" : ""
                    }`}
                  >
                    <td className="p-3 text-center">
                      <button
                        onClick={() => handleSelectRow(order.id)}
                        className="text-slate-600 hover:text-slate-300 transition-colors focus:outline-none cursor-pointer"
                        id={`chk-order-${order.id}`}
                      >
                        {isSelected ? (
                          <CheckSquare className="w-4 h-4 text-cyan-400 mx-auto" />
                        ) : (
                          <Square className="w-4 h-4 mx-auto" />
                        )}
                      </button>
                    </td>
                    <td className="p-3 text-cyan-400 font-bold">
                      {order.id}
                    </td>
                    <td className="p-3 text-slate-500 text-[11px] hidden sm:table-cell">
                      {order.sku}
                    </td>
                    <td className="p-3 text-center text-slate-300">
                      {order.quantity}
                    </td>
                    <td className="p-3 text-center">
                      <span className={`inline-block px-2.5 py-0.5 rounded-full text-[9px] font-bold uppercase border tracking-wider ${getStatusBadge(order.status)}`}>
                        {order.status}
                      </span>
                    </td>
                    <td className="p-3 text-right pr-4">
                      <button
                        onClick={() => onOpenMemberModal(order)}
                        className="px-2.5 py-1 bg-white/5 border border-white/10 rounded text-[10px] text-white hover:bg-white/10 uppercase tracking-widest font-bold cursor-pointer transition-all inline-flex items-center gap-1"
                        id={`btn-inspect-member-${order.id}`}
                      >
                        <Eye className="w-3 h-3 text-cyan-400" />
                        <span>Inspect</span>
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        )}
      </div>

      {/* Table Footer */}
      <div className="bg-[#0c0d0f] px-4 py-2 border-t border-white/10 text-[10px] text-slate-600 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2 font-mono">
        <span>
          STORAGE: <strong className="text-slate-500 uppercase">PostgresQL_15_orders</strong>
        </span>
        <span className="uppercase">
          Click &apos;Inspect&apos; for member-level REST operations
        </span>
      </div>
    </div>
  );
}
