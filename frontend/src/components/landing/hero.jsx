import React from "react";
import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";
import { Container } from "@/components/layout/container";
import { Sparkles, ArrowRight } from "lucide-react";

export function Hero() {
  return (
    <section className="relative min-h-screen overflow-hidden pt-20 flex items-center justify-center">
      {/* Background Video / Overlay */}
      <div className="absolute inset-0 z-0">
        <div className="absolute inset-0 bg-[#050505]/80 backdrop-blur-sm z-10" />
        <div className="absolute inset-0 bg-gradient-to-t from-[#050505] via-transparent to-[#050505] z-10" />
        {/* Placeholder gradient for video */}
        <div className="w-full h-full bg-gradient-to-br from-indigo-900/20 via-purple-900/10 to-black animate-pulse" />
      </div>

      <Container className="relative z-20 text-center">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, ease: "easeOut" }}
          className="mx-auto max-w-4xl"
        >
          <div className="mb-6 flex justify-center">
            <span className="inline-flex items-center rounded-full border border-white/10 bg-white/5 px-4 py-1.5 text-sm font-medium text-white/80 backdrop-blur-md">
              <Sparkles className="mr-2 h-4 w-4 text-white/70" />
              Introducing ResumeAI 2.0
            </span>
          </div>
          
          <h1 className="mb-8 text-5xl font-extrabold tracking-tight text-white sm:text-6xl lg:text-7xl">
            Land your dream job with <br className="hidden sm:block" />
            <span className="text-gradient">AI-Powered precision.</span>
          </h1>
          
          <p className="mx-auto mb-10 max-w-2xl text-lg text-white/60 sm:text-xl leading-relaxed">
            Optimize your resume, beat the ATS, and match with the perfect roles. Our advanced AI evaluates your experience against job descriptions instantly.
          </p>

          <div className="flex flex-col sm:flex-row items-center justify-center space-y-4 sm:space-y-0 sm:space-x-6">
            <Button size="lg" className="w-full sm:w-auto rounded-full text-base font-semibold px-8 h-12 group">
              Start for free
              <ArrowRight className="ml-2 h-4 w-4 transition-transform group-hover:translate-x-1" />
            </Button>
            <Button variant="glass" size="lg" className="w-full sm:w-auto rounded-full text-base font-semibold px-8 h-12">
              View demo
            </Button>
          </div>
        </motion.div>

        {/* Floating Glass Cards */}
        <motion.div
          initial={{ opacity: 0, y: 50 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 1, delay: 0.2, ease: "easeOut" }}
          className="mt-20 mx-auto max-w-5xl"
        >
          <div className="glass-panel p-2">
            <div className="rounded-[var(--radius-md)] overflow-hidden border border-white/5 bg-black/50 aspect-video relative">
               <div className="absolute inset-0 flex items-center justify-center text-white/20">
                  Dashboard Preview Graphic
               </div>
            </div>
          </div>
        </motion.div>
      </Container>
    </section>
  );
}
