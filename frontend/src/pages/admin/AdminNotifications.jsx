import React, { useCallback, useEffect, useState } from "react";
import {
  Bell,
  RefreshCw,
  Info,
  CheckCircle2,
  AlertTriangle,
  XCircle,
  Settings,
  Send,
} from "lucide-react";
import AdminLayout from "@/components/admin/AdminLayout";
import adminService from "@/services/adminService";
import { useAuth } from "@/context/AuthContext";

const TYPE_CONFIG = {
  info: { icon: Info, cls: "text-sky-400 bg-sky-500/10 border-sky-500/20" },
  success: { icon: CheckCircle2, cls: "text-emerald-400 bg-emerald-500/10 border-emerald-500/20" },
  warning: { icon: AlertTriangle, cls: "text-amber-400 bg-amber-500/10 border-amber-500/20" },
  error: { icon: XCircle, cls: "text-rose-400 bg-rose-500/10 border-rose-500/20" },
  system: { icon: Settings, cls: "text-violet-400 bg-violet-500/10 border-violet-500/20" },
};

function NotificationItem({ notif }) {
  const cfg = TYPE_CONFIG[notif.type] ?? TYPE_CONFIG.info;
  const Icon = cfg.icon;
  return (
    <div
      className={`flex items-start gap-4 rounded-xl border px-5 py-4 transition-all ${
        notif.is_read
          ? "border-white/5 bg-white/[0.02]"
          : "border-white/10 bg-white/[0.04]"
      }`}
    >
      <div className={`flex h-8 w-8 shrink-0 items-center justify-center rounded-lg border ${cfg.cls}`}>
        <Icon className="h-4 w-4" />
      </div>
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2 mb-0.5">
          <p className={`text-sm font-semibold ${notif.is_read ? "text-white/60" : "text-white"}`}>
            {notif.title}
          </p>
          {!notif.is_read && (
            <span className="h-1.5 w-1.5 rounded-full bg-indigo-400 shrink-0" />
          )}
        </div>
        <p className="text-sm text-white/40 leading-relaxed">{notif.message}</p>
        <p className="text-xs text-white/20 mt-1">
          {notif.created_at ? new Date(notif.created_at).toLocaleString() : ""}
        </p>
      </div>
    </div>
  );
}

export default function AdminNotifications() {
  const { user } = useAuth();
  const [notifications, setNotifications] = useState([]);
  const [meta, setMeta] = useState({ total: 0, page: 1, per_page: 50, pages: 1 });
  const [unreadCount, setUnreadCount] = useState(0);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [showUnreadOnly, setShowUnreadOnly] = useState(false);
  const [showCreate, setShowCreate] = useState(false);
  const [form, setForm] = useState({ user_id: "", title: "", message: "", type: "info" });
  const [sending, setSending] = useState(false);
  const [toast, setToast] = useState(null);

  const showToast = (message, type = "success") => {
    setToast({ message, type });
    setTimeout(() => setToast(null), 3500);
  };

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const params = { page, per_page: 50 };
      if (showUnreadOnly) params.is_read = false;
      const data = await adminService.getNotifications(params);
      setNotifications(data.notifications ?? []);
      setMeta(data.meta ?? { total: 0, page: 1, per_page: 50, pages: 1 });
      setUnreadCount(data.unread_count ?? 0);
    } finally {
      setLoading(false);
    }
  }, [page, showUnreadOnly]);

  useEffect(() => { load(); }, [load]);

  const handleSend = async () => {
    if (!form.title || !form.message) {
      showToast("Title and message are required.", "error");
      return;
    }
    setSending(true);
    try {
      if (form.user_id) {
        await adminService.createNotification({ ...form });
      } else {
        await adminService.broadcastNotification({ title: form.title, message: form.message, type: form.type, user_id: user?.id });
      }
      showToast(form.user_id ? "Notification sent." : "Notification broadcast to all users.");
      setForm({ user_id: "", title: "", message: "", type: "info" });
      setShowCreate(false);
      load();
    } catch (err) {
      showToast(err?.response?.data?.message ?? "Failed to send.", "error");
    } finally {
      setSending(false);
    }
  };

  return (
    <AdminLayout>
      <div className="px-6 py-8 max-w-3xl mx-auto space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-white flex items-center gap-2">
              Notifications
              {unreadCount > 0 && (
                <span className="inline-flex h-5 min-w-[1.25rem] items-center justify-center rounded-full bg-indigo-600 px-1.5 text-xs font-bold text-white">
                  {unreadCount}
                </span>
              )}
            </h1>
            <p className="text-sm text-white/40 mt-1">
              {meta.total.toLocaleString()} total notifications
            </p>
          </div>
          <div className="flex items-center gap-3">
            <button
              onClick={() => setShowCreate((s) => !s)}
              className="flex items-center gap-2 rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-500 transition-all"
            >
              <Send className="h-4 w-4" />
              Send Notification
            </button>
            <button
              onClick={load}
              className="flex items-center gap-2 rounded-lg border border-white/10 px-3 py-2 text-sm text-white/60 hover:text-white hover:border-white/20 transition-all"
            >
              <RefreshCw className={`h-4 w-4 ${loading ? "animate-spin" : ""}`} />
            </button>
          </div>
        </div>

        {toast && (
          <div className={`flex items-center gap-3 rounded-lg border px-4 py-3 text-sm ${toast.type === "error" ? "border-rose-500/20 bg-rose-500/10 text-rose-400" : "border-emerald-500/20 bg-emerald-500/10 text-emerald-400"}`}>
            {toast.type === "error" ? <AlertTriangle className="h-4 w-4" /> : <CheckCircle2 className="h-4 w-4" />}
            {toast.message}
          </div>
        )}

        {/* Create Panel */}
        {showCreate && (
          <div className="rounded-xl border border-indigo-500/20 bg-indigo-500/5 p-5 space-y-4">
            <h3 className="text-sm font-semibold text-white">Send Notification</h3>
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
              <div>
                <label className="text-xs text-white/40 mb-1 block">User ID (blank = broadcast)</label>
                <input
                  type="text"
                  placeholder="Leave blank to broadcast to all"
                  value={form.user_id}
                  onChange={(e) => setForm((f) => ({ ...f, user_id: e.target.value }))}
                  className="w-full rounded-lg border border-white/10 bg-white/[0.03] px-3 py-2 text-sm text-white placeholder-white/20 focus:border-indigo-500/50 focus:outline-none"
                />
              </div>
              <div>
                <label className="text-xs text-white/40 mb-1 block">Type</label>
                <select
                  value={form.type}
                  onChange={(e) => setForm((f) => ({ ...f, type: e.target.value }))}
                  className="w-full rounded-lg border border-white/10 bg-[#111] py-2 px-3 text-sm text-white/60 focus:border-indigo-500/50 focus:outline-none"
                >
                  {["info", "success", "warning", "error", "system"].map((t) => (
                    <option key={t} value={t}>{t}</option>
                  ))}
                </select>
              </div>
            </div>
            <div>
              <label className="text-xs text-white/40 mb-1 block">Title</label>
              <input
                type="text"
                placeholder="Notification title"
                value={form.title}
                onChange={(e) => setForm((f) => ({ ...f, title: e.target.value }))}
                className="w-full rounded-lg border border-white/10 bg-white/[0.03] px-3 py-2 text-sm text-white placeholder-white/20 focus:border-indigo-500/50 focus:outline-none"
              />
            </div>
            <div>
              <label className="text-xs text-white/40 mb-1 block">Message</label>
              <textarea
                rows={3}
                placeholder="Notification body"
                value={form.message}
                onChange={(e) => setForm((f) => ({ ...f, message: e.target.value }))}
                className="w-full rounded-lg border border-white/10 bg-white/[0.03] px-3 py-2 text-sm text-white placeholder-white/20 focus:border-indigo-500/50 focus:outline-none resize-none"
              />
            </div>
            <div className="flex justify-end gap-3">
              <button onClick={() => setShowCreate(false)} className="text-sm text-white/40 hover:text-white transition-colors">Cancel</button>
              <button
                onClick={handleSend}
                disabled={sending}
                className="flex items-center gap-2 rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-500 disabled:opacity-50 transition-all"
              >
                <Send className="h-4 w-4" />
                {sending ? "Sending…" : form.user_id ? "Send" : "Broadcast"}
              </button>
            </div>
          </div>
        )}

        {/* Filter */}
        <div className="flex items-center gap-4">
          <button
            onClick={() => { setShowUnreadOnly(false); setPage(1); }}
            className={`text-sm transition-colors ${!showUnreadOnly ? "text-white font-medium" : "text-white/40 hover:text-white"}`}
          >
            All
          </button>
          <button
            onClick={() => { setShowUnreadOnly(true); setPage(1); }}
            className={`text-sm transition-colors ${showUnreadOnly ? "text-white font-medium" : "text-white/40 hover:text-white"}`}
          >
            Unread
            {unreadCount > 0 && (
              <span className="ml-1.5 rounded-full bg-indigo-600/70 px-1.5 py-0.5 text-xs font-bold text-white">
                {unreadCount}
              </span>
            )}
          </button>
        </div>

        {/* List */}
        <div className="space-y-3">
          {loading
            ? Array.from({ length: 5 }).map((_, i) => (
                <div key={i} className="h-20 rounded-xl border border-white/5 bg-white/[0.02] animate-pulse" />
              ))
            : notifications.length === 0
            ? (
              <div className="flex flex-col items-center py-16 text-center">
                <Bell className="h-10 w-10 text-white/10 mb-3" />
                <p className="text-sm text-white/30">No notifications yet.</p>
              </div>
            )
            : notifications.map((n) => (
                <NotificationItem key={n.id} notif={n} />
              ))}
        </div>

        {/* Pagination */}
        {meta.pages > 1 && (
          <div className="flex items-center justify-center gap-3 pt-2">
            <button
              disabled={page <= 1}
              onClick={() => setPage((p) => p - 1)}
              className="rounded-lg border border-white/10 px-4 py-2 text-sm text-white/60 hover:text-white disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
            >
              Previous
            </button>
            <span className="text-sm text-white/40">
              {page} / {meta.pages}
            </span>
            <button
              disabled={page >= meta.pages}
              onClick={() => setPage((p) => p + 1)}
              className="rounded-lg border border-white/10 px-4 py-2 text-sm text-white/60 hover:text-white disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
            >
              Next
            </button>
          </div>
        )}
      </div>
    </AdminLayout>
  );
}
