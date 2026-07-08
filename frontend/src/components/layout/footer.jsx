import React from "react";
import { Link } from "react-router-dom";
import { Container } from "./container";

export function Footer() {
  return (
    <footer className="border-t border-white/10 bg-[#050505] py-12 md:py-16">
      <Container>
        <div className="grid grid-cols-2 gap-8 md:grid-cols-4 lg:grid-cols-5">
          <div className="col-span-2 lg:col-span-2">
            <Link to="/" className="flex items-center space-x-2 mb-4">
              <div className="h-6 w-6 rounded-md bg-white" />
              <span className="text-lg font-semibold text-white">ResumeAI</span>
            </Link>
            <p className="max-w-xs text-sm leading-relaxed text-white/60">
              The premier AI platform for accelerating your career. Optimize your resume, master ATS, and land your dream job faster.
            </p>
          </div>
          <div>
            <h3 className="mb-4 text-sm font-semibold text-white">Platform</h3>
            <ul className="space-y-3 text-sm text-white/60">
              <li><a href="#" className="hover:text-white transition-colors">Resume Analysis</a></li>
              <li><a href="#" className="hover:text-white transition-colors">ATS Scoring</a></li>
              <li><a href="#" className="hover:text-white transition-colors">Job Matching</a></li>
              <li><a href="#" className="hover:text-white transition-colors">AI Assistant</a></li>
            </ul>
          </div>
          <div>
            <h3 className="mb-4 text-sm font-semibold text-white">Company</h3>
            <ul className="space-y-3 text-sm text-white/60">
              <li><a href="#" className="hover:text-white transition-colors">About Us</a></li>
              <li><a href="#" className="hover:text-white transition-colors">Careers</a></li>
              <li><a href="#" className="hover:text-white transition-colors">Blog</a></li>
              <li><a href="#" className="hover:text-white transition-colors">Contact</a></li>
            </ul>
          </div>
          <div>
            <h3 className="mb-4 text-sm font-semibold text-white">Legal</h3>
            <ul className="space-y-3 text-sm text-white/60">
              <li><a href="#" className="hover:text-white transition-colors">Privacy Policy</a></li>
              <li><a href="#" className="hover:text-white transition-colors">Terms of Service</a></li>
              <li><a href="#" className="hover:text-white transition-colors">Cookie Policy</a></li>
            </ul>
          </div>
        </div>
        <div className="mt-12 flex flex-col items-center justify-between border-t border-white/10 pt-8 sm:flex-row">
          <p className="text-xs text-white/40">
            &copy; {new Date().getFullYear()} ResumeAI Inc. All rights reserved.
          </p>
          <div className="mt-4 flex space-x-4 sm:mt-0">
            {/* Social Links Placeholders */}
            <a href="#" className="text-white/40 hover:text-white">Twitter</a>
            <a href="#" className="text-white/40 hover:text-white">LinkedIn</a>
          </div>
        </div>
      </Container>
    </footer>
  );
}
