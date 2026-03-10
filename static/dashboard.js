/**
 * ArthSakshar AI – Campaign Dashboard
 * Fetches data from API and renders stats, calls, campaigns, and events.
 */

const API_BASE = '';

// ─── Utilities ──────────────────────────────────────────────
function showToast(message, type = 'info') {
    const toast = document.getElementById('toast');
    toast.textContent = message;
    toast.className = `toast show ${type}`;
    setTimeout(() => toast.classList.remove('show'), 3500);
}

function formatDate(dateStr) {
    if (!dateStr) return '—';
    try {
        const d = new Date(dateStr);
        return d.toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' });
    } catch {
        return dateStr;
    }
}

function formatTime(dateStr) {
    if (!dateStr) return '';
    try {
        const d = new Date(dateStr);
        return d.toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' });
    } catch {
        return '';
    }
}

function getStatusClass(status) {
    const map = {
        completed: 'completed',
        transferred: 'transferred',
        failed: 'failed',
        initiated: 'initiated',
        callback: 'callback',
        'no-answer': 'failed',
        busy: 'failed',
        canceled: 'failed',
        running: 'initiated',
        pending: 'initiated',
    };
    return map[status] || 'initiated';
}

function getStatusIcon(status) {
    const map = {
        completed: '✅',
        transferred: '📲',
        failed: '❌',
        initiated: '📞',
        callback: '🔁',
        'no-answer': '📵',
        busy: '🔴',
    };
    return map[status] || '📞';
}

function getLangFlag(lang) {
    const map = {
        marathi: '🇮🇳 MR',
        hindi: '🇮🇳 HI',
        english: '🇮🇳 EN',
    };
    return map[lang] || '🌐';
}


// ─── Fetch Stats ────────────────────────────────────────────
async function fetchStats() {
    try {
        const res = await fetch(`${API_BASE}/api/stats`);
        const data = await res.json();

        document.getElementById('statTotalCalls').textContent = data.total_calls || 0;
        document.getElementById('statCompleted').textContent = data.completed_calls || 0;
        document.getElementById('statTransferred').textContent = data.transferred_calls || 0;
        document.getElementById('statInterested').textContent = data.interested_count || 0;
        document.getElementById('statCallbacks').textContent = data.callback_requests || 0;
        document.getElementById('statCities').textContent = data.cities_reached || 0;

        // Animate the values
        document.querySelectorAll('.stat-value').forEach(el => {
            el.style.opacity = '0';
            el.style.transform = 'translateY(10px)';
            setTimeout(() => {
                el.style.transition = 'all 0.5s ease';
                el.style.opacity = '1';
                el.style.transform = 'translateY(0)';
            }, 100);
        });
    } catch (e) {
        console.error('Failed to fetch stats:', e);
    }
}


// ─── Fetch Calls ────────────────────────────────────────────
async function fetchCalls() {
    try {
        const res = await fetch(`${API_BASE}/api/calls?limit=30`);
        const calls = await res.json();
        const list = document.getElementById('callList');
        const countEl = document.getElementById('callCount');

        countEl.textContent = `${calls.length} calls`;

        if (calls.length === 0) {
            list.innerHTML = `
                <div class="empty-state">
                    <div class="icon">📞</div>
                    <p>No calls yet. Launch a campaign to start calling!</p>
                </div>
            `;
            return;
        }

        list.innerHTML = calls.map(call => `
            <li class="call-item">
                <div class="call-info">
                    <div class="call-avatar ${getStatusClass(call.status)}">
                        ${getStatusIcon(call.status)}
                    </div>
                    <div class="call-details">
                        <h4>${call.ca_name || call.phone_number || 'Unknown'}</h4>
                        <p>${call.city || '—'} · ${getLangFlag(call.language)} · ${call.duration || 0}s</p>
                    </div>
                </div>
                <div class="call-meta">
                    <span class="call-status ${getStatusClass(call.status)}">${call.status}</span>
                    <div class="call-time">${formatDate(call.created_at)} ${formatTime(call.created_at)}</div>
                </div>
            </li>
        `).join('');
    } catch (e) {
        console.error('Failed to fetch calls:', e);
        document.getElementById('callList').innerHTML = `
            <div class="empty-state">
                <div class="icon">⚠️</div>
                <p>Could not load calls.</p>
            </div>
        `;
    }
}


// ─── Fetch Campaigns ────────────────────────────────────────
async function fetchCampaigns() {
    try {
        const res = await fetch(`${API_BASE}/api/campaigns`);
        const campaigns = await res.json();
        const container = document.getElementById('campaignList');

        if (campaigns.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <div class="icon">🚀</div>
                    <p>No campaigns yet. Create one above to start!</p>
                </div>
            `;
            return;
        }

        container.innerHTML = campaigns.map(c => `
            <div class="call-item">
                <div class="call-info">
                    <div class="call-avatar ${getStatusClass(c.status)}">
                        ${c.status === 'completed' ? '✅' : c.status === 'running' ? '🔄' : '⏳'}
                    </div>
                    <div class="call-details">
                        <h4>${c.name}</h4>
                        <p>${c.completed_calls || 0} / ${c.total_calls || 0} calls · ${c.interested_count || 0} interested</p>
                    </div>
                </div>
                <div class="call-meta">
                    <span class="call-status ${getStatusClass(c.status)}">${c.status}</span>
                    <div class="call-time">${formatDate(c.created_at)}</div>
                </div>
            </div>
        `).join('');
    } catch (e) {
        console.error('Failed to fetch campaigns:', e);
    }
}


// ─── Fetch Events ───────────────────────────────────────────
async function fetchEvents() {
    try {
        const res = await fetch(`${API_BASE}/api/events`);
        const events = await res.json();
        const tbody = document.getElementById('eventsBody');
        const countEl = document.getElementById('eventCount');

        countEl.textContent = `${events.length} events`;

        if (events.length === 0) {
            tbody.innerHTML = `
                <tr><td colspan="5">
                    <div class="empty-state">
                        <div class="icon">📍</div>
                        <p>No events scheduled.</p>
                    </div>
                </td></tr>
            `;
            return;
        }

        tbody.innerHTML = events.map(evt => `
            <tr>
                <td><span class="city-badge">📍 ${evt.city}</span></td>
                <td>${formatDate(evt.event_date)}</td>
                <td>${evt.venue}</td>
                <td>${evt.coordinator_name}</td>
                <td>${evt.coordinator_phone}</td>
            </tr>
        `).join('');
    } catch (e) {
        console.error('Failed to fetch events:', e);
    }
}


// ─── Start Campaign ─────────────────────────────────────────
async function startCampaign() {
    const nameInput = document.getElementById('campaignName');
    const name = nameInput.value.trim();

    if (!name) {
        showToast('Please enter a campaign name.', 'error');
        nameInput.focus();
        return;
    }

    try {
        const res = await fetch(`${API_BASE}/api/campaigns/start`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name }),
        });
        const data = await res.json();

        showToast(`🚀 ${data.message}`, 'success');
        nameInput.value = '';

        // Refresh data after a short delay
        setTimeout(refreshAll, 2000);
    } catch (e) {
        showToast('Failed to start campaign. Check server connection.', 'error');
        console.error('Campaign start error:', e);
    }
}


// ─── Refresh All ────────────────────────────────────────────
async function refreshAll() {
    await Promise.all([
        fetchStats(),
        fetchCalls(),
        fetchCampaigns(),
        fetchEvents(),
    ]);
    showToast('Dashboard refreshed!', 'info');
}


// ─── Auto Refresh ───────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
    refreshAll();
    // Auto-refresh every 30 seconds
    setInterval(refreshAll, 30000);
});

// Allow Enter key to start campaign
document.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && document.activeElement.id === 'campaignName') {
        startCampaign();
    }
});
