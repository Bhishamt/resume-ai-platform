import React from "react";
import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { AlertTriangle, Home, RefreshCw } from "lucide-react";

export class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error("ErrorBoundary caught an error", error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen bg-[#050505] text-white flex flex-col items-center justify-center p-4">
          <div className="max-w-md w-full text-center bg-white/[0.02] border border-white/10 p-8 rounded-2xl shadow-2xl relative overflow-hidden">
            <div className="absolute top-0 left-0 right-0 h-1 bg-red-500" />
            <div className="mb-6 mx-auto w-16 h-16 rounded-full bg-red-500/10 flex items-center justify-center">
              <AlertTriangle className="h-8 w-8 text-red-500" />
            </div>
            <h1 className="text-2xl font-bold tracking-tight text-white mb-3">
              Application Error
            </h1>
            <p className="text-sm text-white/60 mb-8">
              Something went wrong in the application. Try refreshing the page, or navigate back home.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Button
                onClick={() => window.location.reload()}
                variant="outline"
                className="rounded-full flex-1 hover:bg-white/5 border-white/20 text-white"
              >
                <RefreshCw className="mr-2 h-4 w-4" />
                Reload Page
              </Button>
              <Button
                asChild
                className="rounded-full flex-1 bg-white text-black hover:bg-white/90"
              >
                <Link to="/" onClick={() => this.setState({ hasError: false })}>
                  <Home className="mr-2 h-4 w-4" />
                  Return Home
                </Link>
              </Button>
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}
