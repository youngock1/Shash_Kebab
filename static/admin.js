let state = null;

async function fetchState() {
    const res = await fetch('/admin/api/state');
    state = await res.json();
    render();
}

function render() {
    renderShiftBar();
    renderAnalytics();
    renderOrders();
    renderShifts();
}

// --- Смена ---
function renderShiftBar() {
    const statusEl = document.getElementById('shift-status');
    const openBtn = document.getElementById('open-shift-btn');
    const closeBtn = document.getElementById('close-shift-btn');
    const shift = state.current_shift;

    if (shift) {
        statusEl.textContent = `Смена №${shift.id} открыта с ${formatDate(shift.opened_at)}`;
        statusEl.className = 'open';
        openBtn.disabled = true;
        closeBtn.disabled = false;
    } else {
        statusEl.textContent = 'Смена закрыта';
        statusEl.className = 'closed';
        openBtn.disabled = false;
        closeBtn.disabled = true;
    }
}

// --- Аналитика ---
function renderAnalytics() {
    const a = state.analytics;
    const grid = document.getElementById('stats-grid');
    grid.innerHTML = `
        ${statCard(a.revenue + ' ₽', 'Выручка')}
        ${statCard(a.total_orders, 'Всего заказов')}
        ${statCard(a.orders_new, 'Новые')}
        ${statCard(a.orders_accepted, 'В работе')}
        ${statCard(a.orders_done, 'Выполнено')}
        ${statCard(a.orders_rejected, 'Отклонено')}
        ${statCard(a.avg_check + ' ₽', 'Средний чек')}
    `;

    const tbody = document.querySelector('#top-products tbody');
    tbody.innerHTML = '';
    if (a.top_products.length === 0) {
        tbody.innerHTML = '<tr><td colspan="3" class="empty">Пока нет данных</td></tr>';
    } else {
        a.top_products.forEach(p => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${p.name}</td>
                <td>${p.qty}</td>
                <td>${p.revenue} ₽</td>
            `;
            tbody.appendChild(tr);
        });
    }
}

function statCard(value, label) {
    return `<div class="stat-card">
        <div class="value">${value}</div>
        <div class="label">${label}</div>
    </div>`;
}

// --- Заказы ---
function renderOrders() {
    const currentContainer = document.getElementById('current-orders');
    const allContainer = document.getElementById('all-orders');

    // Текущие = new + accepted
    const current = state.orders.filter(o => o.status === 'new' || o.status === 'accepted');
    // Все — в обратном порядке (свежие сверху)
    const all = [...state.orders].reverse();

    currentContainer.innerHTML = current.length
        ? current.map(orderCard).join('')
        : '<div class="empty">Нет активных заказов</div>';

    allContainer.innerHTML = all.length
        ? all.map(orderCard).join('')
        : '<div class="empty">Заказов пока нет</div>';
}

function orderCard(o) {
    const itemsHtml = o.items
        .map(i => `${i.name} × ${i.qty} — ${i.price * i.qty} ₽`)
        .join('<br>');

    let actions = '';
    if (o.status === 'new') {
        actions = `
            <button class="btn-accept" data-id="${o.id}" data-action="accept">Принять</button>
            <button class="btn-reject" data-id="${o.id}" data-action="reject">Отклонить</button>
        `;
    } else if (o.status === 'accepted') {
        actions = `
            <button class="btn-done" data-id="${o.id}" data-action="done">Завершить</button>
            <button class="btn-reject" data-id="${o.id}" data-action="reject">Отклонить</button>
        `;
    }

    return `
        <div class="order-card ${o.status}">
            <div class="order-head">
                <strong>Заказ №${o.id}</strong>
                <span class="status ${o.status}">${statusLabel(o.status)}</span>
            </div>
            <div class="order-items">${itemsHtml}</div>
            <div class="order-meta">
                <div>👤 ${o.customer.name || '—'} · 📞 ${o.customer.phone || '—'}</div>
                <div>📍 ${o.customer.address || '—'}</div>
                ${o.customer.comment ? `<div>💬 ${o.customer.comment}</div>` : ''}
                <div>🕒 ${formatDate(o.created_at)} · Смена: ${o.shift_id ?? '—'}</div>
                <div><strong>Итого: ${o.total} ₽</strong></div>
            </div>
            <div class="order-actions">${actions}</div>
        </div>
    `;
}

function statusLabel(s) {
    return {
        new: 'Новый',
        accepted: 'В работе',
        done: 'Выполнен',
        rejected: 'Отклонён',
    }[s] || s;
}

// --- Смены ---
function renderShifts() {
    const tbody = document.querySelector('#shifts-table tbody');
    tbody.innerHTML = '';
    const shifts = [...state.shifts].reverse();

    if (shifts.length === 0) {
        tbody.innerHTML = '<tr><td colspan="8" class="empty">Смен пока не было</td></tr>';
        return;
    }

    shifts.forEach(s => {
        const st = s.stats || {};
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${s.id}</td>
            <td>${formatDate(s.opened_at)}</td>
            <td>${s.closed_at ? formatDate(s.closed_at) : '—'}</td>
            <td>${s.admin}</td>
            <td>${st.orders_total ?? '—'}</td>
            <td>${st.orders_done ?? '—'}</td>
            <td>${st.orders_rejected ?? '—'}</td>
            <td>${st.revenue ?? '—'} ₽</td>
        `;
        tbody.appendChild(tr);
    });
}

// --- Вспомогательные ---
function formatDate(iso) {
    if (!iso) return '—';
    const d = new Date(iso);
    return d.toLocaleString('ru-RU');
}

// --- Обработчики ---
document.getElementById('open-shift-btn').addEventListener('click', async () => {
    const res = await fetch('/admin/api/shift/open', { method: 'POST' });
    const r = await res.json();
    if (!r.success) alert(r.message);
    fetchState();
});

document.getElementById('close-shift-btn').addEventListener('click', async () => {
    if (!confirm('Закрыть смену?')) return;
    const res = await fetch('/admin/api/shift/close', { method: 'POST' });
    const r = await res.json();
    if (!r.success) alert(r.message);
    fetchState();
});

document.body.addEventListener('click', async (e) => {
    const btn = e.target.closest('button[data-action]');
    if (!btn) return;
    const id = btn.dataset.id;
    const action = btn.dataset.action;

    const res = await fetch(`/admin/api/order/${id}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action }),
    });
    const r = await res.json();
    if (!r.success) alert(r.message);
    fetchState();
});

// Автообновление раз в 5 секунд
setInterval(fetchState, 5000);

// Старт
fetchState();