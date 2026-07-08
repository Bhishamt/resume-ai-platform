import React from "react";
import { cn } from "@/lib/utils";

const Divider = React.forwardRef(({ className, orientation = "horizontal", ...props }, ref) => (
  <div
    ref={ref}
    role="separator"
    aria-orientation={orientation}
    className={cn(
      "shrink-0 bg-white/10",
      orientation === "horizontal" ? "h-[1px] w-full" : "h-full w-[1px]",
      className
    )}
    {...props}
  />
));
Divider.displayName = "Divider";

export { Divider };
