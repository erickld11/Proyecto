const API_BASE = 'http://localhost:8000';

// ── Token management ──────────────────────────────────────────────────────────

function getToken() {
  return localStorage.getItem('eco_token');
}

function setAuth(token, user) {
  localStorage.setItem('eco_token', token);
  localStorage.setItem('eco_user', JSON.stringify(user));
}

function clearAuth() {
  localStorage.removeItem('eco_token');
  localStorage.removeItem('eco_user');
}

function getUser() {
  try {
    var u = localStorage.getItem('eco_user');
    return u ? JSON.parse(u) : null;
  } catch (e) {
    return null;
  }
}

function isLoggedIn() {
  var token = localStorage.getItem('eco_token');
  return token !== null && token !== undefined && token !== '';
}

// ── HTTP helpers ──────────────────────────────────────────────────────────────

async function request(method, endpoint, body, auth) {
  if (auth === undefined) auth = true;

  var headers = { 'Content-Type': 'application/json' };

  if (auth) {
    var token = getToken();
    if (!token) {
      window.location.replace('/index.html');
      return null;
    }
    headers['Authorization'] = 'Bearer ' + token;
  }

  var options = { method: method, headers: headers };
  if (body) options.body = JSON.stringify(body);

  var res = await fetch(API_BASE + endpoint, options);

  if (res.status === 204) return null;

  var data = null;
  try { data = await res.json(); } catch (e) {}

  if (res.status === 401 && auth) {
    clearAuth();
    window.location.replace('/index.html');
    return null;
  }

  if (!res.ok) {
    var msg = 'Error en la petición';
    if (data && data.detail) {
      if (typeof data.detail === 'string') {
        msg = data.detail;
      } else if (Array.isArray(data.detail)) {
        msg = data.detail.map(function(e) { return e.msg || String(e); }).join(', ');
      }
    }
    throw new Error(msg);
  }

  return data;
}

// ── API object ────────────────────────────────────────────────────────────────

var api = {
  register: function(data) { return request('POST', '/api/auth/register', data, false); },
  login: function(data) { return request('POST', '/api/auth/login', data, false); },
  me: function() { return request('GET', '/api/auth/me', null, true); },
  dashboard: function() { return request('GET', '/api/dashboard', null, true); },
  getConsumptions: function() { return request('GET', '/api/consumptions', null, true); },
  createConsumption: function(data) { return request('POST', '/api/consumptions', data, true); },
  updateConsumption: function(id, data) { return request('PATCH', '/api/consumptions/' + id, data, true); },
  deleteConsumption: function(id) { return request('DELETE', '/api/consumptions/' + id, null, true); },
  getBreakdown: function(id) { return request('GET', '/api/consumptions/breakdown/' + id, null, true); },
  generateAIPlan: function(id) { return request('POST', '/api/consumptions/' + id + '/ai-plan', null, true); },
};

// ── Toast ─────────────────────────────────────────────────────────────────────

function showToast(message, type) {
  if (!type) type = 'success';
  var existing = document.querySelector('.toast');
  if (existing) existing.remove();
  var toast = document.createElement('div');
  toast.className = 'toast ' + type;
  toast.textContent = message;
  document.body.appendChild(toast);
  setTimeout(function() { if (toast.parentNode) toast.remove(); }, 3500);
}

// ── Guards ────────────────────────────────────────────────────────────────────

function requireAuth() {
  if (!isLoggedIn()) {
    window.location.replace('/index.html');
    return false;
  }
  return true;
}

function redirectIfLoggedIn() {
  if (isLoggedIn()) {
    window.location.replace('/pages/dashboard.html');
  }
}

// ── Sidebar ───────────────────────────────────────────────────────────────────

function renderSidebar(activePage) {
  var user = getUser();
  var userName = (user && user.name) ? user.name : 'Usuario';
  var userSub = (user && user.company) ? user.company : ((user && user.email) ? user.email : '');

  var items = [
    { id: 'dashboard', label: 'Dashboard', icon: '📊', href: '/pages/dashboard.html' },
    { id: 'consumptions', label: 'Mis Consumos', icon: '⚡', href: '/pages/consumptions.html' },
    { id: 'register-consumption', label: 'Registrar', icon: '➕', href: '/pages/register-consumption.html' },
    { id: 'ai-plan', label: 'Plan IA', icon: '🤖', href: '/pages/ai-plan.html' },
  ];

  var navHTML = items.map(function(item) {
    var cls = 'nav-item' + (activePage === item.id ? ' active' : '');
    return '<a href="' + item.href + '" class="' + cls + '"><span class="icon">' + item.icon + '</span>' + item.label + '</a>';
  }).join('');

  return '<aside class="sidebar">' +
    '<div class="sidebar-logo">🌱 EcoTrack Pro<span>Sostenibilidad empresarial</span></div>' +
    '<nav class="sidebar-nav">' + navHTML + '</nav>' +
    '<div class="sidebar-footer">' +
    '<div class="sidebar-user"><strong>' + userName + '</strong>' + userSub + '</div>' +
    '<button class="btn-secondary btn-sm" onclick="logout()" style="width:100%">Cerrar sesión</button>' +
    '</div></aside>';
}

function logout() {
  clearAuth();
  window.location.replace('/index.html');
}

// Exportar todo globalmente
window.api = api;
window.getToken = getToken;
window.getUser = getUser;
window.setAuth = setAuth;
window.clearAuth = clearAuth;
window.isLoggedIn = isLoggedIn;
window.showToast = showToast;
window.requireAuth = requireAuth;
window.redirectIfLoggedIn = redirectIfLoggedIn;
window.renderSidebar = renderSidebar;
window.logout = logout;
