import React, { useState } from "react";
import { useAuth } from "@/context/AuthContext";
import { useForm } from "react-hook-form";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { User as UserIcon, Mail, Calendar, Camera, Shield, LogOut, Check } from "lucide-react";
import { useToast } from "@/hooks/useToast";
import { Toast, ToastClose, ToastDescription, ToastProvider, ToastTitle, ToastViewport } from "@/components/ui/toast";

export default function Profile() {
  const { user, updateProfile, logout } = useAuth();
  const { toasts, success, error, removeToast } = useToast();
  const [isUpdating, setIsUpdating] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm({
    defaultValues: {
      full_name: user?.full_name || "",
      avatar_url: user?.avatar_url || "",
    },
  });

  const onSubmit = async (data) => {
    setIsUpdating(true);
    try {
      await updateProfile(data);
      success("Profile updated successfully.");
    } catch (err) {
      const msg = err.response?.data?.message || "Failed to update profile.";
      error(msg);
    } finally {
      setIsUpdating(false);
    }
  };

  const formattedDate = user?.created_at
    ? new Date(user.created_at).toLocaleDateString(undefined, {
        year: "numeric",
        month: "long",
        day: "numeric",
      })
    : "Unknown date";

  return (
    <ToastProvider>
      <div className="min-h-screen bg-[#050505] text-white">
        {/* Header Spacer */}
        <div className="h-24" />

        <div className="mx-auto max-w-4xl px-4 py-8 sm:px-6 lg:px-8">
          <div className="mb-8 flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-semibold tracking-tight text-white">Profile</h1>
              <p className="mt-2 text-sm text-white/55">
                Manage your personal information and preferences
              </p>
            </div>
            <Button
              variant="danger"
              size="sm"
              onClick={logout}
              className="rounded-full gap-2 border border-red-500/20 bg-red-500/10 hover:bg-red-500/20 text-red-400 font-medium"
            >
              <LogOut className="h-4 w-4" />
              Sign Out
            </Button>
          </div>

          <div className="grid grid-cols-1 gap-8 md:grid-cols-3">
            {/* User Details Sidebar */}
            <div className="md:col-span-1 space-y-6">
              <Card className="p-6 flex flex-col items-center text-center">
                <div className="relative mb-4">
                  <div className="h-24 w-24 overflow-hidden rounded-full border-2 border-white/10 bg-white/5 flex items-center justify-center">
                    {user?.avatar_url ? (
                      <img
                        src={user.avatar_url}
                        alt={user.full_name}
                        className="h-full w-full object-cover"
                        onError={(e) => {
                          e.target.src = ""; // Fallback if image fails to load
                        }}
                      />
                    ) : (
                      <UserIcon className="h-10 w-10 text-white/35" />
                    )}
                  </div>
                </div>

                <h2 className="text-lg font-semibold text-white">{user?.full_name}</h2>
                <p className="text-xs text-white/40 mb-4">{user?.email}</p>

                <div className="w-full border-t border-white/5 pt-4 space-y-3 text-left">
                  <div className="flex items-center gap-2.5 text-xs text-white/55">
                    <Calendar className="h-4 w-4 text-white/35 shrink-0" />
                    <span>Member since {formattedDate}</span>
                  </div>
                  <div className="flex items-center gap-2.5 text-xs text-white/55">
                    <Shield className="h-4 w-4 text-white/35 shrink-0" />
                    <span className="capitalize">Role: {user?.role || "User"}</span>
                  </div>
                  <div className="flex items-center gap-2.5 text-xs text-white/55">
                    <Check className={`h-4 w-4 shrink-0 ${user?.is_verified ? "text-green-400" : "text-white/35"}`} />
                    <span>{user?.is_verified ? "Verified Account" : "Unverified Account"}</span>
                  </div>
                </div>
              </Card>
            </div>

            {/* Profile Settings Form */}
            <div className="md:col-span-2">
              <Card className="p-6">
                <CardHeader className="p-0 mb-6">
                  <CardTitle className="text-xl font-semibold text-white">General Information</CardTitle>
                  <CardDescription className="text-white/55 mt-1">
                    Update your display name and avatar image URL
                  </CardDescription>
                </CardHeader>

                <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
                  {/* Email (Readonly) */}
                  <div className="space-y-2">
                    <label className="text-sm font-medium text-white/75 flex items-center gap-1.5">
                      <Mail className="h-4 w-4 text-white/35" />
                      Email Address
                    </label>
                    <Input
                      type="email"
                      value={user?.email || ""}
                      disabled
                      className="opacity-60 cursor-not-allowed bg-white/5"
                    />
                    <p className="text-xs text-white/35">
                      Your email address cannot be changed. Contact support if you need to change it.
                    </p>
                  </div>

                  {/* Full Name */}
                  <div className="space-y-2">
                    <label htmlFor="profile-name" className="text-sm font-medium text-white/75 flex items-center gap-1.5">
                      <UserIcon className="h-4 w-4 text-white/35" />
                      Full Name
                    </label>
                    <Input
                      id="profile-name"
                      type="text"
                      placeholder="Jane Doe"
                      {...register("full_name", {
                        required: "Full name is required.",
                        minLength: {
                          value: 2,
                          message: "Name must be at least 2 characters.",
                        },
                      })}
                    />
                    {errors.full_name && (
                      <p className="text-xs text-red-400">{errors.full_name.message}</p>
                    )}
                  </div>

                  {/* Avatar URL */}
                  <div className="space-y-2">
                    <label htmlFor="profile-avatar" className="text-sm font-medium text-white/75 flex items-center gap-1.5">
                      <Camera className="h-4 w-4 text-white/35" />
                      Avatar Image URL
                    </label>
                    <Input
                      id="profile-avatar"
                      type="text"
                      placeholder="https://example.com/avatar.jpg"
                      {...register("avatar_url")}
                    />
                    {errors.avatar_url && (
                      <p className="text-xs text-red-400">{errors.avatar_url.message}</p>
                    )}
                  </div>

                  <div className="flex justify-end pt-2">
                    <Button type="submit" className="rounded-full px-6" isLoading={isUpdating}>
                      Save Changes
                    </Button>
                  </div>
                </form>
              </Card>
            </div>
          </div>
        </div>

        {/* Toast Notification Viewport */}
        <ToastViewport />
        {toasts.map(({ id, title, description, variant }) => (
          <Toast key={id} className={variant === "error" ? "border-red-500/20 bg-red-500/10 text-red-400" : "border-green-500/20 bg-green-500/10 text-green-400"}>
            <div className="grid gap-1">
              {title && <ToastTitle>{title}</ToastTitle>}
              {description && <ToastDescription>{description}</ToastDescription>}
            </div>
            <ToastClose onClick={() => removeToast(id)} />
          </Toast>
        ))}
      </div>
    </ToastProvider>
  );
}
