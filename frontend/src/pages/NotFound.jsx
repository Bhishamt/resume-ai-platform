import React from "react";
import { Link, useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";
import { Search, Home, ArrowLeft } from "lucide-react";

export default function NotFound() {
  const navigate = useNavigate();
  return (
    <div className="min-h-screen bg-[#050505] text-white flex flex-col items-center justify-center p-4">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="max-w-md w-full text-center"
      >
        <div className="mb-8 relative mx-auto w-32 h-32 flex items-center justify-center">
          <div className="absolute inset-0 bg-indigo-500/20 rounded-full blur-2xl animate-pulse" />
          <div className="relative h-20 w-20 rounded-2xl bg-white/5 border border-white/10 flex items-center justify-center backdrop-blur-sm shadow-xl">
            <Search className="h-10 w-10 text-white/50" />
          </div>
        </div>

        <h1 className="text-8xl font-black text-transparent bg-clip-text bg-gradient-to-br from-white to-white/30 mb-4">
          404
        </h1>
        <h2 className="text-2xl font-bold tracking-tight text-white mb-4">
          Page Not Found
        </h2>
        <p className="text-white/60 mb-8 leading-relaxed">
          The page you're looking for doesn't exist or has been moved. Check the URL or navigate back to safety.
        </p>

        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <Button onClick={() => navigate(-1)} variant="outline" className="rounded-full h-12 px-6 hover:bg-white/5 text-white border-white/20">
            <ArrowLeft className="mr-2 h-4 w-4" />
            Go Back
          </Button>
          <Button asChild className="rounded-full h-12 px-6 bg-white text-black hover:bg-white/90">
            <Link to="/dashboard">
              <Home className="mr-2 h-4 w-4" />
              Return Home
            </Link>
          </Button>
        </div>
      </motion.div>
    </div>
  );
}
