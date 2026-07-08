import React from "react";
import { Slot } from "@radix-ui/react-slot";
import { cn } from "@/lib/utils";
import { Loader2 } from "lucide-react";

const buttonVariants = {
  default: "bg-white text-black hover:bg-white/90",
  secondary: "bg-[#222222] text-white hover:bg-[#333333]",
  glass: "glass text-white hover:bg-white/10",
  outline: "border border-white/20 text-white hover:bg-white/10",
  ghost: "text-white hover:bg-white/10 hover:text-white",
  danger: "bg-red-500 text-white hover:bg-red-600",
};

const buttonSizes = {
  default: "h-10 px-4 py-2",
  sm: "h-9 rounded-md px-3",
  lg: "h-11 rounded-md px-8",
  icon: "h-10 w-10",
};

const Button = React.forwardRef(
  ({ className, variant = "default", size = "default", asChild = false, isLoading = false, children, disabled, ...props }, ref) => {
    const Comp = asChild ? Slot : "button";
    
    return (
      <Comp
        className={cn(
          "inline-flex items-center justify-center rounded-[var(--radius-sm)] text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-white/50 disabled:pointer-events-none disabled:opacity-50",
          buttonVariants[variant],
          buttonSizes[size],
          className
        )}
        ref={ref}
        disabled={disabled || isLoading}
        {...props}
      >
        {isLoading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
        {children}
      </Comp>
    );
  }
);
Button.displayName = "Button";

export { Button, buttonVariants };
