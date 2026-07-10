/**
 * adminService.js
 * All API calls for the Enterprise Admin Panel (Phase 9).
 * Extends the shared axios instance (api.js) which handles auth headers.
 */

import api from "./api";

const BASE = "/admin";

// ---------------------------------------------------------------------------
// Dashboard & Analytics
// ---------------------------------------------------------------------------

export const getDashboardStats = () =>
  api.get(`${BASE}/dashboard`).then((r) => r.data.data);

export const getAnalytics = (days = 30) =>
  api.get(`${BASE}/analytics`, { params: { days } }).then((r) => r.data.data);

// ---------------------------------------------------------------------------
// User Management
// ---------------------------------------------------------------------------

export const getUsers = (params = {}) =>
  api.get(`${BASE}/users`, { params }).then((r) => r.data.data);

export const getUserById = (userId) =>
  api.get(`${BASE}/users/${userId}`).then((r) => r.data.data);

export const updateUser = (userId, payload) =>
  api.put(`${BASE}/users/${userId}`, payload).then((r) => r.data.data);

export const deleteUser = (userId) =>
  api.delete(`${BASE}/users/${userId}`).then((r) => r.data);

// ---------------------------------------------------------------------------
// Resume Management
// ---------------------------------------------------------------------------

export const getResumes = (params = {}) =>
  api.get(`${BASE}/resumes`, { params }).then((r) => r.data.data);

export const deleteResume = (resumeId) =>
  api.delete(`${BASE}/resumes/${resumeId}`).then((r) => r.data);

// ---------------------------------------------------------------------------
// AI Monitoring
// ---------------------------------------------------------------------------

export const getAIMonitoring = () =>
  api.get(`${BASE}/ai-monitoring`).then((r) => r.data.data);

// ---------------------------------------------------------------------------
// Audit Logs
// ---------------------------------------------------------------------------

export const getLogs = (params = {}) =>
  api.get(`${BASE}/logs`, { params }).then((r) => r.data.data);

// ---------------------------------------------------------------------------
// Settings
// ---------------------------------------------------------------------------

export const getSettings = () =>
  api.get(`${BASE}/settings`).then((r) => r.data.data);

export const updateSettings = (settings) =>
  api.put(`${BASE}/settings`, { settings }).then((r) => r.data.data);

// ---------------------------------------------------------------------------
// System Health
// ---------------------------------------------------------------------------

export const getSystemHealth = () =>
  api.get(`${BASE}/system`).then((r) => r.data.data);

// ---------------------------------------------------------------------------
// Notifications
// ---------------------------------------------------------------------------

export const getNotifications = (params = {}) =>
  api.get(`${BASE}/notifications`, { params }).then((r) => r.data.data);

export const createNotification = (payload) =>
  api.post(`${BASE}/notifications`, payload).then((r) => r.data.data);

export const broadcastNotification = (payload) =>
  api
    .post(`${BASE}/notifications/broadcast`, payload)
    .then((r) => r.data.data);

const adminService = {
  getDashboardStats,
  getAnalytics,
  getUsers,
  getUserById,
  updateUser,
  deleteUser,
  getResumes,
  deleteResume,
  getAIMonitoring,
  getLogs,
  getSettings,
  updateSettings,
  getSystemHealth,
  getNotifications,
  createNotification,
  broadcastNotification,
};

export default adminService;
