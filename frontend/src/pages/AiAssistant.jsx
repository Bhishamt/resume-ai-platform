import React, { useState, useEffect, useCallback, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Sparkles,
  FileText,
  Briefcase,
  HelpCircle,
  TrendingUp,
  History,
  Copy,
  Download,
  Printer,
  Trash2,
  Send,
  Loader2,
  FileCode,
  Check,
  ArrowRight,
  BookOpen,
  Award
} from "lucide-react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import aiService from "@/services/aiService";
import resumeService from "@/services/resumeService";
import jobMatchingService from "@/services/jobMatchingService";
import { useToast } from "@/hooks/useToast";
import { ToastProvider } from "@/components/ui/toast";

export default function AiAssistant() {
  const { success, error } = useToast();
  const [resumes, setResumes] = useState([]);
  const [jobs, setJobs] = useState([]);
  const [selectedResumeId, setSelectedResumeId] = useState("");
  const [selectedJobId, setSelectedJobId] = useState("");
  
  // Custom job fields (if not selecting a saved job description)
  const [companyName, setCompanyName] = useState("");
  const [jobTitle, setJobTitle] = useState("");
  const [jobText, setJobText] = useState("");

  const [loading, setLoading] = useState(true);
  const [aiLoading, setAiLoading] = useState(false);
  const [activeTab, setActiveTab] = useState("review"); // review, cover-letter, rewrite, interview, career, history
  
  // Results
  const [resultData, setResultData] = useState(null);
  const [historyList, setHistoryList] = useState([]);
  const [copied, setCopied] = useState(false);

  // Chat/Interactive state
  const [chatMessages, setChatMessages] = useState([
    {
      role: "assistant",
      content: "Hello! I am your AI Career Assistant. Select a resume and choose one of the tools below, or click a Prompt Card to get started!"
    }
  ]);
  const [chatInput, setChatInput] = useState("");
  const chatEndRef = useRef(null);

  // Load Resumes, Job Descriptions and AI History
  const loadInitialData = useCallback(async () => {
    try {
      setLoading(true);
      const [resumesRes, jobsRes, historyRes] = await Promise.all([
        resumeService.getResumes(),
        jobMatchingService.getMatches().catch(() => ({ data: [] })), // Fallback to avoid breaking
        aiService.getHistory().catch(() => ({ data: [] }))
      ]);

      setResumes(resumesRes.data || []);
      setHistoryList(historyRes.data || []);

      if (resumesRes.data && resumesRes.data.length > 0) {
        setSelectedResumeId(resumesRes.data[0].id);
      }

      // Try to load raw job descriptions
      // Note: We can also search in matches for job descriptions
      const uniqueJobs = [];
      const seenJobs = new Set();
      (jobsRes.data || []).forEach(match => {
        if (match.job_description && !seenJobs.has(match.job_description.id)) {
          seenJobs.add(match.job_description.id);
          uniqueJobs.push(match.job_description);
        }
      });
      setJobs(uniqueJobs);
      if (uniqueJobs.length > 0) {
        setSelectedJobId(uniqueJobs[0].id);
      }
    } catch (err) {
      console.error(err);
      error("Failed to load workspace data. Please reload.");
    } finally {
      setLoading(false);
    }
  }, [error]);

  useEffect(() => {
    loadInitialData();
  }, [loadInitialData]);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [chatMessages]);

  const handleCopy = () => {
    if (!resultData) return;
    const textToCopy = typeof resultData === "object" ? JSON.stringify(resultData, null, 2) : resultData;
    navigator.clipboard.writeText(textToCopy);
    setCopied(true);
    success("Copied to clipboard!");
    setTimeout(() => setCopied(false), 2000);
  };

  const handleExportMarkdown = () => {
    if (!resultData) return;
    let markdown = `# AI Career Workspace - ${activeTab.toUpperCase()} REPORT\n\n`;

    if (activeTab === "review") {
      markdown += `## Overall Review\n${resultData.overall_review || ""}\n\n`;
      markdown += `## Resume Improvements\n${(resultData.resume_improvements || []).map(i => `- ${i}`).join("\n")}\n\n`;
      markdown += `## Better Summary\n${resultData.better_summary || ""}\n\n`;
      markdown += `## Suggested Skills\n${(resultData.better_skills || []).map(s => `- ${s}`).join("\n")}\n\n`;
      markdown += `## Experience Recommendations\n${resultData.better_experience || ""}\n\n`;
      markdown += `## Better Project Descriptions\n${(resultData.better_projects || []).map(p => `- ${p}`).join("\n")}\n`;
    } else if (activeTab === "cover-letter") {
      markdown += `## Professional Cover Letter\n\n${resultData.professional_cover_letter || ""}\n\n`;
      markdown += `## Company-Specific Version\n\n${resultData.company_specific_version || ""}\n\n`;
      markdown += `## ATS-Friendly Version\n\n${resultData.ats_friendly_version || ""}\n`;
    } else if (activeTab === "rewrite") {
      markdown += `## Stronger Bullet Points\n${(resultData.stronger_bullet_points || []).map(b => `- ${b}`).join("\n")}\n\n`;
      markdown += `## Action Verbs to Use\n${(resultData.better_action_verbs || []).map(v => `- ${v}`).join("\n")}\n\n`;
      markdown += `## Better Project Descriptions\n${(resultData.better_project_descriptions || []).map(d => `- ${d}`).join("\n")}\n`;
    } else if (activeTab === "interview") {
      const cats = ["technical_questions", "hr_questions", "behavioral_questions", "resume_based_questions"];
      cats.forEach(cat => {
        markdown += `## ${cat.replace("_", " ").toUpperCase()}\n\n`;
        (resultData[cat] || []).forEach((q, idx) => {
          markdown += `### Q${idx + 1}: ${q.question}\n**Suggested Answer:** ${q.suggested_answer}\n\n`;
        });
      });
    } else if (activeTab === "career") {
      markdown += `## Learning Roadmap\n${(resultData.learning_roadmap || []).map(r => `- ${r}`).join("\n")}\n\n`;
      markdown += `## Missing Technologies\n${(resultData.missing_technologies || []).map(t => `- ${t}`).join("\n")}\n\n`;
      markdown += `## Certifications Suggested\n${(resultData.certifications || []).map(c => `- ${c}`).join("\n")}\n\n`;
      markdown += `## Career Suggestions\n${(resultData.career_suggestions || []).map(s => `- ${s}`).join("\n")}\n`;
    }

    const blob = new Blob([markdown], { type: "text/markdown;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.setAttribute("download", `ai-${activeTab}-report.md`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    success("Downloaded Markdown file!");
  };

  const handlePrintPDF = () => {
    const printWindow = window.open("", "_blank");
    printWindow.document.write(`
      <html>
        <head>
          <title>AI Workspace - ${activeTab.toUpperCase()}</title>
          <style>
            body { font-family: Arial, sans-serif; padding: 40px; color: #333; line-height: 1.6; }
            h1 { border-bottom: 2px solid #000; padding-bottom: 10px; font-size: 24px; }
            h2 { color: #555; margin-top: 30px; font-size: 18px; }
            ul { padding-left: 20px; }
            li { margin-bottom: 8px; }
            p { white-space: pre-line; }
            .question-box { background: #f9f9f9; border-left: 4px solid #333; padding: 15px; margin: 20px 0; }
          </style>
        </head>
        <body>
          <h1>AI Career Assistant - ${activeTab.replace("-", " ").toUpperCase()} REPORT</h1>
          <div id="content"></div>
        </body>
      </html>
    `);

    const container = printWindow.document.getElementById("content");
    let html = "";

    if (activeTab === "review") {
      html += `<h2>Overall Review</h2><p>${resultData.overall_review || ""}</p>`;
      html += `<h2>Resume Improvements</h2><ul>${(resultData.resume_improvements || []).map(i => `<li>${i}</li>`).join("")}</ul>`;
      html += `<h2>Better Summary</h2><p>${resultData.better_summary || ""}</p>`;
      html += `<h2>Suggested Skills</h2><ul>${(resultData.better_skills || []).map(s => `<li>${s}</li>`).join("")}</ul>`;
      html += `<h2>Experience Recommendations</h2><p>${resultData.better_experience || ""}</p>`;
      html += `<h2>Better Project Descriptions</h2><ul>${(resultData.better_projects || []).map(p => `<li>${p}</li>`).join("")}</ul>`;
    } else if (activeTab === "cover-letter") {
      html += `<h2>Professional Cover Letter</h2><p>${resultData.professional_cover_letter || ""}</p>`;
      html += `<h2>Company-Specific Version</h2><p>${resultData.company_specific_version || ""}</p>`;
      html += `<h2>ATS-Friendly Version</h2><p>${resultData.ats_friendly_version || ""}</p>`;
    } else if (activeTab === "rewrite") {
      html += `<h2>Stronger Bullet Points</h2><ul>${(resultData.stronger_bullet_points || []).map(b => `<li>${b}</li>`).join("")}</ul>`;
      html += `<h2>Action Verbs to Use</h2><ul>${(resultData.better_action_verbs || []).map(v => `<li>${v}</li>`).join("")}</ul>`;
      html += `<h2>Better Project Descriptions</h2><ul>${(resultData.better_project_descriptions || []).map(d => `<li>${d}</li>`).join("")}</ul>`;
    } else if (activeTab === "interview") {
      const cats = ["technical_questions", "hr_questions", "behavioral_questions", "resume_based_questions"];
      cats.forEach(cat => {
        html += `<h2>${cat.replace("_", " ").toUpperCase()}</h2>`;
        (resultData[cat] || []).forEach((q, idx) => {
          html += `<div class="question-box"><h3>Q${idx + 1}: ${q.question}</h3><p><strong>Suggested Answer:</strong> ${q.suggested_answer}</p></div>`;
        });
      });
    } else if (activeTab === "career") {
      html += `<h2>Learning Roadmap</h2><ul>${(resultData.learning_roadmap || []).map(r => `<li>${r}</li>`).join("")}</ul>`;
      html += `<h2>Missing Technologies</h2><ul>${(resultData.missing_technologies || []).map(t => `<li>${t}</li>`).join("")}</ul>`;
      html += `<h2>Certifications Suggested</h2><ul>${(resultData.certifications || []).map(c => `<li>${c}</li>`).join("")}</ul>`;
      html += `<h2>Career Suggestions</h2><ul>${(resultData.career_suggestions || []).map(s => `<li>${s}</li>`).join("")}</ul>`;
    }

    container.innerHTML = html;
    printWindow.document.close();
    printWindow.focus();
    setTimeout(() => {
      printWindow.print();
    }, 500);
  };

  const handleRunAI = async (toolType = activeTab) => {
    if (!selectedResumeId) {
      error("Please upload or select a resume first.");
      return;
    }

    setAiLoading(true);
    setResultData(null);
    
    // Add User Message to Chat for interactivity
    const toolNames = {
      review: "Resume Review",
      "cover-letter": "Cover Letter Generator",
      rewrite: "Resume Rewrite",
      interview: "Interview prep Generator",
      career: "Career Advisor"
    };
    
    setChatMessages(prev => [
      ...prev,
      { role: "user", content: `Triggering AI Tool: ${toolNames[toolType] || toolType}...` }
    ]);

    try {
      let data = null;
      if (toolType === "review") {
        const res = await aiService.reviewResume(selectedResumeId);
        data = res.data;
      } else if (toolType === "cover-letter") {
        const payload = {
          jobDescriptionId: selectedJobId === "custom" ? null : selectedJobId,
          companyName: selectedJobId === "custom" ? companyName : null,
          jobTitle: selectedJobId === "custom" ? jobTitle : null,
          jobText: selectedJobId === "custom" ? jobText : null,
        };
        const res = await aiService.generateCoverLetter(selectedResumeId, payload);
        data = res.data;
      } else if (toolType === "rewrite") {
        const res = await aiService.improveSummary(selectedResumeId);
        data = res.data;
      } else if (toolType === "interview") {
        const jobDescId = selectedJobId === "custom" ? null : selectedJobId;
        const res = await aiService.prepareInterview(selectedResumeId, jobDescId);
        data = res.data;
      } else if (toolType === "career") {
        const res = await aiService.suggestCareer(selectedResumeId);
        data = res.data;
      }

      setResultData(data);
      
      // Update Chat
      setChatMessages(prev => [
        ...prev,
        { role: "assistant", content: `Analysis complete! I've loaded the results into your workspace. You can view the details or export them using the actions below.` }
      ]);
      
      success("AI response generated and saved!");
      
      // Reload history
      const historyRes = await aiService.getHistory();
      setHistoryList(historyRes.data || []);
    } catch (err) {
      const errMsg = err.response?.data?.detail || err.message || "Failed to call AI assistant.";
      error(errMsg);
      setChatMessages(prev => [
        ...prev,
        { role: "assistant", content: `I encountered an error: ${errMsg}. Please ensure your API keys are configured and try again.` }
      ]);
    } finally {
      setAiLoading(false);
    }
  };

  const handleChatSubmit = (e) => {
    e.preventDefault();
    if (!chatInput.trim()) return;

    const input = chatInput.toLowerCase().trim();
    setChatMessages(prev => [...prev, { role: "user", content: chatInput }]);
    setChatInput("");

    // Simple routing rules to feel like an agent
    setTimeout(() => {
      if (input.includes("review") || input.includes("analyze")) {
        setChatMessages(prev => [
          ...prev,
          { role: "assistant", content: "I'll run a comprehensive Resume Review for you right away..." }
        ]);
        setActiveTab("review");
        handleRunAI("review");
      } else if (input.includes("cover letter") || input.includes("letter")) {
        setChatMessages(prev => [
          ...prev,
          { role: "assistant", content: "Opening the Cover Letter Generator. Please make sure to fill out the target company or description details, then click 'Generate Cover Letter'." }
        ]);
        setActiveTab("cover-letter");
      } else if (input.includes("rewrite") || input.includes("bullet") || input.includes("summary")) {
        setChatMessages(prev => [
          ...prev,
          { role: "assistant", content: "I'll rewrite your summary and experience bullet points to maximize impact..." }
        ]);
        setActiveTab("rewrite");
        handleRunAI("rewrite");
      } else if (input.includes("interview") || input.includes("question") || input.includes("hr")) {
        setChatMessages(prev => [
          ...prev,
          { role: "assistant", content: "Let's prepare for your interview! Generating mock questions now..." }
        ]);
        setActiveTab("interview");
        handleRunAI("interview");
      } else if (input.includes("career") || input.includes("roadmap") || input.includes("missing")) {
        setChatMessages(prev => [
          ...prev,
          { role: "assistant", content: "Analyzing career trajectories and generating roadmaps..." }
        ]);
        setActiveTab("career");
        handleRunAI("career");
      } else {
        setChatMessages(prev => [
          ...prev,
          { role: "assistant", content: "I can help you with: \n- 'Review my resume'\n- 'Generate a cover letter'\n- 'Rewrite my summary'\n- 'Generate interview questions'\n- 'Career roadmap guidance'\n\nSimply type one of the commands or click a tool tab!" }
        ]);
      }
    }, 600);
  };

  const handleDeleteHistory = async (id) => {
    try {
      await aiService.deleteHistory(id);
      success("History log deleted.");
      setHistoryList(prev => prev.filter(item => item.id !== id));
    } catch (err) {
      console.error(err);
      error("Failed to delete log.");
    }
  };

  const handleLoadHistoryItem = (item) => {
    try {
      const parsed = JSON.parse(item.response);
      setResultData(parsed);
      setActiveTab(item.prompt_type);
      setSelectedResumeId(item.resume_id || selectedResumeId);
      success(`Loaded ${item.prompt_type} from history.`);
      
      setChatMessages(prev => [
        ...prev,
        { role: "assistant", content: `I've loaded a historical ${item.prompt_type.replace("-", " ")} record from ${new Date(item.created_at).toLocaleDateString()}.` }
      ]);
    } catch (e) {
      console.error(e);
      error("Failed to parse historical response.");
    }
  };

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-[#050505] text-white">
        <div className="flex flex-col items-center gap-4">
          <Loader2 className="h-10 w-10 animate-spin text-white/50" />
          <p className="text-sm text-white/55">Initializing AI Workspace...</p>
        </div>
      </div>
    );
  }

  const promptCards = [
    { title: "Review Resume", desc: "Detailed ATS & content review", type: "review", icon: FileText },
    { title: "Cover Letter", desc: "Tailored to job & company", type: "cover-letter", icon: Briefcase },
    { title: "Rewrite Bullets", desc: "STAR method rephrasing", type: "rewrite", icon: FileCode },
    { title: "Interview Prep", desc: "Custom mock Q&A list", type: "interview", icon: HelpCircle },
    { title: "Career Advisor", desc: "Skill gap & certificate paths", type: "career", icon: TrendingUp },
  ];

  return (
    <ToastProvider>
      <div className="min-h-screen bg-[#050505] text-white">
        <div className="h-24" />

        <main className="mx-auto w-full max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
          
          {/* Header */}
          <div className="mb-8 flex flex-col md:flex-row md:items-center md:justify-between gap-4">
            <div>
              <h1 className="text-3xl font-semibold tracking-tight text-white flex items-center gap-2">
                <Sparkles className="h-8 w-8 text-white/80" />
                AI Assistant Workspace
              </h1>
              <p className="text-sm text-white/55 mt-1">
                Generate high-impact modifications, custom cover letters, and prepare for interviews using Groq AI.
              </p>
            </div>

            {/* Select Resume Bar */}
            <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-3">
              <div className="flex flex-col gap-1">
                <label className="text-xs text-white/50 font-medium">Select Resume</label>
                <select
                  value={selectedResumeId}
                  onChange={(e) => setSelectedResumeId(e.target.value)}
                  className="bg-[#111] border border-white/10 rounded-xl px-4 py-2 text-sm text-white focus:outline-none focus:ring-1 focus:ring-white/20 min-w-[200px]"
                >
                  {resumes.length === 0 ? (
                    <option value="">No resumes uploaded</option>
                  ) : (
                    resumes.map(r => (
                      <option key={r.id} value={r.id}>{r.title}</option>
                    ))
                  )}
                </select>
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
            
            {/* Left Column: Chat & Tool Panel */}
            <div className="lg:col-span-5 flex flex-col gap-6">
              
              {/* AI Chat Box */}
              <Card className="glass-card flex flex-col h-[380px] p-4">
                <div className="flex items-center gap-2 border-b border-white/5 pb-3 mb-3">
                  <div className="h-2 w-2 rounded-full bg-green-500 animate-pulse" />
                  <span className="text-xs font-semibold uppercase tracking-wider text-white/50">AI Copilot</span>
                </div>

                <div className="flex-1 overflow-y-auto pr-2 space-y-3 scrollbar-thin">
                  {chatMessages.map((msg, idx) => (
                    <div key={idx} className={`flex gap-2.5 ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
                      {msg.role === "assistant" && (
                        <div className="h-7 w-7 rounded-full bg-white/10 flex items-center justify-center flex-shrink-0">
                          <Sparkles className="h-4 w-4 text-white/70" />
                        </div>
                      )}
                      <div
                        className={`rounded-2xl px-4 py-2.5 text-sm max-w-[80%] whitespace-pre-wrap leading-relaxed ${
                          msg.role === "user"
                            ? "bg-white text-black rounded-tr-none"
                            : "bg-[#161616] text-white/90 border border-white/5 rounded-tl-none"
                        }`}
                      >
                        {msg.content}
                      </div>
                    </div>
                  ))}
                  <div ref={chatEndRef} />
                </div>

                <form onSubmit={handleChatSubmit} className="mt-4 flex gap-2">
                  <input
                    type="text"
                    value={chatInput}
                    onChange={(e) => setChatInput(e.target.value)}
                    placeholder="Ask AI, e.g. 'Review my resume'..."
                    className="flex-1 bg-[#111] border border-white/5 rounded-xl px-4 py-2.5 text-sm text-white focus:outline-none focus:ring-1 focus:ring-white/20"
                  />
                  <Button type="submit" size="icon" className="rounded-xl h-10 w-10">
                    <Send className="h-4 w-4" />
                  </Button>
                </form>
              </Card>

              {/* Prompt Cards Grid */}
              <div className="grid grid-cols-2 gap-3">
                {promptCards.map((card) => {
                  const Icon = card.icon;
                  return (
                    <button
                      key={card.type}
                      onClick={() => {
                        setActiveTab(card.type);
                        setChatMessages(prev => [
                          ...prev,
                          { role: "assistant", content: `Switching to ${card.title}. You can now run the tool or change configuration parameters.` }
                        ]);
                      }}
                      className={`text-left p-3 rounded-xl border border-white/5 transition-all duration-200 ${
                        activeTab === card.type
                          ? "bg-white/10 border-white/20 shadow-md"
                          : "bg-surface/30 hover:bg-surface/60"
                      }`}
                    >
                      <Icon className="h-5 w-5 text-white/60 mb-2" />
                      <h3 className="text-xs font-semibold text-white">{card.title}</h3>
                      <p className="text-[10px] text-white/40 mt-0.5">{card.desc}</p>
                    </button>
                  );
                })}
              </div>

            </div>

            {/* Right Column: Active Tool Workbench */}
            <div className="lg:col-span-7 flex flex-col gap-6">
              
              {/* Workspace Container */}
              <Card className="glass-card p-6 flex flex-col min-h-[500px]">
                
                {/* Tabs */}
                <div className="flex border-b border-white/5 pb-3 mb-6 overflow-x-auto gap-4 scrollbar-none">
                  {promptCards.map(tab => (
                    <button
                      key={tab.type}
                      onClick={() => {
                        setActiveTab(tab.type);
                        setResultData(null);
                      }}
                      className={`text-sm font-medium pb-2 border-b-2 transition-all relative ${
                        activeTab === tab.type
                          ? "text-white border-white"
                          : "text-white/40 border-transparent hover:text-white/60"
                      }`}
                    >
                      {tab.title}
                    </button>
                  ))}
                  <button
                    onClick={() => {
                      setActiveTab("history");
                      setResultData(null);
                    }}
                    className={`text-sm font-medium pb-2 border-b-2 transition-all flex items-center gap-1.5 ${
                      activeTab === "history"
                        ? "text-white border-white"
                        : "text-white/40 border-transparent hover:text-white/60"
                    }`}
                  >
                    <History className="h-3.5 w-3.5" />
                    History
                  </button>
                </div>

                {/* Workbench Configuration / Form Content */}
                <div className="flex-1 flex flex-col">
                  
                  {activeTab === "cover-letter" && (
                    <div className="mb-6 p-4 rounded-xl border border-white/5 bg-white/[0.01] space-y-4">
                      <div className="flex flex-col gap-1">
                        <label className="text-xs text-white/50 font-medium">Select Job Description (Optional)</label>
                        <select
                          value={selectedJobId}
                          onChange={(e) => setSelectedJobId(e.target.value)}
                          className="bg-[#111] border border-white/10 rounded-xl px-4 py-2 text-sm text-white focus:outline-none"
                        >
                          {jobs.map(j => (
                            <option key={j.id} value={j.id}>{j.company} — {j.title}</option>
                          ))}
                          <option value="custom">-- Create Custom Job Description --</option>
                        </select>
                      </div>

                      {selectedJobId === "custom" && (
                        <motion.div
                          initial={{ opacity: 0, height: 0 }}
                          animate={{ opacity: 1, height: "auto" }}
                          className="space-y-3 pt-2"
                        >
                          <div className="grid grid-cols-2 gap-3">
                            <div className="flex flex-col gap-1">
                              <label className="text-xs text-white/50 font-medium">Company Name</label>
                              <input
                                type="text"
                                value={companyName}
                                onChange={(e) => setCompanyName(e.target.value)}
                                className="bg-[#111] border border-white/5 rounded-xl px-3 py-2 text-sm text-white"
                                placeholder="Google"
                              />
                            </div>
                            <div className="flex flex-col gap-1">
                              <label className="text-xs text-white/50 font-medium">Job Title</label>
                              <input
                                type="text"
                                value={jobTitle}
                                onChange={(e) => setJobTitle(e.target.value)}
                                className="bg-[#111] border border-white/5 rounded-xl px-3 py-2 text-sm text-white"
                                placeholder="Frontend Architect"
                              />
                            </div>
                          </div>
                          <div className="flex flex-col gap-1">
                            <label className="text-xs text-white/50 font-medium">Job Description / Requirements</label>
                            <textarea
                              value={jobText}
                              onChange={(e) => setJobText(e.target.value)}
                              rows={3}
                              className="bg-[#111] border border-white/5 rounded-xl px-3 py-2 text-sm text-white resize-none"
                              placeholder="Paste key skills, responsibilities, and requirements here..."
                            />
                          </div>
                        </motion.div>
                      )}
                    </div>
                  )}

                  {activeTab === "interview" && (
                    <div className="mb-6 p-4 rounded-xl border border-white/5 bg-white/[0.01] space-y-4">
                      <div className="flex flex-col gap-1">
                        <label className="text-xs text-white/50 font-medium">Select Job (Optional: aligns questions to target job)</label>
                        <select
                          value={selectedJobId}
                          onChange={(e) => setSelectedJobId(e.target.value)}
                          className="bg-[#111] border border-white/10 rounded-xl px-4 py-2 text-sm text-white focus:outline-none"
                        >
                          <option value="">-- No job description (Resume-based only) --</option>
                          {jobs.map(j => (
                            <option key={j.id} value={j.id}>{j.company} — {j.title}</option>
                          ))}
                        </select>
                      </div>
                    </div>
                  )}

                  {/* Run Button (for non-history tabs) */}
                  {activeTab !== "history" && !resultData && (
                    <div className="flex-1 flex flex-col items-center justify-center p-8 text-center border border-dashed border-white/10 rounded-xl">
                      <Sparkles className="h-10 w-10 text-white/30 mb-3 animate-pulse" />
                      <h3 className="text-sm font-semibold text-white">Ready to Process</h3>
                      <p className="text-xs text-white/40 max-w-[280px] mt-1 mb-4">
                        Press the generate button to analyze details and calculate insights using Groq AI.
                      </p>
                      <Button
                        onClick={() => handleRunAI()}
                        disabled={aiLoading}
                        className="rounded-full px-6"
                      >
                        {aiLoading ? (
                          <>
                            <Loader2 className="h-4 w-4 animate-spin mr-2" />
                            Processing with AI...
                          </>
                        ) : (
                          <>
                            Run AI Workspace
                            <ArrowRight className="h-4 w-4 ml-2" />
                          </>
                        )}
                      </Button>
                    </div>
                  )}

                  {/* Show Results with Animations */}
                  <AnimatePresence>
                    {resultData && activeTab !== "history" && (
                      <motion.div
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0 }}
                        className="space-y-6"
                      >
                        {/* Result Control Actions */}
                        <div className="flex justify-between items-center bg-white/[0.02] border border-white/5 p-3 rounded-xl mb-4">
                          <span className="text-xs text-white/40 font-mono">Report Ready</span>
                          <div className="flex gap-2">
                            <Button variant="ghost" size="sm" onClick={handleCopy} className="text-white/60 hover:text-white">
                              {copied ? <Check className="h-4 w-4 mr-1 text-green-400" /> : <Copy className="h-4 w-4 mr-1" />}
                              Copy
                            </Button>
                            <Button variant="ghost" size="sm" onClick={handleExportMarkdown} className="text-white/60 hover:text-white">
                              <Download className="h-4 w-4 mr-1" />
                              Markdown
                            </Button>
                            <Button variant="ghost" size="sm" onClick={handlePrintPDF} className="text-white/60 hover:text-white">
                              <Printer className="h-4 w-4 mr-1" />
                              PDF
                            </Button>
                          </div>
                        </div>

                        {/* Rendering by active tab */}
                        {activeTab === "review" && (
                          <div className="space-y-5">
                            <div>
                              <h3 className="text-sm font-semibold text-white mb-1.5 flex items-center gap-1.5">
                                <FileText className="h-4 w-4 text-white/60" />
                                Overall Review
                              </h3>
                              <p className="text-sm text-white/70 leading-relaxed bg-[#111] p-3 rounded-lg border border-white/5">
                                {resultData.overall_review}
                              </p>
                            </div>

                            <div>
                              <h3 className="text-sm font-semibold text-white mb-1.5">Resume Improvements</h3>
                              <ul className="space-y-1 bg-[#111] p-3 rounded-lg border border-white/5">
                                {(resultData.resume_improvements || []).map((imp, i) => (
                                  <li key={i} className="text-sm text-white/75 flex items-start gap-2">
                                    <span className="text-red-400">•</span>
                                    {imp}
                                  </li>
                                ))}
                              </ul>
                            </div>

                            <div>
                              <h3 className="text-sm font-semibold text-white mb-1.5">Better Profile Summary</h3>
                              <p className="text-sm text-white/70 leading-relaxed bg-[#111] p-3 rounded-lg border border-white/5 italic">
                                "{resultData.better_summary}"
                              </p>
                            </div>

                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                              <div>
                                <h3 className="text-sm font-semibold text-white mb-1.5 flex items-center gap-1">
                                  <Award className="h-3.5 w-3.5 text-white/50" />
                                  Suggested Skills
                                </h3>
                                <div className="flex flex-wrap gap-1.5 bg-[#111] p-3 rounded-lg border border-white/5">
                                  {(resultData.better_skills || []).map((sk, i) => (
                                    <span key={i} className="text-[10px] bg-white/10 text-white/90 px-2 py-0.5 rounded-full">
                                      {sk}
                                    </span>
                                  ))}
                                </div>
                              </div>
                              <div>
                                <h3 className="text-sm font-semibold text-white mb-1.5 flex items-center gap-1">
                                  <BookOpen className="h-3.5 w-3.5 text-white/50" />
                                  Experience Boosters
                                </h3>
                                <p className="text-xs text-white/70 bg-[#111] p-3 rounded-lg border border-white/5 leading-relaxed">
                                  {resultData.better_experience}
                                </p>
                              </div>
                            </div>
                          </div>
                        )}

                        {activeTab === "cover-letter" && (
                          <div className="space-y-6">
                            <div>
                              <h3 className="text-sm font-semibold text-white mb-2">Professional Cover Letter</h3>
                              <p className="text-xs text-white/75 bg-[#111] p-4 rounded-xl border border-white/5 whitespace-pre-wrap leading-relaxed">
                                {resultData.professional_cover_letter}
                              </p>
                            </div>
                            <div>
                              <h3 className="text-sm font-semibold text-white mb-2">Company-Specific Variant</h3>
                              <p className="text-xs text-white/75 bg-[#111] p-4 rounded-xl border border-white/5 whitespace-pre-wrap leading-relaxed">
                                {resultData.company_specific_version}
                              </p>
                            </div>
                            <div>
                              <h3 className="text-sm font-semibold text-white mb-2">ATS-Friendly Version</h3>
                              <p className="text-xs text-white/75 bg-[#111] p-4 rounded-xl border border-white/5 whitespace-pre-wrap leading-relaxed">
                                {resultData.ats_friendly_version}
                              </p>
                            </div>
                          </div>
                        )}

                        {activeTab === "rewrite" && (
                          <div className="space-y-4">
                            <div>
                              <h3 className="text-sm font-semibold text-white mb-1.5">Stronger Bullet Points (STAR Method)</h3>
                              <ul className="space-y-2 bg-[#111] p-3 rounded-lg border border-white/5">
                                {(resultData.stronger_bullet_points || []).map((bullet, i) => (
                                  <li key={i} className="text-sm text-white/75 flex items-start gap-2">
                                    <span className="text-white/30">•</span>
                                    {bullet}
                                  </li>
                                ))}
                              </ul>
                            </div>
                            <div>
                              <h3 className="text-sm font-semibold text-white mb-1.5">Better Project Descriptions</h3>
                              <ul className="space-y-2 bg-[#111] p-3 rounded-lg border border-white/5">
                                {(resultData.better_project_descriptions || []).map((desc, i) => (
                                  <li key={i} className="text-sm text-white/75 flex items-start gap-2">
                                    <span className="text-white/30">•</span>
                                    {desc}
                                  </li>
                                ))}
                              </ul>
                            </div>
                            <div>
                              <h3 className="text-sm font-semibold text-white mb-1.5">Action Verbs to Incorporate</h3>
                              <div className="flex flex-wrap gap-1.5">
                                {(resultData.better_action_verbs || []).map((v, i) => (
                                  <span key={i} className="text-xs bg-white/5 text-white/80 border border-white/5 px-2.5 py-1 rounded-lg">
                                    {v}
                                  </span>
                                ))}
                              </div>
                            </div>
                          </div>
                        )}

                        {activeTab === "interview" && (
                          <div className="space-y-5">
                            {["technical_questions", "hr_questions", "behavioral_questions", "resume_based_questions"].map(cat => {
                              const list = resultData[cat] || [];
                              if (list.length === 0) return null;
                              return (
                                <div key={cat}>
                                  <h3 className="text-sm font-semibold uppercase tracking-wider text-white/55 mb-2.5">
                                    {cat.replace("_", " ")}
                                  </h3>
                                  <div className="space-y-3">
                                    {list.map((item, idx) => (
                                      <div key={idx} className="bg-[#111] border border-white/5 p-4 rounded-xl">
                                        <h4 className="text-sm font-medium text-white mb-1.5">Q: {item.question}</h4>
                                        <p className="text-xs text-white/60 leading-relaxed pl-3 border-l-2 border-white/20">
                                          {item.suggested_answer}
                                        </p>
                                      </div>
                                    ))}
                                  </div>
                                </div>
                              );
                            })}
                          </div>
                        )}

                        {activeTab === "career" && (
                          <div className="space-y-5">
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
                              <div>
                                <h3 className="text-sm font-semibold text-white mb-2">Learning Roadmap</h3>
                                <ul className="space-y-1.5 bg-[#111] p-3 rounded-lg border border-white/5">
                                  {(resultData.learning_roadmap || []).map((r, i) => (
                                    <li key={i} className="text-xs text-white/70 flex items-start gap-2">
                                      <span className="text-white/40 font-mono">{i+1}.</span>
                                      {r}
                                    </li>
                                  ))}
                                </ul>
                              </div>
                              <div>
                                <h3 className="text-sm font-semibold text-white mb-2">Suggested Certifications</h3>
                                <ul className="space-y-1.5 bg-[#111] p-3 rounded-lg border border-white/5">
                                  {(resultData.certifications || []).map((c, i) => (
                                    <li key={i} className="text-xs text-white/70 flex items-start gap-2">
                                      <span className="text-yellow-500">•</span>
                                      {c}
                                    </li>
                                  ))}
                                </ul>
                              </div>
                            </div>

                            <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
                              <div>
                                <h3 className="text-sm font-semibold text-white mb-2">Missing Skills & Technologies</h3>
                                <div className="flex flex-wrap gap-1.5">
                                  {(resultData.missing_technologies || []).map((t, i) => (
                                    <span key={i} className="text-xs bg-red-500/10 border border-red-500/20 text-red-300 px-3 py-1 rounded-xl">
                                      {t}
                                    </span>
                                  ))}
                                </div>
                              </div>
                              <div>
                                <h3 className="text-sm font-semibold text-white mb-2">Alternative Career Suggests</h3>
                                <ul className="space-y-1 bg-[#111] p-3 rounded-lg border border-white/5">
                                  {(resultData.career_suggestions || []).map((s, i) => (
                                    <li key={i} className="text-xs text-white/70">
                                      → {s}
                                    </li>
                                  ))}
                                </ul>
                              </div>
                            </div>
                          </div>
                        )}

                        <div className="flex justify-end pt-4">
                          <Button variant="outline" className="rounded-full" onClick={() => setResultData(null)}>
                            Clear Results
                          </Button>
                        </div>

                      </motion.div>
                    )}
                  </AnimatePresence>

                  {/* History View */}
                  {activeTab === "history" && (
                    <div className="space-y-3">
                      {historyList.length === 0 ? (
                        <div className="text-center py-12 text-white/40">
                          <History className="h-8 w-8 mx-auto mb-2 text-white/20" />
                          <p className="text-sm">No historical AI logs found.</p>
                        </div>
                      ) : (
                        <div className="space-y-3 max-h-[480px] overflow-y-auto pr-1">
                          {historyList.map((item) => (
                            <div
                              key={item.id}
                              className="bg-surface/30 border border-white/5 p-4 rounded-xl flex items-center justify-between hover:bg-surface/60 transition-all cursor-pointer"
                              onClick={() => handleLoadHistoryItem(item)}
                            >
                              <div className="flex items-center gap-3">
                                <div className="h-8 w-8 rounded-lg bg-white/5 flex items-center justify-center">
                                  <Sparkles className="h-4 w-4 text-white/60" />
                                </div>
                                <div>
                                  <h4 className="text-xs font-semibold text-white uppercase tracking-wider">
                                    {item.prompt_type.replace("-", " ")}
                                  </h4>
                                  <p className="text-[10px] text-white/40 mt-0.5">
                                    Provider: {item.provider} | {new Date(item.created_at).toLocaleString()}
                                  </p>
                                </div>
                              </div>
                              <div className="flex items-center gap-2">
                                <Button
                                  variant="ghost"
                                  size="icon"
                                  onClick={(e) => {
                                    e.stopPropagation();
                                    handleDeleteHistory(item.id);
                                  }}
                                  className="text-white/40 hover:text-red-400 rounded-lg h-8 w-8"
                                >
                                  <Trash2 className="h-4 w-4" />
                                </Button>
                              </div>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  )}

                </div>

              </Card>

            </div>

          </div>

        </main>
      </div>
    </ToastProvider>
  );
}
