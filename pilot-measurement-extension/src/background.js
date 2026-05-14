'use strict';

const STORAGE_KEY = 'humanenerdia_pilot_extension_state_v1';

const TASKS = [
  {
    id: 'O1',
    title: 'Factory overview and top consumers',
    persona: 'Operational user',
    module: 'Monitoring',
    task: 'Get a factory overview and identify the top 3 energy consumers.',
    manual: 'Grafana Factory Overview: Energy Today, Current Power, Cost Today, Active Anomalies, Machine Status & Health, Energy by Machine (Today).',
    assistant: 'OVOS: Give me a factory overview; Show top 3 energy consumers.',
    stop: 'Stop when today/current factory status and top consumers Compressor-2, Injection-Molding-1, and Compressor-1 are visible.'
  },
  {
    id: 'O2',
    title: "Compressor-1 status and today's energy",
    persona: 'Operational user',
    module: 'Monitoring',
    task: "Check the status and today's energy of Compressor-1.",
    manual: 'Grafana Machine Health for Compressor-1. Use Operational Efficiency / Machine Status Overview if running status must be shown explicitly.',
    assistant: "OVOS: What's the status of Compressor-1?",
    stop: "Stop when Compressor-1 running status, current power, today's energy, and anomaly status are visible."
  },
  {
    id: 'O3',
    title: 'ISO 50001 and energy baseline',
    persona: 'Operational user',
    module: 'Documentation',
    task: 'Understand what ISO 50001 is and what an energy baseline means.',
    manual: '/energy-management-learning.html, optionally /api/analytics/ui/baseline.',
    assistant: 'Rasa: What is ISO 50001?; What is an energy baseline?',
    stop: 'Stop when both ISO 50001 and energy baseline definitions are visible.'
  },
  {
    id: 'O4',
    title: 'Anomaly or efficiency procedure',
    persona: 'Operational user',
    module: 'Documentation',
    task: 'Find the policy and procedure guidance for responding to an anomaly or efficiency issue.',
    manual: '/pilot-procedures.html, optionally /api/analytics/ui/anomaly.',
    assistant: 'Rasa: What should we do when an anomaly appears?; What is the procedure for responding to an efficiency issue?',
    stop: 'Stop when anomaly response and efficiency response guidance are visible.'
  },
  {
    id: 'T1',
    title: 'Review anomalies',
    persona: 'Technical user',
    module: 'Monitoring',
    task: 'Review anomalies and identify the issue requiring attention.',
    manual: '/api/analytics/ui/anomaly, optionally Grafana Anomaly Detection with Last 7 days.',
    assistant: 'OVOS: Show me recent anomalies.',
    stop: 'Stop when the unresolved high-severity or critical issue is identified, normally Compressor-2 if it is active.'
  },
  {
    id: 'T2',
    title: 'Baseline analysis and recommendations',
    persona: 'Technical user',
    module: 'Analyses',
    task: 'Analyze Compressor-1 against baseline, check forecast context, and retrieve recommendations.',
    manual: 'Grafana Machine Health, /api/analytics/ui/forecast with Short (1-4 hours), and /api/analytics/ui/opportunities.',
    assistant: 'OVOS: Analyze performance of Compressor-1; Energy forecast for Compressor-1; What are the energy saving opportunities?',
    stop: 'Stop after baseline evidence, forecast result, and top opportunities are found.'
  },
  {
    id: 'T3',
    title: 'KPI and EnPI status',
    persona: 'Technical user',
    module: 'Analyses',
    task: 'Retrieve factory KPI and EnPI status for 2026-Q1.',
    manual: '/api/analytics/ui/kpi and /api/analytics/ui/enpi-report, optionally Grafana ISO 50001 EnPI.',
    assistant: 'OVOS: Show energy performance indicators report.',
    stop: 'Stop when 2026-Q1 status, deviation, and performance gap are visible.'
  },
  {
    id: 'T4',
    title: 'April 2026 report',
    persona: 'Technical user',
    module: 'Analyses / Documentation',
    task: 'Generate the April 2026 monthly report and summarize the result.',
    manual: '/reports.html with the simulated Romanian pilot factory and April 2026 selected.',
    assistant: 'OVOS: download report of Apr 2026.',
    stop: 'Stop when the April 2026 report generation or download result is visible.'
  }
];

function blankState() {
  return {
    condition: 'A',
    taskId: 'O1',
    trial: '1',
    sessionName: 'official-run',
    running: false,
    startedAt: null,
    elapsedMs: 0,
    clicks: 0,
    screens: 0,
    lastScreenKey: null,
    expertHelp: false,
    manualReasoning: true,
    success: true,
    autoStopAssistant: true,
    notes: '',
    overlayCollapsed: false,
    records: []
  };
}

async function loadState() {
  const stored = await chrome.storage.local.get(STORAGE_KEY);
  return { ...blankState(), ...(stored[STORAGE_KEY] || {}) };
}

async function saveState(state) {
  await chrome.storage.local.set({ [STORAGE_KEY]: state });
}

function taskById(taskId) {
  return TASKS.find(task => task.id === taskId) || TASKS[0];
}

function elapsedMs(state) {
  if (!state.running || !state.startedAt) {
    return state.elapsedMs || 0;
  }
  return (state.elapsedMs || 0) + (Date.now() - state.startedAt);
}

function screenKeyFromUrl(url) {
  if (!url) {
    return '';
  }
  try {
    const parsed = new URL(url);
    return `${parsed.origin}${parsed.pathname}${parsed.search}${parsed.hash}`;
  } catch (_) {
    return url;
  }
}

function currentRecord(state, reason, context) {
  const task = taskById(state.taskId);
  return {
    timestamp: new Date().toISOString(),
    session: state.sessionName,
    condition: state.condition,
    trial: state.trial,
    persona: task.persona,
    taskId: task.id,
    task: task.title,
    module: task.module,
    elapsedSec: Number((elapsedMs(state) / 1000).toFixed(1)),
    clicks: state.clicks,
    screens: state.screens,
    expertHelp: state.expertHelp ? 1 : 0,
    manualReasoning: state.manualReasoning ? 1 : 0,
    success: state.success ? 1 : 0,
    stopReason: reason || 'answer_found',
    url: context?.url || '',
    title: context?.title || '',
    notes: state.notes || ''
  };
}

function median(values) {
  const sorted = values.filter(Number.isFinite).sort((a, b) => a - b);
  if (!sorted.length) {
    return null;
  }
  const mid = Math.floor(sorted.length / 2);
  return sorted.length % 2 ? sorted[mid] : (sorted[mid - 1] + sorted[mid]) / 2;
}

function taskRecords(state, taskId, condition) {
  return state.records.filter(record => record.taskId === taskId && record.condition === condition);
}

function flagSummary(records, key) {
  if (!records.length) {
    return '';
  }
  return records.some(record => Number(record[key]) === 1) ? 1 : 0;
}

function successSummary(records) {
  if (!records.length) {
    return '';
  }
  return records.every(record => Number(record.success) === 1) ? 1 : 0;
}

function summaryRows(state) {
  return TASKS.map(task => {
    const conditionA = taskRecords(state, task.id, 'A');
    const conditionB = taskRecords(state, task.id, 'B');
    const aSec = median(conditionA.map(record => Number(record.elapsedSec)));
    const bSec = median(conditionB.map(record => Number(record.elapsedSec)));
    const aClicks = median(conditionA.map(record => Number(record.clicks)));
    const bClicks = median(conditionB.map(record => Number(record.clicks)));
    const aScreens = median(conditionA.map(record => Number(record.screens)));
    const bScreens = median(conditionB.map(record => Number(record.screens)));
    const reduction = aSec && bSec !== null ? ((aSec - bSec) / aSec) * 100 : null;
    const clickReduction = aClicks && bClicks !== null ? ((aClicks - bClicks) / aClicks) * 100 : null;

    return {
      persona: task.persona,
      taskId: task.id,
      module: task.module,
      taskName: task.task,
      conditionAMedianSec: aSec === null ? '' : Number(aSec.toFixed(1)),
      conditionBMedianSec: bSec === null ? '' : Number(bSec.toFixed(1)),
      timeReductionPercent: reduction === null ? '' : Number(reduction.toFixed(2)),
      conditionAMedianClicks: aClicks === null ? '' : Number(aClicks.toFixed(1)),
      conditionBMedianClicks: bClicks === null ? '' : Number(bClicks.toFixed(1)),
      clickReductionPercent: clickReduction === null ? '' : Number(clickReduction.toFixed(2)),
      conditionAMedianScreens: aScreens === null ? '' : Number(aScreens.toFixed(1)),
      conditionBMedianScreens: bScreens === null ? '' : Number(bScreens.toFixed(1)),
      conditionAExpertHelp: flagSummary(conditionA, 'expertHelp'),
      conditionBExpertHelp: flagSummary(conditionB, 'expertHelp'),
      conditionAManualReasoning: flagSummary(conditionA, 'manualReasoning'),
      conditionBManualReasoning: flagSummary(conditionB, 'manualReasoning'),
      conditionASuccess: successSummary(conditionA),
      conditionBSuccess: successSummary(conditionB),
      notes: ''
    };
  });
}

function csvEscape(value) {
  return `"${String(value ?? '').replaceAll('"', '""')}"`;
}

function rowsToCsv(headers, rows) {
  return [
    headers.join(','),
    ...rows.map(row => headers.map(header => csvEscape(row[header])).join(','))
  ].join('\n');
}

function rawCsv(state) {
  const headers = [
    'timestamp', 'session', 'condition', 'trial', 'persona', 'taskId', 'task',
    'module', 'elapsedSec', 'clicks', 'screens', 'expertHelp',
    'manualReasoning', 'success', 'stopReason', 'url', 'title', 'notes'
  ];
  return rowsToCsv(headers, state.records);
}

function summaryCsv(state) {
  const headers = [
    'persona', 'taskId', 'module', 'taskName', 'conditionAMedianSec',
    'conditionBMedianSec', 'timeReductionPercent', 'conditionAMedianClicks',
    'conditionBMedianClicks', 'clickReductionPercent', 'conditionAMedianScreens',
    'conditionBMedianScreens', 'conditionAExpertHelp', 'conditionBExpertHelp',
    'conditionAManualReasoning', 'conditionBManualReasoning',
    'conditionASuccess', 'conditionBSuccess', 'notes'
  ];
  return rowsToCsv(headers, summaryRows(state));
}

async function broadcastState(state) {
  const tabs = await chrome.tabs.query({});
  await Promise.all(tabs.map(tab => (
    tab.id
      ? chrome.tabs.sendMessage(tab.id, { type: 'stateUpdated', state, tasks: TASKS }).catch(() => undefined)
      : Promise.resolve()
  )));
}

async function updateState(mutator) {
  const state = await loadState();
  const result = await mutator(state);
  await saveState(state);
  await broadcastState(state);
  return result ?? { state, tasks: TASKS };
}

async function startTask(context) {
  return updateState(state => {
    state.elapsedMs = 0;
    state.startedAt = Date.now();
    state.running = true;
    state.clicks = 0;
    state.screens = 1;
    state.lastScreenKey = screenKeyFromUrl(context?.url);
    state.expertHelp = false;
    state.manualReasoning = state.condition === 'A';
    state.success = true;
    state.autoStopAssistant = state.autoStopAssistant !== false;
    return { state, tasks: TASKS };
  });
}

async function stopTask(reason, context) {
  return updateState(state => {
    if (!state.running) {
      return { state, tasks: TASKS };
    }
    state.elapsedMs = elapsedMs(state);
    state.startedAt = null;
    state.running = false;
    state.records.push(currentRecord(state, reason, context));
    return { state, tasks: TASKS };
  });
}

async function incrementScreen(context) {
  return updateState(state => {
    if (!state.running) {
      return { state, tasks: TASKS };
    }
    const screenKey = context?.screenKey || screenKeyFromUrl(context?.url);
    if (screenKey && screenKey !== state.lastScreenKey) {
      state.screens += 1;
      state.lastScreenKey = screenKey;
    }
    return { state, tasks: TASKS };
  });
}

async function handleMessage(message, sender) {
  const context = {
    url: message?.url || sender?.tab?.url || '',
    title: message?.title || sender?.tab?.title || '',
    screenKey: message?.screenKey
  };

  if (message?.type === 'getState') {
    const state = await loadState();
    return { state, tasks: TASKS, rawCsv: rawCsv(state), summaryCsv: summaryCsv(state) };
  }

  if (message?.type === 'updateSettings') {
    return updateState(state => {
      Object.assign(state, message.patch || {});
      if (Object.prototype.hasOwnProperty.call(message.patch || {}, 'condition') && !state.running) {
        state.manualReasoning = state.condition === 'A';
      }
      return { state, tasks: TASKS };
    });
  }

  if (message?.type === 'startTask') {
    return startTask(context);
  }

  if (message?.type === 'stopTask') {
    return stopTask(message.reason || 'answer_found', context);
  }

  if (message?.type === 'assistantResponseComplete') {
    return updateState(state => {
      if (state.condition !== 'B' || !state.running) {
        return { state, tasks: TASKS };
      }
      state.success = message.success !== false;
      if (state.autoStopAssistant === false) {
        return { state, tasks: TASKS };
      }
      state.elapsedMs = elapsedMs(state);
      state.startedAt = null;
      state.running = false;
      state.records.push(currentRecord(state, message.reason || 'assistant_response_complete', context));
      return { state, tasks: TASKS };
    });
  }

  if (message?.type === 'incrementClick') {
    return updateState(state => {
      if (state.running) {
        state.clicks += 1;
      }
      return { state, tasks: TASKS };
    });
  }

  if (message?.type === 'incrementScreen') {
    return incrementScreen(context);
  }

  if (message?.type === 'adjustCounter') {
    return updateState(state => {
      const key = message.counter === 'screens' ? 'screens' : 'clicks';
      state[key] = Math.max(0, Number(state[key] || 0) + Number(message.delta || 0));
      return { state, tasks: TASKS };
    });
  }

  if (message?.type === 'resetCurrent') {
    return updateState(state => {
      const records = state.records;
      const preserved = {
        condition: state.condition,
        taskId: state.taskId,
        trial: state.trial,
        sessionName: state.sessionName,
        overlayCollapsed: state.overlayCollapsed
      };
      Object.assign(state, blankState(), preserved, { records });
      state.manualReasoning = state.condition === 'A';
      return { state, tasks: TASKS };
    });
  }

  if (message?.type === 'deleteLast') {
    return updateState(state => {
      state.records.pop();
      return { state, tasks: TASKS };
    });
  }

  if (message?.type === 'clearAll') {
    return updateState(state => {
      Object.assign(state, blankState());
      return { state, tasks: TASKS };
    });
  }

  if (message?.type === 'export') {
    const state = await loadState();
    return { state, tasks: TASKS, rawCsv: rawCsv(state), summaryCsv: summaryCsv(state) };
  }

  return { state: await loadState(), tasks: TASKS };
}

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  handleMessage(message, sender)
    .then(sendResponse)
    .catch(error => sendResponse({ error: error.message }));
  return true;
});

chrome.webNavigation.onHistoryStateUpdated.addListener(details => {
  if (details.frameId !== 0) {
    return;
  }
  incrementScreen({ url: details.url, screenKey: screenKeyFromUrl(details.url) }).catch(() => undefined);
});

chrome.webNavigation.onCommitted.addListener(details => {
  if (details.frameId !== 0) {
    return;
  }
  incrementScreen({ url: details.url, screenKey: screenKeyFromUrl(details.url) }).catch(() => undefined);
});

chrome.commands.onCommand.addListener(command => {
  chrome.tabs.query({ active: true, currentWindow: true }).then(tabs => {
    const tab = tabs[0];
    const context = { url: tab?.url || '', title: tab?.title || '' };
    if (command === 'start-task') {
      return startTask(context);
    }
    if (command === 'answer-found') {
      return stopTask('answer_found', context);
    }
    if (command === 'add-screen') {
      return updateState(state => {
        state.screens += 1;
        return { state, tasks: TASKS };
      });
    }
    return undefined;
  }).catch(() => undefined);
});
