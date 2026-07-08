import React from "react";
import { motion } from "framer-motion";
import { Container } from "@/components/layout/container";
import { Section } from "@/components/layout/section";
import { Card, CardContent } from "@/components/ui/card";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";

const testimonials = [
  {
    quote: "ResumeAI transformed my job search. The ATS scoring helped me realize I was missing key terms. I landed 3 interviews in a week.",
    name: "Sarah Jenkins",
    role: "Product Manager",
    initials: "SJ",
  },
  {
    quote: "The tailored resume feature is magic. It perfectly aligns my experience with what the job description is actually asking for.",
    name: "David Chen",
    role: "Software Engineer",
    initials: "DC",
  },
  {
    quote: "I've tried other resume builders, but the semantic matching here is on another level. It feels like having a personal recruiter.",
    name: "Emily Rodriguez",
    role: "Marketing Director",
    initials: "ER",
  },
];

export function Testimonials() {
  return (
    <Section>
      <Container>
        <div className="mb-16 text-center">
          <h2 className="text-3xl font-bold tracking-tight text-white sm:text-4xl mb-4">
            Loved by job seekers
          </h2>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {testimonials.map((t, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.5, delay: index * 0.1 }}
            >
              <Card className="h-full bg-white/[0.02] border-white/[0.05]">
                <CardContent className="pt-6">
                  <div className="mb-6 flex gap-1">
                    {[1, 2, 3, 4, 5].map((star) => (
                      <svg key={star} className="h-4 w-4 text-yellow-500 fill-yellow-500" viewBox="0 0 20 20">
                        <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                      </svg>
                    ))}
                  </div>
                  <p className="text-white/80 mb-6 line-clamp-4">"{t.quote}"</p>
                  <div className="flex items-center gap-3">
                    <Avatar>
                      <AvatarFallback>{t.initials}</AvatarFallback>
                    </Avatar>
                    <div>
                      <div className="font-semibold text-white text-sm">{t.name}</div>
                      <div className="text-xs text-white/50">{t.role}</div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          ))}
        </div>
      </Container>
    </Section>
  );
}
