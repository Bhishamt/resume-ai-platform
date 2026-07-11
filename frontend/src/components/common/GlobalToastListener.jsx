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
        <Toast key={t.id} className="border-red-500/20 bg-red-500/10 text-red-400">
          <div className="grid gap-1">
            {t.title && <ToastTitle>{t.title}</ToastTitle>}
            {t.description && <ToastDescription>{t.description}</ToastDescription>}
          </div>
          <ToastClose onClick={() => removeToast(t.id)} />
        </Toast>
      ))}
    </ToastProvider>
  );
}
