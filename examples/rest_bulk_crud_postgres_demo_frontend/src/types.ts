export interface Order {
  id: string;
  sku: string;
  quantity: number;
  status: string;
}

export interface ApiTrace {
  id: string;
  timestamp: string;
  method: "GET" | "POST" | "PATCH" | "PUT" | "DELETE";
  url: string;
  requestBody?: string;
  status?: number;
  responseBody?: string;
  latencyMs?: number;
  type: "collection" | "bulk" | "member" | "system";
}

export interface DemoConfig {
  engine_kind: string;
  resource: string;
  source: string;
  host: string;
  port: number;
  user: string;
  db: string;
}

export interface HealthStatus {
  status: string;
}
