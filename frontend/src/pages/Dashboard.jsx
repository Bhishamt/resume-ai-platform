import React, { useState, useEffect, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  AreaChart,
  Area,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell
} from "recharts";
import {
  Loader2,
  Briefcase,
  Award,
  ChevronUp,
  ChevronDown,
  Printer,
  TrendingUp,
  Calendar,
  Grid,
  Clock
} from "lucide-react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import dashboardService from "@/services/dashboardService";
import { useToast } from "@/hooks/useToast";
import { ToastProvider } from "@/components/ui/toast";

// Progress Ring Component
function ProgressRing({ percentage, size = 50, strokeWidth = 4, color = "#ffffff" }) {
  const radius = (size - strokeWidth) / 2;
  const circumference = radius * 2 * Math.PI;
  const offset = circumference - (Math.min(100, Math.max(0, percentage)) / 100) * circumference;
  return (
    <div className="relative flex items-center justify-center">
      <svg width={size} height={size} className="transform -rotate-90">
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke="rgba(255,255,255,0.03)"
          strokeWidth={strokeWidth}
          fill="transparent"
        />
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke={color}
          strokeWidth={strokeWidth}
          fill="transparent"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          className="transition-all duration-700 ease-out"
        />
      </svg>
      <span className="absolute text-[10px] font-semibold text-white/90">{Math.round(percentage)}%</span>
    </div>
  );
}

// Contribution Grid Calendar Component (Simulating last 12 weeks of resume uploads)
function ContributionCalendar({ uploadTimeline }) {
  // Convert upload timeline list to a lookup map
  const timelineMap = {};
  (uploadTimeline || []).forEach(item => {
    timelineMap[item.date] = item.count;
  });

  // Generate date array for the last 84 days (12 weeks)
  const days = [];
  const today = new Date();
  for (let i = 83; i >= 0; i--) {
    const d = new Date();
    d.setDate(today.getDate() - i);
    const dateStr = d.toISOString().split("T")[0];
    days.push({
      date: dateStr,
      count: timelineMap[dateStr] || 0
    });
  }

  // Group days by week (arrays of 7 days)
  const weeks = [];
  for (let i = 0; i < days.length; i += 7) {
    weeks.push(days.slice(i, i + 7));
  }

  const getIntensityClass = (count) => {
    if (count === 0) return "bg-white/[0.02] border border-white/[0.02]";
    if (count === 1) return "bg-white/20 border border-white/10";
    if (count === 2) return "bg-white/50 border border-white/10";
    return "bg-white border border-white/20"; // 3+ uploads
  };

  return (
    <div className="flex flex-col gap-2 p-4 rounded-xl border border-white/5 bg-white/[0.01]">
      <div className="flex items-center gap-2 mb-2 text-xs text-white/50">
        <Calendar className="h-3.5 w-3.5" />
        <span>Resume upload activity grid (last 12 weeks)</span>
      </div>
      <div className="flex gap-1.5 overflow-x-auto pb-2 scrollbar-thin">
        {weeks.map((week, wIdx) => (
          <div key={wIdx} className="flex flex-col gap-1.5">
            {week.map((day, dIdx) => (
              <div
                key={dIdx}
                title={`${day.date}: ${day.count} uploads`}
                className={`h-3 w-3 rounded-[3px] transition-colors duration-300 ${getIntensityClass(day.count)}`}
              />
            ))}
          </div>
        ))}
      </div>
      <div className="flex justify-between items-center text-[10px] text-white/35 px-1 mt-1">
        <span>Less</span>
        <div className="flex gap-1 items-center">
          <div className="h-2 w-2 rounded-[2px] bg-white/[0.02]" />
          <div className="h-2 w-2 rounded-[2px] bg-white/20" />
          <div className="h-2 w-2 rounded-[2px] bg-white/50" />
          <div className="h-2 w-2 rounded-[2px] bg-white" />
        </div>
        <span>More</span>
      </div>
    </div>
  );
}

export default function Dashboard() {
  const { success, error } = useToast();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [savingPrefs, setSavingPrefs] = useState(false);

  // Load Dashboard Data
  const loadDashboardData = useCallback(async () => {
    try {
      setLoading(true);
      const response = await dashboardService.getDashboard();
      setData(response.data);
    } catch (err) {
      console.error(err);
      error("Failed to load analytics dashboard.");
    } finally {
      setLoading(false);
    }
  }, [error]);

  useEffect(() => {
    loadDashboardData();
  }, [loadDashboardData]);

  // Handle Widget Position Reordering
  const handleMoveWidget = async (index, direction) => {
    if (!data?.preferences?.layout) return;
    const layout = [...data.preferences.layout];
    const targetIdx = direction === "up" ? index - 1 : index + 1;

    if (targetIdx < 0 || targetIdx >= layout.length) return;

    // Swap elements
    const temp = layout[index];
    layout[index] = layout[targetIdx];
    layout[targetIdx] = temp;

    setSavingPrefs(true);
    try {
      await dashboardService.updatePreferences({ layout });
      // Update local state
      setData(prev => ({
        ...prev,
        preferences: {
          ...prev.preferences,
          layout
        }
      }));
      success("Dashboard layout updated!");
    } catch (err) {
      console.error(err);
      error("Failed to save layout preferences.");
    } finally {
      setSavingPrefs(false);
    }
  };

  // Export Dashboard to PDF Print Sheet
  const handleExportPDF = () => {
    const printWindow = window.open("", "_blank");
    printWindow.document.write(`
      <html>
        <head>
          <title>Career Intelligence Report - ${new Date().toLocaleDateString()}</title>
          <style>
            body { font-family: -apple-system, BlinkMacSystemFont, Arial, sans-serif; padding: 40px; color: #111; line-height: 1.5; }
            h1 { font-size: 24px; border-bottom: 2px solid #111; padding-bottom: 10px; margin-bottom: 20px; }
            h2 { font-size: 16px; margin-top: 30px; text-transform: uppercase; color: #444; border-bottom: 1px solid #ddd; padding-bottom: 5px; }
            .kpis { display: flex; justify-content: space-between; margin-bottom: 25px; }
            .kpi-card { background: #f9f9f9; border: 1px solid #eee; padding: 15px; width: 30%; border-radius: 8px; text-align: center; }
            .kpi-card h3 { margin: 0; font-size: 12px; color: #666; }
            .kpi-card p { margin: 5px 0 0 0; font-size: 20px; font-weight: bold; }
            .insight-box { background: #f4f4f5; border-left: 4px solid #18181b; padding: 15px; margin: 15px 0; border-radius: 4px; }
            ul { padding-left: 20px; }
            li { margin-bottom: 8px; font-size: 13px; }
            .grid-cols-2 { display: flex; justify-content: space-between; }
            .col { width: 48%; }
          </style>
        </head>
        <body>
          <h1>Career Intelligence & Analytics Dashboard</h1>
          
          <div class="kpis">
            <div class="kpi-card">
              <h3>Average ATS Score</h3>
              <p>${data?.stats?.average_ats_score || 0}</p>
            </div>
            <div class="kpi-card">
              <h3>Average Job Match</h3>
              <p>${data?.stats?.average_job_match || 0}%</p>
            </div>
            <div class="kpi-card">
              <h3>Total Resumes</h3>
              <p>${data?.stats?.resume_count || 0}</p>
            </div>
          </div>

          <h2>Career Insights & Recommendations</h2>
          <div class="insight-box">
            <strong>ATS Improvement:</strong> ${data?.recommendations?.ats_improvement?.evaluation || ""}
          </div>
          <div class="insight-box">
            <strong>Interview Readiness:</strong> ${data?.recommendations?.interview_readiness?.description || ""}
          </div>

          <div class="grid-cols-2">
            <div class="col">
              <h2>Technologies to Learn</h2>
              <ul>
                ${(data?.recommendations?.technologies_to_learn || []).map(t => `<li>${t}</li>`).join("")}
              </ul>
            </div>
            <div class="col">
              <h2>Career Growth Suggestions</h2>
              <ul>
                ${(data?.recommendations?.career_growth_suggestions || []).map(s => `<li>${s}</li>`).join("")}
              </ul>
            </div>
          </div>
        </body>
      </html>
    `);
    printWindow.document.close();
    printWindow.focus();
    setTimeout(() => {
      printWindow.print();
    }, 500);
  };

  if (loading) {
    return (
      <ToastProvider>
        <div className="min-h-screen bg-[#050505] text-white">
          <div className="h-24" />
          <main className="mx-auto w-full max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
            <div className="mb-8 flex flex-col md:flex-row md:items-center md:justify-between gap-4">
              <div>
                <div className="h-8 w-64 bg-white/5 rounded-md animate-pulse mb-2" />
                <div className="h-4 w-96 bg-white/5 rounded-md animate-pulse" />
              </div>
              <div className="h-9 w-32 bg-white/5 rounded-xl animate-pulse" />
            </div>
            <div className="grid grid-cols-1 md:grid-cols-12 gap-8">
              <div className="md:col-span-12 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
                {[1, 2, 3, 4].map(i => (
                  <div key={i} className="glass-card p-5 h-[100px] bg-white/[0.02] border border-white/5 animate-pulse rounded-xl" />
                ))}
              </div>
              {[1, 2, 3, 4].map(i => (
                <div key={`chart-${i}`} className="md:col-span-6 glass-card p-6 h-[350px] bg-white/[0.02] border border-white/5 animate-pulse rounded-xl" />
              ))}
            </div>
          </main>
        </div>
      </ToastProvider>
    );
  }

  // Pre-calculate data fields
  const stats = data?.stats || {};
  const trends = data?.trends || {};
  const skills = data?.skills || {};
  const recommendations = data?.recommendations || {};
  const preferences = data?.preferences || { layout: DEFAULT_LAYOUT };
  const recentActivity = data?.recent_activity || [];

  // Colors for Charts
  const COLORS = ["#ffffff", "#e4e4e7", "#a1a1aa", "#71717a", "#3f3f46"];

  // Pie chart dataset mapping
  const pieData = Object.keys(stats.most_requested_ai_features || {}).map(key => ({
    name: key.replace("_", " ").toUpperCase(),
    value: stats.most_requested_ai_features[key]
  }));

  // Skills radar dataset mapping
  const radarData = (skills.top_skills || []).map(item => ({
    subject: item.skill,
    A: item.count,
    fullMark: Math.max(...(skills.top_skills || []).map(i => i.count), 1) + 2
  }));

  // Render Widget based on its ID
  const renderWidget = (widgetId, idx) => {
    const isFirst = idx === 0;
    const isLast = idx === preferences.layout.length - 1;

    const widgetControls = (
      <div className="flex items-center gap-1.5">
        <button
          onClick={() => handleMoveWidget(idx, "up")}
          disabled={isFirst || savingPrefs}
          className="text-white/40 hover:text-white disabled:opacity-20 p-1 transition-all"
          title="Move Up"
        >
          <ChevronUp className="h-4 w-4" />
        </button>
        <button
          onClick={() => handleMoveWidget(idx, "down")}
          disabled={isLast || savingPrefs}
          className="text-white/40 hover:text-white disabled:opacity-20 p-1 transition-all"
          title="Move Down"
        >
          <ChevronDown className="h-4 w-4" />
        </button>
      </div>
    );

    switch (widgetId) {
      case "kpi_cards":
        return (
          <motion.div layout key="kpi_cards" className="md:col-span-12">
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
              {/* KPI 1 */}
              <motion.div whileHover={{ y: -4 }} transition={{ type: "spring", stiffness: 300 }}>
                <Card className="glass-card p-5 flex items-center justify-between hover:border-white/20 transition-all duration-300 shadow-lg hover:shadow-green-500/10">
                  <div>
                    <h3 className="text-xs font-semibold uppercase tracking-wider text-white/50">Average ATS Score</h3>
                    <p className="text-3xl font-semibold mt-1 tracking-tight">{stats.average_ats_score}</p>
                  </div>
                  <ProgressRing percentage={stats.average_ats_score} color="#22c55e" />
                </Card>
              </motion.div>

              {/* KPI 2 */}
              <motion.div whileHover={{ y: -4 }} transition={{ type: "spring", stiffness: 300 }}>
                <Card className="glass-card p-5 flex items-center justify-between hover:border-white/20 transition-all duration-300 shadow-lg hover:shadow-purple-500/10">
                  <div>
                    <h3 className="text-xs font-semibold uppercase tracking-wider text-white/50">Best ATS Score</h3>
                    <p className="text-3xl font-semibold mt-1 tracking-tight">{stats.best_ats_score}</p>
                  </div>
                  <div className="h-10 w-10 bg-white/5 border border-white/5 rounded-xl flex items-center justify-center">
                    <TrendingUp className="h-5 w-5 text-white/70" />
                  </div>
                </Card>
              </motion.div>

              {/* KPI 3 */}
              <motion.div whileHover={{ y: -4 }} transition={{ type: "spring", stiffness: 300 }}>
                <Card className="glass-card p-5 flex items-center justify-between hover:border-white/20 transition-all duration-300 shadow-lg hover:shadow-blue-500/10">
                  <div>
                    <h3 className="text-xs font-semibold uppercase tracking-wider text-white/50">Average Job Match</h3>
                    <p className="text-3xl font-semibold mt-1 tracking-tight">{stats.average_job_match}%</p>
                  </div>
                  <ProgressRing percentage={stats.average_job_match} color="#3b82f6" />
                </Card>
              </motion.div>

              {/* KPI 4 */}
              <motion.div whileHover={{ y: -4 }} transition={{ type: "spring", stiffness: 300 }}>
                <Card className="glass-card p-5 flex items-center justify-between hover:border-white/20 transition-all duration-300 shadow-lg hover:shadow-indigo-500/10">
                  <div>
                    <h3 className="text-xs font-semibold uppercase tracking-wider text-white/50">Best Job Match</h3>
                    <p className="text-3xl font-semibold mt-1 tracking-tight">{stats.best_job_match}%</p>
                  </div>
                  <div className="h-10 w-10 bg-white/5 border border-white/5 rounded-xl flex items-center justify-center">
                    <Award className="h-5 w-5 text-white/70" />
                  </div>
                </Card>
              </motion.div>
            </div>
          </motion.div>
        );

      case "ats_trend":
        return (
          <motion.div layout key="ats_trend" className="md:col-span-6">
            <Card className="glass-card p-6 flex flex-col h-[350px]">
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-sm font-semibold uppercase tracking-wider text-white/70">ATS Score Trend</h3>
                {widgetControls}
              </div>
              <div className="flex-1 w-full text-xs">
                {trends.ats_trend && trends.ats_trend.length > 0 ? (
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={trends.ats_trend}>
                      <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                      <XAxis dataKey="date" stroke="rgba(255,255,255,0.3)" />
                      <YAxis stroke="rgba(255,255,255,0.3)" domain={[0, 100]} />
                      <Tooltip
                        contentStyle={{ backgroundColor: "#111", borderColor: "rgba(255,255,255,0.1)" }}
                        labelStyle={{ color: "rgba(255,255,255,0.5)" }}
                      />
                      <Line
                        type="monotone"
                        dataKey="score"
                        stroke="#ffffff"
                        strokeWidth={2}
                        activeDot={{ r: 6 }}
                      />
                    </LineChart>
                  </ResponsiveContainer>
                ) : (
                  <div className="flex h-full items-center justify-center text-white/40">No score trend details found.</div>
                )}
              </div>
            </Card>
          </motion.div>
        );

      case "job_match_trend":
        return (
          <motion.div layout key="job_match_trend" className="md:col-span-6">
            <Card className="glass-card p-6 flex flex-col h-[350px]">
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-sm font-semibold uppercase tracking-wider text-white/70">Job Match Timeline</h3>
                {widgetControls}
              </div>
              <div className="flex-1 w-full text-xs">
                {trends.job_match_trend && trends.job_match_trend.length > 0 ? (
                  <ResponsiveContainer width="100%" height="100%">
                    <AreaChart data={trends.job_match_trend}>
                      <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                      <XAxis dataKey="date" stroke="rgba(255,255,255,0.3)" />
                      <YAxis stroke="rgba(255,255,255,0.3)" domain={[0, 100]} />
                      <Tooltip
                        contentStyle={{ backgroundColor: "#111", borderColor: "rgba(255,255,255,0.1)" }}
                      />
                      <Area
                        type="monotone"
                        dataKey="score"
                        stroke="#ffffff"
                        fill="rgba(255,255,255,0.05)"
                        strokeWidth={1.5}
                      />
                    </AreaChart>
                  </ResponsiveContainer>
                ) : (
                  <div className="flex h-full items-center justify-center text-white/40">No job matches run.</div>
                )}
              </div>
            </Card>
          </motion.div>
        );

      case "resume_timeline":
        return (
          <motion.div layout key="resume_timeline" className="md:col-span-6">
            <Card className="glass-card p-6 flex flex-col h-[350px]">
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-sm font-semibold uppercase tracking-wider text-white/70">Resume Activity Timeline</h3>
                {widgetControls}
              </div>
              <div className="flex-1 flex flex-col gap-4 justify-center">
                <ContributionCalendar uploadTimeline={trends.upload_timeline} />
                <div className="flex-1 max-h-[120px] text-xs">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={trends.upload_timeline || []}>
                      <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                      <XAxis dataKey="date" stroke="rgba(255,255,255,0.3)" />
                      <YAxis stroke="rgba(255,255,255,0.3)" allowDecimals={false} />
                      <Tooltip
                        contentStyle={{ backgroundColor: "#111", borderColor: "rgba(255,255,255,0.1)" }}
                      />
                      <Bar dataKey="count" fill="#ffffff" radius={[3, 3, 0, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>
            </Card>
          </motion.div>
        );

      case "skills_radar":
        return (
          <motion.div layout key="skills_radar" className="md:col-span-6">
            <Card className="glass-card p-6 flex flex-col h-[350px]">
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-sm font-semibold uppercase tracking-wider text-white/70">Matching Skills Radar</h3>
                {widgetControls}
              </div>
              <div className="flex-1 w-full text-xs">
                {radarData.length > 0 ? (
                  <ResponsiveContainer width="100%" height="100%">
                    <RadarChart cx="50%" cy="50%" radius="70%" data={radarData}>
                      <PolarGrid stroke="rgba(255,255,255,0.05)" />
                      <PolarAngleAxis dataKey="subject" stroke="rgba(255,255,255,0.4)" />
                      <PolarRadiusAxis stroke="rgba(255,255,255,0.2)" />
                      <Radar
                        name="Skills Frequency"
                        dataKey="A"
                        stroke="#ffffff"
                        fill="rgba(255,255,255,0.1)"
                        fillOpacity={0.6}
                      />
                    </RadarChart>
                  </ResponsiveContainer>
                ) : (
                  <div className="flex h-full items-center justify-center text-white/40">Match resumes with jobs to display skills.</div>
                )}
              </div>
            </Card>
          </motion.div>
        );

      case "missing_skills":
        return (
          <motion.div layout key="missing_skills" className="md:col-span-6">
            <Card className="glass-card p-6 flex flex-col h-[350px] overflow-y-auto">
              <div className="flex justify-between items-center mb-4 border-b border-white/5 pb-2">
                <h3 className="text-sm font-semibold uppercase tracking-wider text-white/70">Top Missing Skills</h3>
                {widgetControls}
              </div>
              {skills.missing_skills && skills.missing_skills.length > 0 ? (
                <div className="space-y-3.5">
                  {skills.missing_skills.map((item, idx) => (
                    <div key={idx} className="flex justify-between items-center">
                      <span className="text-xs bg-red-500/10 border border-red-500/10 text-red-300 px-3 py-1 rounded-lg">
                        {item.skill}
                      </span>
                      <div className="flex items-center gap-2">
                        <div className="h-1.5 w-24 bg-white/5 rounded-full overflow-hidden">
                          <div
                            className="h-full bg-red-400"
                            style={{
                              width: `${(item.count / Math.max(...skills.missing_skills.map(i => i.count))) * 100}%`
                            }}
                          />
                        </div>
                        <span className="text-xs text-white/40">{item.count} matches</span>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="flex flex-1 items-center justify-center text-white/40">No missing skills detected yet.</div>
              )}
            </Card>
          </motion.div>
        );

      case "career_insights":
        return (
          <motion.div layout key="career_insights" className="md:col-span-6">
            <Card className="glass-card p-6 flex flex-col h-[350px] overflow-y-auto">
              <div className="flex justify-between items-center mb-4 border-b border-white/5 pb-2">
                <h3 className="text-sm font-semibold uppercase tracking-wider text-white/70">Career Insights</h3>
                {widgetControls}
              </div>
              <div className="space-y-4">
                {/* Improvement evaluation */}
                <div className="p-3 bg-white/[0.02] border border-white/5 rounded-xl flex items-start gap-2.5">
                  <TrendingUp className="h-4 w-4 text-green-400 mt-0.5 flex-shrink-0" />
                  <div>
                    <h4 className="text-[10px] font-bold text-white/40 uppercase tracking-wider">ATS Improvement</h4>
                    <p className="text-xs text-white/75 leading-relaxed mt-0.5">{recommendations.ats_improvement?.evaluation}</p>
                  </div>
                </div>

                {/* Interview readiness */}
                <div className="p-3 bg-white/[0.02] border border-white/5 rounded-xl flex items-start gap-2.5">
                  <Briefcase className="h-4 w-4 text-blue-400 mt-0.5 flex-shrink-0" />
                  <div>
                    <h4 className="text-[10px] font-bold text-white/40 uppercase tracking-wider">
                      Interview Readiness: <span className="text-white">{recommendations.interview_readiness?.status}</span>
                    </h4>
                    <p className="text-xs text-white/75 leading-relaxed mt-0.5">{recommendations.interview_readiness?.description}</p>
                  </div>
                </div>

                {/* Suggestions list */}
                <div>
                  <h4 className="text-[10px] font-bold text-white/45 uppercase tracking-wider mb-2">Growth Actions</h4>
                  <ul className="space-y-1.5 pl-1.5">
                    {(recommendations.career_growth_suggestions || []).map((s, i) => (
                      <li key={i} className="text-xs text-white/70 flex items-start gap-2">
                        <span className="text-white/30">•</span>
                        {s}
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            </Card>
          </motion.div>
        );

      case "ai_usage":
        return (
          <motion.div layout key="ai_usage" className="md:col-span-6">
            <Card className="glass-card p-6 flex flex-col h-[350px]">
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-sm font-semibold uppercase tracking-wider text-white/70">AI Assistant Activity</h3>
                {widgetControls}
              </div>
              <div className="flex-1 flex gap-4 items-center">
                {pieData.length > 0 ? (
                  <>
                    <div className="flex-1 h-full text-xs">
                      <ResponsiveContainer width="100%" height="100%">
                        <PieChart>
                          <Pie
                            data={pieData}
                            cx="50%"
                            cy="50%"
                            innerRadius={50}
                            outerRadius={75}
                            paddingAngle={4}
                            dataKey="value"
                          >
                            {pieData.map((entry, index) => (
                              <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                            ))}
                          </Pie>
                          <Tooltip
                            contentStyle={{ backgroundColor: "#111", borderColor: "rgba(255,255,255,0.1)" }}
                          />
                        </PieChart>
                      </ResponsiveContainer>
                    </div>
                    <div className="flex flex-col gap-2 w-[180px]">
                      {pieData.map((item, idx) => (
                        <div key={idx} className="flex items-center justify-between text-[10px]">
                          <div className="flex items-center gap-1.5">
                            <div className="h-2 w-2 rounded-[2px]" style={{ backgroundColor: COLORS[idx % COLORS.length] }} />
                            <span className="text-white/60 truncate max-w-[100px]">{item.name}</span>
                          </div>
                          <span className="font-semibold text-white">{item.value} runs</span>
                        </div>
                      ))}
                    </div>
                  </>
                ) : (
                  <div className="flex flex-1 h-full items-center justify-center text-white/40">No AI requests logged.</div>
                )}
              </div>
            </Card>
          </motion.div>
        );

      case "recent_activity":
        return (
          <motion.div layout key="recent_activity" className="md:col-span-6">
            <Card className="glass-card p-6 flex flex-col h-[350px] overflow-y-auto">
              <div className="flex justify-between items-center mb-4 border-b border-white/5 pb-2">
                <h3 className="text-sm font-semibold uppercase tracking-wider text-white/70">Recent Workspace Activity</h3>
                {widgetControls}
              </div>
              {recentActivity.length > 0 ? (
                <div className="space-y-4">
                  {recentActivity.map((activity, idx) => (
                    <div key={idx} className="flex gap-3">
                      <div className="h-7 w-7 rounded-lg bg-white/5 flex items-center justify-center flex-shrink-0 border border-white/5 mt-0.5">
                        <Clock className="h-3.5 w-3.5 text-white/60" />
                      </div>
                      <div>
                        <h4 className="text-xs font-semibold text-white">{activity.title}</h4>
                        <p className="text-[10px] text-white/40 mt-0.5">
                          {activity.description} • {new Date(activity.timestamp).toLocaleString()}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="flex flex-1 h-full items-center justify-center text-white/40">No activity logged.</div>
              )}
            </Card>
          </motion.div>
        );

      default:
        return null;
    }
  };

  return (
    <ToastProvider>
      <div className="min-h-screen bg-[#050505] text-white">
        <div className="h-24" />

        <main className="mx-auto w-full max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
          
          {/* Welcome Header */}
          <div className="mb-8 flex flex-col md:flex-row md:items-center md:justify-between gap-4">
            <div>
              <h1 className="text-3xl font-semibold tracking-tight text-white flex items-center gap-2">
                <Grid className="h-8 w-8 text-white/70" />
                Career Intelligence Dashboard
              </h1>
              <p className="text-sm text-white/55 mt-1">
                Visualizing scores, matching parameters, and deterministic career suggestions.
              </p>
            </div>
            
            <div className="flex gap-3 items-center">
              <Button
                variant="outline"
                size="sm"
                onClick={handleExportPDF}
                className="rounded-xl"
              >
                <Printer className="h-4 w-4 mr-2" />
                Export PDF
              </Button>
            </div>
          </div>

          {/* Draggable/Reorderable Responsive Grid Layout */}
          <div className="grid grid-cols-1 md:grid-cols-12 gap-8">
            <AnimatePresence mode="popLayout">
              {preferences.layout.map((widgetId, index) => renderWidget(widgetId, index))}
            </AnimatePresence>
          </div>

        </main>
      </div>
    </ToastProvider>
  );
}
