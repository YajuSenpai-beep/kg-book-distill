const $ = (id) => document.getElementById(id);
const svg = $("graph");
const NS = "http://www.w3.org/2000/svg";
let current = null;

async function api(path) {
  const r = await fetch(path);
  return r.json();
}

function el(tag, attrs = {}, text = "") {
  const e = document.createElementNS(NS, tag);
  for (const [k, v] of Object.entries(attrs)) e.setAttribute(k, v);
  if (text) e.textContent = text;
  return e;
}

async function init() {
  const s = await api("/api/stats");
  $("stats").textContent = `${s.nodes} 实例节点 · ${s.docs} 可检索条目 · ${s.edges} 边`;
  search("TransE");
}

async function search(q) {
  if (!q) return;
  const d = await api("/api/search?q=" + encodeURIComponent(q));
  const box = $("resultList");
  box.innerHTML = "";
  for (const n of d.results) {
    const div = document.createElement("div");
    div.className = "result";
    div.innerHTML = `<span class="badge">${n.type}</span><span>${n.label}</span>`;
    div.onclick = () => load(n.id);
    box.appendChild(div);
  }
}

async function load(id) {
  const d = await api("/api/node/" + encodeURIComponent(id));
  if (!d || d.error) return;
  current = d;
  renderDetail(d);
  renderGraph(d);
  $("from").value = id;
}

function renderDetail(d) {
  const n = d.node;
  const rows = [`<div class="kv"><b>${n.label}</b> <span class="badge">${n.type}</span></div>`,
                `<div class="kv">ID：${n.id}</div>`];
  if (n.point_id) rows.push(`<div class="kv">知识点：${n.point_id}</div>`);
  for (const key of ["book", "page", "role", "data_status"]) {
    if (n[key] !== undefined && n[key] !== "") rows.push(`<div class="kv">${key}：${n[key]}</div>`);
  }
  const edges = [...d.out.map(e => ({...e, dir: "→"})), ...d.in.map(e => ({...e, dir: "←"}))];
  rows.push(`<h2 style="margin-top:14px">关系 (${edges.length})</h2>`);
  for (const e of edges) {
    const other = e.dir === "→" ? e.target : e.source;
    rows.push(`<div class="edge"><span class="rel">${e.type}</span> ${e.dir} ` +
              `<a href="#" data-id="${other}">${other}</a></div>`);
  }
  $("detailBody").innerHTML = rows.join("");
  $("detailBody").querySelectorAll("a[data-id]").forEach(a => {
    a.onclick = (ev) => { ev.preventDefault(); load(a.dataset.id); };
  });
}

function renderGraph(d) {
  svg.innerHTML = "";
  const cx = 380, cy = 270, R = 190;
  const neighbors = Object.entries(d.neighbors).slice(0, 18);
  const center = el("circle", { cx, cy, r: 26, fill: "#4aa8ff" });
  svg.appendChild(center);
  const ct = el("text", { x: cx, y: cy + 4, "text-anchor": "middle", class: "centerLabel" });
  ct.textContent = (d.node.label || d.node.id).slice(0, 10);
  svg.appendChild(ct);

  neighbors.forEach(([id, label], i) => {
    const a = (2 * Math.PI * i) / Math.max(neighbors.length, 1) - Math.PI / 2;
    const x = cx + R * Math.cos(a), y = cy + R * Math.sin(a);
    const line = el("line", { x1: cx, y1: cy, x2: x, y2: y, stroke: "#2a3542", "stroke-width": 1.2 });
    svg.appendChild(line);
    const c = el("circle", { cx: x, cy: y, r: 15, fill: "#1f6fb2", cursor: "pointer" });
    c.onclick = () => load(id);
    svg.appendChild(c);
    const t = el("text", { x, y: y + 30, "text-anchor": "middle", class: "nodeLabel" });
    t.textContent = label.length > 12 ? label.slice(0, 12) + "…" : label;
    svg.appendChild(t);
  });
}

async function findPath() {
  const from = $("from").value.trim(), to = $("to").value.trim();
  if (!from || !to) return;
  const d = await api(`/api/path?from=${encodeURIComponent(from)}&to=${encodeURIComponent(to)}`);
  $("pathResult").textContent = d.path ? d.path.join(" → ") : "未找到 5 跳内路径";
}

$("go").onclick = () => search($("q").value.trim());
$("q").addEventListener("keydown", e => { if (e.key === "Enter") search($("q").value.trim()); });
$("path").onclick = findPath;
init();
