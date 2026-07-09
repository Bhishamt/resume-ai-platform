import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useForm } from "react-hook-form";
import { useAuth } from "@/context/AuthContext";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Mail,
  Lock,
  User,
  ArrowRight,
  AlertCircle,
  Check,
  X,
} from "lucide-react";

const PASSWORD_RULES = [
  { label: "At least 8 characters", test: (v) => v.length >= 8 },
  { label: "One uppercase letter", test: (v) => /[A-Z]/.test(v) },
  { label: "One lowercase letter", test: (v) => /[a-z]/.test(v) },
  { label: "One digit", test: (v) => /\d/.test(v) },
  {
    label: "One special character",
    test: (v) => /[!@#$%^&*()_+\-=[\]{};':"\\|,.<>/?`~]/.test(v),
  },
];

export default function Register() {
  const navigate = useNavigate();
  const { register: registerUser } = useAuth();
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const {
    register,
    handleSubmit,
    watch,
    formState: { errors },
  } = useForm();

  const password = watch("password", "");

  const onSubmit = async (data) => {
    if (data.password !== data.confirmPassword) {
      setError("Passwords do not match.");
      return;
    }

    setError("");
    setIsLoading(true);
    try {
      await registerUser({
        full_name: data.full_name,
        email: data.email,
        password: data.password,
      });
      navigate("/login", {
        state: { message: "Registration successful! Please sign in." },
      });
    } catch (err) {
      const message =
        err.response?.data?.message || "Registration failed. Please try again.";
      setError(message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-[#050505] px-4 py-12">
      {/* Background accents */}
      <div className="pointer-events-none fixed inset-0 overflow-hidden">
        <div className="absolute -top-40 -right-40 h-80 w-80 rounded-full bg-white/[0.02] blur-3xl" />
        <div className="absolute -bottom-40 -left-40 h-80 w-80 rounded-full bg-white/[0.02] blur-3xl" />
      </div>

      <div className="relative w-full max-w-md">
        {/* Logo */}
        <div className="mb-8 flex items-center justify-center gap-3">
          <Link to="/" className="flex items-center gap-2">
            <div className="h-8 w-8 rounded-lg bg-gradient-to-br from-white to-white/50" />
            <span className="text-xl font-semibold tracking-tight text-white">
              ResumeAI
            </span>
          </Link>
        </div>

        {/* Card */}
        <div className="glass-panel p-8">
          <div className="mb-8 text-center">
            <h1 className="text-2xl font-semibold text-white">
              Create your account
            </h1>
            <p className="mt-2 text-sm text-white/55">
              Start optimizing your resume with AI
            </p>
          </div>

          {/* Error Alert */}
          {error && (
            <div className="mb-6 flex items-center gap-3 rounded-[var(--radius-sm)] border border-red-500/20 bg-red-500/10 p-3">
              <AlertCircle className="h-4 w-4 shrink-0 text-red-400" />
              <p className="text-sm text-red-400">{error}</p>
            </div>
          )}

          <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">
            {/* Full Name */}
            <div className="space-y-2">
              <label
                htmlFor="register-name"
                className="text-sm font-medium text-white/75"
              >
                Full Name
              </label>
              <div className="relative">
                <User className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-white/40" />
                <Input
                  id="register-name"
                  type="text"
                  placeholder="John Doe"
                  className="pl-10"
                  {...register("full_name", {
                    required: "Full name is required.",
                    minLength: {
                      value: 2,
                      message: "Name must be at least 2 characters.",
                    },
                  })}
                />
              </div>
              {errors.full_name && (
                <p className="text-xs text-red-400">
                  {errors.full_name.message}
                </p>
              )}
            </div>

            {/* Email */}
            <div className="space-y-2">
              <label
                htmlFor="register-email"
                className="text-sm font-medium text-white/75"
              >
                Email
              </label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-white/40" />
                <Input
                  id="register-email"
                  type="email"
                  placeholder="you@example.com"
                  className="pl-10"
                  {...register("email", {
                    required: "Email is required.",
                    pattern: {
                      value: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
                      message: "Please enter a valid email.",
                    },
                  })}
                />
              </div>
              {errors.email && (
                <p className="text-xs text-red-400">{errors.email.message}</p>
              )}
            </div>

            {/* Password */}
            <div className="space-y-2">
              <label
                htmlFor="register-password"
                className="text-sm font-medium text-white/75"
              >
                Password
              </label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-white/40" />
                <Input
                  id="register-password"
                  type="password"
                  placeholder="••••••••"
                  className="pl-10"
                  {...register("password", {
                    required: "Password is required.",
                    minLength: {
                      value: 8,
                      message: "Password must be at least 8 characters.",
                    },
                  })}
                />
              </div>
              {errors.password && (
                <p className="text-xs text-red-400">
                  {errors.password.message}
                </p>
              )}

              {/* Password Strength Indicator */}
              {password.length > 0 && (
                <div className="mt-3 space-y-1.5 rounded-[var(--radius-sm)] border border-white/5 bg-white/[0.02] p-3">
                  {PASSWORD_RULES.map((rule) => {
                    const passed = rule.test(password);
                    return (
                      <div
                        key={rule.label}
                        className="flex items-center gap-2"
                      >
                        {passed ? (
                          <Check className="h-3.5 w-3.5 text-green-400" />
                        ) : (
                          <X className="h-3.5 w-3.5 text-white/30" />
                        )}
                        <span
                          className={`text-xs ${
                            passed ? "text-green-400" : "text-white/40"
                          }`}
                        >
                          {rule.label}
                        </span>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>

            {/* Confirm Password */}
            <div className="space-y-2">
              <label
                htmlFor="register-confirm"
                className="text-sm font-medium text-white/75"
              >
                Confirm Password
              </label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-white/40" />
                <Input
                  id="register-confirm"
                  type="password"
                  placeholder="••••••••"
                  className="pl-10"
                  {...register("confirmPassword", {
                    required: "Please confirm your password.",
                  })}
                />
              </div>
              {errors.confirmPassword && (
                <p className="text-xs text-red-400">
                  {errors.confirmPassword.message}
                </p>
              )}
            </div>

            <Button
              type="submit"
              className="w-full rounded-full"
              isLoading={isLoading}
            >
              Create Account
              {!isLoading && <ArrowRight className="ml-2 h-4 w-4" />}
            </Button>
          </form>

          <p className="mt-6 text-center text-sm text-white/50">
            Already have an account?{" "}
            <Link
              to="/login"
              className="font-medium text-white transition-colors hover:text-white/80"
            >
              Sign in
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
