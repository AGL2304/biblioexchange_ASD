// Client API minimal partagé par toutes les pages.
// Passe par le proxy Nginx /api/ -> backend:8000 (voir frontend/nginx.conf).
const API_BASE = "/api";

function getToken() {
  return localStorage.getItem("be_token");
}

function setToken(token) {
  localStorage.setItem("be_token", token);
}

function clearToken() {
  localStorage.removeItem("be_token");
}

async function apiFetch(path, options = {}) {
  const headers = options.headers || {};
  const token = getToken();
  if (token) headers["Authorization"] = "Bearer " + token;
  if (options.body && !(options.body instanceof URLSearchParams)) {
    headers["Content-Type"] = "application/json";
  }

  const res = await fetch(`${API_BASE}${path}`, { ...options, headers });

  if (res.status === 401) {
    let detail = "Identifiants invalides";
    try { detail = (await res.json()).detail || detail; } catch (_) {}

    if (token) {
      // Un token existait et n'est plus valide : session expirée -> on redirige
      clearToken();
      window.location.href = "login.html";
      return;
    }
    // Pas de token = tentative de login/register avec de mauvais identifiants
    throw new Error(detail);
  }
  if (!res.ok) {
    let detail = "Erreur inconnue";
    try { detail = (await res.json()).detail; } catch (_) {}
    throw new Error(detail);
  }
  if (res.status === 204) return null;
  return res.json();
}

const api = {
  register: (email, password, nom) =>
    apiFetch("/auth/register", { method: "POST", body: JSON.stringify({ email, password, nom }) }),

  login: async (email, password) => {
    const body = new URLSearchParams({ username: email, password });
    const data = await apiFetch("/auth/login", { method: "POST", body });
    setToken(data.access_token);
    return data;
  },

  logout: () => { clearToken(); window.location.href = "index.html"; },
  isLoggedIn: () => !!getToken(),

  me: () => apiFetch("/users/me"),
  updateMe: (payload) => apiFetch("/users/me", { method: "PATCH", body: JSON.stringify(payload) }),
  updateCredentials: (payload) => apiFetch("/users/me/credentials", { method: "PATCH", body: JSON.stringify(payload) }),

  listBooks: (q) => apiFetch(`/books${q ? "?q=" + encodeURIComponent(q) : ""}`),
  myBooks: () => apiFetch("/books/mine"),
  getBook: (id) => apiFetch(`/books/${id}`),
  createBook: (payload) => apiFetch("/books", { method: "POST", body: JSON.stringify(payload) }),
  updateBook: (id, payload) => apiFetch(`/books/${id}`, { method: "PATCH", body: JSON.stringify(payload) }),
  deleteBook: (id) => apiFetch(`/books/${id}`, { method: "DELETE" }),
  setBookStatus: (id, statut) => apiFetch(`/books/${id}/status`, { method: "PATCH", body: JSON.stringify({ statut }) }),

  myExchanges: () => apiFetch("/users/me/exchanges"),
  proposeExchange: (book_offered_id, book_requested_id) =>
    apiFetch("/exchanges", { method: "POST", body: JSON.stringify({ book_offered_id, book_requested_id }) }),
  acceptExchange: (id) => apiFetch(`/exchanges/${id}/accept`, { method: "PATCH" }),
  refuseExchange: (id) => apiFetch(`/exchanges/${id}/refuse`, { method: "PATCH" }),
  proposeRendezvous: (exchangeId, payload) =>
    apiFetch(`/exchanges/${exchangeId}/rendezvous`, { method: "POST", body: JSON.stringify(payload) }),

  notifications: () => apiFetch("/notifications"),
  markNotificationRead: (id) => apiFetch(`/notifications/${id}/read`, { method: "PATCH" }),

  // Admin
  adminUsers: (statut) => apiFetch(`/admin/users${statut ? "?statut=" + statut : ""}`),
  adminSuspendUser: (id) => apiFetch(`/admin/users/${id}/suspend`, { method: "PATCH" }),
  adminReactivateUser: (id) => apiFetch(`/admin/users/${id}/reactivate`, { method: "PATCH" }),
  adminPendingBooks: () => apiFetch("/admin/books?pending_only=true"),
  adminValidateBook: (id) => apiFetch(`/admin/books/${id}/validate`, { method: "PATCH" }),
  adminRejectBook: (id) => apiFetch(`/admin/books/${id}/reject`, { method: "PATCH" }),
  adminReports: (statut) => apiFetch(`/admin/reports${statut ? "?statut=" + statut : ""}`),
  adminResolveReport: (id) => apiFetch(`/admin/reports/${id}/resolve`, { method: "PATCH" }),
  adminStatsExchanges: () => apiFetch("/admin/stats/exchanges"),
  adminStatsModeration: () => apiFetch("/admin/stats/moderation"),
};