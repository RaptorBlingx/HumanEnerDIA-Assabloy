(function () {
  'use strict';

  const rootId = 'hpd-recorder';
  let state = null;
  let tasks = [];
  let timer = null;
  let lastUrl = location.href;
  let lastMessage = 'Extension loaded. Select a task and start measuring.';
  let dragState = null;
  let extensionContextValid = true;
  let optimisticOverlayPosition = null;

  function isContextInvalidated(error) {
    return /Extension context invalidated|context invalidated/i.test(String(error?.message || error || ''));
  }

  function handleContextInvalidated() {
    extensionContextValid = false;
    if (timer) {
      window.clearInterval(timer);
      timer = null;
    }
    setLast('Extension was reloaded. Refresh this page to reconnect the recorder.');
    const overlay = document.getElementById(rootId);
    if (overlay) {
      overlay.classList.add('hpd-context-invalid');
    }
    return null;
  }

  function send(message) {
    if (!extensionContextValid) {
      return Promise.resolve(null);
    }

    try {
      if (typeof chrome === 'undefined' || !chrome.runtime?.id) {
        return Promise.resolve(handleContextInvalidated());
      }
      return chrome.runtime.sendMessage({
        url: location.href,
        title: document.title,
        ...message
      }).catch(error => {
        if (isContextInvalidated(error)) {
          return handleContextInvalidated();
        }
        throw error;
      });
    } catch (error) {
      if (isContextInvalidated(error)) {
        return Promise.resolve(handleContextInvalidated());
      }
      return Promise.reject(error);
    }
  }

  function elapsedMs() {
    if (!state) {
      return 0;
    }
    if (!state.running || !state.startedAt) {
      return state.elapsedMs || 0;
    }
    return (state.elapsedMs || 0) + (Date.now() - state.startedAt);
  }

  function formatTime(ms) {
    const totalSeconds = Math.floor(ms / 1000);
    const minutes = Math.floor(totalSeconds / 60);
    const seconds = totalSeconds % 60;
    const tenths = Math.floor((ms % 1000) / 100);
    return `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}.${tenths}`;
  }

  function currentTask() {
    return tasks.find(task => task.id === state?.taskId) || tasks[0];
  }

  function csvDownload(filename, content, type) {
    const blob = new Blob([content], { type });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    link.remove();
    URL.revokeObjectURL(url);
  }

  async function copyText(text, label) {
    try {
      await navigator.clipboard.writeText(text);
      setLast(`${label} copied.`);
    } catch (_) {
      window.prompt(`Copy ${label}:`, text);
    }
  }

  function setLast(message) {
    lastMessage = message;
    const last = document.querySelector('#hpd-last');
    if (last) {
      last.textContent = message;
    }
  }

  function clamp(value, min, max) {
    return Math.min(Math.max(value, min), max);
  }

  function currentOptimisticOverlayPosition() {
    if (!optimisticOverlayPosition) {
      return null;
    }
    if (Date.now() > optimisticOverlayPosition.expiresAt) {
      optimisticOverlayPosition = null;
      return null;
    }
    return optimisticOverlayPosition;
  }

  function applyOverlayPosition() {
    const overlay = document.getElementById(rootId);
    if (!overlay || !state) {
      return null;
    }

    if (dragState) {
      const rect = overlay.getBoundingClientRect();
      return { left: rect.left, top: rect.top };
    }

    const storedPosition = currentOptimisticOverlayPosition() || state.overlayPosition;

    if (!storedPosition || !Number.isFinite(storedPosition.left) || !Number.isFinite(storedPosition.top)) {
      overlay.style.left = 'auto';
      overlay.style.top = 'auto';
      overlay.style.right = '16px';
      overlay.style.bottom = '16px';
      return null;
    }

    const maxLeft = Math.max(window.innerWidth - overlay.offsetWidth - 8, 8);
    const maxTop = Math.max(window.innerHeight - overlay.offsetHeight - 8, 8);
    const left = clamp(storedPosition.left, 8, maxLeft);
    const top = clamp(storedPosition.top, 8, maxTop);

    overlay.style.left = `${left}px`;
    overlay.style.top = `${top}px`;
    overlay.style.right = 'auto';
    overlay.style.bottom = 'auto';
    return { left, top };
  }

  function createOverlay() {
    if (document.getElementById(rootId)) {
      return;
    }

    const overlay = document.createElement('div');
    overlay.id = rootId;
    overlay.innerHTML = `
      <div class="hpd-header">
        <div class="hpd-title">Pilot Measurement</div>
        <div class="hpd-header-actions">
          <button class="hpd-icon" id="hpd-toggle" title="Collapse panel">-</button>
        </div>
      </div>
      <div class="hpd-body">
        <div class="hpd-timer" id="hpd-timer">00:00.0</div>
        <div class="hpd-status">
          <span id="hpd-running">Idle</span>
          <span id="hpd-records">0 records</span>
        </div>
        <div class="hpd-grid">
          <label class="hpd-field">Condition
            <select id="hpd-condition">
              <option value="A">A - Manual</option>
              <option value="B">B - Assistant</option>
            </select>
          </label>
          <label class="hpd-field">Task
            <select id="hpd-task"></select>
          </label>
          <label class="hpd-field">Trial
            <select id="hpd-trial">
              <option value="1">Trial 1</option>
              <option value="2">Trial 2</option>
              <option value="3">Trial 3</option>
              <option value="extra">Extra</option>
            </select>
          </label>
          <label class="hpd-field">Session
            <input id="hpd-session" type="text" value="official-run">
          </label>
        </div>
        <div class="hpd-metrics">
          <div class="hpd-metric"><span>Clicks</span><strong id="hpd-clicks">0</strong></div>
          <div class="hpd-metric"><span>Screens</span><strong id="hpd-screens">0</strong></div>
          <div class="hpd-metric"><span>Success</span><strong id="hpd-success-value">1</strong></div>
        </div>
        <div class="hpd-actions">
          <button class="hpd-start" id="hpd-start">Start Task</button>
          <button class="hpd-stop" id="hpd-stop">Answer Found</button>
        </div>
        <div class="hpd-counters">
          <button class="hpd-muted" id="hpd-minus-click">-Click</button>
          <button class="hpd-muted" id="hpd-plus-click">+Click</button>
          <button class="hpd-muted" id="hpd-minus-screen">-Screen</button>
          <button class="hpd-muted" id="hpd-plus-screen">+Screen</button>
        </div>
        <div class="hpd-checks">
          <label><input type="checkbox" id="hpd-expert"> Expert</label>
          <label><input type="checkbox" id="hpd-reasoning"> Manual</label>
          <label><input type="checkbox" id="hpd-success" checked> Success</label>
          <label><input type="checkbox" id="hpd-autostop" checked> Auto</label>
        </div>
        <label class="hpd-field hpd-notes">Notes
          <textarea id="hpd-notes" rows="2"></textarea>
        </label>
        <div class="hpd-export">
          <button class="hpd-muted" id="hpd-copy-raw">Copy Raw</button>
          <button class="hpd-muted" id="hpd-copy-summary">Copy KPI</button>
          <button class="hpd-muted" id="hpd-download-json">JSON</button>
        </div>
        <div class="hpd-actions hpd-reset-actions">
          <button class="hpd-muted" id="hpd-reset-current">Reset Current</button>
          <button class="hpd-muted" id="hpd-delete-last">Delete Last Try</button>
          <button class="hpd-danger" id="hpd-clear-all">Reset All</button>
        </div>
        <div class="hpd-task" id="hpd-task-detail"></div>
        <div class="hpd-last" id="hpd-last"></div>
      </div>
    `;
    document.documentElement.appendChild(overlay);
    bindOverlayEvents();
  }

  function renderTaskOptions() {
    const select = document.getElementById('hpd-task');
    if (!select || !tasks.length) {
      return;
    }
    const currentValue = select.value;
    select.innerHTML = tasks.map(task => `<option value="${task.id}">${task.id} - ${task.title}</option>`).join('');
    select.value = state?.taskId || currentValue || 'O1';
  }

  function render() {
    if (!state) {
      return;
    }
    createOverlay();
    renderTaskOptions();

    const overlay = document.getElementById(rootId);
    overlay.classList.toggle('hpd-collapsed', !!state.overlayCollapsed);
    applyOverlayPosition();
    const task = currentTask();
    document.getElementById('hpd-condition').value = state.condition;
    document.getElementById('hpd-task').value = state.taskId;
    document.getElementById('hpd-trial').value = state.trial;
    document.getElementById('hpd-session').value = state.sessionName || 'official-run';
    document.getElementById('hpd-expert').checked = !!state.expertHelp;
    document.getElementById('hpd-reasoning').checked = !!state.manualReasoning;
    document.getElementById('hpd-success').checked = !!state.success;
    document.getElementById('hpd-autostop').checked = state.autoStopAssistant !== false;
    document.getElementById('hpd-notes').value = state.notes || '';
    document.getElementById('hpd-timer').textContent = formatTime(elapsedMs());
    document.getElementById('hpd-clicks').textContent = state.clicks;
    document.getElementById('hpd-screens').textContent = state.screens;
    document.getElementById('hpd-success-value').textContent = state.success ? '1' : '0';
    document.getElementById('hpd-running').textContent = state.running ? 'Running' : 'Idle';
    document.getElementById('hpd-records').textContent = `${state.records.length} records`;
    document.getElementById('hpd-start').disabled = state.running;
    document.getElementById('hpd-stop').disabled = !state.running;
    document.getElementById('hpd-task-detail').innerHTML = task
      ? `<strong>${task.persona} / ${task.module}</strong><br>${task.stop}`
      : '';
    document.getElementById('hpd-last').textContent = lastMessage;
  }

  function applyResponse(response) {
    if (!response?.state) {
      return false;
    }
    const optimisticPosition = currentOptimisticOverlayPosition();
    if (
      optimisticPosition &&
      response.state.overlayPosition &&
      Number.isFinite(response.state.overlayPosition.left) &&
      Number.isFinite(response.state.overlayPosition.top) &&
      Math.abs(response.state.overlayPosition.left - optimisticPosition.left) < 1 &&
      Math.abs(response.state.overlayPosition.top - optimisticPosition.top) < 1
    ) {
      optimisticOverlayPosition = null;
    }
    state = response.state;
    tasks = response.tasks || tasks;
    render();
    return true;
  }

  async function refresh() {
    const response = await send({ type: 'getState' });
    applyResponse(response);
  }

  function updateSettings(patch) {
    send({ type: 'updateSettings', patch }).then(applyResponse).catch(() => undefined);
  }

  function persistOverlayPosition(position) {
    optimisticOverlayPosition = { ...position, expiresAt: Date.now() + 3000 };
    if (state) {
      state.overlayPosition = position;
    }
    updateSettings({ overlayPosition: position });
  }

  function bindOverlayEvents() {
    bindOverlayDragging();

    document.getElementById('hpd-toggle').addEventListener('click', () => {
      const overlay = document.getElementById(rootId);
      const nextCollapsed = !state.overlayCollapsed;
      overlay.classList.toggle('hpd-collapsed', nextCollapsed);
      state.overlayCollapsed = nextCollapsed;
      const position = applyOverlayPosition();
      updateSettings({
        overlayCollapsed: nextCollapsed,
        ...(position ? { overlayPosition: position } : {})
      });
    });
    document.getElementById('hpd-condition').addEventListener('change', event => updateSettings({ condition: event.target.value }));
    document.getElementById('hpd-task').addEventListener('change', event => updateSettings({ taskId: event.target.value }));
    document.getElementById('hpd-trial').addEventListener('change', event => updateSettings({ trial: event.target.value }));
    document.getElementById('hpd-session').addEventListener('input', event => updateSettings({ sessionName: event.target.value.trim() || 'official-run' }));
    document.getElementById('hpd-expert').addEventListener('change', event => updateSettings({ expertHelp: event.target.checked }));
    document.getElementById('hpd-reasoning').addEventListener('change', event => updateSettings({ manualReasoning: event.target.checked }));
    document.getElementById('hpd-success').addEventListener('change', event => updateSettings({ success: event.target.checked }));
    document.getElementById('hpd-autostop').addEventListener('change', event => updateSettings({ autoStopAssistant: event.target.checked }));
    document.getElementById('hpd-notes').addEventListener('input', event => updateSettings({ notes: event.target.value }));
    document.getElementById('hpd-start').addEventListener('click', () => {
      send({ type: 'startTask' }).then(response => {
        if (!applyResponse(response)) {
          return;
        }
        setLast(`Started ${state.condition}-${state.taskId}.`);
      }).catch(() => undefined);
    });
    document.getElementById('hpd-stop').addEventListener('click', () => {
      send({ type: 'stopTask', reason: 'answer_found' }).then(response => {
        if (!applyResponse(response)) {
          return;
        }
        setLast(`Saved ${state.records.at(-1)?.condition || ''}-${state.records.at(-1)?.taskId || ''}.`);
      }).catch(() => undefined);
    });
    document.getElementById('hpd-minus-click').addEventListener('click', () => send({ type: 'adjustCounter', counter: 'clicks', delta: -1 }).then(applyResponse).catch(() => undefined));
    document.getElementById('hpd-plus-click').addEventListener('click', () => send({ type: 'adjustCounter', counter: 'clicks', delta: 1 }).then(applyResponse).catch(() => undefined));
    document.getElementById('hpd-minus-screen').addEventListener('click', () => send({ type: 'adjustCounter', counter: 'screens', delta: -1 }).then(applyResponse).catch(() => undefined));
    document.getElementById('hpd-plus-screen').addEventListener('click', () => send({ type: 'adjustCounter', counter: 'screens', delta: 1 }).then(applyResponse).catch(() => undefined));
    document.getElementById('hpd-copy-raw').addEventListener('click', async () => {
      const response = await send({ type: 'export' });
      if (!response?.rawCsv) {
        return;
      }
      await copyText(response.rawCsv, 'Raw CSV');
    });
    document.getElementById('hpd-copy-summary').addEventListener('click', async () => {
      const response = await send({ type: 'export' });
      if (!response?.summaryCsv) {
        return;
      }
      await copyText(response.summaryCsv, 'KPI Summary CSV');
    });
    document.getElementById('hpd-download-json').addEventListener('click', async () => {
      const response = await send({ type: 'getState' });
      if (!response?.state) {
        return;
      }
      csvDownload(`pilot-measurement-${new Date().toISOString().slice(0, 10)}.json`, JSON.stringify(response.state.records, null, 2), 'application/json');
    });
    document.getElementById('hpd-reset-current').addEventListener('click', () => {
      send({ type: 'resetCurrent' }).then(response => {
        if (!applyResponse(response)) {
          return;
        }
        setLast('Current task reset.');
      }).catch(() => undefined);
    });
    document.getElementById('hpd-delete-last').addEventListener('click', () => {
      if (!window.confirm('Delete the last saved try?')) {
        return;
      }
      send({ type: 'deleteLast' }).then(response => {
        if (!applyResponse(response)) {
          return;
        }
        setLast('Last saved try deleted.');
      }).catch(() => undefined);
    });
    document.getElementById('hpd-clear-all').addEventListener('click', () => {
      if (!window.confirm('Reset all saved tries and current counters?')) {
        return;
      }
      send({ type: 'clearAll' }).then(response => {
        if (!applyResponse(response)) {
          return;
        }
        setLast('All saved tries reset.');
      }).catch(() => undefined);
    });
  }

  function bindOverlayDragging() {
    const overlay = document.getElementById(rootId);
    const header = overlay?.querySelector('.hpd-header');
    if (!overlay || !header) {
      return;
    }

    header.addEventListener('pointerdown', event => {
      if (event.target.closest('button')) {
        return;
      }
      const rect = overlay.getBoundingClientRect();
      dragState = {
        pointerId: event.pointerId,
        offsetX: event.clientX - rect.left,
        offsetY: event.clientY - rect.top
      };
      overlay.classList.add('hpd-dragging');
      header.setPointerCapture(event.pointerId);
      event.preventDefault();
    });

    header.addEventListener('pointermove', event => {
      if (!dragState || event.pointerId !== dragState.pointerId) {
        return;
      }
      const maxLeft = Math.max(window.innerWidth - overlay.offsetWidth - 8, 8);
      const maxTop = Math.max(window.innerHeight - overlay.offsetHeight - 8, 8);
      const left = clamp(event.clientX - dragState.offsetX, 8, maxLeft);
      const top = clamp(event.clientY - dragState.offsetY, 8, maxTop);
      overlay.style.left = `${left}px`;
      overlay.style.top = `${top}px`;
      overlay.style.right = 'auto';
      overlay.style.bottom = 'auto';
    });

    const finishDrag = event => {
      if (!dragState || event.pointerId !== dragState.pointerId) {
        return;
      }
      const rect = overlay.getBoundingClientRect();
      const position = { left: rect.left, top: rect.top };
      dragState = null;
      overlay.classList.remove('hpd-dragging');
      persistOverlayPosition(position);
    };

    header.addEventListener('pointerup', finishDrag);
    header.addEventListener('pointercancel', finishDrag);
    window.addEventListener('resize', () => {
      applyOverlayPosition();
      const rect = overlay.getBoundingClientRect();
      persistOverlayPosition({ left: rect.left, top: rect.top });
    });
  }

  function bindClickCounter() {
    document.addEventListener('click', event => {
      if (event.target.closest(`#${rootId}`)) {
        return;
      }
      send({ type: 'incrementClick' }).catch(() => undefined);
    }, true);
  }

  function reportScreenChange(source) {
    const url = location.href;
    if (url === lastUrl) {
      return;
    }
    lastUrl = url;
    send({ type: 'incrementScreen', source }).catch(() => undefined);
  }

  function bindNavigationCounter() {
    const wrapHistory = method => {
      const original = history[method];
      history[method] = function () {
        const result = original.apply(this, arguments);
        window.setTimeout(() => reportScreenChange(method), 0);
        return result;
      };
    };
    wrapHistory('pushState');
    wrapHistory('replaceState');
    window.addEventListener('hashchange', () => reportScreenChange('hashchange'));
    window.addEventListener('popstate', () => reportScreenChange('popstate'));
  }

  function bindAssistantTimingEvents() {
    window.addEventListener('humanenerdia:pilot:assistant-query-start', event => {
      if (state?.condition !== 'B' || state.running) {
        return;
      }
      send({
        type: 'startTask',
        source: event.detail?.source || 'assistant'
      }).then(response => {
        if (!applyResponse(response)) {
          return;
        }
        setLast('Assistant task started automatically.');
      }).catch(() => undefined);
    });

    window.addEventListener('humanenerdia:pilot:assistant-response-complete', event => {
      if (state?.condition !== 'B' || !state.running) {
        return;
      }
      send({
        type: 'assistantResponseComplete',
        success: event.detail?.success !== false,
        reason: event.detail?.stopReason || 'assistant_response_complete',
        source: event.detail?.source || 'assistant'
      }).then(response => {
        if (!applyResponse(response)) {
          return;
        }
        setLast(state.running
          ? 'Assistant response complete. Auto-stop is off.'
          : 'Assistant response complete. Task saved.'
        );
      }).catch(() => undefined);
    });
  }

  chrome.runtime.onMessage.addListener(message => {
    if (message?.type === 'stateUpdated') {
      state = message.state;
      tasks = message.tasks || tasks;
      render();
    }
  });

  function init() {
    createOverlay();
    refresh().catch(() => undefined);
    bindClickCounter();
    bindNavigationCounter();
    bindAssistantTimingEvents();
    timer = window.setInterval(render, 100);
    window.addEventListener('beforeunload', () => {
      if (timer) {
        window.clearInterval(timer);
      }
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
