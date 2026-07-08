import React from "react";
import { motion } from "framer-motion";
import { Container } from "@/components/layout/container";
import { Section } from "@/components/layout/section";
import { FileText, Target, Bot, Zap } from "lucide-react";
import { Card, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";

const features = [
  {
    title: "Smart ATS Scoring",
    description: "Our AI scans your resume exactly like enterprise Applicant Tracking Systems do, giving you an accurate pass/fail probability.",
    icon: Target,
  },
  {
    title: "AI Resume Tailoring",
    description: "Instantly rewrite bullets and summaries to perfectly match the keywords and tone of your target job description.",
    icon: FileText,
  },
  {
    title: "Intelligent Job Matching",
    description: "Discover roles you're highly qualified for based on a semantic analysis of your entire career history.",
    icon: Zap,
  },
  {
    title: "AI Interview Prep",
    description: "Generate likely interview questions based on the gaps between your resume and the job description.",
    icon: Bot,
  },
];

export function Features() {
  return (
    <Section id="features">
      <Container>
        <div className="mb-16 text-center max-w-3xl mx-auto">
          <h2 className="text-3xl font-bold tracking-tight text-white sm:text-4xl mb-4">
            Everything you need to get hired
          </h2>
          <p className="text-lg text-white/60">
            A comprehensive suite of tools designed to optimize every step of your job search process.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {features.map((feature, index) => (
            <motion.div
              key={feature.title}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.5, delay: index * 0.1 }}
            >
              <Card className="h-full bg-white/[0.02] border-white/[0.05] hover:bg-white/[0.04] transition-colors">
                <CardHeader>
                  <div className="h-12 w-12 rounded-lg bg-white/10 flex items-center justify-center mb-4">
                    <feature.icon className="h-6 w-6 text-white" />
                  </div>
                  <CardTitle className="text-xl">{feature.title}</CardTitle>
                  <CardDescription className="text-base mt-2">{feature.description}</CardDescription>
                </CardHeader>
              </Card>
            </motion.div>
          ))}
        </div>
      </Container>
    </Section>
  );
}
