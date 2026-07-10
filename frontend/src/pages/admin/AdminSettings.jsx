import React, { useCallback, useEffect, useState } from "react";
import { Save, RefreshCw, CheckCircle2, AlertTriangle, Settings } from "lucide-react";
import AdminLayout from "@/components/admin/AdminLayout";
import adminService from "@/services/adminService";

export default function AdminSettings() {
  const [settings, setSettings] = useState([]);
  const [edits, setEdits] = useState({});
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [toast, setToast] = useState(null);

  const showToast = (message, type = "success") => {
    setToast({ message, type });
    setTimeout(() => setToast(null), 3500);
  };

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const data = await adminService.getSettings();
      setSettings(data.settings ?? []);
      // Build edits map from current values
      const editMap = {};
      (data.settings ?? []).forEach((s) => { editMap[s.key] = s.value ?? ""; });
      setEdits(editMap);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { load(); }, [load]);

  const handleChange = (key, value) => {
    setEdits((prev) => ({ ...prev, [key]: value }));
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      const payload = settings.map((s) => ({
        key: s.key,
        value: edits[s.key] ?? s.value ?? "",
        description: s.description,
      }));
      const data = await adminService.updateSettings(payload);
      setSettings(data.settings ?? []);
      showToast("Settings saved successfully.");
    } catch (err) {
      showToast(err?.response?.data?.message ?? "Failed to save settings.", "error");
    } finally {
      setSaving(false);
    }
  };

  const isDirty = settings.some((s) => edits[s.key] !== (s.value ?? ""));

  return (
    <AdminLayout>
      <div className="px-6 py-8 max-w-3xl mx-auto space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-white">System Settings</h1>
            <p className="text-sm text-white/40 mt-1">
              Configure platform-wide behaviour
            </p>
          </div>
          <div className="flex items-center gap-3">
            <button
              onClick={load}
              disabled={loading}
              className="flex items-center gap-2 rounded-lg border border-white/10 px-3 py-2 text-sm text-white/60 hover:text-white hover:border-white/20 disabled:opacity-50 transition-all"
            >
              <RefreshCw className={`h-4 w-4 ${loading ? "animate-spin" : ""}`} />
            </button>
            <button
              onClick={handleSave}
              disabled={saving || !isDirty}
              className="flex items-center gap-2 rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-500 disabled:opacity-40 disabled:cursor-not-allowed transition-all"
            >
              <Save className="h-4 w-4" />
              {saving ? "Saving…" : "Save Changes"}
            </button>
          </div>
        </div>

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

        <div className="rounded-xl border border-white/5 bg-white/[0.03] divide-y divide-white/5">
          {loading
            ? Array.from({ length: 6 }).map((_, i) => (
                <div key={i} className="px-5 py-5 animate-pulse">
                  <div className="h-3 w-40 rounded bg-white/5 mb-3" />
                  <div className="h-10 rounded bg-white/5" />
                  <div className="h-3 w-64 rounded bg-white/5 mt-2" />
                </div>
              ))
            : settings.map((setting) => (
                <div key={setting.key} className="px-5 py-5">
                  <div className="flex items-center gap-2 mb-2">
                    <Settings className="h-4 w-4 text-indigo-400" />
                    <label className="text-sm font-medium text-white font-mono">
                      {setting.key}
                    </label>
                    {edits[setting.key] !== (setting.value ?? "") && (
                      <span className="text-xs text-amber-400 ml-auto">Modified</span>
                    )}
                  </div>
                  <input
                    type="text"
                    value={edits[setting.key] ?? ""}
                    onChange={(e) => handleChange(setting.key, e.target.value)}
                    className="w-full rounded-lg border border-white/10 bg-white/[0.03] px-3 py-2 text-sm text-white placeholder-white/20 focus:border-indigo-500/50 focus:outline-none focus:ring-1 focus:ring-indigo-500/20 transition-all"
                  />
                  {setting.description && (
                    <p className="mt-2 text-xs text-white/30">{setting.description}</p>
                  )}
                  {setting.updated_at && (
                    <p className="mt-1 text-xs text-white/20">
                      Last updated: {new Date(setting.updated_at).toLocaleString()}
                    </p>
                  )}
                </div>
              ))}

          {!loading && settings.length === 0 && (
            <div className="px-5 py-12 text-center text-sm text-white/30">
              No settings configured yet.
            </div>
          )}
        </div>

        {isDirty && (
          <div className="rounded-lg border border-amber-500/20 bg-amber-500/10 px-4 py-3 text-sm text-amber-400">
            You have unsaved changes. Click "Save Changes" to apply them.
          </div>
        )}
      </div>
    </AdminLayout>
  );
}
