import React from "react";
import { Container } from "@/components/layout/container";
import { Section } from "@/components/layout/section";
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion";

const faqs = [
  {
    question: "How does the ATS scoring work?",
    answer: "Our system uses NLP (Natural Language Processing) similar to major enterprise Applicant Tracking Systems. It scans for keywords, formatting compatibility, and semantic relevance against a provided job description to generate a pass/fail probability score.",
  },
  {
    question: "Is my resume data kept private?",
    answer: "Yes, completely. We use industry-standard encryption for data at rest and in transit. Your resumes are never sold to third parties, and you can delete your data at any time from your account settings.",
  },
  {
    question: "Which AI model powers the recommendations?",
    answer: "We utilize advanced LLMs tailored specifically for HR and recruiting datasets. This ensures the rewritten bullet points and summaries sound professional, action-oriented, and authentic.",
  },
  {
    question: "Can I try it for free?",
    answer: "Yes! You can analyze and score up to 3 resumes per month on our free tier. To unlock unlimited analysis and AI tailoring, you can upgrade to our Pro plan.",
  },
];

export function FAQ() {
  return (
    <Section className="bg-[#0a0a0a]">
      <Container className="max-w-3xl">
        <div className="mb-12 text-center">
          <h2 className="text-3xl font-bold tracking-tight text-white mb-4">
            Frequently asked questions
          </h2>
        </div>
        
        <Accordion type="single" collapsible className="w-full">
          {faqs.map((faq, index) => (
            <AccordionItem key={index} value={`item-${index}`}>
              <AccordionTrigger className="text-left text-base">{faq.question}</AccordionTrigger>
              <AccordionContent className="text-white/60 leading-relaxed">
                {faq.answer}
              </AccordionContent>
            </AccordionItem>
          ))}
        </Accordion>
      </Container>
    </Section>
  );
}
