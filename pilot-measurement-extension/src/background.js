'use strict';

const STORAGE_KEY = 'humanenerdia_pilot_extension_state_v1';

const TASKS = [
  {
    id: 'O1',
    title: 'Partner KPI overview',
    persona: 'Operational user',
    module: 'Monitoring',
    task: 'Retrieve the ASSA ABLOY press-shop KPI overview: total energy, total production, and group SEC values.',
    manual: 'HumanEnerDIA partner KPI/dashboard views and reports.',
    assistant: 'OVOS: Show KPIs for the ASSA ABLOY partner press shop.',
    stop: 'Stop when total energy 141,254.85 kWh, total production 27,625,665 units, and Bret/Raster/Dimeco SEC values are visible.'
  },
  {
    id: 'O2',
    title: 'Energy group comparison',
    persona: 'Operational user',
    module: 'Monitoring',
    task: 'Compare Bret, Raster, and Dimeco group energy consumption for the partner KPI period.',
    manual: 'HumanEnerDIA partner energy charts or partner summary API evidence.',
    assistant: 'OVOS: Compare Bret, Raster, and Dimeco energy consumption.',
    stop: 'Stop when Dimeco 59,661.97 kWh, Raster 41,981.81 kWh, and Bret 39,611.06 kWh are visible.'
  },
  {
    id: 'O3',
    title: 'Production and SEC meaning',
    persona: 'Operational user',
    module: 'Analyses / Documentation',
    task: 'Understand production-normalized performance using SEC and partner production totals.',
    manual: 'HumanEnerDIA KPI view plus ISO/EnPI documentation.',
    assistant: 'OVOS: Explain SEC for the partner press shop. Optional chatbot: What is SEC?',
    stop: 'Stop when SEC is defined as kWh per produced unit and Bret/Raster/Dimeco SEC values are visible.'
  },
  {
    id: 'O4',
    title: 'Baseline concept and active baselines',
    persona: 'Operational user',
    module: 'Documentation / Analyses',
    task: 'Understand the energy-baseline concept and confirm which partner meter groups have active EnPI baselines.',
    manual: 'HumanEnerDIA baseline UI and ISO 50001 documentation.',
    assistant: 'Chatbot: What is an energy baseline? OVOS: Which partner meter groups have baselines?',
    stop: 'Stop when the baseline concept and active EnPI baselines for 3 of 3 partner meter groups are visible.'
  },
  {
    id: 'T1',
    title: 'Data inventory verification',
    persona: 'Technical user',
    module: 'Documentation',
    task: 'Verify imported ASSA ABLOY energy and production row counts.',
    manual: 'Partner data verification document and partner profile/API evidence.',
    assistant: 'OVOS: How many readings and rows were imported for ASSA ABLOY?',
    stop: 'Stop when 1,978 energy readings and 6,336 materialized production rows are visible.'
  },
  {
    id: 'T2',
    title: 'Meter boundary and per-press guardrail',
    persona: 'Technical user',
    module: 'Documentation / Analyses',
    task: 'Confirm the Bret transformer reference-meter boundary and verify that per-press energy is not invented.',
    manual: 'Partner ingestion/verification document and partner summary/API evidence.',
    assistant: 'OVOS: What does the Bret transformer reference meter show? OVOS: Energy consumption of Bret125-1.',
    stop: 'Stop when the transformer shows 743 rows and 263,999.16 kWh excluded from KPIs, and Bret125-1 per-press energy is refused.'
  },
  {
    id: 'T3',
    title: 'SEU and baseline readiness',
    persona: 'Technical user',
    module: 'Analyses',
    task: 'Identify partner SEUs and confirm baseline readiness for the three partner meter groups.',
    manual: 'HumanEnerDIA baseline/model-performance views and partner ML readiness API evidence.',
    assistant: 'OVOS: What are the significant energy uses in the partner press shop? OVOS: Which partner meter groups have baselines?',
    stop: 'Stop when Bret, Dimeco, and Raster Presses Electricity are listed and active baselines are shown for 3 of 3 meter groups.'
  },
  {
    id: 'T4',
    title: 'Monthly reporting',
    persona: 'Technical user',
    module: 'Analyses / Documentation',
    task: 'Generate or retrieve a monthly reporting result for the partner press shop.',
    manual: 'HumanEnerDIA reports page with ASSA ABLOY Partner Press Shop and May 2026 selected.',
    assistant: 'OVOS: download the ASSA ABLOY partner press shop report for May 2026.',
    stop: 'Stop when the May 2026 monthly energy report is generated/downloaded or the report-ready response is visible.'
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
    overlayPosition: null,
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
    if (parsed.pathname.startsWith('/grafana/d/')) {
      return `${parsed.origin}${parsed.pathname}`;
    }
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
    const screenKey = screenKeyFromUrl(context?.url || context?.screenKey);
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
        autoStopAssistant: state.autoStopAssistant,
        overlayCollapsed: state.overlayCollapsed,
        overlayPosition: state.overlayPosition
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
      const preserved = {
        overlayCollapsed: state.overlayCollapsed,
        overlayPosition: state.overlayPosition
      };
      Object.assign(state, blankState(), preserved);
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
