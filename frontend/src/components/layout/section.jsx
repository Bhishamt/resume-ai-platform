import React from "react";
import { cn } from "@/lib/utils";

export function Section({ className, children, id, ...props }) {
  return (
    <section
      id={id}
      className={cn("relative py-16 md:py-24 lg:py-32", className)}
      {...props}
    >
      {children}
    </section>
  );
}
