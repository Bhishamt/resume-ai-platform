import React, { useCallback, useEffect, useState } from "react";
import {
  PieChart, Pie, Cell, Tooltip, ResponsiveContainer, Legend, BarChart, Bar, XAxis, YAxis, CartesianGrid,
} from "recharts";
import { Brain, Zap, Clock, RefreshCw, Activity } from "lucide-react";
import AdminLayout from "@/components/admin/AdminLayout";
import StatsCard from "@/components/admin/StatsCard";
import adminService from "@/services/adminService";

const COLORS = ["#6366f1", "#22d3ee", "#a78bfa", "#34d399", "#f59e0b"];

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

export default function AdminAIMonitoring() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const result = await adminService.getAIMonitoring();
      setData(result);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { load(); }, [load]);

  return (
    <AdminLayout>
      <div className="px-6 py-8 max-w-screen-2xl mx-auto space-y-8">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-white">AI Monitoring</h1>
            <p className="text-sm text-white/40 mt-1">
              AI provider usage, token consumption, and performance
            </p>
          </div>
          <button
            onClick={load}
            className="flex items-center gap-2 rounded-lg border border-white/10 px-4 py-2 text-sm text-white/60 hover:text-white hover:border-white/20 transition-all"
          >
            <RefreshCw className={`h-4 w-4 ${loading ? "animate-spin" : ""}`} />
            Refresh
          </button>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 xl:grid-cols-5">
          <StatsCard title="Total AI Requests" value={data?.total_requests} icon={Brain} color="indigo" loading={loading} />
          <StatsCard title="Requests Today" value={data?.requests_today} icon={Activity} color="sky" loading={loading} />
          <StatsCard
            title="Total Tokens"
            value={data?.total_tokens ? `${(data.total_tokens / 1_000_000).toFixed(2)}M` : "—"}
            icon={Zap}
            color="amber"
            loading={loading}
          />
          <StatsCard
            title="Tokens Today"
            value={data?.tokens_today ? `${(data.tokens_today / 1000).toFixed(1)}K` : "—"}
            icon={Zap}
            color="violet"
            loading={loading}
          />
          <StatsCard
            title="Avg Response"
            value={data?.avg_response_time_ms ? `${data.avg_response_time_ms.toFixed(0)}ms` : "—"}
            icon={Clock}
            color="rose"
            loading={loading}
          />
        </div>

        {/* Charts */}
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
          {/* Provider Pie */}
          <div className="rounded-xl border border-white/5 bg-white/[0.03] p-5">
            <h3 className="text-sm font-semibold text-white mb-4">Provider Distribution</h3>
            {loading ? (
              <div className="h-64 animate-pulse rounded bg-white/5" />
            ) : !data?.provider_stats?.length ? (
              <div className="flex h-64 items-center justify-center text-sm text-white/30">
                No AI requests recorded yet.
              </div>
            ) : (
              <ResponsiveContainer width="100%" height={260}>
                <PieChart>
                  <Pie
                    data={data.provider_stats}
                    dataKey="count"
                    nameKey="provider"
                    cx="50%"
                    cy="50%"
                    outerRadius={100}
                    innerRadius={55}
                    paddingAngle={3}
                  >
                    {data.provider_stats.map((_, i) => (
                      <Cell key={i} fill={COLORS[i % COLORS.length]} />
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

          {/* Provider Bar */}
          <div className="rounded-xl border border-white/5 bg-white/[0.03] p-5">
            <h3 className="text-sm font-semibold text-white mb-4">Requests by Provider</h3>
            {loading ? (
              <div className="h-64 animate-pulse rounded bg-white/5" />
            ) : !data?.provider_stats?.length ? (
              <div className="flex h-64 items-center justify-center text-sm text-white/30">
                No data available.
              </div>
            ) : (
              <ResponsiveContainer width="100%" height={260}>
                <BarChart data={data.provider_stats} layout="vertical">
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                  <XAxis type="number" tick={{ fill: "rgba(255,255,255,0.3)", fontSize: 11 }} axisLine={false} tickLine={false} />
                  <YAxis type="category" dataKey="provider" tick={{ fill: "rgba(255,255,255,0.5)", fontSize: 12 }} axisLine={false} tickLine={false} width={60} />
                  <Tooltip content={<CustomTooltip />} />
                  <Bar dataKey="count" name="Requests" radius={[0, 4, 4, 0]}>
                    {data.provider_stats.map((_, i) => (
                      <Cell key={i} fill={COLORS[i % COLORS.length]} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            )}
          </div>
        </div>

        {/* Performance note */}
        <div className="rounded-xl border border-white/5 bg-white/[0.03] p-5">
          <h3 className="text-sm font-semibold text-white mb-3">Performance Overview</h3>
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
            {[
              { label: "Average Response Time", value: data?.avg_response_time_ms ? `${data.avg_response_time_ms.toFixed(0)} ms` : "—", hint: "Lower is better" },
              { label: "Total Tokens Consumed", value: data?.total_tokens?.toLocaleString() ?? "—", hint: "Cumulative all-time" },
              { label: "Avg Tokens per Request", value: data?.total_requests ? Math.round((data.total_tokens ?? 0) / data.total_requests).toLocaleString() : "—", hint: "Efficiency metric" },
            ].map((item) => (
              <div key={item.label} className="rounded-lg border border-white/5 bg-white/[0.02] p-4">
                <p className="text-xs text-white/40 mb-1">{item.label}</p>
                <p className="text-2xl font-bold text-white">{loading ? "…" : item.value}</p>
                <p className="text-xs text-white/20 mt-1">{item.hint}</p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </AdminLayout>
  );
}
