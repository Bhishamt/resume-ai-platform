import React, { useEffect, useState, useCallback } from "react";
import {
  Users,
  FileText,
  Brain,
  BarChart3,
  Activity,
  Briefcase,
  Zap,
  RefreshCw,
} from "lucide-react";
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Legend,
} from "recharts";
import AdminLayout from "@/components/admin/AdminLayout";
import StatsCard from "@/components/admin/StatsCard";
import SystemHealthCard from "@/components/admin/SystemHealthCard";
import adminService from "@/services/adminService";

const CHART_COLORS = ["#6366f1", "#22d3ee", "#a78bfa", "#34d399", "#f59e0b"];

const CustomTooltip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null;
  return (
    <div className="rounded-lg border border-white/10 bg-[#111] px-3 py-2 shadow-xl">
      <p className="text-xs text-white/40 mb-1">{label}</p>
      {payload.map((p, i) => (
        <p key={i} className="text-xs font-medium" style={{ color: p.color }}>
          {p.name}: {p.value?.toLocaleString()}
        </p>
      ))}
    </div>
  );
};

export default function AdminDashboard() {
  const [stats, setStats] = useState(null);
  const [analytics, setAnalytics] = useState(null);
  const [health, setHealth] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [refreshing, setRefreshing] = useState(false);

  const load = useCallback(async (silent = false) => {
    if (!silent) setLoading(true);
    else setRefreshing(true);
    setError(null);
    try {
      const [statsData, analyticsData, healthData] = await Promise.all([
        adminService.getDashboardStats(),
        adminService.getAnalytics(30),
        adminService.getSystemHealth(),
      ]);
      setStats(statsData);
      setAnalytics(analyticsData);
      setHealth(healthData);
    } catch (err) {
      setError(err?.response?.data?.message ?? "Failed to load dashboard.");
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  const statCards = [
    { title: "Total Users", value: stats?.total_users, icon: Users, color: "indigo" },
    { title: "Active Users", value: stats?.active_users, icon: Activity, color: "emerald" },
    { title: "Total Resumes", value: stats?.total_resumes, icon: FileText, color: "violet" },
    { title: "Analysis Reports", value: stats?.total_analysis_reports, icon: BarChart3, color: "sky" },
    { title: "Job Matches", value: stats?.total_job_matches, icon: Briefcase, color: "amber" },
    { title: "AI Requests", value: stats?.total_ai_requests, icon: Brain, color: "rose" },
  ];

  return (
    <AdminLayout>
      <div className="px-6 py-8 max-w-screen-2xl mx-auto space-y-8">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-white">Dashboard</h1>
            <p className="text-sm text-white/40 mt-1">
              Platform overview and system health
            </p>
          </div>
          <button
            onClick={() => load(true)}
            disabled={refreshing}
            className="flex items-center gap-2 rounded-lg border border-white/10 px-4 py-2 text-sm text-white/60 hover:text-white hover:border-white/20 disabled:opacity-50 transition-all"
          >
            <RefreshCw
              className={`h-4 w-4 ${refreshing ? "animate-spin" : ""}`}
            />
            Refresh
          </button>
        </div>

        {error && (
          <div className="rounded-lg border border-rose-500/20 bg-rose-500/10 px-4 py-3 text-sm text-rose-400">
            {error}
          </div>
        )}

        {/* Stats Grid */}
        <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 xl:grid-cols-6">
          {statCards.map((card) => (
            <StatsCard key={card.title} {...card} loading={loading} />
          ))}
        </div>

        {/* Today stats row */}
        <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
          <StatsCard
            title="New Users Today"
            value={stats?.new_users_today}
            icon={Users}
            color="emerald"
            loading={loading}
            subtitle="vs yesterday"
          />
          <StatsCard
            title="Resumes Today"
            value={stats?.resumes_today}
            icon={FileText}
            color="violet"
            loading={loading}
          />
          <StatsCard
            title="AI Requests Today"
            value={stats?.ai_requests_today}
            icon={Zap}
            color="amber"
            loading={loading}
          />
          <StatsCard
            title="Tokens Used"
            value={
              stats?.total_tokens_used
                ? `${(stats.total_tokens_used / 1_000_000).toFixed(2)}M`
                : "—"
            }
            icon={Brain}
            color="indigo"
            loading={loading}
            subtitle="Total all-time"
          />
        </div>

        {/* Charts + Health */}
        <div className="grid grid-cols-1 gap-6 xl:grid-cols-3">
          {/* User Growth */}
          <div className="xl:col-span-2 rounded-xl border border-white/5 bg-white/[0.03] p-5">
            <h3 className="text-sm font-semibold text-white mb-4">
              User Growth (30 days)
            </h3>
            {loading ? (
              <div className="h-48 animate-pulse rounded bg-white/5" />
            ) : (
              <ResponsiveContainer width="100%" height={200}>
                <LineChart data={analytics?.user_growth ?? []}>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                  <XAxis
                    dataKey="day"
                    tick={{ fill: "rgba(255,255,255,0.3)", fontSize: 11 }}
                    axisLine={false}
                    tickLine={false}
                    tickFormatter={(v) => v.slice(5)}
                  />
                  <YAxis
                    tick={{ fill: "rgba(255,255,255,0.3)", fontSize: 11 }}
                    axisLine={false}
                    tickLine={false}
                    width={30}
                  />
                  <Tooltip content={<CustomTooltip />} />
                  <Line
                    type="monotone"
                    dataKey="count"
                    name="New Users"
                    stroke="#6366f1"
                    strokeWidth={2}
                    dot={false}
                    activeDot={{ r: 4, fill: "#6366f1" }}
                  />
                </LineChart>
              </ResponsiveContainer>
            )}
          </div>

          {/* System Health */}
          <SystemHealthCard data={health} loading={loading} />
        </div>

        {/* More Charts */}
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-2 xl:grid-cols-3">
          {/* Daily Uploads */}
          <div className="rounded-xl border border-white/5 bg-white/[0.03] p-5">
            <h3 className="text-sm font-semibold text-white mb-4">
              Daily Uploads (30 days)
            </h3>
            {loading ? (
              <div className="h-44 animate-pulse rounded bg-white/5" />
            ) : (
              <ResponsiveContainer width="100%" height={180}>
                <BarChart data={analytics?.daily_uploads ?? []}>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                  <XAxis
                    dataKey="day"
                    tick={{ fill: "rgba(255,255,255,0.3)", fontSize: 10 }}
                    axisLine={false}
                    tickLine={false}
                    tickFormatter={(v) => v.slice(5)}
                  />
                  <YAxis
                    tick={{ fill: "rgba(255,255,255,0.3)", fontSize: 10 }}
                    axisLine={false}
                    tickLine={false}
                    width={25}
                  />
                  <Tooltip content={<CustomTooltip />} />
                  <Bar dataKey="count" name="Uploads" fill="#a78bfa" radius={[3, 3, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            )}
          </div>

          {/* ATS Distribution */}
          <div className="rounded-xl border border-white/5 bg-white/[0.03] p-5">
            <h3 className="text-sm font-semibold text-white mb-4">
              ATS Score Distribution
            </h3>
            {loading ? (
              <div className="h-44 animate-pulse rounded bg-white/5" />
            ) : (
              <ResponsiveContainer width="100%" height={180}>
                <BarChart data={analytics?.ats_distribution ?? []}>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                  <XAxis
                    dataKey="range"
                    tick={{ fill: "rgba(255,255,255,0.3)", fontSize: 10 }}
                    axisLine={false}
                    tickLine={false}
                  />
                  <YAxis
                    tick={{ fill: "rgba(255,255,255,0.3)", fontSize: 10 }}
                    axisLine={false}
                    tickLine={false}
                    width={25}
                  />
                  <Tooltip content={<CustomTooltip />} />
                  <Bar dataKey="count" name="Reports" fill="#34d399" radius={[3, 3, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            )}
          </div>

          {/* AI Provider Stats */}
          <div className="rounded-xl border border-white/5 bg-white/[0.03] p-5">
            <h3 className="text-sm font-semibold text-white mb-4">
              AI Provider Distribution
            </h3>
            {loading ? (
              <div className="h-44 animate-pulse rounded bg-white/5" />
            ) : (analytics?.ai_provider_stats?.length ?? 0) === 0 ? (
              <div className="flex h-44 items-center justify-center text-sm text-white/30">
                No AI requests yet
              </div>
            ) : (
              <ResponsiveContainer width="100%" height={180}>
                <PieChart>
                  <Pie
                    data={analytics?.ai_provider_stats ?? []}
                    dataKey="count"
                    nameKey="provider"
                    cx="50%"
                    cy="50%"
                    outerRadius={70}
                    innerRadius={40}
                  >
                    {(analytics?.ai_provider_stats ?? []).map((_, i) => (
                      <Cell
                        key={i}
                        fill={CHART_COLORS[i % CHART_COLORS.length]}
                      />
                    ))}
                  </Pie>
                  <Tooltip content={<CustomTooltip />} />
                  <Legend
                    formatter={(v) => (
                      <span className="text-xs text-white/50">{v}</span>
                    )}
                  />
                </PieChart>
              </ResponsiveContainer>
            )}
          </div>
        </div>
      </div>
    </AdminLayout>
  );
}
