import React, { useState, useEffect, useCallback } from "react";
import { useParams, Link, useNavigate } from "react-router-dom";
import {
  ArrowLeft,
  CheckCircle,
  AlertTriangle,
  Lightbulb,
  FileText,
  Loader2,
  TrendingUp,
  Brain,
  Hash,
  ShieldCheck
} from "lucide-react";
import {
  ResponsiveContainer,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  BarChart,
  CartesianGrid,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  Bar
} from "recharts";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { EmptyState } from "@/components/ui/EmptyState";
import atsService from "@/services/atsService";
import resumeService from "@/services/resumeService";
import { useToast } from "@/hooks/useToast";

export default function AtsDashboard() {
  const { id } = useParams(); // resume_id
  const navigate = useNavigate();
  const { toasts, success, error, removeToast } = useToast();

  const [resume, setResume] = useState(null);
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(true);
  const [analyzing, setAnalyzing] = useState(false);
  const [expandedCategory, setExpandedCategory] = useState(null);

  const handleTriggerAnalysis = useCallback(async (isAuto = false) => {
    setAnalyzing(true);
    if (!isAuto) {
      setLoading(true);
    }
    try {
      const response = await atsService.analyzeResume(id);
      setReport(response.data);
      success("ATS Score calculated successfully!");
    } catch {
      error("ATS scan failed. Please try again.");
    } finally {
      setAnalyzing(false);
      setLoading(false);
    }
  }, [id, success, error]);

  useEffect(() => {
    async function loadData() {
      try {
        // 1. Fetch resume details
        const resumeData = await resumeService.getResumeById(id);
        setResume(resumeData.data);

        // 2. Fetch analysis history to see if there's an existing report
        const historyData = await atsService.getAnalyses();
        const existingReport = historyData.data.find(
          (rep) => rep.resume_id === id
        );

        if (existingReport) {
          setReport(existingReport);
        } else {
          // No report yet, auto-trigger analysis
          await handleTriggerAnalysis(true);
        }
      } catch {
        error("Failed to load ATS details. Redirecting...");
        setTimeout(() => navigate(`/resumes/${id}`), 2000);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, [id, navigate, error, handleTriggerAnalysis]);

  if (loading) {
    return (
      <div className="min-h-screen bg-[#050505] text-white">
        <div className="h-24" />
        <main className="mx-auto w-full max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
          <div className="mb-8 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
            <div className="flex items-center gap-3">
              <Skeleton className="h-10 w-10 rounded-full" />
              <div>
                <Skeleton className="h-6 w-48 mb-2" />
                <Skeleton className="h-3 w-32" />
              </div>
            </div>
            <Skeleton className="h-10 w-32 rounded-full" />
          </div>
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            <Skeleton className="lg:col-span-1 p-8 h-80 rounded-xl" />
            <Skeleton className="lg:col-span-2 p-8 h-80 rounded-xl" />
          </div>
        </main>
      </div>
    );
  }

  // Pre-calculate chart data
  const categoryData = report
    ? [
        { subject: "Keywords", score: report.keyword_score, fullMark: 100 },
        { subject: "Experience", score: report.experience_score, fullMark: 100 },
        { subject: "Formatting", score: report.formatting_score, fullMark: 100 },
        { subject: "Sections", score: report.section_score || 0, fullMark: 100 },
        { subject: "Projects", score: report.projects_score, fullMark: 100 },
        { subject: "Education", score: report.education_score, fullMark: 100 },
        { subject: "Grammar", score: report.grammar_score, fullMark: 100 }
      ]
    : [];

  const comparisonData = report
    ? [
        { name: "Keywords", Candidate: report.keyword_score, Benchmark: 75 },
        { name: "Experience", Candidate: report.experience_score, Benchmark: 70 },
        { name: "Formatting", Candidate: report.formatting_score, Benchmark: 80 },
        { name: "Sections", Candidate: report.section_score || 0, Benchmark: 75 },
        { name: "Projects", Candidate: report.projects_score, Benchmark: 65 },
        { name: "Education", Candidate: report.education_score, Benchmark: 70 },
        { name: "Grammar", Candidate: report.grammar_score, Benchmark: 85 }
      ]
    : [];

  // Determine score color/feedback
  const score = report?.ats_score || 0;
  let scoreColor = "text-red-500 border-red-500/20 bg-red-500/5";
  let scoreText = "Weak Match";
  if (score >= 80) {
    scoreColor = "text-green-400 border-green-500/20 bg-green-500/5";
    scoreText = "Excellent Match";
  } else if (score >= 60) {
    scoreColor = "text-yellow-500 border-yellow-500/20 bg-yellow-500/5";
    scoreText = "Good Match";
  }

  return (
    <div className="min-h-screen bg-[#050505] text-white">
      <div className="h-24" />

      <main className="mx-auto w-full max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        {/* Header Action Row */}
        <div className="mb-8 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div className="flex items-center gap-3">
            <Link
              to={`/resumes/${id}`}
              className="p-2 rounded-full hover:bg-white/5 transition-colors text-white/55 hover:text-white"
              aria-label="Back to resume"
            >
                <ArrowLeft className="h-5 w-5" />
              </Link>
              <div>
                <h1 className="text-2xl font-semibold tracking-tight text-white">
                  ATS Score Analysis
                </h1>
                <p className="mt-1 text-xs text-white/45">
                  Resume: <code className="text-white/60">{resume?.title}</code>
                </p>
              </div>
            </div>

            <Button
              variant="outline"
              onClick={() => handleTriggerAnalysis(false)}
              disabled={analyzing}
              className="rounded-full gap-1.5 text-xs font-semibold"
            >
              {analyzing ? (
                <Loader2 className="h-3.5 w-3.5 animate-spin" />
              ) : (
                <TrendingUp className="h-3.5 w-3.5" />
              )}
              Re-Run Audit
            </Button>
          </div>

        {!report ? (
          <Card className="p-0 border-white/5 bg-white/[0.01]">
            <EmptyState 
              title="No ATS Audit Available" 
              description='No scores could be extracted. Click "Re-Run Audit" to calculate scores using our deterministic parser.' 
              icon={AlertTriangle} 
            />
          </Card>
        ) : (
            <div className="space-y-8">
              {/* Score summary and radar chart row */}
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                {/* Score gauge card */}
                <Card className="lg:col-span-1 p-8 flex flex-col items-center justify-center border-white/5 bg-white/[0.02] backdrop-blur-md relative overflow-hidden">
                  <div className="absolute inset-0 bg-radial-gradient from-white/5 to-transparent pointer-events-none" />
                  <span className="text-xs font-semibold text-white/45 tracking-widest uppercase mb-4">
                    ATS Match Score
                  </span>
                  
                  {/* Gauge */}
                  <div className="relative flex items-center justify-center h-48 w-48 mb-4">
                    <svg className="w-full h-full transform -rotate-90" viewBox="0 0 100 100">
                      {/* Outer track */}
                      <circle
                        cx="50"
                        cy="50"
                        r="42"
                        className="stroke-white/5"
                        strokeWidth="8"
                        fill="transparent"
                      />
                      {/* Score indicator */}
                      <circle
                        cx="50"
                        cy="50"
                        r="42"
                        className="transition-all duration-1000 ease-out"
                        strokeWidth="8"
                        strokeDasharray={2 * Math.PI * 42}
                        strokeDashoffset={2 * Math.PI * 42 * (1 - score / 100)}
                        stroke={score >= 80 ? "#22c55e" : score >= 60 ? "#f59e0b" : "#ef4444"}
                        strokeLinecap="round"
                        fill="transparent"
                      />
                    </svg>
                    <div className="absolute flex flex-col items-center">
                      <span className="text-5xl font-bold tracking-tight text-white">
                        {score}
                      </span>
                      <span className="text-[10px] text-white/40 mt-1 uppercase font-medium">
                        out of 100
                      </span>
                    </div>
                  </div>

                  <div className={`mt-2 rounded-full border px-4 py-1 text-xs font-semibold ${scoreColor}`}>
                    {scoreText}
                  </div>
                </Card>

                {/* Radar category breakdown card */}
                <Card className="lg:col-span-2 p-8 border-white/5 bg-white/[0.02] backdrop-blur-md">
                  <h3 className="text-sm font-semibold text-white mb-6 flex items-center gap-2">
                    <Brain className="h-4 w-4 text-white/50" />
                    Scoring Breakdown
                  </h3>
                  <div className="h-64 w-full flex items-center justify-center">
                    <ResponsiveContainer width="100%" height="100%">
                      <RadarChart cx="50%" cy="50%" outerRadius="80%" data={categoryData}>
                        <PolarGrid stroke="rgba(255,255,255,0.05)" />
                        <PolarAngleAxis
                          dataKey="subject"
                          tick={{ fill: "rgba(255,255,255,0.55)", fontSize: 11 }}
                        />
                        <PolarRadiusAxis
                          angle={30}
                          domain={[0, 100]}
                          tick={{ fill: "rgba(255,255,255,0.3)", fontSize: 9 }}
                        />
                        <Radar
                          name="Resume Score"
                          dataKey="score"
                          stroke="#ffffff"
                          fill="rgba(255, 255, 255, 0.15)"
                          fillOpacity={0.6}
                        />
                      </RadarChart>
                    </ResponsiveContainer>
                  </div>
                </Card>
              </div>

              {/* Progress bars & comparison chart row */}
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                {/* Progress bars list */}
                <Card className="lg:col-span-1 p-8 border-white/5 bg-white/[0.02]">
                  <h3 className="text-sm font-semibold text-white flex items-center gap-2">
                    <Hash className="h-4 w-4 text-white/50" />
                    Category Ratings
                  </h3>
                  <p className="text-[10px] text-white/30 mt-1 mb-6 font-normal">Click a category below to view explainable scoring reasons</p>
                  <div className="space-y-5">
                    {categoryData.map((cat) => {
                      let color = "bg-red-500";
                      if (cat.score >= 80) color = "bg-green-500";
                      else if (cat.score >= 60) color = "bg-yellow-500";

                      return (
                        <div
                          key={cat.subject}
                          className="space-y-1.5 cursor-pointer hover:bg-white/[0.02] p-2 -mx-2 rounded transition-all duration-200"
                          onClick={() => setExpandedCategory(expandedCategory === cat.subject ? null : cat.subject)}
                        >
                          <div className="flex items-center justify-between text-xs">
                            <span className="text-white/60 font-medium">{cat.subject}</span>
                            <div className="flex items-center gap-1.5">
                              <span className="text-white font-semibold">{cat.score}%</span>
                              <span className="text-[9px] text-white/30">
                                {expandedCategory === cat.subject ? "▼" : "▶"}
                              </span>
                            </div>
                          </div>
                          <div className="h-1.5 w-full bg-white/5 rounded-full overflow-hidden">
                            <div
                              className={`h-full ${color} rounded-full transition-all duration-1000`}
                              style={{ width: `${cat.score}%` }}
                            />
                          </div>

                          {expandedCategory === cat.subject && report.scoring_explanations?.[cat.subject] && (
                            <div className="mt-2.5 pl-3 border-l-2 border-white/10 space-y-1.5 text-[11px] text-white/70">
                              <div className="text-white/40 mb-1 flex justify-between text-[10px] tracking-wide uppercase font-semibold">
                                <span>Weighted Score:</span>
                                <span>
                                  {report.scoring_explanations[cat.subject].score} / {report.scoring_explanations[cat.subject].max_score} pts
                                </span>
                              </div>
                              {report.scoring_explanations[cat.subject].reasons.length === 0 ? (
                                <p className="text-green-400 italic">All checks passed, no deductions applied.</p>
                              ) : (
                                <div className="space-y-1.5">
                                  {report.scoring_explanations[cat.subject].reasons.map((reason, idx) => (
                                    <div key={idx} className="flex justify-between items-start gap-2">
                                      <span>• {reason.rule}</span>
                                      <span className={reason.points > 0 ? "text-green-400 font-semibold shrink-0" : "text-red-400 font-semibold shrink-0"}>
                                        {reason.points > 0 ? `+${reason.points}` : reason.points}
                                      </span>
                                    </div>
                                  ))}
                                </div>
                              )}
                            </div>
                          )}
                        </div>
                      );
                    })}
                  </div>
                </Card>

                {/* Benchmark Bar Chart */}
                <Card className="lg:col-span-2 p-8 border-white/5 bg-white/[0.02]">
                  <h3 className="text-sm font-semibold text-white mb-6 flex items-center gap-2">
                    <TrendingUp className="h-4 w-4 text-white/50" />
                    Comparison vs Industry Benchmarks
                  </h3>
                  <div className="h-64 w-full">
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart data={comparisonData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                        <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                        <XAxis
                          dataKey="name"
                          tick={{ fill: "rgba(255,255,255,0.55)", fontSize: 11 }}
                          axisLine={false}
                          tickLine={false}
                        />
                        <YAxis
                          domain={[0, 100]}
                          tick={{ fill: "rgba(255,255,255,0.3)", fontSize: 10 }}
                          axisLine={false}
                          tickLine={false}
                        />
                        <Tooltip
                          contentStyle={{
                            backgroundColor: "#111",
                            border: "1px solid rgba(255,255,255,0.1)",
                            borderRadius: "8px",
                            color: "#fff"
                          }}
                        />
                        <Legend wrapperStyle={{ fontSize: 11, paddingTop: 10 }} />
                        <Bar dataKey="Candidate" fill="#ffffff" radius={[4, 4, 0, 0]} />
                        <Bar dataKey="Benchmark" fill="rgba(255,255,255,0.2)" radius={[4, 4, 0, 0]} />
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                </Card>
              </div>

              {/* Strengths & Weaknesses row */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                {/* Strengths */}
                <Card className="p-8 border-white/5 bg-white/[0.02]">
                  <h3 className="text-sm font-semibold text-green-400 mb-6 flex items-center gap-2">
                    <CheckCircle className="h-4 w-4" />
                    Identified Strengths
                  </h3>
                  <ul className="space-y-4">
                    {report.strengths.map((str, idx) => (
                      <li key={idx} className="flex items-start gap-3 text-xs text-white/70 leading-relaxed border-b border-white/5 pb-3 last:border-0 last:pb-0">
                        <span className="h-1.5 w-1.5 rounded-full bg-green-400 mt-2 shrink-0" />
                        {str}
                      </li>
                    ))}
                  </ul>
                </Card>

                {/* Weaknesses */}
                <Card className="p-8 border-white/5 bg-white/[0.02]">
                  <h3 className="text-sm font-semibold text-red-400 mb-6 flex items-center gap-2">
                    <AlertTriangle className="h-4 w-4" />
                    Areas for Improvement
                  </h3>
                  <ul className="space-y-4">
                    {report.weaknesses.map((weak, idx) => (
                      <li key={idx} className="flex items-start gap-3 text-xs text-white/70 leading-relaxed border-b border-white/5 pb-3 last:border-0 last:pb-0">
                        <span className="h-1.5 w-1.5 rounded-full bg-red-400 mt-2 shrink-0" />
                        {weak}
                      </li>
                    ))}
                  </ul>
                </Card>
              </div>

              {/* Missing keywords & Suggestions row */}
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                {/* Missing keywords */}
                <Card className="lg:col-span-1 p-8 border-white/5 bg-white/[0.02]">
                  <h3 className="text-sm font-semibold text-yellow-500 mb-6 flex items-center gap-2">
                    <Hash className="h-4 w-4" />
                    Missing Critical Keywords
                  </h3>
                  {report.missing_keywords.length === 0 ? (
                    <div className="text-center py-6">
                      <ShieldCheck className="h-8 w-8 text-green-500 mx-auto mb-2" />
                      <p className="text-xs text-white/60">All recommended keywords detected!</p>
                    </div>
                  ) : (
                    <div className="flex flex-wrap gap-2">
                      {report.missing_keywords.map((kw, idx) => (
                        <span
                          key={idx}
                          className="rounded-full bg-yellow-500/10 border border-yellow-500/20 px-3 py-1 text-xs text-yellow-500 font-medium"
                        >
                          {kw}
                        </span>
                      ))}
                    </div>
                  )}
                </Card>

                {/* Actionable suggestions */}
                <Card className="lg:col-span-2 p-8 border-white/5 bg-white/[0.02]">
                  <h3 className="text-sm font-semibold text-white mb-6 flex items-center gap-2">
                    <Lightbulb className="h-4 w-4 text-white/50" />
                    Actionable Optimization Suggestions
                  </h3>
                  <ul className="space-y-4">
                    {report.suggestions.map((sug, idx) => (
                      <li key={idx} className="flex items-start gap-3 text-xs text-white/70 leading-relaxed border-b border-white/5 pb-3 last:border-0 last:pb-0">
                        <span className="h-1.5 w-1.5 rounded-full bg-white/30 mt-2 shrink-0" />
                        {sug}
                      </li>
                    ))}
                  </ul>
                </Card>
              </div>

              {/* Quality Report metadata card */}
              <Card className="p-8 border-white/5 bg-white/[0.02] flex flex-col md:flex-row md:items-center justify-between gap-6">
                <div className="flex items-center gap-4">
                  <div className="h-12 w-12 rounded-xl bg-white/5 flex items-center justify-center text-white/60 border border-white/10 shadow-inner">
                    <FileText className="h-6 w-6" />
                  </div>
                  <div>
                    <h3 className="text-sm font-semibold text-white">Resume Quality Audit Report</h3>
                    <p className="text-xs text-white/45 mt-0.5">
                      Report generated on {new Date(report.created_at).toLocaleString()}
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  <Button
                    variant="outline"
                    onClick={() => navigate(`/resumes/${id}`)}
                    className="rounded-full text-xs font-semibold"
                  >
                    Back to Viewer
                  </Button>
                </div>
              </Card>
            </div>
          )}
      </main>
    </div>
  );
}
