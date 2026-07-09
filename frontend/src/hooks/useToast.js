import { useState, useCallback } from "react";

let toastIdCounter = 0;

export function useToast() {
  const [toasts, setToasts] = useState([]);

  const addToast = useCallback(({ title, description, variant = "default", duration = 5000 }) => {
    const id = ++toastIdCounter;
    const toast = { id, title, description, variant };

    setToasts((prev) => [...prev, toast]);

    if (duration > 0) {
      setTimeout(() => {
        setToasts((prev) => prev.filter((t) => t.id !== id));
      }, duration);
    }

    return id;
  }, []);

  const removeToast = useCallback((id) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  }, []);

  const success = useCallback(
    (message) => addToast({ title: "Success", description: message, variant: "success" }),
    [addToast]
  );

  const error = useCallback(
    (message) => addToast({ title: "Error", description: message, variant: "error" }),
    [addToast]
  );

  const info = useCallback(
    (message) => addToast({ title: "Info", description: message, variant: "default" }),
    [addToast]
  );

  return { toasts, addToast, removeToast, success, error, info };
}
