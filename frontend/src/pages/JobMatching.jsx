import React, { useState, useEffect, useCallback } from "react";
import {
  Briefcase,
  CheckCircle,
  AlertTriangle,
  Lightbulb,
  Loader2,
  Trash2,
  Eye,
  PlusCircle,
  ChevronDown,
  ChevronUp,
  MapPin,
  Clock,
  Sparkles
} from "lucide-react";
import {
  ResponsiveContainer,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  Tooltip
} from "recharts";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { EmptyState } from "@/components/ui/EmptyState";
import jobMatchingService from "@/services/jobMatchingService";
import resumeService from "@/services/resumeService";
import { useToast } from "@/hooks/useToast";

export default function JobMatching() {
  const { success, error } = useToast();

  const [resumes, setResumes] = useState([]);
  const [history, setHistory] = useState([]);
  const [selectedResumeId, setSelectedResumeId] = useState("");
  
  // Form State
  const [form, setForm] = useState({
    title: "",
    company: "",
    location: "",
    employment_type: "Full-time",
    description: "",
    required_skills: "",
    preferred_skills: "",
    required_experience: "",
    education_requirement: ""
  });

  const [loading, setLoading] = useState(true);
  const [matching, setMatching] = useState(false);
  const [activeReport, setActiveReport] = useState(null);
  const [expandedCategory, setExpandedCategory] = useState(null);

  // Load Resumes and Match History
  const loadData = useCallback(async () => {
    try {
      const resumesData = await resumeService.getResumes();
      setResumes(resumesData.data || []);
      if (resumesData.data && resumesData.data.length > 0) {
        setSelectedResumeId(resumesData.data[0].id);
      }

      const historyData = await jobMatchingService.getMatches();
      setHistory(historyData.data || []);
    } catch (err) {
      console.error(err);
      error("Failed to load initial data. Please reload the page.");
    } finally {
      setLoading(false);
    }
  }, [error]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  // Handle Form Change
  const handleChange = (e) => {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  };

  // Run Match
  const handleMatch = async (e) => {
    e.preventDefault();
    if (!selectedResumeId) {
      error("Please select a resume to match.");
      return;
    }
    if (!form.title || !form.company || !form.description) {
      error("Job Title, Company, and Job Description are required.");
      return;
    }

    setMatching(true);
    try {
      const payload = {
        resume_id: selectedResumeId,
        job_description: {
          title: form.title,
          company: form.company,
          location: form.location || null,
          employment_type: form.employment_type || null,
          description: form.description,
          required_skills: form.required_skills
            ? form.required_skills.split(",").map((s) => s.trim()).filter(Boolean)
            : [],
          preferred_skills: form.preferred_skills
            ? form.preferred_skills.split(",").map((s) => s.trim()).filter(Boolean)
            : [],
          required_experience: form.required_experience || null,
          education_requirement: form.education_requirement || null
        }
      };

      const response = await jobMatchingService.matchJob(payload);
      setActiveReport(response.data);
      success("Job match calculations computed!");
      
      // Refresh history list
      const updatedHistory = await jobMatchingService.getMatches();
      setHistory(updatedHistory.data || []);
    } catch (err) {
      error(err.response?.data?.message || "Job match calculation failed.");
    } finally {
      setMatching(false);
    }
  };

  // View historical report
  const handleViewReport = async (id) => {
    setLoading(true);
    try {
      const response = await jobMatchingService.getMatchById(id);
      setActiveReport(response.data);
      success("Loaded job match report.");
      window.scrollTo({ top: 0, behavior: "smooth" });
    } catch (err) {
      console.error(err);
      error("Failed to load match report details.");
    } finally {
      setLoading(false);
    }
  };

  // Delete historical report
  const handleDeleteReport = async (id) => {
    try {
      await jobMatchingService.deleteMatch(id);
      success("Match report deleted.");
      setHistory((prev) => prev.filter((item) => item.id !== id));
      if (activeReport && activeReport.id === id) {
        setActiveReport(null);
      }
    } catch (err) {
      console.error(err);
      error("Failed to delete match report.");
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-[#050505] text-white">
        <div className="h-24" />
        <main className="mx-auto w-full max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
          <div className="mb-8 flex flex-col md:flex-row md:items-center md:justify-between gap-4">
            <div>
              <Skeleton className="h-8 w-64 mb-2" />
              <Skeleton className="h-4 w-96" />
            </div>
          </div>
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
            <div className="lg:col-span-5 space-y-6">
              <Skeleton className="h-[600px] w-full rounded-xl" />
            </div>
            <div className="lg:col-span-7 space-y-6">
              <Skeleton className="h-[400px] w-full rounded-xl" />
            </div>
          </div>
        </main>
      </div>
    );
  }

  // Pre-calculate Radar Chart Data
  const radarData = activeReport?.score_explanations
    ? Object.keys(activeReport.score_explanations).map((key) => ({
        subject: key,
        Score: activeReport.score_explanations[key].percentage,
        fullMark: 100
      }))
    : [];

  const getPriorityColor = (prio) => {
    if (prio === "High") return "text-red-400 border-red-500/20 bg-red-500/5";
    if (prio === "Medium") return "text-yellow-400 border-yellow-500/20 bg-yellow-500/5";
    return "text-green-400 border-green-500/20 bg-green-500/5";
  };

  return (
      <div className="min-h-screen bg-[#050505] text-white">
        <div className="h-24" />

        <main className="mx-auto w-full max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
          <div className="mb-8 flex flex-col md:flex-row md:items-center md:justify-between gap-4">
            <div>
              <h1 className="text-3xl font-semibold tracking-tight text-white flex items-center gap-2">
                <Briefcase className="h-8 w-8 text-white/70" />
                Job Matching Engine
              </h1>
              <p className="mt-1 text-sm text-white/45">
                Deterministic, rule-based algorithmic matching without AI dependencies.
              </p>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
            
            {/* LEFT: JOB DESCRIPTION FORM & CONFIG */}
            <div className="lg:col-span-5 space-y-6">
              <Card className="p-6 border-white/5 bg-white/[0.02] backdrop-blur-md">
                <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                  <PlusCircle className="h-5 w-5 text-white/60" />
                  Job Specification
                </h2>

                <form onSubmit={handleMatch} className="space-y-4">
                  {/* Select Resume */}
                  <div>
                    <label className="block text-xs font-semibold text-white/50 uppercase tracking-wider mb-2">
                      Target Resume
                    </label>
                    <select
                      value={selectedResumeId}
                      onChange={(e) => setSelectedResumeId(e.target.value)}
                      className="w-full rounded-lg border border-white/10 bg-white/5 px-3 py-2 text-sm text-white focus:outline-none focus:ring-1 focus:ring-white/20"
                    >
                      {resumes.map((res) => (
                        <option key={res.id} value={res.id} className="bg-black text-white">
                          {res.title}
                        </option>
                      ))}
                    </select>
                    {resumes.length === 0 && (
                      <p className="mt-1.5 text-xs text-red-400">
                        No resumes found. Please upload a resume first.
                      </p>
                    )}
                  </div>

                  {/* Title & Company */}
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-xs font-semibold text-white/50 uppercase tracking-wider mb-2">
                        Job Title *
                      </label>
                      <input
                        type="text"
                        name="title"
                        required
                        value={form.title}
                        onChange={handleChange}
                        placeholder="e.g. Backend Engineer"
                        className="w-full rounded-lg border border-white/10 bg-white/5 px-3 py-2 text-sm text-white focus:outline-none focus:ring-1 focus:ring-white/20 placeholder-white/20"
                      />
                    </div>
                    <div>
                      <label className="block text-xs font-semibold text-white/50 uppercase tracking-wider mb-2">
                        Company *
                      </label>
                      <input
                        type="text"
                        name="company"
                        required
                        value={form.company}
                        onChange={handleChange}
                        placeholder="e.g. TechCorp"
                        className="w-full rounded-lg border border-white/10 bg-white/5 px-3 py-2 text-sm text-white focus:outline-none focus:ring-1 focus:ring-white/20 placeholder-white/20"
                      />
                    </div>
                  </div>

                  {/* Location & Type */}
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-xs font-semibold text-white/50 uppercase tracking-wider mb-2">
                        Location
                      </label>
                      <input
                        type="text"
                        name="location"
                        value={form.location}
                        onChange={handleChange}
                        placeholder="e.g. San Francisco, CA"
                        className="w-full rounded-lg border border-white/10 bg-white/5 px-3 py-2 text-sm text-white focus:outline-none focus:ring-1 focus:ring-white/20 placeholder-white/20"
                      />
                    </div>
                    <div>
                      <label className="block text-xs font-semibold text-white/50 uppercase tracking-wider mb-2">
                        Employment Type
                      </label>
                      <select
                        name="employment_type"
                        value={form.employment_type}
                        onChange={handleChange}
                        className="w-full rounded-lg border border-white/10 bg-white/5 px-3 py-2 text-sm text-white focus:outline-none focus:ring-1 focus:ring-white/20"
                      >
                        <option value="Full-time" className="bg-black">Full-time</option>
                        <option value="Part-time" className="bg-black">Part-time</option>
                        <option value="Contract" className="bg-black">Contract</option>
                        <option value="Internship" className="bg-black">Internship</option>
                      </select>
                    </div>
                  </div>

                  {/* Required & Preferred Skills */}
                  <div>
                    <label className="block text-xs font-semibold text-white/50 uppercase tracking-wider mb-1">
                      Required Skills (Comma separated)
                    </label>
                    <input
                      type="text"
                      name="required_skills"
                      value={form.required_skills}
                      onChange={handleChange}
                      placeholder="e.g. Python, Docker, Kubernetes"
                      className="w-full rounded-lg border border-white/10 bg-white/5 px-3 py-2 text-sm text-white focus:outline-none focus:ring-1 focus:ring-white/20 placeholder-white/20"
                    />
                  </div>

                  <div>
                    <label className="block text-xs font-semibold text-white/50 uppercase tracking-wider mb-1">
                      Preferred Skills (Comma separated)
                    </label>
                    <input
                      type="text"
                      name="preferred_skills"
                      value={form.preferred_skills}
                      onChange={handleChange}
                      placeholder="e.g. AWS, React, PostgreSQL"
                      className="w-full rounded-lg border border-white/10 bg-white/5 px-3 py-2 text-sm text-white focus:outline-none focus:ring-1 focus:ring-white/20 placeholder-white/20"
                    />
                  </div>

                  {/* Experience & Education requirements */}
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-xs font-semibold text-white/50 uppercase tracking-wider mb-2">
                        Required Experience
                      </label>
                      <input
                        type="text"
                        name="required_experience"
                        value={form.required_experience}
                        onChange={handleChange}
                        placeholder="e.g. 5+ years"
                        className="w-full rounded-lg border border-white/10 bg-white/5 px-3 py-2 text-sm text-white focus:outline-none focus:ring-1 focus:ring-white/20 placeholder-white/20"
                      />
                    </div>
                    <div>
                      <label className="block text-xs font-semibold text-white/50 uppercase tracking-wider mb-2">
                        Education Requirement
                      </label>
                      <input
                        type="text"
                        name="education_requirement"
                        value={form.education_requirement}
                        onChange={handleChange}
                        placeholder="e.g. Bachelor's in CS"
                        className="w-full rounded-lg border border-white/10 bg-white/5 px-3 py-2 text-sm text-white focus:outline-none focus:ring-1 focus:ring-white/20 placeholder-white/20"
                      />
                    </div>
                  </div>

                  {/* Description Textarea */}
                  <div>
                    <label className="block text-xs font-semibold text-white/50 uppercase tracking-wider mb-2">
                      Full Job Description *
                    </label>
                    <textarea
                      name="description"
                      required
                      rows={5}
                      value={form.description}
                      onChange={handleChange}
                      placeholder="Paste the full job details here..."
                      className="w-full rounded-lg border border-white/10 bg-white/5 px-3 py-2 text-sm text-white focus:outline-none focus:ring-1 focus:ring-white/20 placeholder-white/20"
                    />
                  </div>

                  {/* Match Trigger */}
                  <Button
                    type="submit"
                    disabled={matching || resumes.length === 0}
                    className="w-full bg-white hover:bg-white/90 text-black font-semibold rounded-full gap-2 transition-all"
                  >
                    {matching ? (
                      <>
                        <Loader2 className="h-4 w-4 animate-spin" />
                        Calculating Matches...
                      </>
                    ) : (
                      <>
                        <Sparkles className="h-4 w-4" />
                        Calculate Match Scores
                      </>
                    )}
                  </Button>
                </form>
              </Card>
            </div>

            {/* RIGHT: MATCH REPORTS DASHBOARD & VISUALIZATION */}
            <div className="lg:col-span-7 space-y-6">
              {!activeReport ? (
                <Card className="p-8 text-center border-white/5 bg-white/[0.01] flex flex-col items-center justify-center h-full min-h-[400px]">
                  <Briefcase className="h-12 w-12 text-white/20 mb-4" />
                  <h3 className="text-base font-semibold text-white">No Match Calculated</h3>
                  <p className="text-xs text-white/50 mt-2 max-w-sm">
                    Select a resume, paste the job details on the left, and click match to see the compliance score reports.
                  </p>
                </Card>
              ) : (
                <div className="space-y-6">
                  {/* Gauge & Radar Grid */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    {/* Score Ring Card */}
                    <Card className="p-6 border-white/5 bg-white/[0.02] backdrop-blur-md flex flex-col items-center justify-center min-h-[260px] relative overflow-hidden">
                      <div className="absolute inset-0 bg-radial-gradient from-white/5 to-transparent pointer-events-none" />
                      <span className="text-xs font-semibold text-white/45 tracking-widest uppercase mb-6">
                        Overall Match Score
                      </span>

                      {/* Circle Ring */}
                      <div className="relative flex items-center justify-center">
                        <svg className="w-36 h-36 transform -rotate-90">
                          <circle
                            cx="72"
                            cy="72"
                            r="64"
                            className="stroke-white/5 fill-transparent"
                            strokeWidth="10"
                          />
                          <circle
                            cx="72"
                            cy="72"
                            r="64"
                            className="stroke-white fill-transparent transition-all duration-1000 ease-out"
                            strokeWidth="10"
                            strokeDasharray={2 * Math.PI * 64}
                            strokeDashoffset={
                              2 * Math.PI * 64 * (1 - activeReport.overall_match / 100)
                            }
                            strokeLinecap="round"
                          />
                        </svg>
                        <div className="absolute flex flex-col items-center">
                          <span className="text-3xl font-bold tracking-tight text-white">
                            {activeReport.overall_match}%
                          </span>
                          <span className="text-[10px] text-white/45 uppercase font-medium mt-0.5">
                            Deterministic
                          </span>
                        </div>
                      </div>
                    </Card>

                    {/* Radar breakdown Chart */}
                    <Card className="p-6 border-white/5 bg-white/[0.02] backdrop-blur-md flex flex-col items-center justify-center min-h-[260px]">
                      <span className="text-xs font-semibold text-white/45 tracking-widest uppercase mb-4">
                        Category Breakdown
                      </span>
                      <div className="w-full h-48">
                        <ResponsiveContainer width="100%" height="100%">
                          <RadarChart cx="50%" cy="50%" r="75%" data={radarData}>
                            <PolarGrid stroke="rgba(255, 255, 255, 0.05)" />
                            <PolarAngleAxis
                              dataKey="subject"
                              tick={{ fill: "rgba(255,255,255,0.6)", fontSize: 10 }}
                            />
                            <PolarRadiusAxis
                              angle={30}
                              domain={[0, 100]}
                              tick={{ fill: "rgba(255,255,255,0.3)", fontSize: 8 }}
                            />
                            <Radar
                              name="Score"
                              dataKey="Score"
                              stroke="#ffffff"
                              fill="#ffffff"
                              fillOpacity={0.15}
                            />
                            <Tooltip />
                          </RadarChart>
                        </ResponsiveContainer>
                      </div>
                    </Card>
                  </div>

                  {/* Recommendations */}
                  <Card className="p-6 border-white/5 bg-white/[0.02] backdrop-blur-md space-y-4">
                    <div className="flex items-center justify-between">
                      <h3 className="text-sm font-semibold text-white flex items-center gap-2">
                        <Lightbulb className="h-4 w-4 text-white/60" />
                        Recommendations & Priority
                      </h3>
                      <div className={`px-2.5 py-1 text-[10px] font-bold uppercase tracking-wider rounded-full border ${getPriorityColor(activeReport.improvement_priority)}`}>
                        {activeReport.improvement_priority} Priority
                      </div>
                    </div>
                    <ul className="space-y-2">
                      {activeReport.recommendations.map((rec, i) => (
                        <li key={i} className="text-xs text-white/65 flex gap-2">
                          <span className="text-white/40">•</span>
                          {rec}
                        </li>
                      ))}
                    </ul>
                  </Card>

                  {/* Skill Comparison */}
                  <Card className="p-6 border-white/5 bg-white/[0.02] backdrop-blur-md grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                      <h3 className="text-xs font-semibold uppercase text-white/50 tracking-wider mb-3 flex items-center gap-1.5">
                        <CheckCircle className="h-3.5 w-3.5 text-green-400" />
                        Matching Skills
                      </h3>
                      <div className="flex flex-wrap gap-1.5">
                        {activeReport.matching_skills.map((s, idx) => (
                          <span key={idx} className="px-2 py-0.5 rounded text-[10px] font-semibold bg-green-500/10 text-green-400 border border-green-500/20">
                            {s}
                          </span>
                        ))}
                        {activeReport.matching_skills.length === 0 && (
                          <span className="text-xs text-white/35">No skills matched yet.</span>
                        )}
                      </div>
                    </div>

                    <div>
                      <h3 className="text-xs font-semibold uppercase text-white/50 tracking-wider mb-3 flex items-center gap-1.5">
                        <AlertTriangle className="h-3.5 w-3.5 text-red-400" />
                        Missing Required Skills
                      </h3>
                      <div className="flex flex-wrap gap-1.5">
                        {activeReport.missing_skills.map((s, idx) => (
                          <span key={idx} className="px-2 py-0.5 rounded text-[10px] font-semibold bg-red-500/10 text-red-400 border border-red-500/20">
                            {s}
                          </span>
                        ))}
                        {activeReport.missing_skills.length === 0 && (
                          <span className="text-xs text-green-400 font-medium">All required skills met!</span>
                        )}
                      </div>
                    </div>
                  </Card>

                  {/* Missing Keywords */}
                  <Card className="p-6 border-white/5 bg-white/[0.02] backdrop-blur-md">
                    <h3 className="text-xs font-semibold uppercase text-white/50 tracking-wider mb-3 flex items-center gap-1.5">
                      <AlertTriangle className="h-3.5 w-3.5 text-yellow-500" />
                      Missing Keywords Gap
                    </h3>
                    <div className="flex flex-wrap gap-1.5">
                      {activeReport.missing_keywords.map((kw, idx) => (
                        <span key={idx} className="px-2 py-0.5 rounded text-[10px] font-semibold bg-yellow-500/10 text-yellow-500 border border-yellow-500/20">
                          {kw}
                        </span>
                      ))}
                      {activeReport.missing_keywords.length === 0 && (
                        <span className="text-xs text-green-400 font-medium">No missing keywords found.</span>
                      )}
                    </div>
                  </Card>

                  {/* Collapsible Explanations Category List */}
                  <Card className="p-6 border-white/5 bg-white/[0.02] backdrop-blur-md space-y-4">
                    <h3 className="text-sm font-semibold text-white">
                      Rule Explanations & Deductions
                    </h3>
                    <div className="space-y-2">
                      {Object.keys(activeReport.score_explanations).map((catName) => {
                        const cat = activeReport.score_explanations[catName];
                        const isExpanded = expandedCategory === catName;
                        return (
                          <div key={catName} className="border border-white/5 rounded-lg overflow-hidden bg-white/[0.01]">
                            {/* Header Toggle */}
                            <button
                              onClick={() => setExpandedCategory(isExpanded ? null : catName)}
                              className="w-full flex items-center justify-between px-4 py-3 hover:bg-white/[0.02] transition-colors"
                            >
                              <div className="flex items-center gap-3">
                                <span className="text-xs font-semibold text-white/70">{catName}</span>
                                <span className="text-[10px] text-white/45">({cat.percentage}%)</span>
                              </div>
                              <div className="flex items-center gap-2">
                                <span className="text-xs font-bold text-white/70">
                                  {cat.score} / {cat.max_score} pts
                                </span>
                                {isExpanded ? <ChevronUp className="h-4 w-4 text-white/45" /> : <ChevronDown className="h-4 w-4 text-white/45" />}
                              </div>
                            </button>

                            {/* Expanded Rules Details */}
                            {isExpanded && (
                              <div className="px-4 pb-4 pt-2 border-t border-white/5 space-y-2">
                                {cat.reasons.map((rule, ruleIdx) => (
                                  <div key={ruleIdx} className="flex justify-between items-center text-xs">
                                    <span className="text-white/60">{rule.rule}</span>
                                    <span className={`font-semibold ${rule.points < 0 ? "text-red-400" : "text-green-400"}`}>
                                      {rule.points < 0 ? `${rule.points}` : rule.points > 0 ? `+${rule.points}` : "—"}
                                    </span>
                                  </div>
                                ))}
                              </div>
                            )}
                          </div>
                        );
                      })}
                    </div>
                  </Card>
                </div>
              )}
            </div>
          </div>

          {/* SECTION: MATCH HISTORY */}
          <div className="mt-12">
            <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
              <Clock className="h-5 w-5 text-white/60" />
              Job Match History
            </h2>

            <Card className="border-white/5 bg-white/[0.01] overflow-hidden">
              <div className="overflow-x-auto">
                <table className="w-full border-collapse text-left">
                  <thead>
                    <tr className="border-b border-white/5 bg-white/[0.02] text-xs font-semibold text-white/45 tracking-wider uppercase">
                      <th className="p-4">Job Title</th>
                      <th className="p-4">Company</th>
                      <th className="p-4">Location</th>
                      <th className="p-4">Match %</th>
                      <th className="p-4">Calculated</th>
                      <th className="p-4 text-right">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-white/5 text-xs text-white/75">
                    {history.map((match) => (
                      <tr key={match.id} className="hover:bg-white/[0.01] transition-colors">
                        <td className="p-4 font-semibold text-white">
                          {match.job_description?.title || "Unknown Job"}
                        </td>
                        <td className="p-4">{match.job_description?.company || "Unknown Company"}</td>
                        <td className="p-4 text-white/50">
                          <span className="flex items-center gap-1">
                            <MapPin className="h-3 w-3" />
                            {match.job_description?.location || "Remote"}
                          </span>
                        </td>
                        <td className="p-4">
                          <span className={`font-semibold ${match.overall_match >= 80 ? "text-green-400" : match.overall_match >= 60 ? "text-yellow-500" : "text-red-400"}`}>
                            {match.overall_match}%
                          </span>
                        </td>
                        <td className="p-4 text-white/40">
                          {new Date(match.created_at).toLocaleDateString()}
                        </td>
                        <td className="p-4 text-right space-x-2">
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => handleViewReport(match.id)}
                            className="hover:bg-white/10 text-white/60 hover:text-white rounded-full p-2 h-8 w-8"
                            aria-label="View match report"
                          >
                            <Eye className="h-3.5 w-3.5" />
                          </Button>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => handleDeleteReport(match.id)}
                            className="hover:bg-red-500/10 text-red-400 hover:text-red-400 rounded-full p-2 h-8 w-8"
                            aria-label="Delete match report"
                          >
                            <Trash2 className="h-3.5 w-3.5" />
                          </Button>
                        </td>
                      </tr>
                    ))}
                    {history.length === 0 && (
                      <tr>
                        <td colSpan="6" className="p-0 border-b-0">
                          <EmptyState 
                            title="No Match History" 
                            description="Run your first job match above to see it appear here."
                          />
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </Card>
          </div>
        </main>
      </div>

  );
}
