import React from "react";
import { motion } from "framer-motion";
import { Container } from "@/components/layout/container";
import { Section } from "@/components/layout/section";

export function Previews() {
  return (
    <Section className="overflow-hidden bg-[#0a0a0a]">
      <Container>
        <div className="mb-16 text-center max-w-3xl mx-auto">
          <h2 className="text-3xl font-bold tracking-tight text-white sm:text-4xl mb-4">
            See the platform in action
          </h2>
          <p className="text-lg text-white/60">
            A beautiful, intuitive interface built to give you the edge in your job search.
          </p>
        </div>

        <div className="relative mx-auto max-w-5xl">
          <motion.div
            initial={{ opacity: 0, y: 40 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.7 }}
            className="glass-panel p-2 rounded-[var(--radius-xl)]"
          >
            <div className="aspect-[16/10] bg-[#111] rounded-[var(--radius-lg)] border border-white/5 relative overflow-hidden flex items-center justify-center">
              <div className="text-white/20 font-mono text-sm">
                [ Interactive Dashboard Preview Component ]
              </div>
            </div>
          </motion.div>

          {/* Decorative blurs */}
          <div className="absolute -left-40 top-20 h-72 w-72 rounded-full bg-indigo-500/10 blur-[100px]" />
          <div className="absolute -right-40 bottom-20 h-72 w-72 rounded-full bg-purple-500/10 blur-[100px]" />
        </div>
      </Container>
    </Section>
  );
}
