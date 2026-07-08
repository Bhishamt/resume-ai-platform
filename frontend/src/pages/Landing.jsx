import React from "react";
import { PageWrapper } from "@/components/layout/pagewrapper";
import { Navbar } from "@/components/layout/navbar";
import { Footer } from "@/components/layout/footer";
import { Hero } from "@/components/landing/hero";
import { TrustedBy } from "@/components/landing/trusted-by";
import { Features } from "@/components/landing/features";
import { Previews } from "@/components/landing/previews";
import { Testimonials } from "@/components/landing/testimonials";
import { FAQ } from "@/components/landing/faq";
import { CTA } from "@/components/landing/cta";

export default function Landing() {
  return (
    <PageWrapper className="min-h-screen bg-[#050505] text-white">
      <Navbar />
      <main>
        <Hero />
        <TrustedBy />
        <Features />
        <Previews />
        <Testimonials />
        <FAQ />
        <CTA />
      </main>
      <Footer />
    </PageWrapper>
  );
}
