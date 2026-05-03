// State Management
let token = localStorage.getItem('token');
let currentUser = null;

// DOM Elements
const authScreen = document.getElementById('auth-screen');
const dashboard = document.getElementById('dashboard');
const loginForm = document.getElementById('login-form');
const registerForm = document.getElementById('register-form');
const calcForm = document.getElementById('calc-form');
const calcTbody = document.getElementById('calc-tbody');
const userDisplay = document.getElementById('user-display');

// Tab Switching
document.getElementById('tab-login').onclick = () => {
    document.getElementById('tab-login').classList.add('active');
    document.getElementById('tab-register').classList.remove('active');
    loginForm.classList.remove('hidden');
    registerForm.classList.add('hidden');
};

document.getElementById('tab-register').onclick = () => {
    document.getElementById('tab-register').classList.add('active');
    document.getElementById('tab-login').classList.remove('active');
    registerForm.classList.remove('hidden');
    loginForm.classList.add('hidden');
};

// --- AUTHENTICATION ---

loginForm.onsubmit = async (e) => {
    e.preventDefault();
    const formData = new FormData();
    formData.append('username', document.getElementById('login-username').value);
    formData.append('password', document.getElementById('login-password').value);

    try {
        const res = await fetch('/api/login', { method: 'POST', body: formData });
        const data = await res.json();
        if (res.ok) {
            localStorage.setItem('token', data.access_token);
            token = data.access_token;
            initDashboard();
        } else {
            showMsg('login-error', data.detail, 'error');
        }
    } catch (err) {
        showMsg('login-error', 'Server error', 'error');
    }
};

registerForm.onsubmit = async (e) => {
    e.preventDefault();
    const payload = {
        username: document.getElementById('reg-username').value,
        email: document.getElementById('reg-email').value,
        password: document.getElementById('reg-password').value
    };

    try {
        const res = await fetch('/api/register', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const data = await res.json();
        if (res.ok) {
            showMsg('register-error', 'Account created! Please login.', 'success');
            registerForm.reset();
        } else {
            showMsg('register-error', data.detail, 'error');
        }
    } catch (err) {
        showMsg('register-error', 'Server error', 'error');
    }
};

document.getElementById('logout-btn').onclick = () => {
    localStorage.removeItem('token');
    location.reload();
};

// --- CALCULATIONS (BREAD) ---

async function loadCalculations() {
    const res = await fetch('/api/calculations', {
        headers: { 'Authorization': `Bearer ${token}` }
    });
    if (res.status === 401) return logout();
    const calcs = await res.json();
    renderTable(calcs);
    loadStats(); // Update stats whenever table loads
}

function renderTable(calcs) {
    calcTbody.innerHTML = calcs.length ? '' : '<tr><td colspan="6" style="text-align:center; padding: 2rem; color: #94a3b8;">No calculations yet</td></tr>';
    calcs.reverse().forEach(c => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${new Date(c.timestamp).toLocaleDateString()}</td>
            <td>${c.operand1}</td>
            <td style="color: #818cf8; font-weight: 600;">${formatOp(c.operation)}</td>
            <td>${c.operand2}</td>
            <td style="font-weight: 600;">${c.result}</td>
            <td class="actions">
                <button class="outline-btn" onclick="editCalc(${c.id})">Edit</button>
                <button class="outline-btn" onclick="deleteCalc(${c.id})" style="color: #ef4444;">Delete</button>
            </td>
        `;
        calcTbody.appendChild(row);
    });
}

calcForm.onsubmit = async (e) => {
    e.preventDefault();
    const id = document.getElementById('edit-id').value;
    const payload = {
        operation: document.getElementById('operation').value,
        operand1: parseFloat(document.getElementById('operand1').value),
        operand2: parseFloat(document.getElementById('operand2').value)
    };

    const url = id ? `/api/calculations/${id}` : '/api/calculations';
    const method = id ? 'PUT' : 'POST';

    try {
        const res = await fetch(url, {
            method,
            headers: { 
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify(payload)
        });
        const data = await res.json();
        if (res.ok) {
            showMsg('form-message', id ? 'Updated!' : 'Calculated!', 'success');
            resetForm();
            loadCalculations();
        } else {
            showMsg('form-message', data.detail, 'error');
        }
    } catch (err) {
        showMsg('form-message', 'Error saving', 'error');
    }
};

async function deleteCalc(id) {
    if (!confirm('Delete this calculation?')) return;
    const res = await fetch(`/api/calculations/${id}`, {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${token}` }
    });
    if (res.ok) loadCalculations();
}

async function editCalc(id) {
    const res = await fetch(`/api/calculations/${id}`, {
        headers: { 'Authorization': `Bearer ${token}` }
    });
    const c = await res.json();
    document.getElementById('edit-id').value = c.id;
    document.getElementById('operand1').value = c.operand1;
    document.getElementById('operand2').value = c.operand2;
    document.getElementById('operation').value = c.operation;
    document.getElementById('form-title').innerText = 'Edit Calculation';
    document.getElementById('submit-btn').innerText = 'Update';
    document.getElementById('cancel-btn').classList.remove('hidden');
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

// --- NEW FEATURE: STATISTICS ---

async function loadStats() {
    try {
        const res = await fetch('/api/reports/stats', {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        const stats = await res.json();
        
        document.getElementById('stat-total').innerText = stats.total_count;
        document.getElementById('stat-avg').innerText = stats.average_result;
        
        const ops = stats.operation_counts;
        const topOp = Object.keys(ops).reduce((a, b) => ops[a] > ops[b] ? a : b, '-');
        document.getElementById('stat-top').innerText = formatOp(topOp);
        
        document.getElementById('stat-last').innerText = stats.last_calculation 
            ? new Date(stats.last_calculation).toLocaleTimeString() 
            : 'Never';
    } catch (err) {
        console.error('Stats failed', err);
    }
}

// --- HELPERS ---

function formatOp(op) {
    const map = { add: '+', subtract: '-', multiply: '×', divide: '÷', exponent: '^', modulus: '%' };
    return map[op] || op;
}

function showMsg(id, txt, type) {
    const el = document.getElementById(id);
    el.innerText = txt;
    el.className = `message ${type}`;
    el.style.display = 'block';
    setTimeout(() => el.style.display = 'none', 4000);
}

function resetForm() {
    calcForm.reset();
    document.getElementById('edit-id').value = '';
    document.getElementById('form-title').innerText = 'New Calculation';
    document.getElementById('submit-btn').innerText = 'Calculate';
    document.getElementById('cancel-btn').classList.add('hidden');
}

document.getElementById('cancel-btn').onclick = resetForm;

// --- USER PROFILE & PASSWORD CHANGE (NEW FEATURE) ---

document.getElementById('profile-btn').onclick = () => {
    document.querySelector('.dashboard-content').classList.add('hidden');
    document.getElementById('profile-section').classList.remove('hidden');
    // Pre-fill email
    const emailInput = document.getElementById('prof-email');
    if (emailInput) emailInput.value = localStorage.getItem('userEmail') || '';
};

document.getElementById('close-profile').onclick = () => {
    document.getElementById('profile-section').classList.add('hidden');
    document.querySelector('.dashboard-content').classList.remove('hidden');
};

document.getElementById('profile-form').onsubmit = async (e) => {
    e.preventDefault();
    const payload = {
        email: document.getElementById('prof-email').value,
        password: document.getElementById('prof-password').value
    };

    try {
        const res = await fetch('/api/users/me', {
            method: 'PUT',
            headers: { 
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify(payload)
        });
        const data = await res.json();
        if (res.ok) {
            showMsg('profile-message', 'Profile updated successfully!', 'success');
            if (payload.password) {
                // If password changed, logout to be safe
                setTimeout(() => logout(), 2000);
            }
        } else {
            showMsg('profile-message', data.detail, 'error');
        }
    } catch (err) {
        showMsg('profile-message', 'Error updating profile', 'error');
    }
};

function logout() {
    localStorage.removeItem('token');
    location.reload();
}

document.getElementById('logout-btn').onclick = logout;

function initDashboard() {
    authScreen.classList.add('hidden');
    dashboard.classList.remove('hidden');
    loadCalculations();
}

// Check session on load
if (token) initDashboard();
