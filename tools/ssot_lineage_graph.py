"""Build a self-contained interactive SSOT lineage graph.

The input files are produced by:

    uv run ssot-registry graph export . --format json --output tmp/ssot-lineage-graph.json
    uv run ssot-registry registry export . --format json --output tmp/ssot-registry-export.json
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any


FAMILY_BY_PREFIX = {
    "adr": "ADR",
    "bnd": "Boundary",
    "clm": "Claim",
    "evd": "Evidence",
    "feat": "Feature",
    "iss": "Issue",
    "prf": "Profile",
    "rel": "Release",
    "rsk": "Risk",
    "spc": "Spec",
    "tst": "Test",
}


def family_from_id(entity_id: str) -> str:
    prefix = entity_id.split(":", 1)[0]
    return FAMILY_BY_PREFIX.get(prefix, prefix.upper())


def title_for(item: dict[str, Any]) -> str:
    for key in ("title", "name", "summary", "description"):
        value = item.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return item.get("id", "")


def load_registry(path: Path) -> dict[str, dict[str, Any]]:
    registry = json.loads(path.read_text(encoding="utf-8"))
    nodes: dict[str, dict[str, Any]] = {}
    for family_name, values in registry.items():
        if not isinstance(values, list):
            continue
        for item in values:
            if not isinstance(item, dict):
                continue
            entity_id = item.get("id")
            if not isinstance(entity_id, str):
                continue
            nodes[entity_id] = {
                "id": entity_id,
                "family": family_from_id(entity_id),
                "label": title_for(item) or entity_id,
                "status": item.get("status") or item.get("lifecycle") or "",
                "tier": item.get("tier") or item.get("target_claim_tier") or "",
                "origin": item.get("origin") or "",
                "path": item.get("path") or "",
            }
    return nodes


def build_payload(graph_path: Path, registry_path: Path) -> dict[str, Any]:
    graph = json.loads(graph_path.read_text(encoding="utf-8"))
    edges = [
        {"from": edge["from"], "to": edge["to"], "type": edge.get("type", "RELATED")}
        for edge in graph.get("edges", [])
        if isinstance(edge, dict) and isinstance(edge.get("from"), str) and isinstance(edge.get("to"), str)
    ]
    nodes = load_registry(registry_path)
    for edge in edges:
        for entity_id in (edge["from"], edge["to"]):
            nodes.setdefault(
                entity_id,
                {
                    "id": entity_id,
                    "family": family_from_id(entity_id),
                    "label": entity_id,
                    "status": "",
                    "tier": "",
                    "origin": "",
                    "path": "",
                },
            )

    degree_counts: Counter[str] = Counter()
    for edge in edges:
        degree_counts[edge["from"]] += 1
        degree_counts[edge["to"]] += 1
    for entity_id, node in nodes.items():
        node["degree"] = degree_counts[entity_id]

    family_counts = Counter(node["family"] for node in nodes.values())
    edge_counts = Counter(edge["type"] for edge in edges)
    return {
        "generatedFrom": {
            "graph": str(graph_path),
            "registry": str(registry_path),
        },
        "nodes": sorted(nodes.values(), key=lambda item: item["id"]),
        "edges": edges,
        "summary": {
            "nodeCount": len(nodes),
            "edgeCount": len(edges),
            "families": dict(sorted(family_counts.items())),
            "edgeTypes": dict(sorted(edge_counts.items())),
        },
    }


HTML = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Tigrbl SSOT Lineage Graph</title>
  <style>
    :root {
      color-scheme: light;
      --bg: #f7f8fa;
      --panel: #ffffff;
      --text: #111827;
      --muted: #64748b;
      --line: #d7dde8;
      --accent: #0f766e;
      --accent-2: #b45309;
      --accent-3: #2563eb;
      --shadow: 0 10px 30px rgba(15, 23, 42, 0.08);
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      min-height: 100vh;
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background: var(--bg);
      color: var(--text);
      overflow: hidden;
    }
    .app {
      display: grid;
      grid-template-columns: 340px 1fr 360px;
      height: 100vh;
    }
    aside, main {
      min-width: 0;
      min-height: 0;
    }
    .panel {
      background: var(--panel);
      border-right: 1px solid var(--line);
      overflow: auto;
    }
    .detail {
      border-right: 0;
      border-left: 1px solid var(--line);
    }
    .section {
      padding: 16px;
      border-bottom: 1px solid var(--line);
    }
    h1 {
      margin: 0 0 6px;
      font-size: 18px;
      line-height: 1.25;
      letter-spacing: 0;
    }
    h2 {
      margin: 0 0 10px;
      font-size: 13px;
      color: var(--muted);
      text-transform: uppercase;
      letter-spacing: 0.08em;
    }
    label {
      display: block;
      margin: 12px 0 5px;
      font-size: 12px;
      color: var(--muted);
      font-weight: 650;
    }
    input, select, button {
      width: 100%;
      min-height: 36px;
      border: 1px solid var(--line);
      border-radius: 6px;
      background: #fff;
      color: var(--text);
      font: inherit;
      font-size: 13px;
      padding: 8px 10px;
    }
    button {
      cursor: pointer;
      font-weight: 650;
      background: #f8fafc;
    }
    button.primary {
      background: var(--accent);
      border-color: var(--accent);
      color: #fff;
    }
    button:disabled {
      opacity: 0.5;
      cursor: not-allowed;
    }
    .row {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 8px;
    }
    .stats {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 8px;
      margin-top: 12px;
    }
    .stat {
      border: 1px solid var(--line);
      border-radius: 6px;
      padding: 10px;
      background: #fbfdff;
    }
    .stat strong {
      display: block;
      font-size: 20px;
      line-height: 1.1;
    }
    .stat span {
      display: block;
      color: var(--muted);
      font-size: 12px;
      margin-top: 3px;
    }
    .chips {
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
    }
    .toggles {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 8px;
      margin-top: 8px;
    }
    .toggle {
      display: flex;
      align-items: center;
      gap: 8px;
      min-height: 34px;
      border: 1px solid var(--line);
      border-radius: 6px;
      padding: 7px 9px;
      background: #fff;
      font-size: 12px;
      color: var(--text);
      font-weight: 650;
    }
    .toggle input {
      width: 16px;
      min-height: 16px;
      padding: 0;
      margin: 0;
      flex: 0 0 auto;
    }
    input[type="range"] {
      padding: 0;
      min-height: 28px;
    }
    .chip {
      width: auto;
      min-height: 28px;
      padding: 5px 8px;
      border-radius: 999px;
      font-size: 12px;
      border-color: var(--line);
    }
    .chip.active {
      background: #e0f2f1;
      border-color: #99f6e4;
      color: #115e59;
    }
    .toolbar {
      position: absolute;
      z-index: 5;
      top: 12px;
      left: 12px;
      right: 12px;
      display: flex;
      justify-content: space-between;
      gap: 12px;
      pointer-events: none;
    }
    .toolbar > div {
      display: flex;
      gap: 8px;
      pointer-events: auto;
    }
    .toolbar button {
      width: auto;
      min-width: 40px;
      padding: 8px 12px;
      box-shadow: var(--shadow);
    }
    main {
      position: relative;
      background: #eef2f7;
    }
    canvas {
      display: block;
      width: 100%;
      height: 100%;
      cursor: grab;
    }
    canvas.dragging { cursor: grabbing; }
    .list {
      display: grid;
      gap: 6px;
      max-height: 330px;
      overflow: auto;
    }
    .item {
      width: 100%;
      text-align: left;
      border: 1px solid var(--line);
      border-radius: 6px;
      background: #fff;
      padding: 9px;
    }
    .item strong {
      display: block;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
      font-size: 13px;
    }
    .item span {
      display: block;
      margin-top: 3px;
      color: var(--muted);
      font-size: 12px;
      overflow-wrap: anywhere;
    }
    .item.active {
      border-color: var(--accent);
      box-shadow: 0 0 0 2px rgba(15, 118, 110, 0.16);
    }
    .kv {
      display: grid;
      grid-template-columns: 92px 1fr;
      gap: 8px;
      margin: 8px 0;
      font-size: 13px;
    }
    .kv span:first-child {
      color: var(--muted);
    }
    .wrap {
      overflow-wrap: anywhere;
    }
    .legend {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 8px;
    }
    .legend div {
      display: flex;
      align-items: center;
      gap: 8px;
      font-size: 12px;
      color: var(--muted);
    }
    .dot {
      width: 10px;
      height: 10px;
      border-radius: 999px;
      flex: 0 0 auto;
    }
    .empty {
      color: var(--muted);
      font-size: 13px;
      line-height: 1.45;
    }
    @media (max-width: 1100px) {
      .app { grid-template-columns: 300px 1fr; }
      .detail { display: none; }
    }
    @media (max-width: 760px) {
      body { overflow: auto; }
      .app { grid-template-columns: 1fr; height: auto; }
      .panel { max-height: none; border-right: 0; }
      main { height: 68vh; }
    }
  </style>
</head>
<body>
  <div class="app">
    <aside class="panel">
      <div class="section">
        <h1>Tigrbl SSOT Lineage Graph</h1>
        <div class="empty">Interactive view of the exported SSOT graph. Select a node for details, then use Focus to make it the lineage center.</div>
        <div class="stats">
          <div class="stat"><strong id="nodeCount">0</strong><span>visible nodes</span></div>
          <div class="stat"><strong id="edgeCount">0</strong><span>visible edges</span></div>
          <div class="stat"><strong id="renderNodeCount">0</strong><span>drawn nodes</span></div>
          <div class="stat"><strong id="renderEdgeCount">0</strong><span>drawn edges</span></div>
        </div>
      </div>
      <div class="section">
        <h2>Explore</h2>
        <label for="search">Search</label>
        <input id="search" type="search" placeholder="id, title, path, status">
        <div class="row">
          <div>
            <label for="family">Family</label>
            <select id="family"></select>
          </div>
          <div>
            <label for="edgeType">Edge</label>
            <select id="edgeType"></select>
          </div>
        </div>
        <label for="layoutMode">Layout</label>
        <select id="layoutMode">
          <option value="network">Network</option>
          <option value="lineage">Top-down lineage</option>
        </select>
        <div class="row">
          <div>
            <label for="networkEngine">Network Engine</label>
            <select id="networkEngine">
              <option value="auto" selected>Auto</option>
              <option value="force">Exact Force</option>
              <option value="barnes">Barnes-Hut Force</option>
              <option value="grid">Grid</option>
            </select>
          </div>
          <div>
            <label for="forceCutoff">Force Cutoff</label>
            <input id="forceCutoff" type="range" min="100" max="10000" value="350" step="50">
            <div class="empty" id="forceCutoffValue">350 nodes</div>
          </div>
        </div>
        <div class="empty" id="engineStatus"></div>
        <div class="toggles">
          <button id="showAllFamilies" type="button">Show all</button>
          <button id="hideAllFamilies" type="button">Hide all</button>
        </div>
        <div class="toggles" id="familyToggles"></div>
        <div class="row">
          <div>
            <label for="depth">Lineage Depth</label>
            <select id="depth">
              <option value="0">Search only</option>
              <option value="1">1 hop</option>
              <option value="2" selected>2 hops</option>
              <option value="3">3 hops</option>
              <option value="4">4 hops</option>
              <option value="5">5 hops</option>
              <option value="max">Maximum</option>
            </select>
          </div>
          <div>
            <label for="limit">Node Limit</label>
            <select id="limit">
              <option value="150">150</option>
              <option value="300" selected>300</option>
              <option value="600">600</option>
              <option value="1200">1200</option>
              <option value="all">All</option>
            </select>
          </div>
        </div>
        <div class="row">
          <div>
            <label for="xScale">X Axis Scale</label>
            <input id="xScale" type="range" min="-1" max="3" value="0" step="0.05">
            <div class="empty" id="xScaleValue">1x</div>
          </div>
          <div>
            <label for="yScale">Y Axis Scale</label>
            <input id="yScale" type="range" min="-1" max="3" value="0" step="0.05">
            <div class="empty" id="yScaleValue">1x</div>
          </div>
        </div>
        <label for="ribbonCulling">Ribbon Culling</label>
        <select id="ribbonCulling">
          <option value="off">Off</option>
          <option value="light" selected>Light</option>
          <option value="strong">Strong</option>
        </select>
        <label>Quick Families</label>
        <div class="chips" id="familyChips"></div>
      </div>
      <div class="section">
        <h2>Results</h2>
        <div class="list" id="results"></div>
      </div>
    </aside>
    <main>
      <div class="toolbar">
        <div>
          <button id="zoomIn" title="Zoom in">+</button>
          <button id="zoomOut" title="Zoom out">-</button>
          <button id="fit" title="Fit graph">Fit</button>
        </div>
        <div>
          <button id="reset" title="Clear search and selection">Reset</button>
          <button id="deselect" title="Deselect current node">Deselect</button>
          <button class="primary" id="expand" title="Use the selected node as the lineage center">Focus</button>
        </div>
      </div>
      <canvas id="graph"></canvas>
    </main>
    <aside class="panel detail">
      <div class="section">
        <h2>Selected</h2>
        <div id="selected" class="empty">Select a node in the graph or results list.</div>
      </div>
      <div class="section">
        <h2>Connected Edges</h2>
        <div id="connections" class="list"></div>
      </div>
      <div class="section">
        <h2>Legend</h2>
        <div class="legend" id="legend"></div>
      </div>
    </aside>
  </div>
  <script>
    const DATA = __DATA__;
    const COLORS = {
      ADR: "#7c3aed", Boundary: "#0f766e", Claim: "#dc2626", Evidence: "#b45309",
      Feature: "#2563eb", Issue: "#be123c", Profile: "#0891b2", Release: "#16a34a",
      Risk: "#a16207", Spec: "#4f46e5", Test: "#475569"
    };
    const LINEAGE_RANK = {
      ADR: 0,
      Spec: 1,
      Boundary: 2,
      Profile: 2,
      Feature: 3,
      Claim: 4,
      Test: 5,
      Evidence: 6,
      Release: 7,
      Issue: 8,
      Risk: 8
    };
    const RANK_LABELS = {
      0: "ADRs",
      1: "Specs",
      2: "Profiles / Boundaries",
      3: "Features",
      4: "Claims",
      5: "Tests",
      6: "Evidence",
      7: "Releases",
      8: "Issues / Risks"
    };
    const nodesById = new Map(DATA.nodes.map(n => [n.id, n]));
    const edges = DATA.edges;
    const adjacency = new Map();
    for (const edge of edges) {
      if (!adjacency.has(edge.from)) adjacency.set(edge.from, []);
      if (!adjacency.has(edge.to)) adjacency.set(edge.to, []);
      adjacency.get(edge.from).push(edge);
      adjacency.get(edge.to).push(edge);
    }

    const canvas = document.getElementById("graph");
    const ctx = canvas.getContext("2d");
    const els = {
      search: document.getElementById("search"),
      family: document.getElementById("family"),
      edgeType: document.getElementById("edgeType"),
      layoutMode: document.getElementById("layoutMode"),
      networkEngine: document.getElementById("networkEngine"),
      forceCutoff: document.getElementById("forceCutoff"),
      forceCutoffValue: document.getElementById("forceCutoffValue"),
      engineStatus: document.getElementById("engineStatus"),
      depth: document.getElementById("depth"),
      limit: document.getElementById("limit"),
      xScale: document.getElementById("xScale"),
      yScale: document.getElementById("yScale"),
      xScaleValue: document.getElementById("xScaleValue"),
      yScaleValue: document.getElementById("yScaleValue"),
      ribbonCulling: document.getElementById("ribbonCulling"),
      results: document.getElementById("results"),
      selected: document.getElementById("selected"),
      connections: document.getElementById("connections"),
      nodeCount: document.getElementById("nodeCount"),
      edgeCount: document.getElementById("edgeCount"),
      renderNodeCount: document.getElementById("renderNodeCount"),
      renderEdgeCount: document.getElementById("renderEdgeCount"),
      chips: document.getElementById("familyChips"),
      familyToggles: document.getElementById("familyToggles"),
      legend: document.getElementById("legend")
    };

    let selectedId = null;
    let centerId = null;
    let visibleNodes = [];
    let visibleEdges = [];
    let simNodes = new Map();
    let zoom = 1;
    let pan = {x: 0, y: 0};
    let drag = null;
    let animationStarted = false;
    let deviceRatio = 1;
    let layoutWorker = null;
    let layoutWorkerUrl = null;
    let workerRunId = 0;
    let workerActive = false;
    const LABEL_NODE_LIMIT = 220;
    const ARROW_EDGE_LIMIT = 5000;
    const EXACT_FORCE_HARD_LIMIT = 2500;

    function fillSelect(select, values, allLabel) {
      select.innerHTML = `<option value="">${allLabel}</option>` + values.map(v => `<option value="${v}">${v}</option>`).join("");
    }

    const families = [...new Set(DATA.nodes.map(n => n.family))].sort();
    const edgeTypes = [...new Set(edges.map(e => e.type))].sort();
    fillSelect(els.family, families, "All");
    fillSelect(els.edgeType, edgeTypes, "All");
    els.chips.innerHTML = families.map(f => `<button class="chip" data-family="${f}">${f} ${DATA.summary.families[f] || 0}</button>`).join("");
    els.familyToggles.innerHTML = families.map(f => `<label class="toggle"><input class="family-toggle" type="checkbox" data-toggle-family="${f}" checked> ${f}</label>`).join("");
    els.legend.innerHTML = families.map(f => `<div><span class="dot" style="background:${COLORS[f] || "#334155"}"></span>${f}</div>`).join("");
    const familyToggleInputs = () => [...document.querySelectorAll(".family-toggle")];

    function matchesSearch(node, q) {
      if (!q) return true;
      const hay = `${node.id} ${node.label} ${node.status} ${node.tier} ${node.origin} ${node.path}`.toLowerCase();
      return hay.includes(q);
    }

    function lineageRank(node) {
      return LINEAGE_RANK[node?.family] ?? 9;
    }

    function nodeLimit() {
      return els.limit.value === "all" ? Number.POSITIVE_INFINITY : Number(els.limit.value);
    }

    function axisScale(input) {
      return Math.pow(10, Number(input.value));
    }

    function formatScale(scale) {
      return scale >= 100 ? `${Math.round(scale)}x` : `${Number(scale.toFixed(scale < 10 ? 2 : 1))}x`;
    }

    function updateAxisScaleLabels() {
      els.xScaleValue.textContent = formatScale(axisScale(els.xScale));
      els.yScaleValue.textContent = formatScale(axisScale(els.yScale));
    }

    function forceCutoff() {
      return Number(els.forceCutoff.value);
    }

    function updateForceCutoffLabel() {
      els.forceCutoffValue.textContent = `${forceCutoff()} nodes`;
    }

    function effectiveNetworkEngine() {
      if (els.layoutMode.value === "lineage") return "lineage";
      if (els.networkEngine.value === "grid") return "grid";
      if (els.networkEngine.value === "barnes") return "barnes";
      if (els.networkEngine.value === "force") return visibleNodes.length > EXACT_FORCE_HARD_LIMIT ? "barnes" : "force";
      if (visibleNodes.length > EXACT_FORCE_HARD_LIMIT) return "barnes";
      return visibleNodes.length > forceCutoff() ? "barnes" : "force";
    }

    function updateEngineStatus() {
      const engine = effectiveNetworkEngine();
      if (els.layoutMode.value === "lineage") {
        els.engineStatus.textContent = "Top-down lineage uses deterministic ranked placement.";
      } else if (els.networkEngine.value === "auto" && engine === "barnes" && visibleNodes.length > EXACT_FORCE_HARD_LIMIT) {
        els.engineStatus.textContent = `Auto: Barnes-Hut worker active because exact force is capped at ${EXACT_FORCE_HARD_LIMIT} nodes; cutoff is ${forceCutoff()} nodes.`;
      } else if (els.networkEngine.value === "auto" && engine === "barnes") {
        els.engineStatus.textContent = `Auto: Barnes-Hut worker active above ${forceCutoff()} nodes for ${visibleNodes.length} visible nodes.`;
      } else if (els.networkEngine.value === "force" && engine === "barnes") {
        els.engineStatus.textContent = `Exact force is capped at ${EXACT_FORCE_HARD_LIMIT} nodes; Barnes-Hut worker active for ${visibleNodes.length} visible nodes.`;
      } else if (els.networkEngine.value === "force") {
        els.engineStatus.textContent = `Exact force selected. Large visible graphs may become slow.`;
      } else if (engine === "barnes") {
        els.engineStatus.textContent = `Barnes-Hut worker force active.`;
      } else {
        els.engineStatus.textContent = `Network engine: ${engine}.`;
      }
    }

    const BARNES_HUT_WORKER_SOURCE = `
      let runId = 0;
      let nodeIds = [];
      let indexById = new Map();
      let x = new Float32Array();
      let y = new Float32Array();
      let vx = new Float32Array();
      let vy = new Float32Array();
      let source = new Uint32Array();
      let target = new Uint32Array();
      let running = false;
      let alpha = 1;
      const theta = 0.8;
      const repulsion = 850;
      const spring = 0.006;
      const damping = 0.86;
      const centerPull = 0.002;

      self.onmessage = event => {
        const msg = event.data;
        if (msg.type === "stop") {
          running = false;
          return;
        }
        if (msg.type !== "start") return;
        running = false;
        runId = msg.runId;
        nodeIds = msg.nodes;
        indexById = new Map(nodeIds.map((id, index) => [id, index]));
        const n = nodeIds.length;
        x = new Float32Array(n);
        y = new Float32Array(n);
        vx = new Float32Array(n);
        vy = new Float32Array(n);
        for (let i = 0; i < n; i++) {
          const p = msg.positions[i] || [0, 0];
          x[i] = p[0];
          y[i] = p[1];
        }
        const pairs = [];
        for (const edge of msg.edges) {
          const a = indexById.get(edge[0]);
          const b = indexById.get(edge[1]);
          if (a === undefined || b === undefined || a === b) continue;
          pairs.push(a, b);
        }
        source = new Uint32Array(pairs.length / 2);
        target = new Uint32Array(pairs.length / 2);
        for (let i = 0, j = 0; i < pairs.length; i += 2, j++) {
          source[j] = pairs[i];
          target[j] = pairs[i + 1];
        }
        alpha = 1;
        running = true;
        tickLoop();
      };

      function makeNode(minX, minY, maxX, maxY) {
        return {minX, minY, maxX, maxY, mass: 0, cx: 0, cy: 0, point: -1, children: null};
      }

      function childIndex(node, px, py) {
        const midX = (node.minX + node.maxX) / 2;
        const midY = (node.minY + node.maxY) / 2;
        return (py >= midY ? 2 : 0) + (px >= midX ? 1 : 0);
      }

      function childBounds(node, index) {
        const midX = (node.minX + node.maxX) / 2;
        const midY = (node.minY + node.maxY) / 2;
        if (index === 0) return [node.minX, node.minY, midX, midY];
        if (index === 1) return [midX, node.minY, node.maxX, midY];
        if (index === 2) return [node.minX, midY, midX, node.maxY];
        return [midX, midY, node.maxX, node.maxY];
      }

      function subdivide(node) {
        node.children = [];
        for (let i = 0; i < 4; i++) node.children[i] = makeNode(...childBounds(node, i));
      }

      function insert(node, index) {
        if (node.children) {
          insert(node.children[childIndex(node, x[index], y[index])], index);
          return;
        }
        if (node.point === -1) {
          node.point = index;
          return;
        }
        const old = node.point;
        if (Math.abs(x[old] - x[index]) < 0.001 && Math.abs(y[old] - y[index]) < 0.001) {
          x[index] += (Math.random() - 0.5) * 2;
          y[index] += (Math.random() - 0.5) * 2;
        }
        if (node.maxX - node.minX < 0.001 || node.maxY - node.minY < 0.001) return;
        node.point = -1;
        subdivide(node);
        insert(node.children[childIndex(node, x[old], y[old])], old);
        insert(node.children[childIndex(node, x[index], y[index])], index);
      }

      function accumulate(node) {
        if (node.children) {
          let mass = 0, cx = 0, cy = 0;
          for (const child of node.children) {
            accumulate(child);
            mass += child.mass;
            cx += child.cx * child.mass;
            cy += child.cy * child.mass;
          }
          node.mass = mass;
          node.cx = mass ? cx / mass : 0;
          node.cy = mass ? cy / mass : 0;
        } else if (node.point !== -1) {
          node.mass = 1;
          node.cx = x[node.point];
          node.cy = y[node.point];
        }
      }

      function buildTree() {
        let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;
        for (let i = 0; i < x.length; i++) {
          minX = Math.min(minX, x[i]);
          minY = Math.min(minY, y[i]);
          maxX = Math.max(maxX, x[i]);
          maxY = Math.max(maxY, y[i]);
        }
        const size = Math.max(maxX - minX, maxY - minY, 1) + 1;
        const root = makeNode(minX - size * 0.05, minY - size * 0.05, minX + size * 1.05, minY + size * 1.05);
        for (let i = 0; i < x.length; i++) insert(root, i);
        accumulate(root);
        return root;
      }

      function applyRepulsion(node, index) {
        if (!node.mass || node.point === index) return;
        const dx = x[index] - node.cx;
        const dy = y[index] - node.cy;
        const distSq = dx * dx + dy * dy + 0.01;
        const width = node.maxX - node.minX;
        if (!node.children || width / Math.sqrt(distSq) < theta) {
          const force = repulsion * node.mass / distSq * alpha;
          vx[index] += dx * force;
          vy[index] += dy * force;
          return;
        }
        for (const child of node.children) applyRepulsion(child, index);
      }

      function tickOnce() {
        if (!x.length) return;
        const root = buildTree();
        for (let i = 0; i < x.length; i++) applyRepulsion(root, i);
        for (let i = 0; i < source.length; i++) {
          const a = source[i];
          const b = target[i];
          const dx = x[b] - x[a];
          const dy = y[b] - y[a];
          const d = Math.sqrt(dx * dx + dy * dy) || 1;
          const force = (d - 140) * spring * alpha;
          const fx = dx / d * force;
          const fy = dy / d * force;
          vx[a] += fx;
          vy[a] += fy;
          vx[b] -= fx;
          vy[b] -= fy;
        }
        for (let i = 0; i < x.length; i++) {
          vx[i] += -x[i] * centerPull * alpha;
          vy[i] += -y[i] * centerPull * alpha;
          vx[i] *= damping;
          vy[i] *= damping;
          x[i] += vx[i];
          y[i] += vy[i];
        }
        alpha = Math.max(0.03, alpha * 0.985);
      }

      function tickLoop() {
        if (!running) return;
        for (let i = 0; i < 2; i++) tickOnce();
        self.postMessage({type: "positions", runId, nodes: nodeIds, x, y});
        setTimeout(tickLoop, 16);
      }
    `;

    function visibleFamilies() {
      return new Set(familyToggleInputs().filter(input => input.checked).map(input => input.dataset.toggleFamily));
    }

    function familyVisible(node) {
      if (!node) return false;
      return visibleFamilies().has(node.family);
    }

    function stopLayoutWorker() {
      workerActive = false;
      workerRunId += 1;
      if (layoutWorker) {
        layoutWorker.postMessage({type: "stop"});
        layoutWorker.terminate();
        layoutWorker = null;
      }
      if (layoutWorkerUrl) {
        URL.revokeObjectURL(layoutWorkerUrl);
        layoutWorkerUrl = null;
      }
    }

    function startBarnesHutWorker() {
      stopLayoutWorker();
      if (!visibleNodes.length) return;
      const runId = workerRunId + 1;
      workerRunId = runId;
      layoutWorkerUrl = URL.createObjectURL(new Blob([BARNES_HUT_WORKER_SOURCE], {type: "text/javascript"}));
      layoutWorker = new Worker(layoutWorkerUrl);
      workerActive = true;
      layoutWorker.onmessage = event => {
        const msg = event.data;
        if (!workerActive || msg.type !== "positions" || msg.runId !== workerRunId) return;
        for (let i = 0; i < msg.nodes.length; i++) {
          const current = simNodes.get(msg.nodes[i]);
          if (!current) continue;
          current.x = msg.x[i];
          current.y = msg.y[i];
          current.vx = 0;
          current.vy = 0;
        }
        draw();
      };
      layoutWorker.onerror = () => {
        workerActive = false;
        els.engineStatus.textContent = "Barnes-Hut worker failed; falling back to grid placement.";
        els.networkEngine.value = "grid";
        stopLayoutWorker();
        seedLayout();
        draw();
      };
      const positions = visibleNodes.map(node => {
        const p = simNodes.get(node.id);
        return p ? [p.x, p.y] : [0, 0];
      });
      layoutWorker.postMessage({
        type: "start",
        runId,
        nodes: visibleNodes.map(node => node.id),
        edges: visibleEdges.map(edge => [edge.from, edge.to]),
        positions
      });
    }

    function collectLineage(seedIds, depth, edgeType) {
      const seen = new Set(seedIds);
      let frontier = new Set(seedIds);
      const includedEdges = [];
      const maxDepth = depth === "max" ? DATA.nodes.length : Number(depth);
      for (let level = 0; level < maxDepth; level++) {
        const next = new Set();
        for (const id of frontier) {
          for (const edge of adjacency.get(id) || []) {
            if (edgeType && edge.type !== edgeType) continue;
            const other = edge.from === id ? edge.to : edge.from;
            includedEdges.push(edge);
            if (!seen.has(other)) {
              seen.add(other);
              next.add(other);
            }
          }
        }
        frontier = next;
        if (!frontier.size) break;
      }
      return {ids: seen, edges: includedEdges};
    }

    function currentSeeds() {
      const q = els.search.value.trim().toLowerCase();
      const family = els.family.value;
      const limit = nodeLimit();
      const filtered = DATA.nodes
        .filter(n => (!family || n.family === family) && familyVisible(n) && matchesSearch(n, q))
        .sort((a, b) => {
          if (els.layoutMode.value === "lineage" && !q && !family) {
            return lineageRank(a) - lineageRank(b) || (b.degree || 0) - (a.degree || 0) || a.id.localeCompare(b.id);
          }
          if (!q && !family) return (b.degree || 0) - (a.degree || 0) || a.id.localeCompare(b.id);
          return a.id.localeCompare(b.id);
        });
      if (centerId) return [centerId];
      return filtered.slice(0, limit).map(n => n.id);
    }

    function update() {
      const depthValue = els.depth.value;
      const edgeType = els.edgeType.value;
      const family = els.family.value;
      const limit = nodeLimit();
      let seedIds = currentSeeds();
      if (!seedIds.length && selectedId) seedIds = [selectedId];
      const lineage = collectLineage(seedIds, depthValue, edgeType);
      let nodeIds = [...lineage.ids];
      if (family) nodeIds = nodeIds.filter(id => (nodesById.get(id) || {}).family === family || seedIds.includes(id));
      nodeIds = nodeIds.filter(id => familyVisible(nodesById.get(id))).slice(0, limit);
      const nodeSet = new Set(nodeIds);
      visibleEdges = cullRibbons((depthValue !== "0" ? lineage.edges : edges).filter(e => nodeSet.has(e.from) && nodeSet.has(e.to) && (!edgeType || e.type === edgeType)));
      visibleNodes = nodeIds.map(id => nodesById.get(id)).filter(Boolean);
      seedLayout();
      updateEngineStatus();
      if (effectiveNetworkEngine() === "barnes") startBarnesHutWorker();
      else stopLayoutWorker();
      renderResults();
      renderSelected();
      tick(140);
      draw();
    }

    function seedLayout() {
      const w = canvas.clientWidth || 900;
      const h = canvas.clientHeight || 700;
      const next = new Map();
      if (els.layoutMode.value === "lineage") {
        const layers = new Map();
        for (const node of visibleNodes) {
          const rank = lineageRank(node);
          if (!layers.has(rank)) layers.set(rank, []);
          layers.get(rank).push(node);
        }
        const orderedRanks = [...layers.keys()].sort((a, b) => a - b);
        const top = 90;
        const baseBottom = Math.max(top + 120, h - 80);
        const baseRowGap = orderedRanks.length <= 1 ? 0 : (baseBottom - top) / (orderedRanks.length - 1);
        const rowGap = baseRowGap * axisScale(els.yScale);
        const xScale = axisScale(els.xScale);
        for (const [rankIndex, rank] of orderedRanks.entries()) {
          const row = layers.get(rank).sort((a, b) => (b.degree || 0) - (a.degree || 0) || a.id.localeCompare(b.id));
          const y = top + rankIndex * rowGap;
          const left = 95;
          const baseGap = 90;
          const gap = baseGap * xScale;
          row.forEach((node, index) => {
            const old = simNodes.get(node.id);
            next.set(node.id, {
              id: node.id,
              x: left + index * gap,
              y: y + (row.length > 1 && index % 2 ? 10 : 0),
              vx: old?.vx || 0,
              vy: old?.vy || 0
            });
          });
        }
        simNodes = next;
        return;
      }
      visibleNodes.forEach((node, index) => {
        const old = simNodes.get(node.id);
        if (effectiveNetworkEngine() === "grid") {
          const columns = Math.max(1, Math.ceil(Math.sqrt(visibleNodes.length)));
          const gap = 34;
          const x = w / 2 + (index % columns - columns / 2) * gap;
          const y = h / 2 + (Math.floor(index / columns) - Math.ceil(visibleNodes.length / columns) / 2) * gap;
          next.set(node.id, {id: node.id, x, y, vx: 0, vy: 0});
          return;
        }
        const angle = (index / Math.max(1, visibleNodes.length)) * Math.PI * 2;
        next.set(node.id, old || {
          id: node.id,
          x: w / 2 + Math.cos(angle) * Math.min(w, h) * 0.32,
          y: h / 2 + Math.sin(angle) * Math.min(w, h) * 0.32,
          vx: 0,
          vy: 0
        });
      });
      simNodes = next;
    }

    function tick(iterations = 1) {
      if (els.layoutMode.value === "lineage") {
        draw();
        return;
      }
      const nodeList = [...simNodes.values()];
      if (effectiveNetworkEngine() !== "force") {
        draw();
        return;
      }
      const edgeList = visibleEdges;
      for (let i = 0; i < iterations; i++) {
        for (let a = 0; a < nodeList.length; a++) {
          for (let b = a + 1; b < nodeList.length; b++) {
            const n1 = nodeList[a], n2 = nodeList[b];
            let dx = n2.x - n1.x, dy = n2.y - n1.y;
            let d2 = dx * dx + dy * dy || 1;
            const force = Math.min(1800 / d2, 0.7);
            dx *= force; dy *= force;
            n1.vx -= dx; n1.vy -= dy; n2.vx += dx; n2.vy += dy;
          }
        }
        for (const edge of edgeList) {
          const a = simNodes.get(edge.from), b = simNodes.get(edge.to);
          if (!a || !b) continue;
          const dx = b.x - a.x, dy = b.y - a.y;
          const d = Math.hypot(dx, dy) || 1;
          const target = selectedId && (edge.from === selectedId || edge.to === selectedId) ? 95 : 150;
          const force = (d - target) * 0.012;
          a.vx += dx / d * force; a.vy += dy / d * force;
          b.vx -= dx / d * force; b.vy -= dy / d * force;
        }
        for (const n of nodeList) {
          n.vx += ((canvas.clientWidth || 900) / 2 - n.x) * 0.002;
          n.vy += ((canvas.clientHeight || 700) / 2 - n.y) * 0.002;
          n.vx *= 0.82; n.vy *= 0.82;
          if (!drag || drag.id !== n.id) {
            n.x += n.vx; n.y += n.vy;
          }
        }
      }
      draw();
    }

    function resize() {
      deviceRatio = window.devicePixelRatio || 1;
      canvas.width = Math.max(1, Math.floor(canvas.clientWidth * deviceRatio));
      canvas.height = Math.max(1, Math.floor(canvas.clientHeight * deviceRatio));
      draw();
    }

    function world(point) {
      return {x: (point.x - pan.x) / zoom, y: (point.y - pan.y) / zoom};
    }

    function screen(event) {
      const rect = canvas.getBoundingClientRect();
      return {x: event.clientX - rect.left, y: event.clientY - rect.top};
    }

    function visibleBounds() {
      let minX = Number.POSITIVE_INFINITY;
      let minY = Number.POSITIVE_INFINITY;
      let maxX = Number.NEGATIVE_INFINITY;
      let maxY = Number.NEGATIVE_INFINITY;
      for (const node of visibleNodes) {
        const p = simNodes.get(node.id);
        if (!p) continue;
        const r = node.id === selectedId ? 18 : Math.max(12, Math.min(18, 8 + Math.sqrt(node.degree || 1) * 0.55));
        minX = Math.min(minX, p.x - r);
        minY = Math.min(minY, p.y - r);
        maxX = Math.max(maxX, p.x + r);
        maxY = Math.max(maxY, p.y + r);
      }
      if (!Number.isFinite(minX)) return null;
      return {minX, minY, maxX, maxY, width: Math.max(1, maxX - minX), height: Math.max(1, maxY - minY)};
    }

    function fitGraph() {
      const bounds = visibleBounds();
      if (!bounds) {
        zoom = 1;
        pan = {x: 0, y: 0};
        draw();
        return;
      }
      const w = Math.max(1, canvas.clientWidth);
      const h = Math.max(1, canvas.clientHeight);
      const padding = Math.min(72, Math.max(24, Math.min(w, h) * 0.08));
      const availableW = Math.max(1, w - padding * 2);
      const availableH = Math.max(1, h - padding * 2);
      zoom = Math.min(5, availableW / bounds.width, availableH / bounds.height);
      pan = {
        x: (w - bounds.width * zoom) / 2 - bounds.minX * zoom,
        y: (h - bounds.height * zoom) / 2 - bounds.minY * zoom
      };
      draw();
    }

    function viewportWorldBounds(padding = 90) {
      const topLeft = world({x: -padding, y: -padding});
      const bottomRight = world({x: canvas.clientWidth + padding, y: canvas.clientHeight + padding});
      return {
        minX: Math.min(topLeft.x, bottomRight.x),
        minY: Math.min(topLeft.y, bottomRight.y),
        maxX: Math.max(topLeft.x, bottomRight.x),
        maxY: Math.max(topLeft.y, bottomRight.y)
      };
    }

    function pointInBounds(p, bounds, margin = 0) {
      return p.x >= bounds.minX - margin && p.x <= bounds.maxX + margin && p.y >= bounds.minY - margin && p.y <= bounds.maxY + margin;
    }

    function currentRenderSets() {
      const bounds = viewportWorldBounds();
      const renderNodes = [];
      const renderNodeIds = new Set();
      for (const node of visibleNodes) {
        const p = simNodes.get(node.id);
        if (!p) continue;
        const margin = node.id === selectedId ? 240 : 40;
        if (pointInBounds(p, bounds, margin)) {
          renderNodes.push(node);
          renderNodeIds.add(node.id);
        }
      }
      const renderEdges = [];
      for (const edge of visibleEdges) {
        const selectedEdge = selectedId && (edge.from === selectedId || edge.to === selectedId);
        if (!selectedEdge && !renderNodeIds.has(edge.from) && !renderNodeIds.has(edge.to)) continue;
        const ordered = orderedLineageEdge(edge);
        const a = simNodes.get(ordered.from);
        const b = simNodes.get(ordered.to);
        if (!a || !b) continue;
        renderEdges.push({edge, ordered, a, b, active: selectedEdge});
      }
      return {renderNodes, renderEdges};
    }

    function draw() {
      const w = canvas.clientWidth, h = canvas.clientHeight;
      ctx.setTransform(1, 0, 0, 1, 0, 0);
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      ctx.setTransform(deviceRatio, 0, 0, deviceRatio, 0, 0);
      ctx.save();
      ctx.translate(pan.x, pan.y);
      ctx.scale(zoom, zoom);
      if (els.layoutMode.value === "lineage") {
        drawLineageBands(w, h);
      }
      const {renderNodes, renderEdges} = currentRenderSets();
      const normalEdges = [];
      const activeEdges = [];
      for (const item of renderEdges) {
        if (item.active) activeEdges.push(item);
        else normalEdges.push(item);
      }
      drawEdgeBatch(normalEdges, "rgba(100,116,139,0.22)", 1 / zoom);
      drawEdgeBatch(activeEdges, "rgba(180,83,9,0.9)", 2 / zoom);
      if (els.layoutMode.value === "lineage" && renderEdges.length <= ARROW_EDGE_LIMIT) {
        for (const item of renderEdges) drawArrowHead(item.a, item.b, item.active);
      } else if (els.layoutMode.value === "lineage") {
        for (const item of activeEdges) drawArrowHead(item.a, item.b, true);
      }
      const drawTiny = zoom < 0.18 || renderNodes.length > 5000;
      const showLabels = zoom > 0.95 && renderNodes.length < LABEL_NODE_LIMIT;
      for (const node of renderNodes) {
        const p = simNodes.get(node.id);
        if (!p) continue;
        const active = node.id === selectedId;
        const r = drawTiny && !active ? Math.max(1.5 / zoom, 1.5) : active ? 12 : Math.max(7, Math.min(13, 5 + Math.sqrt(node.degree || 1) * 0.55));
        ctx.fillStyle = COLORS[node.family] || "#334155";
        ctx.beginPath();
        ctx.arc(p.x, p.y, r, 0, Math.PI * 2);
        ctx.fill();
        if (active) {
          ctx.strokeStyle = "#111827";
          ctx.lineWidth = 2 / zoom;
          ctx.stroke();
        }
        if (active || showLabels) {
          ctx.font = `${12 / zoom}px Inter, sans-serif`;
          ctx.fillStyle = "#111827";
          ctx.fillText(node.id, p.x + r + 4 / zoom, p.y + 4 / zoom);
        }
      }
      ctx.restore();
      if (!visibleNodes.length) {
        ctx.fillStyle = "#475569";
        ctx.font = "15px Inter, sans-serif";
        ctx.fillText("No nodes match the current filters.", 28, 74);
      }
      els.nodeCount.textContent = String(visibleNodes.length);
      els.edgeCount.textContent = String(visibleEdges.length);
      els.renderNodeCount.textContent = String(renderNodes.length);
      els.renderEdgeCount.textContent = String(renderEdges.length);
    }

    function drawEdgeBatch(items, strokeStyle, lineWidth) {
      if (!items.length) return;
      ctx.strokeStyle = strokeStyle;
      ctx.lineWidth = lineWidth;
      ctx.beginPath();
      for (const item of items) {
        ctx.moveTo(item.a.x, item.a.y);
        ctx.lineTo(item.b.x, item.b.y);
      }
      ctx.stroke();
    }

    function orderedLineageEdge(edge) {
      if (els.layoutMode.value !== "lineage") return edge;
      const fromRank = lineageRank(nodesById.get(edge.from));
      const toRank = lineageRank(nodesById.get(edge.to));
      if (fromRank <= toRank) return edge;
      return { ...edge, from: edge.to, to: edge.from };
    }

    function cullRibbons(edgeList) {
      if (els.layoutMode.value !== "lineage" || els.ribbonCulling.value === "off") return edgeList;
      const cap = els.ribbonCulling.value === "strong" ? 2 : 6;
      const counts = new Map();
      const kept = [];
      const sorted = [...edgeList].sort((a, b) => {
        const aSelected = selectedId && (a.from === selectedId || a.to === selectedId) ? 1 : 0;
        const bSelected = selectedId && (b.from === selectedId || b.to === selectedId) ? 1 : 0;
        if (aSelected !== bSelected) return bSelected - aSelected;
        const ar = Math.abs(lineageRank(nodesById.get(a.from)) - lineageRank(nodesById.get(a.to)));
        const br = Math.abs(lineageRank(nodesById.get(b.from)) - lineageRank(nodesById.get(b.to)));
        if (ar !== br) return br - ar;
        return a.type.localeCompare(b.type);
      });
      for (const edge of sorted) {
        if (selectedId && (edge.from === selectedId || edge.to === selectedId)) {
          kept.push(edge);
          continue;
        }
        const fromCount = counts.get(edge.from) || 0;
        const toCount = counts.get(edge.to) || 0;
        if (fromCount >= cap || toCount >= cap) continue;
        counts.set(edge.from, fromCount + 1);
        counts.set(edge.to, toCount + 1);
        kept.push(edge);
      }
      return kept;
    }

    function drawArrowHead(a, b, active) {
      const angle = Math.atan2(b.y - a.y, b.x - a.x);
      const size = active ? 8 / zoom : 6 / zoom;
      const offset = 10 / zoom;
      const x = b.x - Math.cos(angle) * offset;
      const y = b.y - Math.sin(angle) * offset;
      ctx.fillStyle = active ? "rgba(180,83,9,0.9)" : "rgba(100,116,139,0.4)";
      ctx.beginPath();
      ctx.moveTo(x, y);
      ctx.lineTo(x - Math.cos(angle - Math.PI / 6) * size, y - Math.sin(angle - Math.PI / 6) * size);
      ctx.lineTo(x - Math.cos(angle + Math.PI / 6) * size, y - Math.sin(angle + Math.PI / 6) * size);
      ctx.closePath();
      ctx.fill();
    }

    function drawLineageBands(w, h) {
      const activeRanks = [...new Set(visibleNodes.map(node => lineageRank(node)))].sort((a, b) => a - b);
      if (!activeRanks.length) return;
      const top = 90;
      const baseBottom = Math.max(top + 120, h - 80);
      const baseRowGap = activeRanks.length <= 1 ? 0 : (baseBottom - top) / (activeRanks.length - 1);
      const rowGap = baseRowGap * axisScale(els.yScale);
      ctx.save();
      ctx.font = `${12 / zoom}px Inter, sans-serif`;
      ctx.textAlign = "left";
      ctx.textBaseline = "middle";
      for (const [index, rank] of activeRanks.entries()) {
        const y = top + index * rowGap;
        ctx.fillStyle = index % 2 ? "rgba(255,255,255,0.36)" : "rgba(15,23,42,0.035)";
        ctx.fillRect(-pan.x / zoom, y - 28, w / zoom, 56);
        ctx.strokeStyle = "rgba(100,116,139,0.18)";
        ctx.beginPath();
        ctx.moveTo(-pan.x / zoom, y);
        ctx.lineTo((w - pan.x) / zoom, y);
        ctx.stroke();
        ctx.fillStyle = "rgba(15,23,42,0.58)";
        ctx.fillText(RANK_LABELS[rank] || "Other", (-pan.x / zoom) + 18 / zoom, y - 18 / zoom);
      }
      ctx.restore();
    }

    function animate() {
      if (els.layoutMode.value === "lineage" || effectiveNetworkEngine() !== "force") {
        requestAnimationFrame(animate);
        return;
      }
      tick(1);
      requestAnimationFrame(animate);
    }

    function pick(point) {
      const p = world(point);
      let best = null;
      let bestDistance = Infinity;
      for (const node of visibleNodes) {
        const pos = simNodes.get(node.id);
        if (!pos) continue;
        const dist = Math.hypot(pos.x - p.x, pos.y - p.y);
        if (dist < bestDistance && dist < 14 / zoom) {
          best = node.id;
          bestDistance = dist;
        }
      }
      return best;
    }

    function renderResults() {
      const q = els.search.value.trim().toLowerCase();
      const family = els.family.value;
      const results = DATA.nodes
        .filter(n => (!family || n.family === family) && matchesSearch(n, q))
        .sort((a, b) => {
          if (els.layoutMode.value === "lineage" && !q && !family) {
            return lineageRank(a) - lineageRank(b) || (b.degree || 0) - (a.degree || 0) || a.id.localeCompare(b.id);
          }
          if (!q && !family) return (b.degree || 0) - (a.degree || 0) || a.id.localeCompare(b.id);
          return a.id.localeCompare(b.id);
        })
        .slice(0, 80);
      els.results.innerHTML = results.map(n => `
        <button class="item ${n.id === selectedId ? "active" : ""}" data-id="${n.id}">
          <strong>${escapeHtml(n.label || n.id)}</strong>
          <span>${escapeHtml(n.id)} · ${escapeHtml(n.family)}${n.status ? " · " + escapeHtml(n.status) : ""}</span>
        </button>`).join("") || `<div class="empty">No matching entities.</div>`;
    }

    function renderSelected() {
      const node = selectedId ? nodesById.get(selectedId) : null;
      if (!node) {
        els.selected.innerHTML = "Select a node in the graph or results list.";
        els.connections.innerHTML = "";
        return;
      }
      els.selected.innerHTML = `
        <div class="kv"><span>ID</span><strong class="wrap">${escapeHtml(node.id)}</strong></div>
        <div class="kv"><span>Title</span><span class="wrap">${escapeHtml(node.label)}</span></div>
        <div class="kv"><span>Family</span><span>${escapeHtml(node.family)}</span></div>
        <div class="kv"><span>Status</span><span>${escapeHtml(node.status || "n/a")}</span></div>
        <div class="kv"><span>Tier</span><span>${escapeHtml(node.tier || "n/a")}</span></div>
        <div class="kv"><span>Origin</span><span>${escapeHtml(node.origin || "n/a")}</span></div>
        <div class="kv"><span>Path</span><span class="wrap">${escapeHtml(node.path || "n/a")}</span></div>`;
      const related = (adjacency.get(selectedId) || []).slice(0, 120);
      els.connections.innerHTML = related.map(e => {
        const other = e.from === selectedId ? e.to : e.from;
        return `<button class="item" data-id="${other}"><strong>${escapeHtml(e.type)}</strong><span>${escapeHtml(e.from)} -> ${escapeHtml(e.to)}</span></button>`;
      }).join("") || `<div class="empty">No connected edges.</div>`;
    }

    function escapeHtml(value) {
      return String(value).replace(/[&<>"']/g, ch => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[ch]));
    }

    function selectNode(id) {
      if (selectedId === id) {
        deselectNode();
        return;
      }
      selectedId = id;
      renderResults();
      renderSelected();
      draw();
    }

    function deselectNode() {
      selectedId = null;
      centerId = null;
      renderResults();
      renderSelected();
      update();
    }

    document.addEventListener("click", event => {
      const nodeButton = event.target.closest("[data-id]");
      if (nodeButton) selectNode(nodeButton.dataset.id);
      const chip = event.target.closest("[data-family]");
      if (chip) {
        els.family.value = els.family.value === chip.dataset.family ? "" : chip.dataset.family;
        [...els.chips.children].forEach(c => c.classList.toggle("active", c.dataset.family === els.family.value));
        centerId = null;
        update();
      }
    });

    for (const input of [els.search, els.family, els.edgeType, els.layoutMode, els.networkEngine, els.forceCutoff, els.depth, els.limit, els.xScale, els.yScale, els.ribbonCulling]) {
      input.addEventListener("input", () => {
        if (input !== els.depth && input !== els.limit && input !== els.xScale && input !== els.yScale && input !== els.ribbonCulling && input !== els.networkEngine && input !== els.forceCutoff) centerId = null;
        if (input === els.xScale || input === els.yScale) updateAxisScaleLabels();
        if (input === els.forceCutoff) updateForceCutoffLabel();
        update();
      });
    }
    for (const input of familyToggleInputs()) {
      input.addEventListener("input", () => {
        centerId = null;
        update();
      });
    }

    document.getElementById("showAllFamilies").addEventListener("click", () => {
      for (const input of familyToggleInputs()) input.checked = true;
      centerId = null;
      update();
    });
    document.getElementById("hideAllFamilies").addEventListener("click", () => {
      for (const input of familyToggleInputs()) input.checked = false;
      centerId = null;
      update();
    });

    document.getElementById("expand").addEventListener("click", () => {
      if (selectedId) {
        centerId = selectedId;
        update();
      }
    });
    document.getElementById("deselect").addEventListener("click", deselectNode);
    document.getElementById("reset").addEventListener("click", () => {
      selectedId = null;
      centerId = null;
      els.search.value = "";
      els.family.value = "";
      els.edgeType.value = "";
      els.layoutMode.value = "network";
      els.networkEngine.value = "auto";
      els.forceCutoff.value = "350";
      updateForceCutoffLabel();
      for (const input of familyToggleInputs()) input.checked = true;
      els.depth.value = "2";
      els.limit.value = "300";
      els.xScale.value = "0";
      els.yScale.value = "0";
      els.ribbonCulling.value = "light";
      updateAxisScaleLabels();
      [...els.chips.children].forEach(c => c.classList.remove("active"));
      update();
    });
    document.getElementById("zoomIn").addEventListener("click", () => { zoom *= 1.2; draw(); });
    document.getElementById("zoomOut").addEventListener("click", () => { zoom /= 1.2; draw(); });
    document.getElementById("fit").addEventListener("click", fitGraph);

    canvas.addEventListener("mousedown", event => {
      const point = screen(event);
      const id = pick(point);
      if (id) {
        if (selectedId === id) {
          deselectNode();
          return;
        }
        selectedId = id;
        drag = {id, start: point};
        canvas.classList.add("dragging");
        renderResults();
        renderSelected();
        draw();
      } else {
        drag = {pan: true, start: point, base: {...pan}};
      }
    });
    window.addEventListener("mousemove", event => {
      if (!drag) return;
      const point = screen(event);
      if (drag.pan) {
        pan.x = drag.base.x + point.x - drag.start.x;
        pan.y = drag.base.y + point.y - drag.start.y;
      } else {
        const pos = simNodes.get(drag.id);
        const p = world(point);
        if (pos) { pos.x = p.x; pos.y = p.y; pos.vx = 0; pos.vy = 0; }
      }
      draw();
    });
    window.addEventListener("mouseup", () => {
      drag = null;
      canvas.classList.remove("dragging");
    });
    canvas.addEventListener("wheel", event => {
      event.preventDefault();
      const point = screen(event);
      const before = world(point);
      zoom *= event.deltaY < 0 ? 1.12 : 0.89;
      zoom = Math.max(0.0001, Math.min(5, zoom));
      pan.x = point.x - before.x * zoom;
      pan.y = point.y - before.y * zoom;
      draw();
    }, {passive: false});

    window.addEventListener("resize", resize);
    updateAxisScaleLabels();
    updateForceCutoffLabel();
    resize();
    update();
    if (!animationStarted) {
      animationStarted = true;
      requestAnimationFrame(animate);
    }
  </script>
</body>
</html>
"""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--graph", default="tmp/ssot-lineage-graph.json", type=Path)
    parser.add_argument("--registry", default="tmp/ssot-registry-export.json", type=Path)
    parser.add_argument("--output", default="tmp/ssot-lineage-graph.html", type=Path)
    args = parser.parse_args()

    payload = build_payload(args.graph, args.registry)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    data = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
    args.output.write_text(HTML.replace("__DATA__", data), encoding="utf-8")
    print(
        json.dumps(
            {
                "output": str(args.output),
                "nodes": payload["summary"]["nodeCount"],
                "edges": payload["summary"]["edgeCount"],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
