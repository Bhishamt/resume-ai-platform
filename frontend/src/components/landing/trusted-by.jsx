import React from "react";
import { Container } from "@/components/layout/container";
import { Section } from "@/components/layout/section";

export function TrustedBy() {
  return (
    <Section className="py-12 border-b border-white/5 bg-[#050505]">
      <Container>
        <p className="text-center text-sm font-medium text-white/40 mb-8 uppercase tracking-widest">
          Trusted by top professionals at
        </p>
        <div className="flex flex-wrap justify-center gap-8 opacity-50 grayscale sm:gap-16">
          {/* Logo Placeholders */}
          {["ACME Corp", "GlobalTech", "Innovate Inc", "Nexus", "Stark Ind"].map((name) => (
            <div key={name} className="flex items-center justify-center text-xl font-bold tracking-tighter text-white">
              {name}
            </div>
          ))}
        </div>
      </Container>
    </Section>
  );
}
