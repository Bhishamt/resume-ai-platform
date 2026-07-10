import React, { useCallback, useEffect, useState } from "react";
import { Filter, RefreshCw, Search } from "lucide-react";
import AdminLayout from "@/components/admin/AdminLayout";
import LogTable from "@/components/admin/LogTable";
import adminService from "@/services/adminService";

const ACTION_OPTIONS = [
  "disable_account",
  "enable_account",
  "change_role",
  "delete_account",
  "delete_resume",
  "update_settings",
  "update_user",
];

const ENTITY_OPTIONS = ["user", "resume", "system_setting", "notification"];

export default function AdminAuditLogs() {
  const [logs, setLogs] = useState([]);
  const [meta, setMeta] = useState({ total: 0, page: 1, per_page: 50, pages: 1 });
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [actionFilter, setActionFilter] = useState("");
  const [entityFilter, setEntityFilter] = useState("");

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const params = { page, per_page: 50 };
      if (actionFilter) params.action = actionFilter;
      if (entityFilter) params.entity = entityFilter;
      const data = await adminService.getLogs(params);
      setLogs(data.logs ?? []);
      setMeta(data.meta ?? { total: 0, page: 1, per_page: 50, pages: 1 });
    } finally {
      setLoading(false);
    }
  }, [page, actionFilter, entityFilter]);

  useEffect(() => { load(); }, [load]);

  const handleActionFilter = (v) => { setActionFilter(v); setPage(1); };
  const handleEntityFilter = (v) => { setEntityFilter(v); setPage(1); };

  return (
    <AdminLayout>
      <div className="px-6 py-8 max-w-screen-2xl mx-auto space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-white">Audit Logs</h1>
            <p className="text-sm text-white/40 mt-1">
              {meta.total.toLocaleString()} total entries
            </p>
          </div>
          <button
            onClick={load}
            className="flex items-center gap-2 rounded-lg border border-white/10 px-4 py-2 text-sm text-white/60 hover:text-white hover:border-white/20 transition-all"
          >
            <RefreshCw className={`h-4 w-4 ${loading ? "animate-spin" : ""}`} />
            Refresh
          </button>
        </div>

        {/* Filters */}
        <div className="flex flex-wrap items-center gap-3">
          <div className="flex items-center gap-2 text-sm text-white/40">
            <Filter className="h-4 w-4" />
            Filter:
          </div>
          <select
            value={actionFilter}
            onChange={(e) => handleActionFilter(e.target.value)}
            className="rounded-lg border border-white/10 bg-[#111] py-2 px-3 text-sm text-white/60 focus:border-indigo-500/50 focus:outline-none"
          >
            <option value="">All Actions</option>
            {ACTION_OPTIONS.map((a) => (
              <option key={a} value={a}>
                {a.replace(/_/g, " ")}
              </option>
            ))}
          </select>

          <select
            value={entityFilter}
            onChange={(e) => handleEntityFilter(e.target.value)}
            className="rounded-lg border border-white/10 bg-[#111] py-2 px-3 text-sm text-white/60 focus:border-indigo-500/50 focus:outline-none"
          >
            <option value="">All Entities</option>
            {ENTITY_OPTIONS.map((e) => (
              <option key={e} value={e}>
                {e}
              </option>
            ))}
          </select>

          {(actionFilter || entityFilter) && (
            <button
              onClick={() => { setActionFilter(""); setEntityFilter(""); setPage(1); }}
              className="text-xs text-white/40 hover:text-white transition-colors"
            >
              Clear
            </button>
          )}
        </div>

        <LogTable
          logs={logs}
          loading={loading}
          page={page}
          totalPages={meta.pages}
          onPageChange={setPage}
          total={meta.total}
        />
      </div>
    </AdminLayout>
  );
}
