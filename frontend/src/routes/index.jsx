import React, { lazy, Suspense } from "react";
import { Routes, Route } from "react-router-dom";
import { Loader2 } from "lucide-react";
import { ProtectedRoute } from "@/components/common/ProtectedRoute";
import { AdminRoute } from "@/components/common/AdminRoute";

// Lazy-load all public pages
const Landing = lazy(() => import("@/pages/Landing"));
const Login = lazy(() => import("@/pages/Login"));
const Register = lazy(() => import("@/pages/Register"));
const ForgotPassword = lazy(() => import("@/pages/ForgotPassword"));
const ResetPassword = lazy(() => import("@/pages/ResetPassword"));

// Lazy-load all protected pages
const Profile = lazy(() => import("@/pages/Profile"));
const ResumeUpload = lazy(() => import("@/pages/ResumeUpload"));
const ResumeList = lazy(() => import("@/pages/ResumeList"));
const ResumeDetails = lazy(() => import("@/pages/ResumeDetails"));
const UploadHistoryPage = lazy(() => import("@/pages/UploadHistoryPage"));
const AtsDashboard = lazy(() => import("@/pages/AtsDashboard"));
const JobMatching = lazy(() => import("@/pages/JobMatching"));
const AiAssistant = lazy(() => import("@/pages/AiAssistant"));
const Dashboard = lazy(() => import("@/pages/Dashboard"));

// Lazy-load all admin pages for performance (code splitting)
const AdminDashboard = lazy(() => import("@/pages/admin/AdminDashboard"));
const AdminUsers = lazy(() => import("@/pages/admin/AdminUsers"));
const AdminUserDetail = lazy(() => import("@/pages/admin/AdminUserDetail"));
const AdminAnalytics = lazy(() => import("@/pages/admin/AdminAnalytics"));
const AdminAIMonitoring = lazy(() => import("@/pages/admin/AdminAIMonitoring"));
const AdminAuditLogs = lazy(() => import("@/pages/admin/AdminAuditLogs"));
const AdminSettings = lazy(() => import("@/pages/admin/AdminSettings"));
const AdminNotifications = lazy(() => import("@/pages/admin/AdminNotifications"));

// 404 Page (Wait, creating a NotFound page was in the checklist!)
const NotFound = lazy(() => import("@/pages/NotFound"));

function GlobalSuspense({ children }) {
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
    <GlobalSuspense>
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
        <Route path="/admin" element={<AdminRoute><AdminDashboard /></AdminRoute>} />
        <Route path="/admin/users" element={<AdminRoute><AdminUsers /></AdminRoute>} />
        <Route path="/admin/users/:userId" element={<AdminRoute><AdminUserDetail /></AdminRoute>} />
        <Route path="/admin/analytics" element={<AdminRoute><AdminAnalytics /></AdminRoute>} />
        <Route path="/admin/ai-monitoring" element={<AdminRoute><AdminAIMonitoring /></AdminRoute>} />
        <Route path="/admin/audit-logs" element={<AdminRoute><AdminAuditLogs /></AdminRoute>} />
        <Route path="/admin/settings" element={<AdminRoute><AdminSettings /></AdminRoute>} />
        <Route path="/admin/notifications" element={<AdminRoute><AdminNotifications /></AdminRoute>} />

        {/* Global 404 Route */}
        <Route path="*" element={<NotFound />} />
      </Routes>
    </GlobalSuspense>
  );
}
