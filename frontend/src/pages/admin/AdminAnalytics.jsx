import React, { useCallback, useEffect, useState } from "react";
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, AreaChart, Area,
} from "recharts";
import { RefreshCw, TrendingUp } from "lucide-react";
import AdminLayout from "@/components/admin/AdminLayout";
import StatsCard from "@/components/admin/StatsCard";
import adminService from "@/services/adminService";

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

export default function AdminAnalytics() {
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [days, setDays] = useState(30);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const data = await adminService.getAnalytics(days);
      setAnalytics(data);
    } finally {
      setLoading(false);
    }
  }, [days]);

  useEffect(() => { load(); }, [load]);

  const s = analytics?.stats;

  return (
    <AdminLayout>
      <div className="px-6 py-8 max-w-screen-2xl mx-auto space-y-8">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-white">Analytics</h1>
            <p className="text-sm text-white/40 mt-1">Platform usage metrics</p>
          </div>
          <div className="flex items-center gap-3">
            <select
              value={days}
              onChange={(e) => setDays(Number(e.target.value))}
              className="rounded-lg border border-white/10 bg-[#111] py-2 px-3 text-sm text-white/60 focus:border-indigo-500/50 focus:outline-none"
            >
              <option value={7}>Last 7 days</option>
              <option value={30}>Last 30 days</option>
              <option value={90}>Last 90 days</option>
            </select>
            <button
              onClick={load}
              className="flex items-center gap-2 rounded-lg border border-white/10 px-4 py-2 text-sm text-white/60 hover:text-white hover:border-white/20 transition-all"
            >
              <RefreshCw className={`h-4 w-4 ${loading ? "animate-spin" : ""}`} />
            </button>
          </div>
        </div>

        {/* Stats grid */}
        <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 xl:grid-cols-6">
          {[
            { title: "Total Users", value: s?.total_users, color: "indigo" },
            { title: "Active Users", value: s?.active_users, color: "emerald" },
            { title: "New This Month", value: s?.new_users_this_month, color: "sky" },
            { title: "Total Resumes", value: s?.total_resumes, color: "violet" },
            { title: "ATS Reports", value: s?.total_analysis_reports, color: "amber" },
            { title: "Job Matches", value: s?.total_job_matches, color: "rose" },
          ].map((card) => (
            <StatsCard key={card.title} {...card} loading={loading} icon={TrendingUp} />
          ))}
        </div>

        {/* Charts */}
        <div className="grid grid-cols-1 gap-6 xl:grid-cols-2">
          {/* User Growth */}
          <div className="rounded-xl border border-white/5 bg-white/[0.03] p-5">
            <h3 className="text-sm font-semibold text-white mb-4">User Growth</h3>
            {loading ? (
              <div className="h-56 animate-pulse rounded bg-white/5" />
            ) : (
              <ResponsiveContainer width="100%" height={220}>
                <AreaChart data={analytics?.user_growth ?? []}>
                  <defs>
                    <linearGradient id="userGrad" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#6366f1" stopOpacity={0.3} />
                      <stop offset="95%" stopColor="#6366f1" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                  <XAxis dataKey="day" tick={{ fill: "rgba(255,255,255,0.3)", fontSize: 10 }} axisLine={false} tickLine={false} tickFormatter={(v) => v.slice(5)} />
                  <YAxis tick={{ fill: "rgba(255,255,255,0.3)", fontSize: 10 }} axisLine={false} tickLine={false} width={30} />
                  <Tooltip content={<CustomTooltip />} />
                  <Area type="monotone" dataKey="count" name="New Users" stroke="#6366f1" fill="url(#userGrad)" strokeWidth={2} dot={false} />
                </AreaChart>
              </ResponsiveContainer>
            )}
          </div>

          {/* Daily Uploads */}
          <div className="rounded-xl border border-white/5 bg-white/[0.03] p-5">
            <h3 className="text-sm font-semibold text-white mb-4">Daily Resume Uploads</h3>
            {loading ? (
              <div className="h-56 animate-pulse rounded bg-white/5" />
            ) : (
              <ResponsiveContainer width="100%" height={220}>
                <AreaChart data={analytics?.daily_uploads ?? []}>
                  <defs>
                    <linearGradient id="uploadGrad" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#a78bfa" stopOpacity={0.3} />
                      <stop offset="95%" stopColor="#a78bfa" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                  <XAxis dataKey="day" tick={{ fill: "rgba(255,255,255,0.3)", fontSize: 10 }} axisLine={false} tickLine={false} tickFormatter={(v) => v.slice(5)} />
                  <YAxis tick={{ fill: "rgba(255,255,255,0.3)", fontSize: 10 }} axisLine={false} tickLine={false} width={30} />
                  <Tooltip content={<CustomTooltip />} />
                  <Area type="monotone" dataKey="count" name="Uploads" stroke="#a78bfa" fill="url(#uploadGrad)" strokeWidth={2} dot={false} />
                </AreaChart>
              </ResponsiveContainer>
            )}
          </div>
        </div>

        {/* ATS Distribution */}
        <div className="rounded-xl border border-white/5 bg-white/[0.03] p-5">
          <h3 className="text-sm font-semibold text-white mb-4">ATS Score Distribution</h3>
          {loading ? (
            <div className="h-56 animate-pulse rounded bg-white/5" />
          ) : (
            <ResponsiveContainer width="100%" height={220}>
              <BarChart data={analytics?.ats_distribution ?? []}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                <XAxis dataKey="range" tick={{ fill: "rgba(255,255,255,0.3)", fontSize: 12 }} axisLine={false} tickLine={false} />
                <YAxis tick={{ fill: "rgba(255,255,255,0.3)", fontSize: 12 }} axisLine={false} tickLine={false} width={35} />
                <Tooltip content={<CustomTooltip />} />
                <Bar dataKey="count" name="Reports" fill="#34d399" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          )}
        </div>
      </div>
    </AdminLayout>
  );
}
