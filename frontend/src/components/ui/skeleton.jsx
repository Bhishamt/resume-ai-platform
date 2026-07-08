import React from "react";
import { cn } from "@/lib/utils";

function Skeleton({ className, ...props }) {
  return (
    <div
      className={cn("animate-pulse rounded-[var(--radius-sm)] bg-white/10", className)}
      {...props}
    />
  );
}

export { Skeleton };
