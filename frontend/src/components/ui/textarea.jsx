import React from "react";
import { cn } from "@/lib/utils";

const Textarea = React.forwardRef(({ className, ...props }, ref) => {
  return (
    <textarea
      className={cn(
        "flex min-h-[80px] w-full rounded-[var(--radius-sm)] border border-white/10 bg-black/20 px-3 py-2 text-sm text-white placeholder:text-white/40 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-white/30 disabled:cursor-not-allowed disabled:opacity-50 transition-colors hover:border-white/20",
        className
      )}
      ref={ref}
      {...props}
    />
  );
});
Textarea.displayName = "Textarea";

export { Textarea };
