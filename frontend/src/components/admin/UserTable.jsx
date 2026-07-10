import React from "react";
import { useNavigate } from "react-router-dom";
import { CheckCircle2, XCircle, ShieldCheck, User, MoreHorizontal } from "lucide-react";

function RoleBadge({ role }) {
  return role === "admin" ? (
    <span className="inline-flex items-center gap-1 rounded-full bg-indigo-500/10 border border-indigo-500/20 px-2 py-0.5 text-xs font-medium text-indigo-400">
      <ShieldCheck className="h-3 w-3" />
      Admin
    </span>
  ) : (
    <span className="inline-flex items-center gap-1 rounded-full bg-white/5 border border-white/10 px-2 py-0.5 text-xs font-medium text-white/50">
      <User className="h-3 w-3" />
      User
    </span>
  );
}

function StatusDot({ isActive }) {
  return isActive ? (
    <span className="inline-flex items-center gap-1 text-xs text-emerald-400">
      <CheckCircle2 className="h-3 w-3" />
      Active
    </span>
  ) : (
    <span className="inline-flex items-center gap-1 text-xs text-rose-400">
      <XCircle className="h-3 w-3" />
      Disabled
    </span>
  );
}

/**
 * UserTable — renders a paginated user list for the admin panel.
 *
 * Props:
 *   users      - array of AdminUserResponse
 *   loading    - boolean
 *   onAction   - (user, action) => void, action: "view"|"enable"|"disable"|"makeAdmin"|"delete"
 *   page       - current page number
 *   totalPages - total pages
 *   onPageChange - (page) => void
 */
export default function UserTable({
  users = [],
  loading = false,
  onAction,
  page = 1,
  totalPages = 1,
  onPageChange,
  total = 0,
}) {
  const navigate = useNavigate();
  const [openMenu, setOpenMenu] = React.useState(null);

  const skeletonRows = Array.from({ length: 5 });

  return (
    <div className="rounded-xl border border-white/5 bg-white/[0.03] overflow-hidden">
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="border-b border-white/5">
              <th className="px-5 py-3 text-left text-xs font-medium text-white/40 uppercase tracking-wider">
                User
              </th>
              <th className="px-5 py-3 text-left text-xs font-medium text-white/40 uppercase tracking-wider hidden md:table-cell">
                Role
              </th>
              <th className="px-5 py-3 text-left text-xs font-medium text-white/40 uppercase tracking-wider hidden md:table-cell">
                Status
              </th>
              <th className="px-5 py-3 text-left text-xs font-medium text-white/40 uppercase tracking-wider hidden lg:table-cell">
                Joined
              </th>
              <th className="px-5 py-3 text-left text-xs font-medium text-white/40 uppercase tracking-wider hidden lg:table-cell">
                Last Login
              </th>
              <th className="px-5 py-3 text-right text-xs font-medium text-white/40 uppercase tracking-wider">
                Actions
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-white/5">
            {loading
              ? skeletonRows.map((_, i) => (
                  <tr key={i} className="animate-pulse">
                    <td className="px-5 py-4">
                      <div className="flex items-center gap-3">
                        <div className="h-8 w-8 rounded-full bg-white/5" />
                        <div className="space-y-1.5">
                          <div className="h-3 w-28 rounded bg-white/5" />
                          <div className="h-3 w-36 rounded bg-white/5" />
                        </div>
                      </div>
                    </td>
                    <td className="px-5 py-4 hidden md:table-cell">
                      <div className="h-5 w-16 rounded-full bg-white/5" />
                    </td>
                    <td className="px-5 py-4 hidden md:table-cell">
                      <div className="h-4 w-14 rounded bg-white/5" />
                    </td>
                    <td className="px-5 py-4 hidden lg:table-cell">
                      <div className="h-3 w-20 rounded bg-white/5" />
                    </td>
                    <td className="px-5 py-4 hidden lg:table-cell">
                      <div className="h-3 w-20 rounded bg-white/5" />
                    </td>
                    <td className="px-5 py-4" />
                  </tr>
                ))
              : users.map((u) => (
                  <tr
                    key={u.id}
                    className="group hover:bg-white/[0.02] transition-colors"
                  >
                    <td className="px-5 py-4">
                      <div className="flex items-center gap-3">
                        <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-indigo-500/20 text-xs font-semibold text-indigo-300">
                          {u.full_name?.[0]?.toUpperCase() ?? "?"}
                        </div>
                        <div>
                          <p className="text-sm font-medium text-white">
                            {u.full_name}
                          </p>
                          <p className="text-xs text-white/40">{u.email}</p>
                        </div>
                      </div>
                    </td>
                    <td className="px-5 py-4 hidden md:table-cell">
                      <RoleBadge role={u.role} />
                    </td>
                    <td className="px-5 py-4 hidden md:table-cell">
                      <StatusDot isActive={u.is_active} />
                    </td>
                    <td className="px-5 py-4 hidden lg:table-cell text-xs text-white/40">
                      {u.created_at
                        ? new Date(u.created_at).toLocaleDateString()
                        : "—"}
                    </td>
                    <td className="px-5 py-4 hidden lg:table-cell text-xs text-white/40">
                      {u.last_login
                        ? new Date(u.last_login).toLocaleDateString()
                        : "Never"}
                    </td>
                    <td className="px-5 py-4 text-right">
                      <div className="relative inline-block">
                        <button
                          onClick={() =>
                            setOpenMenu(openMenu === u.id ? null : u.id)
                          }
                          className="rounded-lg p-1.5 text-white/40 hover:text-white hover:bg-white/5 transition-colors"
                        >
                          <MoreHorizontal className="h-4 w-4" />
                        </button>
                        {openMenu === u.id && (
                          <div
                            className="absolute right-0 top-8 z-20 w-44 rounded-lg border border-white/10 bg-[#111] shadow-xl"
                            onMouseLeave={() => setOpenMenu(null)}
                          >
                            <button
                              className="flex w-full items-center gap-2 px-3 py-2 text-sm text-white/70 hover:text-white hover:bg-white/5 transition-colors"
                              onClick={() => {
                                navigate(`/admin/users/${u.id}`);
                                setOpenMenu(null);
                              }}
                            >
                              View Details
                            </button>
                            <button
                              className="flex w-full items-center gap-2 px-3 py-2 text-sm text-white/70 hover:text-white hover:bg-white/5 transition-colors"
                              onClick={() => {
                                onAction?.(u, u.is_active ? "disable" : "enable");
                                setOpenMenu(null);
                              }}
                            >
                              {u.is_active ? "Disable Account" : "Enable Account"}
                            </button>
                            <button
                              className="flex w-full items-center gap-2 px-3 py-2 text-sm text-white/70 hover:text-white hover:bg-white/5 transition-colors"
                              onClick={() => {
                                onAction?.(
                                  u,
                                  u.role === "admin" ? "makeUser" : "makeAdmin"
                                );
                                setOpenMenu(null);
                              }}
                            >
                              {u.role === "admin"
                                ? "Revoke Admin"
                                : "Grant Admin"}
                            </button>
                            <div className="border-t border-white/5 my-1" />
                            <button
                              className="flex w-full items-center gap-2 px-3 py-2 text-sm text-rose-400 hover:bg-rose-500/10 transition-colors"
                              onClick={() => {
                                onAction?.(u, "delete");
                                setOpenMenu(null);
                              }}
                            >
                              Delete Account
                            </button>
                          </div>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}

            {!loading && users.length === 0 && (
              <tr>
                <td colSpan={6} className="px-5 py-12 text-center text-sm text-white/30">
                  No users found.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-between px-5 py-4 border-t border-white/5">
          <p className="text-xs text-white/30">
            {total.toLocaleString()} total users
          </p>
          <div className="flex items-center gap-2">
            <button
              disabled={page <= 1}
              onClick={() => onPageChange?.(page - 1)}
              className="rounded-lg border border-white/10 px-3 py-1.5 text-xs text-white/60 hover:text-white hover:border-white/20 disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
            >
              Previous
            </button>
            <span className="text-xs text-white/40">
              {page} / {totalPages}
            </span>
            <button
              disabled={page >= totalPages}
              onClick={() => onPageChange?.(page + 1)}
              className="rounded-lg border border-white/10 px-3 py-1.5 text-xs text-white/60 hover:text-white hover:border-white/20 disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
            >
              Next
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
