import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { useAuth } from "@/context/AuthContext";
import { User, LogOut, Menu, X, FileText, Briefcase, Sparkles } from "lucide-react";

export function Navbar() {
  const [scrolled, setScrolled] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const { isAuthenticated, user, logout } = useAuth();

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
        scrolled
          ? "glass-card mx-4 mt-4 h-16 !border-white/10"
          : "bg-transparent border-b border-transparent"
      )}
    >
      <div className="mx-auto flex w-full max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
        <Link to="/" className="flex items-center space-x-2">
          <div className="h-8 w-8 rounded-lg bg-gradient-to-br from-white to-white/50" />
          <span className="text-xl font-semibold tracking-tight text-white">
            ResumeAI
          </span>
        </Link>

        {/* Desktop Nav */}
        <nav className="hidden md:flex items-center space-x-8">
          <a
            href="#features"
            className="text-sm font-medium text-white/70 transition-colors hover:text-white"
          >
            Features
          </a>
          <a
            href="#how-it-works"
            className="text-sm font-medium text-white/70 transition-colors hover:text-white"
          >
            How it Works
          </a>
          <a
            href="#testimonials"
            className="text-sm font-medium text-white/70 transition-colors hover:text-white"
          >
            Testimonials
          </a>
          <a
            href="#pricing"
            className="text-sm font-medium text-white/70 transition-colors hover:text-white"
          >
            Pricing
          </a>
        </nav>

        {/* Auth status desktop */}
        <div className="hidden md:flex items-center space-x-4">
          {isAuthenticated ? (
            <div className="flex items-center space-x-6">
              <Link
                to="/resumes"
                className="flex items-center space-x-2 text-sm font-medium text-white/70 transition-colors hover:text-white"
              >
                <FileText className="h-4 w-4 text-white/60" />
                <span>My Resumes</span>
              </Link>
              <Link
                to="/job-matching"
                className="flex items-center space-x-2 text-sm font-medium text-white/70 transition-colors hover:text-white"
              >
                <Briefcase className="h-4 w-4 text-white/60" />
                <span>Job Match</span>
              </Link>
              <Link
                to="/ai-assistant"
                className="flex items-center space-x-2 text-sm font-medium text-white/70 transition-colors hover:text-white"
              >
                <Sparkles className="h-4 w-4 text-white/60" />
                <span>AI Assistant</span>
              </Link>
              <Link
                to="/profile"
                className="flex items-center space-x-2 text-sm font-medium text-white/70 transition-colors hover:text-white"
              >
                {user?.avatar_url ? (
                  <img
                    src={user.avatar_url}
                    alt={user.full_name}
                    className="h-7 w-7 rounded-full object-cover border border-white/10"
                  />
                ) : (
                  <div className="flex h-7 w-7 items-center justify-center rounded-full bg-white/10">
                    <User className="h-4 w-4 text-white/60" />
                  </div>
                )}
                <span>Profile</span>
              </Link>
              <Button
                variant="ghost"
                size="sm"
                onClick={logout}
                className="text-white/70 hover:text-white"
              >
                <LogOut className="h-4 w-4 mr-2" />
                Sign Out
              </Button>
            </div>
          ) : (
            <>
              <Link
                to="/login"
                className="text-sm font-medium text-white/70 transition-colors hover:text-white"
              >
                Log in
              </Link>
              <Button
                asChild
                variant="default"
                className="rounded-full"
              >
                <Link to="/register">Get Started</Link>
              </Button>
            </>
          )}
        </div>

        {/* Mobile Menu Button */}
        <button
          onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          className="flex md:hidden items-center justify-center p-2 text-white/70 transition-colors hover:text-white"
        >
          {mobileMenuOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
        </button>
      </div>

      {/* Mobile Menu Dropdown */}
      {mobileMenuOpen && (
        <div className="absolute top-full left-4 right-4 mt-2 glass-card p-6 md:hidden flex flex-col space-y-4">
          <a
            href="#features"
            onClick={() => setMobileMenuOpen(false)}
            className="text-sm font-medium text-white/70 transition-colors hover:text-white py-1"
          >
            Features
          </a>
          <a
            href="#how-it-works"
            onClick={() => setMobileMenuOpen(false)}
            className="text-sm font-medium text-white/70 transition-colors hover:text-white py-1"
          >
            How it Works
          </a>
          <a
            href="#testimonials"
            onClick={() => setMobileMenuOpen(false)}
            className="text-sm font-medium text-white/70 transition-colors hover:text-white py-1"
          >
            Testimonials
          </a>
          <a
            href="#pricing"
            onClick={() => setMobileMenuOpen(false)}
            className="text-sm font-medium text-white/70 transition-colors hover:text-white py-1"
          >
            Pricing
          </a>

          <div className="border-t border-white/5 pt-4 flex flex-col space-y-3">
            {isAuthenticated ? (
              <>
                <Link
                  to="/resumes"
                  onClick={() => setMobileMenuOpen(false)}
                  className="flex items-center space-x-2 text-sm font-medium text-white/75"
                >
                  <FileText className="h-4 w-4" />
                  <span>My Resumes</span>
                </Link>
                <Link
                  to="/job-matching"
                  onClick={() => setMobileMenuOpen(false)}
                  className="flex items-center space-x-2 text-sm font-medium text-white/75"
                >
                  <Briefcase className="h-4 w-4" />
                  <span>Job Match</span>
                </Link>
                <Link
                  to="/ai-assistant"
                  onClick={() => setMobileMenuOpen(false)}
                  className="flex items-center space-x-2 text-sm font-medium text-white/75"
                >
                  <Sparkles className="h-4 w-4" />
                  <span>AI Assistant</span>
                </Link>
                <Link
                  to="/profile"
                  onClick={() => setMobileMenuOpen(false)}
                  className="flex items-center space-x-2 text-sm font-medium text-white/75"
                >
                  <User className="h-4 w-4" />
                  <span>Profile ({user?.full_name})</span>
                </Link>
                <button
                  onClick={() => {
                    logout();
                    setMobileMenuOpen(false);
                  }}
                  className="flex items-center space-x-2 text-sm font-medium text-red-400 text-left"
                >
                  <LogOut className="h-4 w-4" />
                  <span>Sign Out</span>
                </button>
              </>
            ) : (
              <>
                <Link
                  to="/login"
                  onClick={() => setMobileMenuOpen(false)}
                  className="text-sm font-medium text-white/70 hover:text-white py-1 text-center"
                >
                  Log in
                </Link>
                <Button
                  asChild
                  variant="default"
                  className="rounded-full w-full"
                  onClick={() => setMobileMenuOpen(false)}
                >
                  <Link to="/register">Get Started</Link>
                </Button>
              </>
            )}
          </div>
        </div>
      )}
    </header>
  );
}
