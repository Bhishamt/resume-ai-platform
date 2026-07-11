import React, { useEffect } from "react";
import { useToast } from "@/hooks/useToast";
import { Toast, ToastClose, ToastDescription, ToastProvider, ToastTitle, ToastViewport } from "@/components/ui/toast";

export function GlobalToastListener({ children }) {
  const { toasts, error, removeToast } = useToast();

  useEffect(() => {
    const handleAppError = (e) => {
      error(e.detail?.message || "An unexpected error occurred.");
    };

    window.addEventListener('app-error', handleAppError);
    return () => window.removeEventListener('app-error', handleAppError);
  }, [error]);

  return (
    <ToastProvider>
      {children}
      <ToastViewport />
      {toasts.map((t) => (
        <Toast 
          key={t.id} 
          className={
            t.type === "error" 
              ? "border-red-500/20 bg-red-500/10 text-red-400" 
              : t.type === "success" 
                ? "border-green-500/20 bg-green-500/10 text-green-400" 
                : "border-white/10 bg-[#111111] text-white"
          }
        >
          <div className="grid gap-1" role="status" aria-live="polite">
            {t.title && <ToastTitle>{t.title}</ToastTitle>}
            {t.description && <ToastDescription>{t.description}</ToastDescription>}
          </div>
          <ToastClose aria-label="Close notification" onClick={() => removeToast(t.id)} />
        </Toast>
      ))}
    </ToastProvider>
  );
}
