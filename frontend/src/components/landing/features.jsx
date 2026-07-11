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
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              whileHover={{ y: -5 }}
              viewport={{ once: true, margin: "-50px" }}
              transition={{ duration: 0.5, delay: index * 0.1, ease: "easeOut" }}
              className="group h-full"
            >
              <Card className="h-full bg-white/[0.02] border-white/[0.05] group-hover:bg-white/[0.04] group-hover:border-white/20 transition-all duration-300 relative overflow-hidden flex flex-col shadow-lg hover:shadow-indigo-500/10">
                <div className="absolute inset-0 bg-gradient-to-br from-indigo-500/0 via-purple-500/0 to-indigo-500/0 group-hover:from-indigo-500/10 group-hover:to-purple-500/10 transition-all duration-500 pointer-events-none" />
                <CardHeader className="flex-1">
                  <div className="h-14 w-14 rounded-xl bg-gradient-to-br from-white/10 to-white/5 border border-white/10 flex items-center justify-center mb-5 group-hover:scale-110 transition-transform duration-300 shadow-inner">
                    <feature.icon className="h-7 w-7 text-white/80 group-hover:text-white transition-colors" />
                  </div>
                  <CardTitle className="text-xl font-bold tracking-tight text-white group-hover:text-indigo-300 transition-colors">{feature.title}</CardTitle>
                  <CardDescription className="text-base mt-3 text-white/60 leading-relaxed">{feature.description}</CardDescription>
                </CardHeader>
              </Card>
            </motion.div>
          ))}
        </div>
      </Container>
    </Section>
  );
}
