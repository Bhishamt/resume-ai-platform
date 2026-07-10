import React, { lazy, Suspense } from "react";
import { Routes, Route } from "react-router-dom";
import { Loader2 } from "lucide-react";
import Landing from "@/pages/Landing";
import Login from "@/pages/Login";
import Register from "@/pages/Register";
import ForgotPassword from "@/pages/ForgotPassword";
import ResetPassword from "@/pages/ResetPassword";
import Profile from "@/pages/Profile";
import ResumeUpload from "@/pages/ResumeUpload";
import ResumeList from "@/pages/ResumeList";
import ResumeDetails from "@/pages/ResumeDetails";
import UploadHistoryPage from "@/pages/UploadHistoryPage";
import AtsDashboard from "@/pages/AtsDashboard";
import JobMatching from "@/pages/JobMatching";
import AiAssistant from "@/pages/AiAssistant";
import Dashboard from "@/pages/Dashboard";
import { ProtectedRoute } from "@/components/common/ProtectedRoute";
import { AdminRoute } from "@/components/common/AdminRoute";

// Lazy-load all admin pages for performance (code splitting)
const AdminDashboard = lazy(() => import("@/pages/admin/AdminDashboard"));
const AdminUsers = lazy(() => import("@/pages/admin/AdminUsers"));
const AdminUserDetail = lazy(() => import("@/pages/admin/AdminUserDetail"));
const AdminAnalytics = lazy(() => import("@/pages/admin/AdminAnalytics"));
const AdminAIMonitoring = lazy(() => import("@/pages/admin/AdminAIMonitoring"));
const AdminAuditLogs = lazy(() => import("@/pages/admin/AdminAuditLogs"));
const AdminSettings = lazy(() => import("@/pages/admin/AdminSettings"));
const AdminNotifications = lazy(() => import("@/pages/admin/AdminNotifications"));

function AdminSuspense({ children }) {
  return (
    <Suspense
      fallback={
        <div className="flex min-h-screen items-center justify-center bg-[#050505]">
          <Loader2 className="h-7 w-7 animate-spin text-white/30" />
        </div>
      }
    >
      {children}
    </Suspense>
  );
}

export default function AppRoutes() {
  return (
    <Routes>
      {/* Public routes */}
      <Route path="/" element={<Landing />} />
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />
      <Route path="/forgot-password" element={<ForgotPassword />} />
      <Route path="/reset-password" element={<ResetPassword />} />

      {/* Protected user routes */}
      <Route path="/profile" element={<ProtectedRoute><Profile /></ProtectedRoute>} />
      <Route path="/resumes" element={<ProtectedRoute><ResumeList /></ProtectedRoute>} />
      <Route path="/resumes/upload" element={<ProtectedRoute><ResumeUpload /></ProtectedRoute>} />
      <Route path="/resumes/history" element={<ProtectedRoute><UploadHistoryPage /></ProtectedRoute>} />
      <Route path="/resumes/:id" element={<ProtectedRoute><ResumeDetails /></ProtectedRoute>} />
      <Route path="/resumes/:id/analysis" element={<ProtectedRoute><AtsDashboard /></ProtectedRoute>} />
      <Route path="/job-matching" element={<ProtectedRoute><JobMatching /></ProtectedRoute>} />
      <Route path="/ai-assistant" element={<ProtectedRoute><AiAssistant /></ProtectedRoute>} />
      <Route path="/dashboard" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />

      {/* Admin-only routes — protected by AdminRoute (role === "admin") */}
      <Route
        path="/admin"
        element={
          <AdminRoute>
            <AdminSuspense>
              <AdminDashboard />
            </AdminSuspense>
          </AdminRoute>
        }
      />
      <Route
        path="/admin/users"
        element={
          <AdminRoute>
            <AdminSuspense>
              <AdminUsers />
            </AdminSuspense>
          </AdminRoute>
        }
      />
      <Route
        path="/admin/users/:userId"
        element={
          <AdminRoute>
            <AdminSuspense>
              <AdminUserDetail />
            </AdminSuspense>
          </AdminRoute>
        }
      />
      <Route
        path="/admin/analytics"
        element={
          <AdminRoute>
            <AdminSuspense>
              <AdminAnalytics />
            </AdminSuspense>
          </AdminRoute>
        }
      />
      <Route
        path="/admin/ai-monitoring"
        element={
          <AdminRoute>
            <AdminSuspense>
              <AdminAIMonitoring />
            </AdminSuspense>
          </AdminRoute>
        }
      />
      <Route
        path="/admin/audit-logs"
        element={
          <AdminRoute>
            <AdminSuspense>
              <AdminAuditLogs />
            </AdminSuspense>
          </AdminRoute>
        }
      />
      <Route
        path="/admin/settings"
        element={
          <AdminRoute>
            <AdminSuspense>
              <AdminSettings />
            </AdminSuspense>
          </AdminRoute>
        }
      />
      <Route
        path="/admin/notifications"
        element={
          <AdminRoute>
            <AdminSuspense>
              <AdminNotifications />
            </AdminSuspense>
          </AdminRoute>
        }
      />
    </Routes>
  );
}
