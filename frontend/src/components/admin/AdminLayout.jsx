import React, { useState } from "react";
import { NavLink, useNavigate } from "react-router-dom";
import { useAuth } from "@/context/AuthContext";
import {
  LayoutDashboard,
  Users,
  BarChart3,
  Brain,
  FileText,
  Settings,
  Bell,
  Shield,
  LogOut,
  Menu,
  X,
  ChevronRight,
} from "lucide-react";

const NAV_ITEMS = [
  { to: "/admin", label: "Dashboard", icon: LayoutDashboard, exact: true },
  { to: "/admin/users", label: "Users", icon: Users },
  { to: "/admin/analytics", label: "Analytics", icon: BarChart3 },
  { to: "/admin/ai-monitoring", label: "AI Monitor", icon: Brain },
  { to: "/admin/audit-logs", label: "Audit Logs", icon: FileText },
  { to: "/admin/settings", label: "Settings", icon: Settings },
  { to: "/admin/notifications", label: "Notifications", icon: Bell },
];

function NavItem({ item, collapsed }) {
  const Icon = item.icon;
  return (
    <NavLink
      to={item.to}
      end={item.exact}
      className={({ isActive }) =>
        `flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-all duration-200 ${
          isActive
            ? "bg-indigo-600/20 text-indigo-400 border border-indigo-500/30"
            : "text-white/60 hover:text-white hover:bg-white/5"
        } ${collapsed ? "justify-center" : ""}`
      }
    >
      <Icon className="h-4 w-4 shrink-0" />
      {!collapsed && <span>{item.label}</span>}
    </NavLink>
  );
}

export default function AdminLayout({ children }) {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [collapsed, setCollapsed] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  const sidebarContent = (
    <div className="flex h-full flex-col">
      {/* Header */}
      <div className="flex items-center gap-3 px-4 py-5 border-b border-white/5">
        <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-indigo-600/20 border border-indigo-500/30 shrink-0">
          <Shield className="h-4 w-4 text-indigo-400" />
        </div>
        {!collapsed && (
          <div className="min-w-0">
            <p className="text-sm font-semibold text-white truncate">Admin Panel</p>
            <p className="text-xs text-white/40 truncate">System Control</p>
          </div>
        )}
        <button
          onClick={() => setCollapsed((c) => !c)}
          className="ml-auto hidden lg:flex h-7 w-7 items-center justify-center rounded-md text-white/40 hover:text-white hover:bg-white/5 transition-colors shrink-0"
        >
          <ChevronRight
            className={`h-4 w-4 transition-transform ${collapsed ? "" : "rotate-180"}`}
          />
        </button>
      </div>

      {/* Navigation */}
      <nav className="flex-1 space-y-1 px-3 py-4 overflow-y-auto">
        {NAV_ITEMS.map((item) => (
          <NavItem key={item.to} item={item} collapsed={collapsed} />
        ))}
      </nav>

      {/* User */}
      <div className="border-t border-white/5 px-3 py-4 space-y-2">
        <div
          className={`flex items-center gap-3 px-3 py-2 rounded-lg bg-white/5 ${
            collapsed ? "justify-center" : ""
          }`}
        >
          <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-indigo-600/30 text-xs font-semibold text-indigo-300">
            {user?.full_name?.[0]?.toUpperCase() ?? "A"}
          </div>
          {!collapsed && (
            <div className="min-w-0">
              <p className="text-xs font-medium text-white truncate">
                {user?.full_name}
              </p>
              <p className="text-xs text-white/40 truncate">{user?.email}</p>
            </div>
          )}
        </div>
        <button
          onClick={handleLogout}
          className={`flex w-full items-center gap-3 rounded-lg px-3 py-2 text-sm text-white/60 hover:text-red-400 hover:bg-red-500/10 transition-all ${
            collapsed ? "justify-center" : ""
          }`}
        >
          <LogOut className="h-4 w-4 shrink-0" />
          {!collapsed && <span>Logout</span>}
        </button>
      </div>
    </div>
  );

  return (
    <div className="flex min-h-screen bg-[#050505]">
      {/* Desktop Sidebar */}
      <aside
        className={`hidden lg:flex flex-col border-r border-white/5 bg-[#0a0a0a] transition-all duration-300 shrink-0 ${
          collapsed ? "w-16" : "w-60"
        }`}
      >
        {sidebarContent}
      </aside>

      {/* Mobile overlay */}
      {mobileOpen && (
        <div
          className="fixed inset-0 z-40 bg-black/60 lg:hidden"
          onClick={() => setMobileOpen(false)}
        />
      )}

      {/* Mobile Sidebar */}
      <aside
        className={`fixed inset-y-0 left-0 z-50 w-64 flex flex-col border-r border-white/5 bg-[#0a0a0a] transition-transform duration-300 lg:hidden ${
          mobileOpen ? "translate-x-0" : "-translate-x-full"
        }`}
      >
        <button
          onClick={() => setMobileOpen(false)}
          className="absolute right-3 top-3 p-2 text-white/40 hover:text-white"
        >
          <X className="h-5 w-5" />
        </button>
        {sidebarContent}
      </aside>

      {/* Main content */}
      <div className="flex flex-1 flex-col min-w-0">
        {/* Mobile topbar */}
        <header className="flex items-center gap-3 border-b border-white/5 px-4 py-3 lg:hidden">
          <button
            onClick={() => setMobileOpen(true)}
            className="p-2 text-white/60 hover:text-white"
          >
            <Menu className="h-5 w-5" />
          </button>
          <div className="flex items-center gap-2">
            <Shield className="h-4 w-4 text-indigo-400" />
            <span className="text-sm font-semibold text-white">Admin Panel</span>
          </div>
        </header>

        {/* Page content */}
        <main className="flex-1 overflow-y-auto">{children}</main>
      </div>
    </div>
  );
}
