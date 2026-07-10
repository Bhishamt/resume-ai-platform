import React from "react";
import { Shield } from "lucide-react";

const ACTION_COLORS = {
  disable_account: "text-amber-400",
  enable_account: "text-emerald-400",
  delete_account: "text-rose-400",
  change_role: "text-indigo-400",
  update_settings: "text-sky-400",
  delete_resume: "text-rose-400",
  update_user: "text-white/70",
};

const ENTITY_COLORS = {
  user: "bg-indigo-500/10 text-indigo-400 border-indigo-500/20",
  resume: "bg-amber-500/10 text-amber-400 border-amber-500/20",
  system_setting: "bg-sky-500/10 text-sky-400 border-sky-500/20",
  notification: "bg-emerald-500/10 text-emerald-400 border-emerald-500/20",
};

function ActionLabel({ action }) {
  const color = ACTION_COLORS[action] ?? "text-white/60";
  const label = action?.replace(/_/g, " ") ?? "—";
  return (
    <span className={`text-xs font-mono font-medium ${color}`}>{label}</span>
  );
}

function EntityBadge({ entity }) {
  const cls = ENTITY_COLORS[entity] ?? "bg-white/5 text-white/40 border-white/10";
  return (
    <span className={`inline-block rounded-md border px-2 py-0.5 text-xs font-medium ${cls}`}>
      {entity}
    </span>
  );
}

/**
 * LogTable — paginated audit log viewer.
 *
 * Props:
 *   logs        - array of AdminLogResponse
 *   loading     - boolean
 *   page        - number
 *   totalPages  - number
 *   onPageChange - (page) => void
 *   total       - number
 */
export default function LogTable({
  logs = [],
  loading = false,
  page = 1,
  totalPages = 1,
  onPageChange,
  total = 0,
}) {
  const skeletonRows = Array.from({ length: 8 });

  return (
    <div className="rounded-xl border border-white/5 bg-white/[0.03] overflow-hidden">
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="border-b border-white/5">
              <th className="px-5 py-3 text-left text-xs font-medium text-white/40 uppercase tracking-wider">
                Timestamp
              </th>
              <th className="px-5 py-3 text-left text-xs font-medium text-white/40 uppercase tracking-wider">
                Action
              </th>
              <th className="px-5 py-3 text-left text-xs font-medium text-white/40 uppercase tracking-wider hidden md:table-cell">
                Entity
              </th>
              <th className="px-5 py-3 text-left text-xs font-medium text-white/40 uppercase tracking-wider hidden lg:table-cell">
                Target ID
              </th>
              <th className="px-5 py-3 text-left text-xs font-medium text-white/40 uppercase tracking-wider hidden xl:table-cell">
                IP Address
              </th>
              <th className="px-5 py-3 text-left text-xs font-medium text-white/40 uppercase tracking-wider hidden xl:table-cell">
                Admin
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-white/5">
            {loading
              ? skeletonRows.map((_, i) => (
                  <tr key={i} className="animate-pulse">
                    <td className="px-5 py-3.5">
                      <div className="h-3 w-32 rounded bg-white/5" />
                    </td>
                    <td className="px-5 py-3.5">
                      <div className="h-3 w-28 rounded bg-white/5" />
                    </td>
                    <td className="px-5 py-3.5 hidden md:table-cell">
                      <div className="h-5 w-16 rounded bg-white/5" />
                    </td>
                    <td className="px-5 py-3.5 hidden lg:table-cell">
                      <div className="h-3 w-24 rounded bg-white/5" />
                    </td>
                    <td className="px-5 py-3.5 hidden xl:table-cell">
                      <div className="h-3 w-24 rounded bg-white/5" />
                    </td>
                    <td className="px-5 py-3.5 hidden xl:table-cell">
                      <div className="h-3 w-20 rounded bg-white/5" />
                    </td>
                  </tr>
                ))
              : logs.map((log) => (
                  <tr
                    key={log.id}
                    className="hover:bg-white/[0.02] transition-colors"
                  >
                    <td className="px-5 py-3.5 text-xs text-white/40 whitespace-nowrap">
                      {log.created_at
                        ? new Date(log.created_at).toLocaleString()
                        : "—"}
                    </td>
                    <td className="px-5 py-3.5">
                      <ActionLabel action={log.action} />
                    </td>
                    <td className="px-5 py-3.5 hidden md:table-cell">
                      <EntityBadge entity={log.entity} />
                    </td>
                    <td className="px-5 py-3.5 hidden lg:table-cell text-xs text-white/30 font-mono truncate max-w-[120px]">
                      {log.entity_id ?? "—"}
                    </td>
                    <td className="px-5 py-3.5 hidden xl:table-cell text-xs text-white/30 font-mono">
                      {log.ip_address ?? "—"}
                    </td>
                    <td className="px-5 py-3.5 hidden xl:table-cell">
                      {log.admin_id ? (
                        <div className="flex items-center gap-1.5">
                          <Shield className="h-3 w-3 text-indigo-400" />
                          <span className="text-xs text-white/40 font-mono truncate max-w-[100px]">
                            {String(log.admin_id).slice(0, 8)}…
                          </span>
                        </div>
                      ) : (
                        <span className="text-xs text-white/20">system</span>
                      )}
                    </td>
                  </tr>
                ))}

            {!loading && logs.length === 0 && (
              <tr>
                <td
                  colSpan={6}
                  className="px-5 py-12 text-center text-sm text-white/30"
                >
                  No audit logs found.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {totalPages > 1 && (
        <div className="flex items-center justify-between px-5 py-4 border-t border-white/5">
          <p className="text-xs text-white/30">
            {total.toLocaleString()} total entries
          </p>
          <div className="flex items-center gap-2">
            <button
              disabled={page <= 1}
              onClick={() => onPageChange?.(page - 1)}
              className="rounded-lg border border-white/10 px-3 py-1.5 text-xs text-white/60 hover:text-white disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
            >
              Previous
            </button>
            <span className="text-xs text-white/40">
              {page} / {totalPages}
            </span>
            <button
              disabled={page >= totalPages}
              onClick={() => onPageChange?.(page + 1)}
              className="rounded-lg border border-white/10 px-3 py-1.5 text-xs text-white/60 hover:text-white disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
            >
              Next
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
