'use strict';

let state = null;
let tasks = [];
let timer = null;

const els = {};

function send(message) {
  return chrome.runtime.sendMessage(message);
}

async function activeContext() {
  const tabs = await chrome.tabs.query({ active: true, currentWindow: true });
  const tab = tabs[0];
  return { url: tab?.url || '', title: tab?.title || '' };
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

function setMessage(message) {
  els.message.textContent = message;
}

function applyResponse(response) {
  state = response.state;
  tasks = response.tasks || tasks;
  render();
}

function renderTaskOptions() {
  els.task.innerHTML = tasks.map(task => `<option value="${task.id}">${task.id} - ${task.title}</option>`).join('');
}

function render() {
  if (!state) {
    return;
  }
  els.condition.value = state.condition;
  els.task.value = state.taskId;
  els.trial.value = state.trial;
  els.timer.textContent = formatTime(elapsedMs());
  els.status.textContent = state.running ? 'Running' : 'Idle';
  els.status.classList.toggle('running', state.running);
  els.clicks.textContent = state.clicks;
  els.screens.textContent = state.screens;
  els.records.textContent = state.records.length;
  els.expert.checked = !!state.expertHelp;
  els.reasoning.checked = !!state.manualReasoning;
  els.success.checked = !!state.success;
  els.autostop.checked = state.autoStopAssistant !== false;
  els.start.disabled = state.running;
  els.stop.disabled = !state.running;
}

async function refresh() {
  const response = await send({ type: 'getState' });
  state = response.state;
  tasks = response.tasks || [];
  renderTaskOptions();
  render();
}

function updateSettings(patch) {
  send({ type: 'updateSettings', patch }).then(response => {
    applyResponse(response);
  });
}

async function copyText(text, label) {
  try {
    await navigator.clipboard.writeText(text);
    setMessage(`${label} copied.`);
  } catch (_) {
    setMessage(`Could not copy ${label}.`);
  }
}

function bind() {
  els.condition.addEventListener('change', event => updateSettings({ condition: event.target.value }));
  els.task.addEventListener('change', event => updateSettings({ taskId: event.target.value }));
  els.trial.addEventListener('change', event => updateSettings({ trial: event.target.value }));
  els.expert.addEventListener('change', event => updateSettings({ expertHelp: event.target.checked }));
  els.reasoning.addEventListener('change', event => updateSettings({ manualReasoning: event.target.checked }));
  els.success.addEventListener('change', event => updateSettings({ success: event.target.checked }));
  els.autostop.addEventListener('change', event => updateSettings({ autoStopAssistant: event.target.checked }));
  els.start.addEventListener('click', async () => send({ type: 'startTask', ...(await activeContext()) }).then(response => {
    applyResponse(response);
    setMessage(`Started ${state.condition}-${state.taskId}.`);
  }));
  els.stop.addEventListener('click', async () => send({ type: 'stopTask', reason: 'answer_found', ...(await activeContext()) }).then(response => {
    applyResponse(response);
    setMessage('Task saved.');
  }));
  els.minusClick.addEventListener('click', () => send({ type: 'adjustCounter', counter: 'clicks', delta: -1 }).then(applyResponse));
  els.plusClick.addEventListener('click', () => send({ type: 'adjustCounter', counter: 'clicks', delta: 1 }).then(applyResponse));
  els.minusScreen.addEventListener('click', () => send({ type: 'adjustCounter', counter: 'screens', delta: -1 }).then(applyResponse));
  els.plusScreen.addEventListener('click', () => send({ type: 'adjustCounter', counter: 'screens', delta: 1 }).then(applyResponse));
  els.deleteLast.addEventListener('click', () => send({ type: 'deleteLast' }).then(response => {
    applyResponse(response);
    setMessage('Last record deleted.');
  }));
  els.clearAll.addEventListener('click', () => {
    if (!window.confirm('Clear all pilot measurement records?')) {
      return;
    }
    send({ type: 'clearAll' }).then(response => {
      applyResponse(response);
      setMessage('All records cleared.');
    });
  });
  els.copyRaw.addEventListener('click', async () => {
    const response = await send({ type: 'export' });
    await copyText(response.rawCsv, 'Raw CSV');
  });
  els.copySummary.addEventListener('click', async () => {
    const response = await send({ type: 'export' });
    await copyText(response.summaryCsv, 'KPI CSV');
  });
}

function collectElements() {
  [
    'status', 'timer', 'condition', 'task', 'trial', 'clicks', 'screens',
    'records', 'start', 'stop', 'minus-click', 'plus-click', 'minus-screen',
    'plus-screen', 'expert', 'reasoning', 'success', 'copy-raw',
    'autostop', 'copy-summary', 'delete-last', 'clear-all', 'message'
  ].forEach(id => {
    const key = id.replace(/-([a-z])/g, (_, letter) => letter.toUpperCase());
    els[key] = document.getElementById(id);
  });
}

chrome.runtime.onMessage.addListener(message => {
  if (message?.type === 'stateUpdated') {
    state = message.state;
    tasks = message.tasks || tasks;
    render();
  }
});

document.addEventListener('DOMContentLoaded', () => {
  collectElements();
  bind();
  refresh();
  timer = window.setInterval(render, 100);
  window.addEventListener('beforeunload', () => {
    if (timer) {
      window.clearInterval(timer);
    }
  });
});
