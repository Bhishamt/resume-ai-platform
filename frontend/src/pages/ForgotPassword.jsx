import React, { useState } from "react";
import { Link } from "react-router-dom";
import { useForm } from "react-hook-form";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Mail, ArrowLeft, CheckCircle, AlertCircle } from "lucide-react";
import authService from "@/services/authService";

export default function ForgotPassword() {
  const [isLoading, setIsLoading] = useState(false);
  const [isSubmitted, setIsSubmitted] = useState(false);
  const [error, setError] = useState("");

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm();

  const onSubmit = async (data) => {
    setError("");
    setIsLoading(true);
    try {
      await authService.forgotPassword(data.email);
      setIsSubmitted(true);
    } catch (err) {
      const message =
        err.response?.data?.message ||
        "Something went wrong. Please try again.";
      setError(message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-[#050505] px-4">
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
          {isSubmitted ? (
            /* Success State */
            <div className="text-center">
              <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-green-500/10">
                <CheckCircle className="h-6 w-6 text-green-400" />
              </div>
              <h1 className="text-2xl font-semibold text-white">
                Check your email
              </h1>
              <p className="mt-3 text-sm text-white/55">
                If an account exists with that email, we&apos;ve sent a password
                reset link. Please check your inbox and spam folder.
              </p>
              <Link
                to="/login"
                className="mt-6 inline-flex items-center gap-2 text-sm font-medium text-white transition-colors hover:text-white/80"
              >
                <ArrowLeft className="h-4 w-4" />
                Back to sign in
              </Link>
            </div>
          ) : (
            /* Form State */
            <>
              <div className="mb-8 text-center">
                <h1 className="text-2xl font-semibold text-white">
                  Forgot your password?
                </h1>
                <p className="mt-2 text-sm text-white/55">
                  Enter your email and we&apos;ll send you a reset link
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
                <div className="space-y-2">
                  <label
                    htmlFor="forgot-email"
                    className="text-sm font-medium text-white/75"
                  >
                    Email
                  </label>
                  <div className="relative">
                    <Mail className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-white/40" />
                    <Input
                      id="forgot-email"
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
                    <p className="text-xs text-red-400">
                      {errors.email.message}
                    </p>
                  )}
                </div>

                <Button
                  type="submit"
                  className="w-full rounded-full"
                  isLoading={isLoading}
                >
                  Send Reset Link
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
