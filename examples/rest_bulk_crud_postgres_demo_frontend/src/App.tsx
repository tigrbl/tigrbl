import { useState, useEffect } from "react";
import Header from "./components/Header";
import OrdersTable from "./components/OrdersTable";
import BulkComposer from "./components/BulkComposer";
import OpenApiDoc from "./components/OpenApiDoc";
import TraceConsole from "./components/TraceConsole";
import MemberCRUDModal from "./components/MemberCRUDModal";
import { Order, ApiTrace, HealthStatus, DemoConfig } from "./types";
import { Database, ArrowRightLeft, BookOpen } from "lucide-react";

export default function App() {
  const [orders, setOrders] = useState<Order[]>([]);
  const [selectedIds, setSelectedIds] = useState<string[]>([]);
  const [traces, setTraces] = useState<ApiTrace[]>([]);
  const [health, setHealth] = useState<HealthStatus | null>(null);
  const [config, setConfig] = useState<DemoConfig | null>(null);
  const [loadingOrders, setLoadingOrders] = useState(false);
  const [loadingHealth, setLoadingHealth] = useState(false);
  const [selectedMemberOrder, setSelectedMemberOrder] = useState<Order | null>(null);

  // ------------------- Core API Exec Handler (Trace Logger) -------------------
  const executeApiRequest = async (
    method: "GET" | "POST" | "PATCH" | "PUT" | "DELETE",
    path: string,
    payload: any,
    type: ApiTrace["type"]
  ): Promise<any> => {
    const traceId = Math.random().toString(36).substring(2, 9);
    const start = performance.now();
    const timestamp = new Date().toLocaleTimeString();

    const requestBodyStr = payload ? JSON.stringify(payload, null, 2) : undefined;

    // Append an initial pending trace record
    const pendingTrace: ApiTrace = {
      id: traceId,
      timestamp,
      method,
      url: `/api${path}`,
      requestBody: requestBodyStr,
      type
    };
    setTraces((prev) => [...prev, pendingTrace]);

    try {
      const options: RequestInit = {
        method,
        headers: {
          "Content-Type": "application/json"
        }
      };

      if (payload && method !== "GET") {
        options.body = JSON.stringify(payload);
      }

      const response = await fetch(`/api${path}`, options);
      const latencyMs = Math.round(performance.now() - start);

      const text = await response.text();
      let responseBodyStr = text;
      let parsedData: any = null;

      try {
        parsedData = JSON.parse(text);
        responseBodyStr = JSON.stringify(parsedData, null, 2);
      } catch {
        // Not JSON
      }

      // Update trace record with response details
      setTraces((prev) =>
        prev.map((t) =>
          t.id === traceId
            ? {
                ...t,
                status: response.status,
                responseBody: responseBodyStr,
                latencyMs
              }
            : t
        )
      );

      if (!response.ok) {
        throw new Error(parsedData?.detail || parsedData?.error || `HTTP Error ${response.status}: ${response.statusText}`);
      }

      return parsedData;
    } catch (err: any) {
      const latencyMs = Math.round(performance.now() - start);
      setTraces((prev) =>
        prev.map((t) =>
          t.id === traceId
            ? {
                ...t,
                status: t.status || 500,
                responseBody: JSON.stringify({ error: err.message || "Network Error" }, null, 2),
                latencyMs
              }
            : t
        )
      );
      throw err;
    }
  };

  // ------------------- Data Fetching -------------------
  const fetchOrders = async () => {
    setLoadingOrders(true);
    try {
      const data = await executeApiRequest("GET", "/orders", null, "collection");
      if (Array.isArray(data)) {
        setOrders(data);
      }
    } catch (err) {
      console.error("Failed to load orders:", err);
    } finally {
      setLoadingOrders(false);
    }
  };

  const fetchHealth = async () => {
    setLoadingHealth(true);
    try {
      const response = await fetch("/api/healthz");
      if (response.ok) {
        const data = await response.json();
        setHealth(data);
      }
    } catch (err) {
      console.error("Failed to load health status:", err);
    } finally {
      setLoadingHealth(false);
    }
  };

  const fetchConfig = async () => {
    try {
      const response = await fetch("/api/demo-config");
      if (response.ok) {
        const data = await response.json();
        setConfig(data);
      }
    } catch (err) {
      console.error("Failed to load demo config:", err);
    }
  };

  // ------------------- Operations -------------------
  const handleBulkDelete = async (ids: string[]) => {
    try {
      await executeApiRequest("DELETE", "/orders", ids, "bulk");
      fetchOrders();
    } catch (err) {
      console.error("Bulk delete failed:", err);
      throw err;
    }
  };

  const handleTriggerSeed = async () => {
    const seedOrders = [
      { id: "ord-demo-301", sku: "sku-demo-301", quantity: 25, status: "pending" },
      { id: "ord-demo-302", sku: "sku-demo-302", quantity: 8, status: "allocated" },
      { id: "ord-demo-303", sku: "sku-demo-303", quantity: 150, status: "ready" },
      { id: "ord-demo-304", sku: "sku-demo-304", quantity: 45, status: "pending" },
      { id: "ord-demo-305", sku: "sku-demo-305", quantity: 2, status: "packed" }
    ];

    try {
      await executeApiRequest("POST", "/orders", seedOrders, "collection");
      fetchOrders();
    } catch (err) {
      console.error("Failed to seed database:", err);
    }
  };

  const handleClearTraces = () => {
    setTraces([]);
  };

  const loadTemplateIntoComposer = (templateName: string) => {
    const event = new CustomEvent("load-openapi-template", {
      detail: { mode: templateName }
    });
    window.dispatchEvent(event);
  };

  // ------------------- Effects & Listeners -------------------
  useEffect(() => {
    fetchConfig();
    fetchHealth();
    fetchOrders();

    // Listen to database mutation events from nested panels to auto-reload
    const handleMutation = () => {
      fetchOrders();
      fetchHealth(); // refresh server telemetry
    };

    window.addEventListener("orders-db-mutated", handleMutation);
    return () => {
      window.removeEventListener("orders-db-mutated", handleMutation);
    };
  }, []);

  return (
    <div className="min-h-screen bg-[#0c0d0f] text-slate-300 font-sans selection:bg-cyan-500/20 selection:text-cyan-300 flex flex-col">
      {/* 1. Header & Live Connection Telemetry */}
      <Header
        health={health}
        config={config}
        loadingHealth={loadingHealth}
        onRefreshHealth={fetchHealth}
      />

      {/* 2. Main Dashboard Bento Layout */}
      <main className="flex-1 max-w-7xl w-full mx-auto p-4 sm:p-6 lg:p-8 flex flex-col gap-6">
        
        {/* Pitch / Quick Info Banner */}
        <div className="bg-[#111216] border border-white/5 rounded-lg p-4 flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="flex items-start gap-3.5">
            <div className="p-2 bg-cyan-600/15 rounded text-cyan-400 shrink-0 border border-cyan-500/20 shadow-[0_0_10px_rgba(6,182,212,0.15)]">
              <Database className="w-5 h-5" />
            </div>
            <div>
              <h4 className="text-xs font-bold uppercase tracking-widest text-white">Relational RestBulkCrudTable Spec Proof</h4>
              <p className="text-[11px] text-slate-400 mt-1 leading-relaxed max-w-2xl uppercase font-mono">
                Operator desk proving standard HTTP rest bulk mutations (POST, PATCH, PUT, DELETE) over relational databases in a single roundtrip transaction without protocol bloat.
              </p>
            </div>
          </div>
          
          <div className="flex items-center gap-3 shrink-0 font-mono text-[10px]">
            <div className="flex items-center gap-1 bg-[#0c0d0f] px-2.5 py-1 rounded text-slate-400 border border-white/5 uppercase">
              <ArrowRightLeft className="w-3.5 h-3.5 text-cyan-500" />
              <span>Base: <strong className="text-white">/api</strong></span>
            </div>
            <div className="flex items-center gap-1 bg-[#0c0d0f] px-2.5 py-1 rounded text-slate-400 border border-white/5 uppercase">
              <BookOpen className="w-3.5 h-3.5 text-cyan-500" />
              <span>Spec: <strong className="text-white">OpenAPI 3.0</strong></span>
            </div>
          </div>
        </div>

        {/* Dynamic Bento Layout Split Screen */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
          
          {/* Left Block (Grid & Composer) - Spans 7 cols */}
          <div className="lg:col-span-7 flex flex-col gap-6">
            
            {/* Orders Table Grid Panel */}
            <div>
              <div className="flex items-center justify-between mb-2 uppercase font-mono text-[10px] tracking-widest text-slate-500">
                <span>PostgreSQL Table Frame</span>
                <span>schema: orders</span>
              </div>
              <OrdersTable
                orders={orders}
                loading={loadingOrders}
                selectedIds={selectedIds}
                onSelectionChange={setSelectedIds}
                onOpenMemberModal={setSelectedMemberOrder}
                onRefreshOrders={fetchOrders}
                onBulkDelete={handleBulkDelete}
                onTriggerSeed={handleTriggerSeed}
              />
            </div>

            {/* Bulk Composer Panel */}
            <div>
              <div className="flex items-center justify-between mb-2 uppercase font-mono text-[10px] tracking-widest text-slate-500">
                <span>Active Payload Composer</span>
                <span className="text-cyan-400 font-bold">Transaction ready</span>
              </div>
              <BulkComposer
                selectedIds={selectedIds}
                onExecuteRequest={executeApiRequest}
              />
            </div>

          </div>

          {/* Right Block (OpenAPI Doc & Request traces) - Spans 5 cols */}
          <div className="lg:col-span-5 flex flex-col gap-6">
            
            {/* OpenAPI Contract Inspector Panel */}
            <div>
              <div className="flex items-center justify-between mb-2 uppercase font-mono text-[10px] tracking-widest text-slate-500">
                <span>Specification Contract Doc</span>
                <span>V3.0.json</span>
              </div>
              <OpenApiDoc
                onLoadTemplate={loadTemplateIntoComposer}
              />
            </div>

            {/* Real-time Traces Console Panel */}
            <div>
              <div className="flex items-center justify-between mb-2 uppercase font-mono text-[10px] tracking-widest text-slate-500">
                <span>Network Stream Observer</span>
                <span className="text-green-400 animate-pulse font-bold">● Active</span>
              </div>
              <TraceConsole
                traces={traces}
                onClearTraces={handleClearTraces}
              />
            </div>

          </div>

        </div>
      </main>

      {/* 3. Member CRUD Modal (GET /orders/{item_id}, etc.) */}
      {selectedMemberOrder && (
        <MemberCRUDModal
          order={selectedMemberOrder}
          onClose={() => setSelectedMemberOrder(null)}
          onExecuteRequest={executeApiRequest}
        />
      )}

      {/* Footer Branding */}
      <footer className="bg-[#0c0d0f] border-t border-white/5 py-6 text-center text-[10px] text-slate-600 font-mono mt-auto uppercase tracking-wider">
        <div className="max-w-7xl mx-auto px-4 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2">
          <span>
            TIGRBL DEMO UNIT &bull; Client-to-Proxy Origin Validation
          </span>
          <span>
            TIGRBL PostgreSQL Console &copy; 2026 - VERSION 1.0.42
          </span>
        </div>
      </footer>
    </div>
  );
}
