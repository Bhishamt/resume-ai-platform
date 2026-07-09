import React, { useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { useForm } from "react-hook-form";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Lock, ArrowLeft, CheckCircle, AlertCircle, Check, X } from "lucide-react";
import authService from "@/services/authService";

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

export default function ResetPassword() {
  const [searchParams] = useSearchParams();
  const [isLoading, setIsLoading] = useState(false);
  const [isSubmitted, setIsSubmitted] = useState(false);
  const [error, setError] = useState("");

  const token = searchParams.get("token");

  const {
    register,
    handleSubmit,
    watch,
    formState: { errors },
  } = useForm();

  const password = watch("password", "");

  const onSubmit = async (data) => {
    if (!token) {
      setError("Reset token is missing from the URL.");
      return;
    }
    if (data.password !== data.confirmPassword) {
      setError("Passwords do not match.");
      return;
    }

    setError("");
    setIsLoading(true);
    try {
      await authService.resetPassword({
        token,
        new_password: data.password,
      });
      setIsSubmitted(true);
    } catch (err) {
      const message =
        err.response?.data?.message ||
        "Failed to reset password. The link may have expired or is invalid.";
      setError(message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-[#050505] px-4">
      <div className="pointer-events-none fixed inset-0 overflow-hidden">
        <div className="absolute -top-40 -right-40 h-80 w-80 rounded-full bg-white/[0.02] blur-3xl" />
        <div className="absolute -bottom-40 -left-40 h-80 w-80 rounded-full bg-white/[0.02] blur-3xl" />
      </div>

      <div className="relative w-full max-w-md">
        <div className="mb-8 flex items-center justify-center gap-3">
          <Link to="/" className="flex items-center gap-2">
            <div className="h-8 w-8 rounded-lg bg-gradient-to-br from-white to-white/50" />
            <span className="text-xl font-semibold tracking-tight text-white">
              ResumeAI
            </span>
          </Link>
        </div>

        <div className="glass-panel p-8">
          {isSubmitted ? (
            <div className="text-center">
              <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-green-500/10">
                <CheckCircle className="h-6 w-6 text-green-400" />
              </div>
              <h1 className="text-2xl font-semibold text-white">
                Password updated
              </h1>
              <p className="mt-3 text-sm text-white/55">
                Your password has been successfully reset. You can now log in with your new password.
              </p>
              <Link
                to="/login"
                className="mt-6 inline-flex w-full items-center justify-center rounded-full bg-white px-4 py-2.5 text-sm font-semibold text-black transition-all hover:bg-white/90"
              >
                Sign In
              </Link>
            </div>
          ) : (
            <>
              <div className="mb-8 text-center">
                <h1 className="text-2xl font-semibold text-white">
                  Reset password
                </h1>
                <p className="mt-2 text-sm text-white/55">
                  Set a secure new password for your account
                </p>
              </div>

              {!token && (
                <div className="mb-6 flex items-center gap-3 rounded-[var(--radius-sm)] border border-red-500/20 bg-red-500/10 p-3">
                  <AlertCircle className="h-4 w-4 shrink-0 text-red-400" />
                  <p className="text-sm text-red-400">
                    No password reset token was found in the URL. Please make sure you clicked the full link from your email.
                  </p>
                </div>
              )}

              {error && (
                <div className="mb-6 flex items-center gap-3 rounded-[var(--radius-sm)] border border-red-500/20 bg-red-500/10 p-3">
                  <AlertCircle className="h-4 w-4 shrink-0 text-red-400" />
                  <p className="text-sm text-red-400">{error}</p>
                </div>
              )}

              <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">
                <div className="space-y-2">
                  <label
                    htmlFor="reset-password"
                    className="text-sm font-medium text-white/75"
                  >
                    New Password
                  </label>
                  <div className="relative">
                    <Lock className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-white/40" />
                    <Input
                      id="reset-password"
                      type="password"
                      placeholder="••••••••"
                      className="pl-10"
                      disabled={!token}
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

                <div className="space-y-2">
                  <label
                    htmlFor="reset-confirm"
                    className="text-sm font-medium text-white/75"
                  >
                    Confirm Password
                  </label>
                  <div className="relative">
                    <Lock className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-white/40" />
                    <Input
                      id="reset-confirm"
                      type="password"
                      placeholder="••••••••"
                      className="pl-10"
                      disabled={!token}
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
                  disabled={!token}
                >
                  Reset Password
                </Button>
              </form>

              <p className="mt-6 text-center text-sm text-white/50">
                <Link
                  to="/login"
                  className="inline-flex items-center gap-1 font-medium text-white transition-colors hover:text-white/80"
                >
                  <ArrowLeft className="h-3.5 w-3.5" />
                  Back to sign in
                </Link>
              </p>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
