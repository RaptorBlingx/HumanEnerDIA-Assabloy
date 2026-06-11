/*
 * ASSA ABLOY partner press-shop pilot helpers.
 *
 * This module keeps UI pages focused on the imported partner dataset in dev
 * pilot mode while leaving the generic simulator/demo paths available as
 * fallback behavior.
 */
(function () {
    const DEFAULT_START = '2025-05-01T00:00:00';
    const DEFAULT_END = '2026-06-01T00:00:00';
    let profilePromise = null;

    function apiBase() {
        return window.API_BASE || (window.location.port === '8001' ? '/api/v1' : '/api/analytics/api/v1');
    }

    function parseDate(value) {
        return new Date(value || DEFAULT_END);
    }

    function endDateForInput(profile) {
        const end = parseDate(profile?.period?.end || DEFAULT_END);
        end.setUTCDate(end.getUTCDate() - 1);
        return end.toISOString().substring(0, 10);
    }

    function period(profile) {
        return {
            start: profile?.period?.start || DEFAULT_START,
            end: profile?.period?.end || DEFAULT_END,
            label: profile?.period?.label || '2025-05-01 to 2026-06-01'
        };
    }

    async function loadProfile() {
        if (!profilePromise) {
            profilePromise = fetch(`${apiBase()}/partner-press/profile`, { cache: 'no-store' })
                .then(response => {
                    if (!response.ok) {
                        throw new Error(`Partner profile HTTP ${response.status}`);
                    }
                    return response.json();
                })
                .then(profile => {
                    if (!profile || !Array.isArray(profile.meter_groups) || !profile.meter_groups.length) {
                        throw new Error('Partner profile has no meter groups');
                    }
                    window.partnerPilot = true;
                    window.partnerProfile = profile;
                    return profile;
                })
                .catch(error => {
                    window.partnerPilot = false;
                    window.partnerProfile = null;
                    profilePromise = null;
                    throw error;
                });
        }
        return profilePromise;
    }

    function setPartnerHeading(titleSelector, subtitleSelector, titleSuffix, subtitle) {
        const profile = window.partnerProfile;
        if (!profile) return;
        const title = document.querySelector(titleSelector);
        const sub = document.querySelector(subtitleSelector);
        if (title) {
            title.textContent = `${profile.display_name}${titleSuffix ? ` ${titleSuffix}` : ''}`;
        }
        if (sub) {
            sub.textContent = subtitle || 'Imported group-meter energy and SQDC production data.';
        }
    }

    function applyDateInputs(startId, endId, profile = window.partnerProfile) {
        const p = period(profile);
        const startEl = document.getElementById(startId);
        const endEl = document.getElementById(endId);
        if (startEl) startEl.value = p.start.substring(0, 10);
        if (endEl) endEl.value = endDateForInput(profile);
    }

    function dateRange(profile = window.partnerProfile, days = null) {
        const p = period(profile);
        if (!days) {
            return { start: p.start, end: p.end, label: p.label };
        }
        const end = parseDate(p.end);
        const start = new Date(end.getTime() - days * 24 * 60 * 60 * 1000);
        return {
            start: start.toISOString(),
            end: end.toISOString(),
            label: `${start.toISOString().substring(0, 10)} to ${end.toISOString().substring(0, 10)}`
        };
    }

    function populateAssetSelect(select, profile, options = {}) {
        if (!select || !profile) return;
        const {
            allLabel = null,
            includeFactory = false,
            includeMeterGroups = true,
            includePresses = false,
            valueMode = 'id',
            meterSuffix = ' (meter group)',
            pressSuffix = ' (production only)'
        } = options;

        select.innerHTML = '';
        if (allLabel !== null) {
            select.appendChild(new Option(allLabel, ''));
        }
        if (includeFactory && profile.factory?.id) {
            select.appendChild(new Option(profile.display_name, profile.factory.id));
        }
        if (includeMeterGroups) {
            (profile.meter_groups || []).forEach(asset => {
                const value = valueMode === 'group' ? asset.group : asset.id;
                const option = new Option(`${asset.name}${meterSuffix}`, value);
                option.dataset.group = asset.group || '';
                option.dataset.assetLevel = asset.asset_level || 'meter_group';
                option.dataset.energyScope = asset.energy_scope || 'group_meter';
                select.appendChild(option);
            });
        }
        if (includePresses) {
            (profile.presses || []).forEach(asset => {
                const value = valueMode === 'group' ? asset.group : asset.id;
                const option = new Option(`${asset.name}${pressSuffix}`, value);
                option.dataset.group = asset.group || '';
                option.dataset.assetLevel = asset.asset_level || 'press';
                option.dataset.energyScope = asset.energy_scope || 'production_only';
                select.appendChild(option);
            });
        }
    }

    async function summary(params = {}) {
        const query = new URLSearchParams(params);
        return fetch(`${apiBase()}/partner-press/summary?${query.toString()}`, { cache: 'no-store' })
            .then(response => {
                if (!response.ok) {
                    throw new Error(`Partner summary HTTP ${response.status}`);
                }
                return response.json();
            });
    }

    window.PartnerPilot = {
        DEFAULT_START,
        DEFAULT_END,
        loadProfile,
        period,
        dateRange,
        applyDateInputs,
        endDateForInput,
        populateAssetSelect,
        setPartnerHeading,
        summary
    };
})();
