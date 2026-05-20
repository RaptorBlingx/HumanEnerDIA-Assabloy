(function () {
    'use strict';

    const STORAGE_KEY = 'humanenerdia_kpi_card_generator_v1';
    const CARD_WIDTH = 1920;
    const CARD_HEIGHT = 1080;

    const TASKS = [
        {
            id: 'O1',
            persona: 'Operational user',
            module: 'Monitoring',
            title: 'Factory Overview And Top Consumers',
            task: 'Get a factory overview and identify the top 3 energy consumers.',
            target: 30,
            targetLabel: '30% operational effort reduction'
        },
        {
            id: 'O2',
            persona: 'Operational user',
            module: 'Monitoring',
            title: "Compressor-1 Status And Today's Energy",
            task: "Check the status and today's energy of Compressor-1.",
            target: 30,
            targetLabel: '30% operational effort reduction'
        },
        {
            id: 'O3',
            persona: 'Operational user',
            module: 'Documentation',
            title: 'ISO 50001 And Energy Baseline',
            task: 'Understand what ISO 50001 is and what an energy baseline means.',
            target: 30,
            targetLabel: '30% operational effort reduction'
        },
        {
            id: 'O4',
            persona: 'Operational user',
            module: 'Documentation',
            title: 'Anomaly Or Efficiency Procedure',
            task: 'Find policy and procedure guidance for responding to an anomaly or efficiency issue.',
            target: 30,
            targetLabel: '30% operational effort reduction'
        },
        {
            id: 'T1',
            persona: 'Technical user',
            module: 'Monitoring',
            title: 'Review Anomalies',
            task: 'Review anomalies and identify the issue requiring attention.',
            target: 25,
            targetLabel: '25% technical intervention reduction'
        },
        {
            id: 'T2',
            persona: 'Technical user',
            module: 'Analyses',
            title: 'Baseline Analysis And Recommendations',
            task: 'Analyze Compressor-1 against baseline, check forecast context, and retrieve recommendations.',
            target: 25,
            targetLabel: '25% technical intervention reduction'
        },
        {
            id: 'T3',
            persona: 'Technical user',
            module: 'Analyses',
            title: 'KPI And EnPI Status',
            task: 'Retrieve factory KPI and EnPI status for 2026-Q1.',
            target: 25,
            targetLabel: '25% technical intervention reduction'
        },
        {
            id: 'T4',
            persona: 'Technical user',
            module: 'Analyses / Documentation',
            title: 'April 2026 Report',
            task: 'Generate the April 2026 monthly report and summarize the result.',
            target: 25,
            targetLabel: '25% technical intervention reduction'
        }
    ];

    const MODULE_TARGETS = ['Monitoring', 'Analyses', 'Documentation'];

    const elements = {};
    let state = loadState();

    document.addEventListener('DOMContentLoaded', init);

    function blankRecord() {
        return {
            a: {
                time: '',
                clicks: '',
                screens: '',
                expert: false,
                manual: true,
                success: true
            },
            b: {
                time: '',
                clicks: '',
                screens: '',
                expert: false,
                manual: false,
                success: true
            }
        };
    }

    function blankState() {
        return {
            mode: 'task',
            selectedTaskId: 'O1',
            records: Object.fromEntries(TASKS.map(task => [task.id, blankRecord()]))
        };
    }

    function loadState() {
        try {
            const parsed = JSON.parse(localStorage.getItem(STORAGE_KEY) || '{}');
            const base = blankState();
            return {
                ...base,
                ...parsed,
                records: {
                    ...base.records,
                    ...(parsed.records || {})
                }
            };
        } catch (_) {
            return blankState();
        }
    }

    function saveState() {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
    }

    function init() {
        [
            'task-select', 'task-detail', 'a-time', 'a-clicks', 'a-screens',
            'a-expert', 'a-manual', 'a-success', 'b-time', 'b-clicks',
            'b-screens', 'b-expert', 'b-manual', 'b-success', 'save-task',
            'export-card', 'copy-text', 'download-json', 'import-json',
            'reset-task', 'reset-all', 'task-list', 'card-canvas',
            'overlay-text', 'selected-kpi', 'current-reduction', 'target-status'
        ].forEach(id => {
            elements[toCamel(id)] = document.getElementById(id);
        });

        TASKS.forEach(task => {
            const option = document.createElement('option');
            option.value = task.id;
            option.textContent = `${task.id} - ${task.title}`;
            elements.taskSelect.append(option);
        });

        document.querySelectorAll('[data-mode]').forEach(button => {
            button.addEventListener('click', () => {
                state.mode = button.dataset.mode;
                saveState();
                render();
            });
        });

        elements.taskSelect.addEventListener('change', () => {
            state.selectedTaskId = elements.taskSelect.value;
            saveState();
            render();
        });

        [
            elements.aTime, elements.aClicks, elements.aScreens,
            elements.bTime, elements.bClicks, elements.bScreens
        ].forEach(input => {
            input.addEventListener('input', () => {
                collectForm();
                renderCalculatedOnly();
            });
        });

        [
            elements.aExpert, elements.aManual, elements.aSuccess,
            elements.bExpert, elements.bManual, elements.bSuccess
        ].forEach(input => {
            input.addEventListener('change', () => {
                collectForm();
                renderCalculatedOnly();
            });
        });

        elements.saveTask.addEventListener('click', () => {
            collectForm();
            saveState();
            flashButton(elements.saveTask, 'Saved');
            render();
        });

        elements.exportCard.addEventListener('click', exportPng);
        elements.copyText.addEventListener('click', copyOverlayText);
        elements.downloadJson.addEventListener('click', downloadJson);
        elements.importJson.addEventListener('change', importJson);
        elements.resetTask.addEventListener('click', resetTask);
        elements.resetAll.addEventListener('click', resetAll);

        render();
    }

    function toCamel(value) {
        return value.replace(/-([a-z])/g, (_, letter) => letter.toUpperCase());
    }

    function taskById(id) {
        return TASKS.find(task => task.id === id) || TASKS[0];
    }

    function currentTask() {
        return taskById(state.selectedTaskId);
    }

    function currentRecord() {
        const id = state.selectedTaskId;
        if (!state.records[id]) {
            state.records[id] = blankRecord();
        }
        return state.records[id];
    }

    function collectForm() {
        const record = currentRecord();
        record.a.time = elements.aTime.value;
        record.a.clicks = elements.aClicks.value;
        record.a.screens = elements.aScreens.value;
        record.a.expert = elements.aExpert.checked;
        record.a.manual = elements.aManual.checked;
        record.a.success = elements.aSuccess.checked;
        record.b.time = elements.bTime.value;
        record.b.clicks = elements.bClicks.value;
        record.b.screens = elements.bScreens.value;
        record.b.expert = elements.bExpert.checked;
        record.b.manual = elements.bManual.checked;
        record.b.success = elements.bSuccess.checked;
        saveState();
    }

    function fillForm() {
        const record = currentRecord();
        elements.aTime.value = record.a.time;
        elements.aClicks.value = record.a.clicks;
        elements.aScreens.value = record.a.screens;
        elements.aExpert.checked = Boolean(record.a.expert);
        elements.aManual.checked = Boolean(record.a.manual);
        elements.aSuccess.checked = Boolean(record.a.success);
        elements.bTime.value = record.b.time;
        elements.bClicks.value = record.b.clicks;
        elements.bScreens.value = record.b.screens;
        elements.bExpert.checked = Boolean(record.b.expert);
        elements.bManual.checked = Boolean(record.b.manual);
        elements.bSuccess.checked = Boolean(record.b.success);
    }

    function parseNumber(value) {
        if (value === '' || value === null || typeof value === 'undefined') {
            return null;
        }
        const parsed = Number(value);
        return Number.isFinite(parsed) ? parsed : null;
    }

    function reduction(aValue, bValue) {
        const a = parseNumber(aValue);
        const b = parseNumber(bValue);
        if (a === null || b === null || a <= 0) {
            return null;
        }
        return ((a - b) / a) * 100;
    }

    function average(values) {
        const valid = values.filter(value => Number.isFinite(value));
        if (!valid.length) {
            return null;
        }
        return valid.reduce((sum, value) => sum + value, 0) / valid.length;
    }

    function sum(values) {
        return values.reduce((total, value) => total + (parseNumber(value) || 0), 0);
    }

    function taskMetrics(taskId) {
        const task = taskById(taskId);
        const record = state.records[task.id] || blankRecord();
        const timeReduction = reduction(record.a.time, record.b.time);
        const clickReduction = reduction(record.a.clicks, record.b.clicks);
        const screenReduction = reduction(record.a.screens, record.b.screens);
        const interactionReduction = average([clickReduction, screenReduction]);
        const effortReduction = average([timeReduction, interactionReduction]);
        const hasPair = parseNumber(record.a.time) !== null && parseNumber(record.b.time) !== null;

        return {
            task,
            record,
            hasPair,
            timeReduction,
            clickReduction,
            screenReduction,
            interactionReduction,
            effortReduction,
            met: Number.isFinite(effortReduction) && effortReduction >= task.target
        };
    }

    function groupMetrics(kind) {
        const ids = TASKS
            .filter(task => kind === 'operational' ? task.id.startsWith('O') : task.id.startsWith('T'))
            .map(task => task.id);
        const metrics = ids.map(taskMetrics).filter(metric => metric.hasPair);
        const target = kind === 'operational' ? 30 : 25;

        return {
            kind,
            target,
            completed: metrics.length,
            total: ids.length,
            timeReduction: average(metrics.map(metric => metric.timeReduction)),
            interactionReduction: average(metrics.map(metric => metric.interactionReduction)),
            effortReduction: average(metrics.map(metric => metric.effortReduction)),
            aTime: sum(metrics.map(metric => metric.record.a.time)),
            bTime: sum(metrics.map(metric => metric.record.b.time)),
            aClicks: sum(metrics.map(metric => metric.record.a.clicks)),
            bClicks: sum(metrics.map(metric => metric.record.b.clicks)),
            aScreens: sum(metrics.map(metric => metric.record.a.screens)),
            bScreens: sum(metrics.map(metric => metric.record.b.screens)),
            aExpert: metrics.filter(metric => metric.record.a.expert).length,
            bExpert: metrics.filter(metric => metric.record.b.expert).length,
            aManual: metrics.filter(metric => metric.record.a.manual).length,
            bManual: metrics.filter(metric => metric.record.b.manual).length,
            aSuccess: metrics.filter(metric => metric.record.a.success).length,
            bSuccess: metrics.filter(metric => metric.record.b.success).length
        };
    }

    function coveredModules() {
        const covered = new Set();
        TASKS.forEach(task => {
            const metric = taskMetrics(task.id);
            if (!metric.hasPair || !metric.record.b.success) {
                return;
            }
            task.module.split('/').map(part => part.trim()).forEach(moduleName => {
                if (MODULE_TARGETS.includes(moduleName)) {
                    covered.add(moduleName);
                }
            });
        });
        return covered;
    }

    function finalMetrics() {
        const operational = groupMetrics('operational');
        const technical = groupMetrics('technical');
        const modules = coveredModules();
        return {
            operational,
            technical,
            modules,
            allTargetsMet:
                Number.isFinite(operational.effortReduction) &&
                Number.isFinite(technical.effortReduction) &&
                operational.effortReduction >= operational.target &&
                technical.effortReduction >= technical.target &&
                MODULE_TARGETS.every(moduleName => modules.has(moduleName))
        };
    }

    function render() {
        document.querySelectorAll('[data-mode]').forEach(button => {
            button.classList.toggle('active', button.dataset.mode === state.mode);
        });

        elements.taskSelect.value = state.selectedTaskId;
        elements.taskSelect.disabled = state.mode !== 'task';
        fillForm();
        renderTaskDetail();
        renderTaskList();
        renderCalculatedOnly();
    }

    function renderCalculatedOnly() {
        const task = currentTask();
        const metric = taskMetrics(task.id);
        const mode = state.mode;

        if (mode === 'task') {
            elements.selectedKpi.textContent = task.targetLabel;
            elements.currentReduction.textContent = formatPercent(metric.effortReduction, 'Waiting for values');
            elements.targetStatus.textContent = metric.hasPair ? (metric.met ? 'Target met' : 'Below target') : 'Not calculated';
            elements.overlayText.value = taskOverlayText(metric);
            drawTaskCard(metric);
            return;
        }

        if (mode === 'operational' || mode === 'technical') {
            const group = groupMetrics(mode);
            elements.selectedKpi.textContent = mode === 'operational'
                ? 'Operational 30% effort target'
                : 'Technical 25% intervention target';
            elements.currentReduction.textContent = formatPercent(group.effortReduction, 'Waiting for values');
            elements.targetStatus.textContent = group.completed ? (group.effortReduction >= group.target ? 'Target met' : 'Below target') : 'Not calculated';
            elements.overlayText.value = groupOverlayText(group);
            drawGroupCard(group);
            return;
        }

        const final = finalMetrics();
        elements.selectedKpi.textContent = 'Final proposal KPI evidence';
        elements.currentReduction.textContent = final.allTargetsMet ? 'All targets met' : 'Targets incomplete';
        elements.targetStatus.textContent = `${final.modules.size}/3 DIA modules covered`;
        elements.overlayText.value = finalOverlayText(final);
        drawFinalCard(final);
    }

    function renderTaskDetail() {
        const task = currentTask();
        elements.taskDetail.innerHTML = `
            <p class="mini-label">${escapeHtml(task.persona)} | ${escapeHtml(task.module)}</p>
            <h2>${escapeHtml(task.id)} - ${escapeHtml(task.title)}</h2>
            <p>${escapeHtml(task.task)}</p>
            <p><strong>Target:</strong> ${escapeHtml(task.targetLabel)}</p>
        `;
    }

    function renderTaskList() {
        elements.taskList.innerHTML = '';
        TASKS.forEach(task => {
            const metric = taskMetrics(task.id);
            const button = document.createElement('button');
            button.type = 'button';
            button.className = 'task-pill';
            button.dataset.done = metric.hasPair ? 'true' : 'false';
            button.dataset.selected = task.id === state.selectedTaskId ? 'true' : 'false';
            button.innerHTML = `
                <span>${task.id}</span>
                <strong>${metric.hasPair ? formatPercent(metric.effortReduction, '0%') : 'empty'}</strong>
            `;
            button.addEventListener('click', () => {
                state.mode = 'task';
                state.selectedTaskId = task.id;
                saveState();
                render();
            });
            elements.taskList.append(button);
        });
    }

    function formatNumber(value, fallback = '-') {
        const parsed = parseNumber(value);
        if (parsed === null) {
            return fallback;
        }
        return Number.isInteger(parsed) ? String(parsed) : parsed.toFixed(1);
    }

    function formatPercent(value, fallback = '-') {
        if (!Number.isFinite(value)) {
            return fallback;
        }
        return `${value.toFixed(1)}%`;
    }

    function taskOverlayText(metric) {
        const { task, record } = metric;
        return [
            `Task ${task.id} comparison: ${task.title}.`,
            `Time: A ${formatNumber(record.a.time)} sec -> B ${formatNumber(record.b.time)} sec (${formatPercent(metric.timeReduction, 'not calculated')} reduction).`,
            `Clicks/screens: A ${formatNumber(record.a.clicks)}/${formatNumber(record.a.screens)} -> B ${formatNumber(record.b.clicks)}/${formatNumber(record.b.screens)}.`,
            `Expert help: A ${flag(record.a.expert)} | B ${flag(record.b.expert)}. Manual reasoning: A ${flag(record.a.manual)} | B ${flag(record.b.manual)}. Success: A ${flag(record.a.success)} | B ${flag(record.b.success)}.`,
            `Measured effort reduction: ${formatPercent(metric.effortReduction, 'not calculated')}; target: ${task.targetLabel}.`
        ].join('\n');
    }

    function groupOverlayText(group) {
        const label = group.kind === 'operational' ? 'Operational user tasks' : 'Technical user tasks';
        return [
            `${label} subtotal: ${group.completed}/${group.total} tasks measured.`,
            `Combined time: A ${formatNumber(group.aTime)} sec -> B ${formatNumber(group.bTime)} sec.`,
            `Combined clicks/screens: A ${formatNumber(group.aClicks)}/${formatNumber(group.aScreens)} -> B ${formatNumber(group.bClicks)}/${formatNumber(group.bScreens)}.`,
            `Average measured effort reduction: ${formatPercent(group.effortReduction, 'not calculated')}; target: ${group.target}%.`,
            `Expert help: A ${group.aExpert} | B ${group.bExpert}. Manual reasoning: A ${group.aManual} | B ${group.bManual}. Success: A ${group.aSuccess}/${group.completed} | B ${group.bSuccess}/${group.completed}.`
        ].join('\n');
    }

    function finalOverlayText(final) {
        const moduleText = MODULE_TARGETS.map(moduleName => `${moduleName}: ${final.modules.has(moduleName) ? 'covered' : 'missing'}`).join(', ');
        return [
            'Final simulated pilot KPI summary.',
            `Operational effort reduction: ${formatPercent(final.operational.effortReduction, 'not calculated')} against 30% target.`,
            `Technical intervention/effort reduction: ${formatPercent(final.technical.effortReduction, 'not calculated')} against 25% target.`,
            `DIA module evidence: ${moduleText}.`,
            final.allTargetsMet ? 'Conclusion: simulated pilot evidence meets the proposal KPI targets.' : 'Conclusion: one or more KPI targets still need complete measured values.'
        ].join('\n');
    }

    function flag(value) {
        return value ? '1' : '0';
    }

    function drawTaskCard(metric) {
        const ctx = canvasContext();
        const { task, record } = metric;
        drawBackground(ctx);
        drawHeader(ctx, `Task ${task.id} Comparison`, task.persona, task.module);
        drawMainTitle(ctx, task.title, task.task);

        drawConditionPanel(ctx, 110, 370, 'Condition A', 'Manual path', record.a, '#ffcc66', 'left');
        drawConditionPanel(ctx, 1040, 370, 'Condition B', 'OVOS / Chatbot', record.b, '#35e0a1', 'right');

        drawReductionBadge(ctx, 690, 570, metric.effortReduction, task.target, metric.met);

        drawBottomEvidence(ctx, [
            ['Time reduction', formatPercent(metric.timeReduction, 'n/a')],
            ['Click reduction', formatPercent(metric.clickReduction, 'n/a')],
            ['Screen reduction', formatPercent(metric.screenReduction, 'n/a')],
            ['Measured effort', formatPercent(metric.effortReduction, 'n/a')],
            ['Target', task.targetLabel],
            ['Status', metric.hasPair ? (metric.met ? 'TARGET MET' : 'BELOW TARGET') : 'WAITING FOR VALUES']
        ]);
    }

    function drawGroupCard(group) {
        const ctx = canvasContext();
        const isOperational = group.kind === 'operational';
        const title = isOperational ? 'Operational User Subtotal' : 'Technical User Subtotal';
        const subtitle = isOperational
            ? 'Proposal KPI: 30% reduction in operational energy-management effort'
            : 'Proposal KPI: 25% reduction in technical intervention / effort';

        drawBackground(ctx);
        drawHeader(ctx, title, `${group.completed}/${group.total} tasks measured`, isOperational ? 'Operational KPI' : 'Technical KPI');
        drawMainTitle(ctx, title, subtitle);

        drawBigMetric(ctx, 110, 380, 500, 250, 'Average Effort Reduction', formatPercent(group.effortReduction, 'n/a'), `Target: ${group.target}%`);
        drawBigMetric(ctx, 710, 380, 500, 250, 'Time', `${formatNumber(group.aTime)}s -> ${formatNumber(group.bTime)}s`, formatPercent(group.timeReduction, 'n/a'));
        drawBigMetric(ctx, 1310, 380, 500, 250, 'Clicks / Screens', `${formatNumber(group.aClicks)}/${formatNumber(group.aScreens)} -> ${formatNumber(group.bClicks)}/${formatNumber(group.bScreens)}`, formatPercent(group.interactionReduction, 'n/a'));

        drawBottomEvidence(ctx, [
            ['Expert help', `A ${group.aExpert} | B ${group.bExpert}`],
            ['Manual reasoning', `A ${group.aManual} | B ${group.bManual}`],
            ['Success', `A ${group.aSuccess}/${group.completed} | B ${group.bSuccess}/${group.completed}`],
            ['Status', group.effortReduction >= group.target ? 'TARGET MET' : 'BELOW TARGET']
        ]);
    }

    function drawFinalCard(final) {
        const ctx = canvasContext();
        drawBackground(ctx);
        drawHeader(ctx, 'Final KPI Evidence Summary', 'Simulated Romanian Pilot Factory', 'WASABI / HumanEnerDIA');
        drawMainTitle(ctx, 'Proposal KPI Results', 'A/B comparison using the same personas, tasks, and measured task-performance criteria.');

        drawBigMetric(ctx, 110, 380, 500, 250, 'Operational Effort', formatPercent(final.operational.effortReduction, 'n/a'), 'Target: 30%');
        drawBigMetric(ctx, 710, 380, 500, 250, 'Technical Effort', formatPercent(final.technical.effortReduction, 'n/a'), 'Target: 25%');
        drawBigMetric(ctx, 1310, 380, 500, 250, 'DIA Modules', `${final.modules.size}/3`, 'Monitoring, Analyses, Documentation');

        drawBottomEvidence(ctx, [
            ['Operational status', final.operational.effortReduction >= 30 ? 'TARGET MET' : 'BELOW TARGET'],
            ['Technical status', final.technical.effortReduction >= 25 ? 'TARGET MET' : 'BELOW TARGET'],
            ['Module coverage', `${final.modules.size}/3 modules covered`],
            ['Final status', final.allTargetsMet ? 'ALL KPI TARGETS MET' : 'INCOMPLETE KPI EVIDENCE']
        ]);
    }

    function canvasContext() {
        const canvas = elements.cardCanvas;
        const ctx = canvas.getContext('2d');
        ctx.clearRect(0, 0, CARD_WIDTH, CARD_HEIGHT);
        return ctx;
    }

    function drawBackground(ctx) {
        const gradient = ctx.createLinearGradient(0, 0, CARD_WIDTH, CARD_HEIGHT);
        gradient.addColorStop(0, '#071a24');
        gradient.addColorStop(0.45, '#0b3a38');
        gradient.addColorStop(1, '#111827');
        ctx.fillStyle = gradient;
        ctx.fillRect(0, 0, CARD_WIDTH, CARD_HEIGHT);

        ctx.fillStyle = 'rgba(246, 200, 95, 0.12)';
        ctx.beginPath();
        ctx.arc(1640, 150, 420, 0, Math.PI * 2);
        ctx.fill();
        ctx.fillStyle = 'rgba(53, 224, 161, 0.11)';
        ctx.beginPath();
        ctx.arc(250, 860, 360, 0, Math.PI * 2);
        ctx.fill();
    }

    function drawHeader(ctx, title, leftMeta, rightMeta) {
        ctx.fillStyle = 'rgba(255, 255, 255, 0.08)';
        roundedRect(ctx, 80, 70, 1760, 120, 34);
        ctx.fill();

        ctx.fillStyle = '#f8fafc';
        ctx.font = '800 42px Bahnschrift, Aptos, Segoe UI, sans-serif';
        ctx.fillText(title, 120, 145);

        ctx.fillStyle = '#f6c85f';
        ctx.font = '700 26px Bahnschrift, Aptos, Segoe UI, sans-serif';
        ctx.fillText(leftMeta, 1270, 125);
        ctx.fillStyle = '#9ff2d0';
        ctx.fillText(rightMeta, 1270, 160);
    }

    function drawMainTitle(ctx, title, description) {
        ctx.fillStyle = '#ffffff';
        ctx.font = '900 62px Bahnschrift, Aptos, Segoe UI, sans-serif';
        wrapText(ctx, title, 110, 285, 1500, 70, 1);
        ctx.fillStyle = '#dbeafe';
        ctx.font = '500 30px Aptos, Segoe UI, sans-serif';
        wrapText(ctx, description, 112, 335, 1500, 40, 2);
    }

    function drawConditionPanel(ctx, x, y, heading, subheading, values, accent, alignment) {
        const isRightAligned = alignment === 'right';
        const left = x + 42;
        const right = x + 718;

        ctx.fillStyle = 'rgba(255, 255, 255, 0.10)';
        roundedRect(ctx, x, y, 760, 360, 38);
        ctx.fill();

        ctx.strokeStyle = accent;
        ctx.lineWidth = 5;
        roundedRect(ctx, x, y, 760, 360, 38);
        ctx.stroke();

        ctx.fillStyle = accent;
        ctx.font = '800 31px Bahnschrift, Aptos, Segoe UI, sans-serif';
        ctx.textAlign = isRightAligned ? 'right' : 'left';
        ctx.fillText(heading, isRightAligned ? right : left, y + 60);

        ctx.fillStyle = '#d9fff0';
        ctx.font = '600 24px Aptos, Segoe UI, sans-serif';
        ctx.fillText(subheading, isRightAligned ? right : left, y + 96);

        ctx.fillStyle = '#ffffff';
        ctx.font = '900 76px Bahnschrift, Aptos, Segoe UI, sans-serif';
        ctx.fillText(`${formatNumber(values.time)}s`, isRightAligned ? right : left, y + 195);

        ctx.fillStyle = '#dbeafe';
        ctx.font = '700 32px Aptos, Segoe UI, sans-serif';
        if (isRightAligned) {
            ctx.fillText(`${formatNumber(values.clicks)} clicks`, x + 500, y + 260);
            ctx.fillText(`${formatNumber(values.screens)} screens`, right, y + 260);
        } else {
            ctx.fillText(`${formatNumber(values.clicks)} clicks`, left, y + 260);
            ctx.fillText(`${formatNumber(values.screens)} screens`, x + 310, y + 260);
        }

        ctx.fillStyle = '#cbd5e1';
        ctx.font = '600 24px Aptos, Segoe UI, sans-serif';
        if (isRightAligned) {
            ctx.fillText(`Expert ${flag(values.expert)}`, x + 360, y + 318);
            ctx.fillText(`Manual reasoning ${flag(values.manual)}`, x + 585, y + 318);
            ctx.fillText(`Success ${flag(values.success)}`, right, y + 318);
        } else {
            ctx.fillText(`Expert ${flag(values.expert)}  |  Manual reasoning ${flag(values.manual)}  |  Success ${flag(values.success)}`, left, y + 318);
        }
        ctx.textAlign = 'left';
    }

    function drawReductionBadge(ctx, x, y, effortReduction, target, met) {
        const fill = met ? '#35e0a1' : '#f6c85f';
        ctx.fillStyle = fill;
        roundedRect(ctx, x, y, 540, 180, 42);
        ctx.fill();
        ctx.fillStyle = '#06131a';
        ctx.font = '900 74px Bahnschrift, Aptos, Segoe UI, sans-serif';
        centerText(ctx, formatPercent(effortReduction, 'n/a'), x, y + 86, 540);
        ctx.font = '800 28px Bahnschrift, Aptos, Segoe UI, sans-serif';
        centerText(ctx, `Measured effort reduction | Target ${target}%`, x, y + 132, 540);
    }

    function drawBigMetric(ctx, x, y, width, height, label, value, sublabel) {
        ctx.fillStyle = 'rgba(255, 255, 255, 0.10)';
        roundedRect(ctx, x, y, width, height, 38);
        ctx.fill();
        ctx.strokeStyle = 'rgba(255, 255, 255, 0.17)';
        ctx.lineWidth = 3;
        roundedRect(ctx, x, y, width, height, 38);
        ctx.stroke();

        ctx.fillStyle = '#9ff2d0';
        ctx.font = '800 26px Bahnschrift, Aptos, Segoe UI, sans-serif';
        centerText(ctx, label, x, y + 56, width);
        ctx.fillStyle = '#ffffff';
        ctx.font = '900 64px Bahnschrift, Aptos, Segoe UI, sans-serif';
        centerText(ctx, value, x, y + 145, width);
        ctx.fillStyle = '#f6c85f';
        ctx.font = '700 27px Aptos, Segoe UI, sans-serif';
        centerText(ctx, sublabel, x, y + 202, width);
    }

    function drawBottomEvidence(ctx, rows) {
        ctx.fillStyle = 'rgba(0, 0, 0, 0.24)';
        roundedRect(ctx, 90, 800, 1740, 190, 34);
        ctx.fill();

        const columnWidth = 1740 / rows.length;
        rows.forEach(([label, value], index) => {
            const x = 110 + index * columnWidth;
            ctx.fillStyle = '#94a3b8';
            ctx.font = '800 21px Bahnschrift, Aptos, Segoe UI, sans-serif';
            wrapText(ctx, label.toUpperCase(), x, 860, columnWidth - 35, 26, 2);
            ctx.fillStyle = '#ffffff';
            ctx.font = '800 29px Bahnschrift, Aptos, Segoe UI, sans-serif';
            wrapText(ctx, value, x, 920, columnWidth - 35, 34, 2);
        });
    }

    function roundedRect(ctx, x, y, width, height, radius) {
        ctx.beginPath();
        ctx.moveTo(x + radius, y);
        ctx.arcTo(x + width, y, x + width, y + height, radius);
        ctx.arcTo(x + width, y + height, x, y + height, radius);
        ctx.arcTo(x, y + height, x, y, radius);
        ctx.arcTo(x, y, x + width, y, radius);
        ctx.closePath();
    }

    function centerText(ctx, text, x, y, width) {
        const measured = ctx.measureText(text).width;
        ctx.fillText(text, x + (width - measured) / 2, y);
    }

    function wrapText(ctx, text, x, y, maxWidth, lineHeight, maxLines) {
        const words = String(text).split(/\s+/);
        let line = '';
        let lines = 0;

        for (let i = 0; i < words.length; i += 1) {
            const testLine = line ? `${line} ${words[i]}` : words[i];
            if (ctx.measureText(testLine).width > maxWidth && line) {
                ctx.fillText(line, x, y);
                y += lineHeight;
                lines += 1;
                line = words[i];
                if (lines >= maxLines) {
                    return;
                }
            } else {
                line = testLine;
            }
        }

        if (line && lines < maxLines) {
            ctx.fillText(line, x, y);
        }
    }

    function exportPng() {
        const canvas = elements.cardCanvas;
        const filename = state.mode === 'task'
            ? `${state.selectedTaskId}-comparison-card.png`
            : `${state.mode}-kpi-card.png`;

        canvas.toBlob(blob => {
            const link = document.createElement('a');
            link.href = URL.createObjectURL(blob);
            link.download = filename;
            document.body.append(link);
            link.click();
            link.remove();
            setTimeout(() => URL.revokeObjectURL(link.href), 1000);
        }, 'image/png');
    }

    async function copyOverlayText() {
        await navigator.clipboard.writeText(elements.overlayText.value);
        flashButton(elements.copyText, 'Copied');
    }

    function downloadJson() {
        const blob = new Blob([JSON.stringify(state, null, 2)], { type: 'application/json' });
        const link = document.createElement('a');
        link.href = URL.createObjectURL(blob);
        link.download = 'humanenerdia-kpi-card-data.json';
        document.body.append(link);
        link.click();
        link.remove();
        setTimeout(() => URL.revokeObjectURL(link.href), 1000);
    }

    function importJson(event) {
        const [file] = event.target.files;
        if (!file) {
            return;
        }
        const reader = new FileReader();
        reader.onload = () => {
            try {
                const imported = JSON.parse(String(reader.result));
                state = {
                    ...blankState(),
                    ...imported,
                    records: {
                        ...blankState().records,
                        ...(imported.records || {})
                    }
                };
                saveState();
                render();
            } catch (_) {
                window.alert('Invalid JSON file.');
            } finally {
                event.target.value = '';
            }
        };
        reader.readAsText(file);
    }

    function resetTask() {
        if (!window.confirm(`Reset values for ${state.selectedTaskId}?`)) {
            return;
        }
        state.records[state.selectedTaskId] = blankRecord();
        saveState();
        render();
    }

    function resetAll() {
        if (!window.confirm('Reset all saved KPI card values?')) {
            return;
        }
        state = blankState();
        saveState();
        render();
    }

    function flashButton(button, text) {
        const original = button.textContent;
        button.textContent = text;
        button.disabled = true;
        setTimeout(() => {
            button.textContent = original;
            button.disabled = false;
        }, 900);
    }

    function escapeHtml(value) {
        return String(value)
            .replaceAll('&', '&amp;')
            .replaceAll('<', '&lt;')
            .replaceAll('>', '&gt;')
            .replaceAll('"', '&quot;')
            .replaceAll("'", '&#039;');
    }
})();
