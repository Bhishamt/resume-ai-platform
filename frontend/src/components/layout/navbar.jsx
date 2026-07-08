import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";

export function Navbar() {
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 20);
    };
    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  return (
    <header
      className={cn(
        "fixed top-0 left-0 right-0 z-50 flex h-20 items-center transition-all duration-300",
        scrolled ? "glass-card mx-4 mt-4 h-16 !border-white/10" : "bg-transparent border-b border-transparent"
      )}
    >
      <div className="mx-auto flex w-full max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
        <Link to="/" className="flex items-center space-x-2">
          <div className="h-8 w-8 rounded-lg bg-gradient-to-br from-white to-white/50" />
          <span className="text-xl font-semibold tracking-tight text-white">ResumeAI</span>
        </Link>
        
        <nav className="hidden md:flex items-center space-x-8">
          <a href="#features" className="text-sm font-medium text-white/70 transition-colors hover:text-white">Features</a>
          <a href="#how-it-works" className="text-sm font-medium text-white/70 transition-colors hover:text-white">How it Works</a>
          <a href="#testimonials" className="text-sm font-medium text-white/70 transition-colors hover:text-white">Testimonials</a>
          <a href="#pricing" className="text-sm font-medium text-white/70 transition-colors hover:text-white">Pricing</a>
        </nav>

        <div className="flex items-center space-x-4">
          <Link to="/login" className="hidden md:block text-sm font-medium text-white/70 transition-colors hover:text-white">
            Log in
          </Link>
          <Button variant="default" className="hidden sm:inline-flex rounded-full">
            Get Started
          </Button>
        </div>
      </div>
    </header>
  );
}
