import React, { useCallback, useEffect, useState } from "react";
import { Search, RefreshCw, AlertCircle, CheckCircle2 } from "lucide-react";
import AdminLayout from "@/components/admin/AdminLayout";
import UserTable from "@/components/admin/UserTable";
import adminService from "@/services/adminService";

export default function AdminUsers() {
  const [users, setUsers] = useState([]);
  const [meta, setMeta] = useState({ total: 0, page: 1, per_page: 20, pages: 1 });
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [roleFilter, setRoleFilter] = useState("");
  const [activeFilter, setActiveFilter] = useState("");
  const [page, setPage] = useState(1);
  const [toast, setToast] = useState(null);

  const showToast = (message, type = "success") => {
    setToast({ message, type });
    setTimeout(() => setToast(null), 3500);
  };

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const params = { page, per_page: 20 };
      if (search) params.search = search;
      if (roleFilter) params.role = roleFilter;
      if (activeFilter !== "") params.is_active = activeFilter === "true";
      const data = await adminService.getUsers(params);
      setUsers(data.users ?? []);
      setMeta(data.meta ?? { total: 0, page: 1, per_page: 20, pages: 1 });
    } catch {
      showToast("Failed to load users.", "error");
    } finally {
      setLoading(false);
    }
  }, [page, search, roleFilter, activeFilter]);

  useEffect(() => {
    load();
  }, [load]);

  // Reset to page 1 on filter change
  const handleSearch = (v) => { setSearch(v); setPage(1); };
  const handleRoleFilter = (v) => { setRoleFilter(v); setPage(1); };
  const handleActiveFilter = (v) => { setActiveFilter(v); setPage(1); };

  const handleAction = async (user, action) => {
    try {
      if (action === "delete") {
        if (!window.confirm(`Permanently delete ${user.email}? This cannot be undone.`)) return;
        await adminService.deleteUser(user.id);
        showToast(`User ${user.email} deleted.`);
      } else if (action === "disable") {
        await adminService.updateUser(user.id, { is_active: false });
        showToast(`${user.email} disabled.`);
      } else if (action === "enable") {
        await adminService.updateUser(user.id, { is_active: true });
        showToast(`${user.email} enabled.`, "success");
      } else if (action === "makeAdmin") {
        await adminService.updateUser(user.id, { role: "admin" });
        showToast(`${user.email} granted admin.`);
      } else if (action === "makeUser") {
        await adminService.updateUser(user.id, { role: "user" });
        showToast(`${user.email} role set to user.`);
      }
      load();
    } catch (err) {
      showToast(err?.response?.data?.message ?? "Action failed.", "error");
    }
  };

  return (
    <AdminLayout>
      <div className="px-6 py-8 max-w-screen-2xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-white">User Management</h1>
            <p className="text-sm text-white/40 mt-1">
              {meta.total.toLocaleString()} total users
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

        {/* Toast */}
        {toast && (
          <div
            className={`flex items-center gap-3 rounded-lg border px-4 py-3 text-sm transition-all ${
              toast.type === "error"
                ? "border-rose-500/20 bg-rose-500/10 text-rose-400"
                : "border-emerald-500/20 bg-emerald-500/10 text-emerald-400"
            }`}
          >
            {toast.type === "error" ? (
              <AlertCircle className="h-4 w-4" />
            ) : (
              <CheckCircle2 className="h-4 w-4" />
            )}
            {toast.message}
          </div>
        )}

        {/* Filters */}
        <div className="flex flex-wrap items-center gap-3">
          <div className="relative flex-1 min-w-[200px] max-w-sm">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-white/30" />
            <input
              type="text"
              placeholder="Search by name or email…"
              value={search}
              onChange={(e) => handleSearch(e.target.value)}
              className="w-full rounded-lg border border-white/10 bg-white/[0.03] py-2 pl-9 pr-4 text-sm text-white placeholder-white/30 focus:border-indigo-500/50 focus:outline-none focus:ring-1 focus:ring-indigo-500/20"
            />
          </div>

          <select
            value={roleFilter}
            onChange={(e) => handleRoleFilter(e.target.value)}
            className="rounded-lg border border-white/10 bg-[#111] py-2 px-3 text-sm text-white/60 focus:border-indigo-500/50 focus:outline-none"
          >
            <option value="">All Roles</option>
            <option value="user">User</option>
            <option value="admin">Admin</option>
          </select>

          <select
            value={activeFilter}
            onChange={(e) => handleActiveFilter(e.target.value)}
            className="rounded-lg border border-white/10 bg-[#111] py-2 px-3 text-sm text-white/60 focus:border-indigo-500/50 focus:outline-none"
          >
            <option value="">All Status</option>
            <option value="true">Active</option>
            <option value="false">Disabled</option>
          </select>

          {(search || roleFilter || activeFilter) && (
            <button
              onClick={() => { setSearch(""); setRoleFilter(""); setActiveFilter(""); setPage(1); }}
              className="text-xs text-white/40 hover:text-white transition-colors"
            >
              Clear filters
            </button>
          )}
        </div>

        {/* Table */}
        <UserTable
          users={users}
          loading={loading}
          onAction={handleAction}
          page={page}
          totalPages={meta.pages}
          onPageChange={setPage}
          total={meta.total}
        />
      </div>
    </AdminLayout>
  );
}
