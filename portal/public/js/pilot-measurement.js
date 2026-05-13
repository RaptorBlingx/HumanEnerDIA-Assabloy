/**
 * HumanEnerDIA Simulated Pilot Measurement Overlay
 *
 * Enabled only when localStorage.humanenerdia_pilot_mode is set to
 * "manual", "assistant", or "pilot", or when ?pilot_mode=... is present.
 */
(function () {
    'use strict';

    const urlParams = new URLSearchParams(window.location.search);
    const mode = (urlParams.get('pilot_mode') || localStorage.getItem('humanenerdia_pilot_mode') || '').toLowerCase();
    const enabled = ['manual', 'assistant', 'pilot'].includes(mode);

    if (!enabled) {
        return;
    }

    const STORAGE_KEY = 'humanenerdia_pilot_measurement_state';
    const DEFAULT_CONDITION = mode === 'assistant' ? 'B' : 'A';
    const TASKS = [
        ['O1', 'Factory overview and top consumers'],
        ['O2', 'Compressor-1 status and today energy'],
        ['O3', 'ISO 50001 and energy baseline'],
        ['O4', 'Anomaly or efficiency procedure'],
        ['T1', 'Review anomalies'],
        ['T2', 'Baseline analysis and recommendations'],
        ['T3', 'KPI and EnPI status'],
        ['T4', 'April 2026 report']
    ];

    const now = () => Date.now();
    const currentUrl = () => `${window.location.pathname}${window.location.search}${window.location.hash}`;

    function blankState() {
        return {
            condition: DEFAULT_CONDITION,
            taskId: 'O1',
            running: false,
            startedAt: null,
            elapsedMs: 0,
            clicks: 0,
            screens: 0,
            lastUrl: null,
            expertHelp: false,
            manualReasoning: DEFAULT_CONDITION === 'A',
            success: true,
            autoStopAssistant: true,
            records: [],
            panelPosition: null
        };
    }

    function loadState() {
        try {
            const parsed = JSON.parse(localStorage.getItem(STORAGE_KEY) || '{}');
            return { ...blankState(), ...parsed };
        } catch (_) {
            return blankState();
        }
    }

    let state = loadState();
    let timerInterval = null;

    function saveState() {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
    }

    function taskLabel(taskId = state.taskId) {
        const task = TASKS.find(([id]) => id === taskId);
        return task ? `${task[0]} - ${task[1]}` : taskId;
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

    function currentRecord(reason) {
        return {
            timestamp: new Date().toISOString(),
            condition: state.condition,
            taskId: state.taskId,
            task: taskLabel(),
            elapsedSec: Number((elapsedMs() / 1000).toFixed(1)),
            clicks: state.clicks,
            screens: state.screens,
            expertHelp: state.expertHelp ? 1 : 0,
            manualReasoning: state.manualReasoning ? 1 : 0,
            success: state.success ? 1 : 0,
            stopReason: reason || 'manual',
            url: currentUrl()
        };
    }

    function csvEscape(value) {
        const text = String(value ?? '');
        return `"${text.replaceAll('"', '""')}"`;
    }

    function recordsCsv() {
        const headers = [
            'timestamp', 'condition', 'taskId', 'task', 'elapsedSec', 'clicks',
            'screens', 'expertHelp', 'manualReasoning', 'success', 'stopReason', 'url'
        ];
        const rows = state.records.map(record => headers.map(header => csvEscape(record[header])).join(','));
        return [headers.join(','), ...rows].join('\n');
    }

    function createStyles() {
        const style = document.createElement('style');
        style.textContent = `
            #pilot-measurement-panel {
                position: fixed;
                left: 18px;
                bottom: 18px;
                z-index: 100000;
                width: 360px;
                max-width: calc(100vw - 36px);
                background: rgba(15, 23, 42, 0.96);
                color: #f8fafc;
                border: 1px solid rgba(148, 163, 184, 0.4);
                border-radius: 18px;
                box-shadow: 0 18px 50px rgba(0, 0, 0, 0.35);
                font-family: Inter, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
                overflow: hidden;
            }
            #pilot-measurement-panel.pilot-collapsed .pilot-body {
                display: none;
            }
            .pilot-header {
                display: flex;
                align-items: center;
                justify-content: space-between;
                padding: 12px 14px;
                background: linear-gradient(135deg, #0f3b5f 0%, #0ea5e9 100%);
                cursor: move;
                user-select: none;
                touch-action: none;
            }
            .pilot-title {
                font-size: 13px;
                font-weight: 800;
                letter-spacing: 0.04em;
                text-transform: uppercase;
            }
            .pilot-toggle {
                background: rgba(255, 255, 255, 0.18);
                color: #fff;
                border: 0;
                border-radius: 999px;
                padding: 4px 9px;
                cursor: pointer;
                font-weight: 800;
            }
            #pilot-measurement-panel.pilot-dragging {
                box-shadow: 0 22px 60px rgba(0, 0, 0, 0.45);
            }
            .pilot-body {
                padding: 12px;
            }
            .pilot-row {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 8px;
                margin-bottom: 8px;
            }
            .pilot-field {
                display: flex;
                flex-direction: column;
                gap: 4px;
                font-size: 11px;
                color: #cbd5e1;
                font-weight: 700;
                text-transform: uppercase;
            }
            .pilot-field select {
                width: 100%;
                border: 1px solid rgba(148, 163, 184, 0.5);
                border-radius: 10px;
                background: #020617;
                color: #f8fafc;
                padding: 8px;
                font-size: 13px;
                text-transform: none;
            }
            .pilot-timer {
                font-size: 36px;
                font-weight: 900;
                line-height: 1;
                letter-spacing: 0.03em;
                padding: 10px 0 6px;
            }
            .pilot-status {
                display: flex;
                justify-content: space-between;
                gap: 8px;
                font-size: 12px;
                color: #cbd5e1;
                margin-bottom: 10px;
            }
            .pilot-metrics {
                display: grid;
                grid-template-columns: repeat(3, 1fr);
                gap: 8px;
                margin-bottom: 10px;
            }
            .pilot-metric {
                background: rgba(15, 23, 42, 0.8);
                border: 1px solid rgba(148, 163, 184, 0.25);
                border-radius: 12px;
                padding: 8px;
            }
            .pilot-metric-label {
                color: #94a3b8;
                font-size: 10px;
                text-transform: uppercase;
                font-weight: 800;
            }
            .pilot-metric-value {
                font-size: 20px;
                font-weight: 900;
                color: #ffffff;
            }
            .pilot-actions {
                display: grid;
                grid-template-columns: repeat(2, 1fr);
                gap: 8px;
                margin-bottom: 8px;
            }
            .pilot-actions button,
            .pilot-small-actions button {
                border: 0;
                border-radius: 11px;
                padding: 9px 10px;
                cursor: pointer;
                font-weight: 800;
                font-size: 12px;
            }
            .pilot-primary { background: #22c55e; color: #052e16; }
            .pilot-stop { background: #fbbf24; color: #422006; }
            .pilot-muted { background: #334155; color: #f8fafc; }
            .pilot-danger { background: #ef4444; color: #fff; }
            .pilot-small-actions {
                display: grid;
                grid-template-columns: repeat(4, 1fr);
                gap: 6px;
                margin-bottom: 8px;
            }
            .pilot-checks {
                display: grid;
                grid-template-columns: repeat(4, 1fr);
                gap: 6px;
                font-size: 11px;
                color: #e2e8f0;
                margin-bottom: 8px;
            }
            .pilot-checks label {
                display: flex;
                align-items: center;
                gap: 4px;
                background: rgba(30, 41, 59, 0.8);
                border-radius: 10px;
                padding: 7px;
            }
            .pilot-last {
                color: #cbd5e1;
                font-size: 11px;
                line-height: 1.35;
                border-top: 1px solid rgba(148, 163, 184, 0.25);
                padding-top: 8px;
            }
        `;
        document.head.appendChild(style);
    }

    function createPanel() {
        const panel = document.createElement('div');
        panel.id = 'pilot-measurement-panel';
        panel.innerHTML = `
            <div class="pilot-header">
                <div class="pilot-title">Pilot Measurement</div>
                <button class="pilot-toggle" id="pilot-toggle-panel">-</button>
            </div>
            <div class="pilot-body">
                <div class="pilot-row">
                    <label class="pilot-field">
                        Condition
                        <select id="pilot-condition">
                            <option value="A">A - Manual</option>
                            <option value="B">B - Assistant</option>
                        </select>
                    </label>
                    <label class="pilot-field">
                        Task
                        <select id="pilot-task">
                            ${TASKS.map(([id, label]) => `<option value="${id}">${id} - ${label}</option>`).join('')}
                        </select>
                    </label>
                </div>
                <div class="pilot-timer" id="pilot-timer">00:00.0</div>
                <div class="pilot-status">
                    <span id="pilot-running-state">Idle</span>
                    <span id="pilot-record-count">0 records</span>
                </div>
                <div class="pilot-metrics">
                    <div class="pilot-metric"><div class="pilot-metric-label">Clicks</div><div class="pilot-metric-value" id="pilot-clicks">0</div></div>
                    <div class="pilot-metric"><div class="pilot-metric-label">Screens</div><div class="pilot-metric-value" id="pilot-screens">0</div></div>
                    <div class="pilot-metric"><div class="pilot-metric-label">Success</div><div class="pilot-metric-value" id="pilot-success">1</div></div>
                </div>
                <div class="pilot-actions">
                    <button class="pilot-primary" id="pilot-start">Start Task</button>
                    <button class="pilot-stop" id="pilot-answer-found">Answer Found</button>
                </div>
                <div class="pilot-small-actions">
                    <button class="pilot-muted" id="pilot-add-click">+Click</button>
                    <button class="pilot-muted" id="pilot-add-screen">+Screen</button>
                    <button class="pilot-muted" id="pilot-copy">Copy CSV</button>
                    <button class="pilot-danger" id="pilot-reset">Reset</button>
                </div>
                <div class="pilot-small-actions" style="grid-template-columns: 1fr 1fr;">
                    <button class="pilot-muted" id="pilot-popout">Open Control Window</button>
                    <button class="pilot-danger" id="pilot-reset-all">Reset All</button>
                </div>
                <div class="pilot-checks">
                    <label><input type="checkbox" id="pilot-expert">Expert</label>
                    <label><input type="checkbox" id="pilot-reasoning">Manual reasoning</label>
                    <label><input type="checkbox" id="pilot-success-check" checked>Success</label>
                    <label><input type="checkbox" id="pilot-auto-stop" checked>Auto-stop</label>
                </div>
                <div class="pilot-last" id="pilot-last">Use Start Task for Condition A. Assistant prompts auto-start in Condition B; disable Auto-stop for multi-prompt tasks.</div>
            </div>
        `;
        document.body.appendChild(panel);
    }

    function syncInputs() {
        const condition = document.getElementById('pilot-condition');
        const task = document.getElementById('pilot-task');
        const expert = document.getElementById('pilot-expert');
        const reasoning = document.getElementById('pilot-reasoning');
        const success = document.getElementById('pilot-success-check');
        const autoStop = document.getElementById('pilot-auto-stop');

        if (condition) condition.value = state.condition;
        if (task) task.value = state.taskId;
        if (expert) expert.checked = !!state.expertHelp;
        if (reasoning) reasoning.checked = !!state.manualReasoning;
        if (success) success.checked = !!state.success;
        if (autoStop) autoStop.checked = state.autoStopAssistant !== false;
    }

    function render() {
        const timer = document.getElementById('pilot-timer');
        if (!timer) {
            return;
        }
        timer.textContent = formatTime(elapsedMs());
        document.getElementById('pilot-clicks').textContent = state.clicks;
        document.getElementById('pilot-screens').textContent = state.screens;
        document.getElementById('pilot-success').textContent = state.success ? '1' : '0';
        document.getElementById('pilot-running-state').textContent = state.running ? 'Running' : 'Idle';
        document.getElementById('pilot-record-count').textContent = `${state.records.length} records`;
        syncInputs();
    }

    function setLast(message) {
        const last = document.getElementById('pilot-last');
        if (last) {
            last.textContent = message;
        }
    }

    function clamp(value, min, max) {
        return Math.min(Math.max(value, min), max);
    }

    function applyPanelPosition() {
        const panel = document.getElementById('pilot-measurement-panel');
        if (!panel) {
            return;
        }

        if (!state.panelPosition || !Number.isFinite(state.panelPosition.left) || !Number.isFinite(state.panelPosition.top)) {
            panel.style.left = '18px';
            panel.style.bottom = '18px';
            panel.style.top = 'auto';
            return;
        }

        const maxLeft = Math.max(window.innerWidth - panel.offsetWidth - 12, 12);
        const maxTop = Math.max(window.innerHeight - panel.offsetHeight - 12, 12);
        const left = clamp(state.panelPosition.left, 12, maxLeft);
        const top = clamp(state.panelPosition.top, 12, maxTop);

        state.panelPosition = { left, top };
        panel.style.left = `${left}px`;
        panel.style.top = `${top}px`;
        panel.style.bottom = 'auto';
    }

    function startTask(source) {
        state.elapsedMs = 0;
        state.startedAt = now();
        state.running = true;
        state.clicks = 0;
        state.screens = 1;
        state.lastUrl = currentUrl();
        state.expertHelp = false;
        state.manualReasoning = state.condition === 'A';
        state.success = true;
        saveState();
        setLast(`Started ${taskLabel()} (${source || 'manual'}).`);
        render();
    }

    function stopTask(reason) {
        if (!state.running) {
            return;
        }
        state.elapsedMs = elapsedMs();
        state.startedAt = null;
        state.running = false;
        const record = currentRecord(reason);
        state.records.push(record);
        saveState();
        setLast(`Saved ${record.condition}-${record.taskId}: ${record.elapsedSec}s, ${record.clicks} clicks, ${record.screens} screens.`);
        render();
    }

    function resetCurrent() {
        state.running = false;
        state.startedAt = null;
        state.elapsedMs = 0;
        state.clicks = 0;
        state.screens = 0;
        state.lastUrl = null;
        saveState();
        setLast('Current task counters reset.');
        render();
    }

    function resetAll() {
        if (!window.confirm('Clear all saved pilot measurement records and counters?')) {
            return;
        }

        const preservedCondition = state.condition;
        const preservedTaskId = state.taskId;
        const preservedAutoStop = state.autoStopAssistant;
        const preservedPanelPosition = state.panelPosition;

        state = {
            ...blankState(),
            condition: preservedCondition,
            taskId: preservedTaskId,
            manualReasoning: preservedCondition === 'A',
            success: false,
            autoStopAssistant: preservedAutoStop !== false,
            panelPosition: preservedPanelPosition
        };
        saveState();
        setLast('All pilot measurement records and counters cleared.');
        render();
    }

    function bindDragging() {
        const panel = document.getElementById('pilot-measurement-panel');
        const header = panel?.querySelector('.pilot-header');
        if (!panel || !header) {
            return;
        }

        let dragState = null;

        header.addEventListener('pointerdown', event => {
            if (event.target.closest('button')) {
                return;
            }

            const rect = panel.getBoundingClientRect();
            dragState = {
                pointerId: event.pointerId,
                offsetX: event.clientX - rect.left,
                offsetY: event.clientY - rect.top
            };
            panel.classList.add('pilot-dragging');
            header.setPointerCapture(event.pointerId);
            event.preventDefault();
        });

        header.addEventListener('pointermove', event => {
            if (!dragState || event.pointerId !== dragState.pointerId) {
                return;
            }

            const maxLeft = Math.max(window.innerWidth - panel.offsetWidth - 12, 12);
            const maxTop = Math.max(window.innerHeight - panel.offsetHeight - 12, 12);
            const left = clamp(event.clientX - dragState.offsetX, 12, maxLeft);
            const top = clamp(event.clientY - dragState.offsetY, 12, maxTop);

            state.panelPosition = { left, top };
            panel.style.left = `${left}px`;
            panel.style.top = `${top}px`;
            panel.style.bottom = 'auto';
        });

        const stopDragging = event => {
            if (!dragState || event.pointerId !== dragState.pointerId) {
                return;
            }

            dragState = null;
            panel.classList.remove('pilot-dragging');
            saveState();
        };

        header.addEventListener('pointerup', stopDragging);
        header.addEventListener('pointercancel', stopDragging);
        window.addEventListener('resize', () => {
            if (!state.panelPosition) {
                return;
            }
            applyPanelPosition();
            saveState();
        });
    }

    function bindPanelEvents() {
        document.getElementById('pilot-toggle-panel').addEventListener('click', () => {
            document.getElementById('pilot-measurement-panel').classList.toggle('pilot-collapsed');
        });

        document.getElementById('pilot-condition').addEventListener('change', (event) => {
            state.condition = event.target.value;
            state.manualReasoning = state.condition === 'A';
            saveState();
            render();
        });

        document.getElementById('pilot-task').addEventListener('change', (event) => {
            state.taskId = event.target.value;
            resetCurrent();
        });

        document.getElementById('pilot-expert').addEventListener('change', event => {
            state.expertHelp = event.target.checked;
            saveState();
            render();
        });

        document.getElementById('pilot-reasoning').addEventListener('change', event => {
            state.manualReasoning = event.target.checked;
            saveState();
            render();
        });

        document.getElementById('pilot-success-check').addEventListener('change', event => {
            state.success = event.target.checked;
            saveState();
            render();
        });

        document.getElementById('pilot-auto-stop').addEventListener('change', event => {
            state.autoStopAssistant = event.target.checked;
            saveState();
            setLast(state.autoStopAssistant
                ? 'Assistant answers will stop the active task automatically.'
                : 'Auto-stop disabled. Click Answer Found after the final assistant answer for this task.'
            );
            render();
        });

        document.getElementById('pilot-start').addEventListener('click', () => startTask('manual button'));
        document.getElementById('pilot-answer-found').addEventListener('click', () => stopTask('answer_found'));
        document.getElementById('pilot-add-click').addEventListener('click', () => {
            state.clicks += 1;
            saveState();
            render();
        });
        document.getElementById('pilot-add-screen').addEventListener('click', () => {
            state.screens += 1;
            saveState();
            render();
        });
        document.getElementById('pilot-reset').addEventListener('click', resetCurrent);
        document.getElementById('pilot-reset-all').addEventListener('click', resetAll);
        document.getElementById('pilot-copy').addEventListener('click', async () => {
            const csv = recordsCsv();
            try {
                await navigator.clipboard.writeText(csv);
                setLast('CSV copied to clipboard.');
            } catch (_) {
                window.prompt('Copy CSV:', csv);
            }
        });
        document.getElementById('pilot-popout').addEventListener('click', () => {
            window.open('/pilot-measurement-control.html', 'humanenerdiaPilotRecorder', 'width=430,height=720,resizable=yes,scrollbars=no');
        });
    }

    function countScreenIfNeeded() {
        if (!state.running) {
            return;
        }
        const url = currentUrl();
        if (state.lastUrl && state.lastUrl !== url) {
            state.screens += 1;
        }
        state.lastUrl = url;
        saveState();
        render();
    }

    function bindCounters() {
        document.addEventListener('click', event => {
            if (!state.running) {
                return;
            }
            if (event.target.closest('#pilot-measurement-panel')) {
                return;
            }
            state.clicks += 1;
            saveState();
            render();
        }, true);

        ['pushState', 'replaceState'].forEach(method => {
            const original = history[method];
            history[method] = function () {
                const result = original.apply(this, arguments);
                window.setTimeout(countScreenIfNeeded, 0);
                return result;
            };
        });

        window.addEventListener('popstate', countScreenIfNeeded);
        window.addEventListener('hashchange', countScreenIfNeeded);
        countScreenIfNeeded();
    }

    function bindAssistantEvents() {
        window.addEventListener('humanenerdia:pilot:assistant-query-start', event => {
            if (state.condition !== 'B') {
                return;
            }
            if (!state.running) {
                startTask(event.detail?.source || 'assistant');
            }
        });

        window.addEventListener('humanenerdia:pilot:assistant-response-complete', event => {
            if (state.condition !== 'B' || !state.running) {
                return;
            }
            state.success = event.detail?.success !== false;
            saveState();
            if (state.autoStopAssistant === false) {
                setLast('Assistant answer visible. Auto-stop is off; continue the task or click Answer Found after the final answer.');
                render();
                return;
            }
            stopTask(event.detail?.source ? `${event.detail.source}_answer_visible` : 'assistant_answer_visible');
        });
    }

    function exposeApi() {
        window.HumanEnerDIAPilot = {
            start: startTask,
            stop: stopTask,
            reset: resetCurrent,
            resetAll,
            setAutoStop: value => {
                state.autoStopAssistant = !!value;
                saveState();
                render();
            },
            exportCsv: recordsCsv,
            state: () => ({ ...state, elapsedMs: elapsedMs() })
        };
    }

    function init() {
        createStyles();
        createPanel();
        applyPanelPosition();
        bindPanelEvents();
        bindDragging();
        bindCounters();
        bindAssistantEvents();
        exposeApi();
        render();
        timerInterval = window.setInterval(render, 100);
        window.addEventListener('beforeunload', () => {
            if (timerInterval) {
                window.clearInterval(timerInterval);
            }
            saveState();
        });
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
