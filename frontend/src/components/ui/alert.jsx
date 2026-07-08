import React from "react";
import { cn } from "@/lib/utils";

const alertVariants = {
  default: "bg-white/5 border-white/10 text-white",
  success: "bg-green-500/10 border-green-500/20 text-green-400",
  warning: "bg-amber-500/10 border-amber-500/20 text-amber-400",
  error: "bg-red-500/10 border-red-500/20 text-red-400",
};

const Alert = React.forwardRef(({ className, variant = "default", ...props }, ref) => (
  <div
    ref={ref}
    role="alert"
    className={cn(
      "relative w-full rounded-[var(--radius-md)] border p-4 [&>svg~*]:pl-7 [&>svg+div]:translate-y-[-3px] [&>svg]:absolute [&>svg]:left-4 [&>svg]:top-4 [&>svg]:text-current",
      alertVariants[variant],
      className
    )}
    {...props}
  />
));
Alert.displayName = "Alert";

const AlertTitle = React.forwardRef(({ className, ...props }, ref) => (
  <h5
    ref={ref}
    className={cn("mb-1 font-medium leading-none tracking-tight", className)}
    {...props}
  />
));
AlertTitle.displayName = "AlertTitle";

const AlertDescription = React.forwardRef(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn("text-sm [&_p]:leading-relaxed opacity-90", className)}
    {...props}
  />
));
AlertDescription.displayName = "AlertDescription";

export { Alert, AlertTitle, AlertDescription };
