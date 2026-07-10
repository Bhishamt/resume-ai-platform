import React from "react";
import { Navigate } from "react-router-dom";
import { useAuth } from "@/context/AuthContext";
import { Loader2, ShieldOff } from "lucide-react";

/**
 * AdminRoute — guards routes that require admin role.
 *
 * Renders children only when:
 * 1. User is authenticated (token valid)
 * 2. user.role === "admin"
 *
 * Otherwise redirects to /login (unauthenticated) or /dashboard (forbidden).
 */
export function AdminRoute({ children }) {
  const { isAuthenticated, isLoading, user } = useAuth();

  if (isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-[#050505]">
        <div className="flex flex-col items-center gap-4">
          <Loader2 className="h-8 w-8 animate-spin text-white/50" />
          <p className="text-sm text-white/50">Loading...</p>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  if (user?.role !== "admin") {
    return (
      <div className="flex min-h-screen items-center justify-center bg-[#050505]">
        <div className="flex flex-col items-center gap-4 text-center px-4">
          <ShieldOff className="h-12 w-12 text-red-400" />
          <h2 className="text-xl font-semibold text-white">Access Denied</h2>
          <p className="text-sm text-white/50 max-w-xs">
            You need administrator privileges to access this area.
          </p>
          <a
            href="/dashboard"
            className="mt-2 rounded-lg bg-white/10 px-5 py-2 text-sm font-medium text-white hover:bg-white/20 transition-colors"
          >
            Back to Dashboard
          </a>
        </div>
      </div>
    );
  }

  return children;
}
