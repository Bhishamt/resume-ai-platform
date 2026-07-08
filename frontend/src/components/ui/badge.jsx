import React from "react";
import { cn } from "@/lib/utils";

const badgeVariants = {
  default: "bg-white/10 text-white border-white/10",
  success: "bg-green-500/10 text-green-400 border-green-500/20",
  warning: "bg-amber-500/10 text-amber-400 border-amber-500/20",
  error: "bg-red-500/10 text-red-400 border-red-500/20",
  outline: "text-white border-white/20",
};

function Badge({ className, variant = "default", ...props }) {
  return (
    <div
      className={cn(
        "inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-white/50",
        badgeVariants[variant],
        className
      )}
      {...props}
    />
  );
}

export { Badge, badgeVariants };
