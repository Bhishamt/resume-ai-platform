import React, { useCallback, useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import {
  ArrowLeft,
  User,
  Mail,
  Shield,
  Calendar,
  Clock,
  CheckCircle2,
  XCircle,
  Trash2,
  ShieldCheck,
  ShieldOff,
  AlertTriangle,
} from "lucide-react";
import AdminLayout from "@/components/admin/AdminLayout";
import adminService from "@/services/adminService";

function InfoRow({ icon: Icon, label, value }) {
  return (
    <div className="flex items-start gap-3 py-3 border-b border-white/5 last:border-0">
      <Icon className="h-4 w-4 text-white/30 mt-0.5 shrink-0" />
      <div className="flex-1 min-w-0">
        <p className="text-xs text-white/40 mb-0.5">{label}</p>
        <p className="text-sm text-white break-all">{value ?? "—"}</p>
      </div>
    </div>
  );
}

export default function AdminUserDetail() {
  const { userId } = useParams();
  const navigate = useNavigate();
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(false);
  const [error, setError] = useState(null);
  const [toast, setToast] = useState(null);

  const showToast = (message, type = "success") => {
    setToast({ message, type });
    setTimeout(() => setToast(null), 3500);
  };

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const data = await adminService.getUserById(userId);
      setUser(data);
    } catch (err) {
      setError(err?.response?.data?.message ?? "User not found.");
    } finally {
      setLoading(false);
    }
  }, [userId]);

  useEffect(() => { load(); }, [load]);

  const handleAction = async (action) => {
    setActionLoading(true);
    try {
      if (action === "delete") {
        if (!window.confirm(`Permanently delete ${user.email}? This cannot be undone.`)) return;
        await adminService.deleteUser(userId);
        showToast("User deleted.");
        setTimeout(() => navigate("/admin/users"), 1000);
        return;
      }
      const payload = {};
      if (action === "disable") payload.is_active = false;
      if (action === "enable") payload.is_active = true;
      if (action === "makeAdmin") payload.role = "admin";
      if (action === "makeUser") payload.role = "user";
      const updated = await adminService.updateUser(userId, payload);
      setUser(updated);
      showToast("User updated successfully.");
    } catch (err) {
      showToast(err?.response?.data?.message ?? "Action failed.", "error");
    } finally {
      setActionLoading(false);
    }
  };

  return (
    <AdminLayout>
      <div className="px-6 py-8 max-w-3xl mx-auto space-y-6">
        {/* Back */}
        <button
          onClick={() => navigate("/admin/users")}
          className="flex items-center gap-2 text-sm text-white/40 hover:text-white transition-colors"
        >
          <ArrowLeft className="h-4 w-4" />
          Back to Users
        </button>

        {error && (
          <div className="rounded-lg border border-rose-500/20 bg-rose-500/10 px-4 py-3 text-sm text-rose-400">
            {error}
          </div>
        )}

        {toast && (
          <div
            className={`flex items-center gap-3 rounded-lg border px-4 py-3 text-sm ${
              toast.type === "error"
                ? "border-rose-500/20 bg-rose-500/10 text-rose-400"
                : "border-emerald-500/20 bg-emerald-500/10 text-emerald-400"
            }`}
          >
            {toast.type === "error" ? (
              <AlertTriangle className="h-4 w-4" />
            ) : (
              <CheckCircle2 className="h-4 w-4" />
            )}
            {toast.message}
          </div>
        )}

        {loading ? (
          <div className="rounded-xl border border-white/5 bg-white/[0.03] p-6 animate-pulse space-y-4">
            {Array.from({ length: 6 }).map((_, i) => (
              <div key={i} className="h-10 rounded bg-white/5" />
            ))}
          </div>
        ) : user ? (
          <>
            {/* User Card */}
            <div className="rounded-xl border border-white/5 bg-white/[0.03] p-6">
              <div className="flex items-center gap-4 mb-6">
                <div className="flex h-14 w-14 items-center justify-center rounded-full bg-indigo-500/20 text-2xl font-bold text-indigo-300">
                  {user.full_name?.[0]?.toUpperCase() ?? "?"}
                </div>
                <div>
                  <h2 className="text-xl font-bold text-white">{user.full_name}</h2>
                  <div className="flex items-center gap-2 mt-1">
                    {user.role === "admin" ? (
                      <span className="inline-flex items-center gap-1 rounded-full bg-indigo-500/10 border border-indigo-500/20 px-2 py-0.5 text-xs font-medium text-indigo-400">
                        <Shield className="h-3 w-3" /> Admin
                      </span>
                    ) : (
                      <span className="inline-flex items-center gap-1 rounded-full bg-white/5 border border-white/10 px-2 py-0.5 text-xs font-medium text-white/50">
                        <User className="h-3 w-3" /> User
                      </span>
                    )}
                    {user.is_active ? (
                      <span className="inline-flex items-center gap-1 text-xs text-emerald-400">
                        <CheckCircle2 className="h-3 w-3" /> Active
                      </span>
                    ) : (
                      <span className="inline-flex items-center gap-1 text-xs text-rose-400">
                        <XCircle className="h-3 w-3" /> Disabled
                      </span>
                    )}
                  </div>
                </div>
              </div>

              <div className="space-y-0">
                <InfoRow icon={Mail} label="Email" value={user.email} />
                <InfoRow icon={Shield} label="Role" value={user.role} />
                <InfoRow
                  icon={CheckCircle2}
                  label="Verified"
                  value={user.is_verified ? "Yes" : "No"}
                />
                <InfoRow
                  icon={Calendar}
                  label="Joined"
                  value={user.created_at ? new Date(user.created_at).toLocaleString() : "—"}
                />
                <InfoRow
                  icon={Clock}
                  label="Last Login"
                  value={user.last_login ? new Date(user.last_login).toLocaleString() : "Never"}
                />
              </div>
            </div>

            {/* Actions */}
            <div className="rounded-xl border border-white/5 bg-white/[0.03] p-5">
              <h3 className="text-sm font-semibold text-white mb-4">Account Actions</h3>
              <div className="flex flex-wrap gap-3">
                {user.is_active ? (
                  <button
                    disabled={actionLoading}
                    onClick={() => handleAction("disable")}
                    className="flex items-center gap-2 rounded-lg border border-amber-500/20 bg-amber-500/10 px-4 py-2 text-sm font-medium text-amber-400 hover:bg-amber-500/20 disabled:opacity-50 transition-all"
                  >
                    <ShieldOff className="h-4 w-4" />
                    Disable Account
                  </button>
                ) : (
                  <button
                    disabled={actionLoading}
                    onClick={() => handleAction("enable")}
                    className="flex items-center gap-2 rounded-lg border border-emerald-500/20 bg-emerald-500/10 px-4 py-2 text-sm font-medium text-emerald-400 hover:bg-emerald-500/20 disabled:opacity-50 transition-all"
                  >
                    <ShieldCheck className="h-4 w-4" />
                    Enable Account
                  </button>
                )}

                {user.role !== "admin" ? (
                  <button
                    disabled={actionLoading}
                    onClick={() => handleAction("makeAdmin")}
                    className="flex items-center gap-2 rounded-lg border border-indigo-500/20 bg-indigo-500/10 px-4 py-2 text-sm font-medium text-indigo-400 hover:bg-indigo-500/20 disabled:opacity-50 transition-all"
                  >
                    <Shield className="h-4 w-4" />
                    Grant Admin
                  </button>
                ) : (
                  <button
                    disabled={actionLoading}
                    onClick={() => handleAction("makeUser")}
                    className="flex items-center gap-2 rounded-lg border border-white/10 bg-white/5 px-4 py-2 text-sm font-medium text-white/60 hover:bg-white/10 disabled:opacity-50 transition-all"
                  >
                    <User className="h-4 w-4" />
                    Revoke Admin
                  </button>
                )}

                <button
                  disabled={actionLoading}
                  onClick={() => handleAction("delete")}
                  className="flex items-center gap-2 rounded-lg border border-rose-500/20 bg-rose-500/10 px-4 py-2 text-sm font-medium text-rose-400 hover:bg-rose-500/20 disabled:opacity-50 transition-all ml-auto"
                >
                  <Trash2 className="h-4 w-4" />
                  Delete Account
                </button>
              </div>
            </div>
          </>
        ) : null}
      </div>
    </AdminLayout>
  );
}
