(() => {
  const socket = io('/stream', { transports: ['websocket'] });
  const container = document.getElementById('frame-stream');
  const filterForm = document.getElementById('frame-filter');
  const maxFrames = 200;
  const queue = [];
  let renderPending = false;

  function ensureContainer() {
    if (!container) {
      return;
    }
    if (!container.dataset.initialized) {
      container.dataset.initialized = '1';
      container.innerHTML = '<ul class="divide-y divide-slate-800 text-xs"></ul>';
    }
  }

  function renderFrames() {
    renderPending = false;
    ensureContainer();
    if (!container) {
      return;
    }
    const list = container.querySelector('ul');
    if (!list) {
      return;
    }
    list.innerHTML = queue
      .slice(-maxFrames)
      .reverse()
      .map((frame) => {
        const decoded = JSON.stringify(frame.decoded, null, 2);
        return `
          <li class="p-3 border-b border-slate-800">
            <div class="flex justify-between">
              <span class="font-semibold text-slate-200">${frame.role.toUpperCase()} ${frame.direction.toUpperCase()}</span>
              <span class="text-slate-400">${frame.timestamp}</span>
            </div>
            <div class="mt-1 text-slate-300">TI ${frame.decoded?.ti ?? ''} · COT ${frame.decoded?.cot ?? ''}</div>
            <div class="mt-1 text-slate-400">APCI ${frame.apci_hex}</div>
            <div class="mt-1 text-slate-400">ASDU ${frame.asdu_hex}</div>
            <pre class="mt-2 bg-slate-900 border border-slate-800 rounded p-2">${decoded}</pre>
          </li>`;
      })
      .join('');
  }

  function scheduleRender() {
    if (renderPending) {
      return;
    }
    renderPending = true;
    requestAnimationFrame(renderFrames);
  }

  socket.on('connect', () => {
    queue.length = 0;
    socket.emit('history', { limit: maxFrames });
  });

  socket.on('frames', (frames) => {
    if (!Array.isArray(frames)) {
      return;
    }
    frames.forEach((frame) => {
      queue.push(frame);
      if (queue.length > maxFrames) {
        queue.shift();
      }
    });
    scheduleRender();
  });

  socket.on('history', (frames) => {
    if (!Array.isArray(frames)) {
      return;
    }
    queue.push(...frames);
    if (queue.length > maxFrames) {
      queue.splice(0, queue.length - maxFrames);
    }
    scheduleRender();
  });

  if (filterForm) {
    let debounceTimer;
    const handler = () => {
      clearTimeout(debounceTimer);
      debounceTimer = setTimeout(() => {
        const data = new FormData(filterForm);
        const payload = Object.fromEntries(data.entries());
        socket.emit('filters', payload);
      }, 150);
    };
    filterForm.addEventListener('change', handler);
    filterForm.addEventListener('input', handler);
  }
})();
