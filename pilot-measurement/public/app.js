(function () {
    'use strict';

    const STORAGE_KEY = 'humanenerdia_standalone_pilot_measurement_v1';

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

    const elements = {};
    const now = () => Date.now();

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
            expertHelp: false,
            manualReasoning: true,
            success: true,
            notes: '',
            records: []
        };
    }

    function loadState() {
        try {
            return { ...blankState(), ...JSON.parse(localStorage.getItem(STORAGE_KEY) || '{}') };
        } catch (_) {
            return blankState();
        }
    }

    let state = loadState();
    let intervalId = null;

    function saveState() {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
    }

    function currentTask() {
        return TASKS.find(task => task.id === state.taskId) || TASKS[0];
    }

    function elapsedMs() {
        if (!state.running || !state.startedAt) {
            return state.elapsedMs || 0;
        }
        return (state.elapsedMs || 0) + (now() - state.startedAt);
    }

    function formatTime(ms) {
        const totalSeconds = Math.floor(ms / 1000);
        const minutes = Math.floor(totalSeconds / 60);
        const seconds = totalSeconds % 60;
        const tenths = Math.floor((ms % 1000) / 100);
        return `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}.${tenths}`;
    }

    function median(values) {
        const sorted = values.filter(Number.isFinite).sort((a, b) => a - b);
        if (!sorted.length) {
            return null;
        }
        const mid = Math.floor(sorted.length / 2);
        return sorted.length % 2 ? sorted[mid] : (sorted[mid - 1] + sorted[mid]) / 2;
    }

    function csvEscape(value) {
        const text = String(value ?? '');
        return `"${text.replaceAll('"', '""')}"`;
    }

    function rowsToCsv(headers, rows) {
        return [
            headers.join(','),
            ...rows.map(row => headers.map(header => csvEscape(row[header])).join(','))
        ].join('\n');
    }

    function currentRecord(reason) {
        const task = currentTask();
        return {
            timestamp: new Date().toISOString(),
            session: state.sessionName,
            condition: state.condition,
            trial: state.trial,
            persona: task.persona,
            taskId: task.id,
            task: task.title,
            module: task.module,
            elapsedSec: Number((elapsedMs() / 1000).toFixed(1)),
            clicks: state.clicks,
            screens: state.screens,
            expertHelp: state.expertHelp ? 1 : 0,
            manualReasoning: state.manualReasoning ? 1 : 0,
            success: state.success ? 1 : 0,
            stopReason: reason,
            notes: state.notes
        };
    }

    function rawCsv() {
        const headers = [
            'timestamp', 'session', 'condition', 'trial', 'persona', 'taskId', 'task',
            'module', 'elapsedSec', 'clicks', 'screens', 'expertHelp',
            'manualReasoning', 'success', 'stopReason', 'notes'
        ];
        return rowsToCsv(headers, state.records);
    }

    function taskRecords(taskId, condition) {
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

    function summaryRows() {
        return TASKS.map(task => {
            const a = taskRecords(task.id, 'A');
            const b = taskRecords(task.id, 'B');
            const aSec = median(a.map(record => Number(record.elapsedSec)));
            const bSec = median(b.map(record => Number(record.elapsedSec)));
            const aClicks = median(a.map(record => Number(record.clicks)));
            const bClicks = median(b.map(record => Number(record.clicks)));
            const aScreens = median(a.map(record => Number(record.screens)));
            const bScreens = median(b.map(record => Number(record.screens)));
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
                conditionAExpertHelp: flagSummary(a, 'expertHelp'),
                conditionBExpertHelp: flagSummary(b, 'expertHelp'),
                conditionAManualReasoning: flagSummary(a, 'manualReasoning'),
                conditionBManualReasoning: flagSummary(b, 'manualReasoning'),
                conditionASuccess: successSummary(a),
                conditionBSuccess: successSummary(b),
                notes: ''
            };
        });
    }

    function summaryCsv() {
        const headers = [
            'persona', 'taskId', 'module', 'taskName', 'conditionAMedianSec',
            'conditionBMedianSec', 'timeReductionPercent', 'conditionAMedianClicks',
            'conditionBMedianClicks', 'clickReductionPercent', 'conditionAMedianScreens',
            'conditionBMedianScreens', 'conditionAExpertHelp', 'conditionBExpertHelp',
            'conditionAManualReasoning', 'conditionBManualReasoning',
            'conditionASuccess', 'conditionBSuccess', 'notes'
        ];
        return rowsToCsv(headers, summaryRows());
    }

    function downloadFile(filename, content, type) {
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
        elements.lastMessage.textContent = message;
    }

    function resetCurrent() {
        state.running = false;
        state.startedAt = null;
        state.elapsedMs = 0;
        state.clicks = 0;
        state.screens = 0;
        state.expertHelp = false;
        state.manualReasoning = state.condition === 'A';
        state.success = true;
        state.notes = '';
        saveState();
        render();
        setLast('Current task counters reset.');
    }

    function startTask() {
        state.elapsedMs = 0;
        state.startedAt = now();
        state.running = true;
        state.clicks = 0;
        state.screens = 1;
        state.expertHelp = false;
        state.manualReasoning = state.condition === 'A';
        state.success = true;
        state.notes = elements.notes.value.trim();
        saveState();
        render();
        setLast(`Started ${state.condition}-${state.taskId}.`);
    }

    function stopTask(reason) {
        if (!state.running) {
            return;
        }
        state.elapsedMs = elapsedMs();
        state.startedAt = null;
        state.running = false;
        state.notes = elements.notes.value.trim();
        const record = currentRecord(reason);
        state.records.push(record);
        saveState();
        render();
        setLast(`Saved ${record.condition}-${record.taskId} trial ${record.trial}: ${record.elapsedSec}s.`);
    }

    function setCondition(value) {
        state.condition = value;
        state.manualReasoning = value === 'A';
        saveState();
        render();
    }

    function renderTaskOptions() {
        elements.task.innerHTML = TASKS.map(task => (
            `<option value="${task.id}">${task.id} - ${task.title}</option>`
        )).join('');
    }

    function renderTaskDetails() {
        const task = currentTask();
        elements.taskPersona.textContent = task.persona;
        elements.taskTitle.textContent = `${task.id} - ${task.title}`;
        elements.taskModule.textContent = task.module;
        elements.taskDescription.textContent = task.task;
        elements.taskManual.textContent = task.manual;
        elements.taskAssistant.textContent = task.assistant;
        elements.taskStop.textContent = task.stop;
    }

    function renderRecords() {
        if (!state.records.length) {
            elements.recordsBody.innerHTML = '<tr class="empty-row"><td colspan="10">No records yet.</td></tr>';
            return;
        }

        elements.recordsBody.innerHTML = state.records.slice().reverse().map(record => `
            <tr>
                <td>${new Date(record.timestamp).toLocaleTimeString()}</td>
                <td>${record.condition}</td>
                <td>${record.trial}</td>
                <td>${record.taskId}</td>
                <td>${record.elapsedSec}</td>
                <td>${record.clicks}</td>
                <td>${record.screens}</td>
                <td>${record.expertHelp}</td>
                <td>${record.manualReasoning}</td>
                <td>${record.success}</td>
            </tr>
        `).join('');
    }

    function renderSummary() {
        elements.summaryBody.innerHTML = summaryRows().map(row => `
            <tr>
                <td>${row.taskId}</td>
                <td>${row.conditionAMedianSec}</td>
                <td>${row.conditionBMedianSec}</td>
                <td>${row.timeReductionPercent === '' ? '' : `${row.timeReductionPercent}%`}</td>
                <td>${row.conditionAMedianClicks}</td>
                <td>${row.conditionBMedianClicks}</td>
            </tr>
        `).join('');
    }

    function render() {
        elements.condition.value = state.condition;
        elements.task.value = state.taskId;
        elements.trial.value = state.trial;
        elements.sessionName.value = state.sessionName;
        elements.expertHelp.checked = !!state.expertHelp;
        elements.manualReasoning.checked = !!state.manualReasoning;
        elements.success.checked = !!state.success;
        elements.notes.value = state.notes || '';
        elements.timer.textContent = formatTime(elapsedMs());
        elements.clicks.textContent = state.clicks;
        elements.screens.textContent = state.screens;
        elements.recordCount.textContent = state.records.length;
        elements.runningState.textContent = state.running ? 'Running' : 'Idle';
        elements.runningState.classList.toggle('running', state.running);
        elements.startTask.disabled = state.running;
        elements.answerFound.disabled = !state.running;
        renderTaskDetails();
        renderRecords();
        renderSummary();
    }

    function bindEvents() {
        elements.condition.addEventListener('change', event => setCondition(event.target.value));
        elements.task.addEventListener('change', event => {
            state.taskId = event.target.value;
            resetCurrent();
        });
        elements.trial.addEventListener('change', event => {
            state.trial = event.target.value;
            saveState();
        });
        elements.sessionName.addEventListener('input', event => {
            state.sessionName = event.target.value.trim() || 'official-run';
            saveState();
        });
        elements.expertHelp.addEventListener('change', event => {
            state.expertHelp = event.target.checked;
            saveState();
        });
        elements.manualReasoning.addEventListener('change', event => {
            state.manualReasoning = event.target.checked;
            saveState();
        });
        elements.success.addEventListener('change', event => {
            state.success = event.target.checked;
            saveState();
        });
        elements.notes.addEventListener('input', event => {
            state.notes = event.target.value;
            saveState();
        });
        elements.startTask.addEventListener('click', startTask);
        elements.answerFound.addEventListener('click', () => stopTask('answer_found'));
        elements.addClick.addEventListener('click', () => {
            state.clicks += 1;
            saveState();
            render();
        });
        elements.removeClick.addEventListener('click', () => {
            state.clicks = Math.max(0, state.clicks - 1);
            saveState();
            render();
        });
        elements.addScreen.addEventListener('click', () => {
            state.screens += 1;
            saveState();
            render();
        });
        elements.removeScreen.addEventListener('click', () => {
            state.screens = Math.max(0, state.screens - 1);
            saveState();
            render();
        });
        elements.resetCurrent.addEventListener('click', resetCurrent);
        elements.deleteLast.addEventListener('click', () => {
            state.records.pop();
            saveState();
            render();
            setLast('Last record deleted.');
        });
        elements.clearAll.addEventListener('click', () => {
            if (!window.confirm('Clear all saved records and current counters?')) {
                return;
            }
            state = blankState();
            saveState();
            render();
            setLast('All records cleared.');
        });
        elements.copyRaw.addEventListener('click', () => copyText(rawCsv(), 'Raw CSV'));
        elements.copySummary.addEventListener('click', () => copyText(summaryCsv(), 'KPI Summary CSV'));
        elements.downloadRaw.addEventListener('click', () => {
            downloadFile(`pilot-measurement-raw-${new Date().toISOString().slice(0, 10)}.csv`, rawCsv(), 'text/csv');
        });
        elements.downloadSummary.addEventListener('click', () => {
            downloadFile(`pilot-measurement-summary-${new Date().toISOString().slice(0, 10)}.csv`, summaryCsv(), 'text/csv');
        });
        elements.downloadJson.addEventListener('click', () => {
            downloadFile(`pilot-measurement-${new Date().toISOString().slice(0, 10)}.json`, JSON.stringify(state.records, null, 2), 'application/json');
        });
        window.addEventListener('beforeunload', saveState);
    }

    function collectElements() {
        [
            'condition', 'task', 'trial', 'session-name', 'running-state', 'timer',
            'clicks', 'screens', 'record-count', 'start-task', 'answer-found',
            'add-click', 'remove-click', 'add-screen', 'remove-screen',
            'expert-help', 'manual-reasoning', 'success', 'notes', 'reset-current',
            'delete-last', 'clear-all', 'copy-raw', 'download-raw', 'copy-summary',
            'download-summary', 'download-json', 'last-message', 'task-persona', 'task-title',
            'task-module', 'task-description', 'task-manual', 'task-assistant',
            'task-stop', 'records-body', 'summary-body'
        ].forEach(id => {
            const key = id.replace(/-([a-z])/g, (_, letter) => letter.toUpperCase());
            elements[key] = document.getElementById(id);
        });
    }

    function init() {
        collectElements();
        renderTaskOptions();
        bindEvents();
        render();
        intervalId = window.setInterval(render, 100);
        window.addEventListener('beforeunload', () => {
            if (intervalId) {
                window.clearInterval(intervalId);
            }
        });
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
