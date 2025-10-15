const state = {
  frames: [],
  filters: {
    role: "",
    dir: "",
    ti: "",
    cot: "",
    ioa: "",
    search: "",
  },
};

const streamContainer = document.getElementById("stream-container");
const filterForm = document.getElementById("stream-filter");
const clearButton = document.getElementById("clear-stream");
const clientStatus = document.getElementById("client-status");
const serverStatus = document.getElementById("server-status");
const clientStats = document.querySelector("#client-stats");
const serverStats = document.querySelector("#server-stats");

let ws;
let needsRender = false;
let renderScheduled = false;

function connectStream() {
  const protocol = window.location.protocol === "https:" ? "wss" : "ws";
  ws = new WebSocket(`${protocol}://${window.location.host}/stream`);
  ws.addEventListener("open", () => updateStatus(true));
  ws.addEventListener("close", () => updateStatus(false));
  ws.addEventListener("message", (event) => {
    const data = JSON.parse(event.data);
    state.frames.push(data);
    if (state.frames.length > 1000) {
      state.frames.splice(0, state.frames.length - 1000);
    }
    needsRender = true;
    scheduleRender();
    updateStats(data);
  });
  ws.addEventListener("error", () => updateStatus(false));
}

function updateStatus(connected) {
  [clientStatus, serverStatus].forEach((el) => {
    if (!el) {
      return;
    }
    el.classList.toggle("bg-emerald-400", connected);
    el.classList.toggle("bg-rose-500", !connected);
  });
}

function updateStats(event) {
  const statsElement = event.role === "client" ? clientStats : serverStats;
  if (!statsElement) {
    return;
  }
  const field = statsElement.querySelector(`[data-field="${event.dir}"]`);
  if (field) {
    const current = Number(field.textContent || "0");
    field.textContent = String(current + 1);
  }
}

function scheduleRender() {
  if (!renderScheduled) {
    renderScheduled = true;
    window.requestAnimationFrame(() => {
      if (needsRender) {
        render();
        needsRender = false;
      }
      renderScheduled = false;
    });
  }
}

function render() {
  if (!streamContainer) {
    return;
  }
  const filtered = state.frames.filter(applyFilters).slice(-300).reverse();
  streamContainer.innerHTML = filtered
    .map(
      (frame) => `
      <article class="bg-slate-800 border border-slate-700 rounded p-3">
        <header class="flex justify-between text-[11px] uppercase tracking-wide text-slate-400">
          <span>${frame.ts}</span>
          <span>${frame.role.toUpperCase()} · ${frame.dir.toUpperCase()}</span>
        </header>
        <div class="mt-2 font-mono text-[11px] text-amber-200 break-words">
          APCI: ${frame.apci}<br />
          ASDU: ${frame.asdu}
        </div>
        <pre class="mt-2 text-[11px] bg-slate-900 rounded p-2 overflow-x-auto">${JSON.stringify(frame.decoded, null, 2)}</pre>
      </article>
    `,
    )
    .join("");
}

function applyFilters(frame) {
  const { role, dir, ti, cot, ioa, search } = state.filters;
  if (role && frame.role !== role) return false;
  if (dir && frame.dir !== dir) return false;
  if (ti && Number(frame.decoded?.ti ?? 0) !== Number(ti)) return false;
  if (cot && Number(frame.decoded?.cot ?? 0) !== Number(cot)) return false;
  if (ioa && !String(frame.decoded?.ioas ?? "").includes(ioa)) return false;
  if (search && !JSON.stringify(frame).toLowerCase().includes(search.toLowerCase())) return false;
  return true;
}

if (filterForm) {
  filterForm.addEventListener("input", (event) => {
    const target = event.target;
    if (!(target instanceof HTMLInputElement || target instanceof HTMLSelectElement)) {
      return;
    }
    state.filters[target.name] = target.value;
    needsRender = true;
    scheduleRender();
  });
}

if (clearButton) {
  clearButton.addEventListener("click", () => {
    state.frames = [];
    needsRender = true;
    scheduleRender();
  });
}

window.addEventListener("DOMContentLoaded", () => {
  connectStream();
});
