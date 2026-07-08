import React from "react";
import { Container } from "@/components/layout/container";
import { Section } from "@/components/layout/section";
import { Button } from "@/components/ui/button";

export function CTA() {
  return (
    <Section className="relative overflow-hidden">
      {/* Decorative background */}
      <div className="absolute inset-0 bg-white/[0.02]" />
      <div className="absolute left-1/2 top-1/2 -z-10 -translate-x-1/2 -translate-y-1/2">
         <div className="h-[400px] w-[800px] rounded-full bg-white/5 blur-[120px]" />
      </div>

      <Container className="relative z-10 text-center">
        <div className="mx-auto max-w-2xl">
          <h2 className="mb-6 text-4xl font-bold tracking-tight text-white sm:text-5xl">
            Ready to land your next role?
          </h2>
          <p className="mb-10 text-lg text-white/60">
            Join thousands of professionals who have accelerated their careers with AI-powered resume optimization.
          </p>
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <Button size="lg" className="w-full sm:w-auto rounded-full px-8 h-12 text-base font-semibold">
              Get Started for Free
            </Button>
          </div>
          <p className="mt-6 text-sm text-white/40">
            No credit card required. Cancel anytime.
          </p>
        </div>
      </Container>
    </Section>
  );
}
