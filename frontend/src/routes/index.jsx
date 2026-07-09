import React from "react";
import { Routes, Route } from "react-router-dom";
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
import { ProtectedRoute } from "@/components/common/ProtectedRoute";

export default function AppRoutes() {
  return (
    <Routes>
      <Route path="/" element={<Landing />} />
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />
      <Route path="/forgot-password" element={<ForgotPassword />} />
      <Route path="/reset-password" element={<ResetPassword />} />
      <Route
        path="/profile"
        element={
          <ProtectedRoute>
            <Profile />
          </ProtectedRoute>
        }
      />
      <Route
        path="/resumes"
        element={
          <ProtectedRoute>
            <ResumeList />
          </ProtectedRoute>
        }
      />
      <Route
        path="/resumes/upload"
        element={
          <ProtectedRoute>
            <ResumeUpload />
          </ProtectedRoute>
        }
      />
      <Route
        path="/resumes/history"
        element={
          <ProtectedRoute>
            <UploadHistoryPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/resumes/:id"
        element={
          <ProtectedRoute>
            <ResumeDetails />
          </ProtectedRoute>
        }
      />
      <Route
        path="/resumes/:id/analysis"
        element={
          <ProtectedRoute>
            <AtsDashboard />
          </ProtectedRoute>
        }
      />
    </Routes>
  );
}

