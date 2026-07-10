import React from "react";
import {
  CheckCircle2,
  AlertTriangle,
  XCircle,
  Database,
  HardDrive,
  Cpu,
  MemoryStick,
  Wifi,
  Brain,
  Server,
} from "lucide-react";

function StatusBadge({ status }) {
  const map = {
    healthy: { label: "Healthy", cls: "bg-emerald-500/10 text-emerald-400 border-emerald-500/20", icon: CheckCircle2 },
    degraded: { label: "Degraded", cls: "bg-amber-500/10 text-amber-400 border-amber-500/20", icon: AlertTriangle },
    offline: { label: "Offline", cls: "bg-rose-500/10 text-rose-400 border-rose-500/20", icon: XCircle },
    unconfigured: { label: "Unconfigured", cls: "bg-white/5 text-white/40 border-white/10", icon: AlertTriangle },
    unknown: { label: "Unknown", cls: "bg-white/5 text-white/40 border-white/10", icon: AlertTriangle },
  };
  const cfg = map[status] ?? map.unknown;
  const Icon = cfg.icon;
  return (
    <span className={`inline-flex items-center gap-1 rounded-full border px-2 py-0.5 text-xs font-medium ${cfg.cls}`}>
      <Icon className="h-3 w-3" />
      {cfg.label}
    </span>
  );
}

function UsageBar({ percent, color = "indigo" }) {
  const colors = {
    indigo: "bg-indigo-500",
    emerald: "bg-emerald-500",
    rose: "bg-rose-500",
    amber: "bg-amber-500",
  };
  const barColor =
    percent >= 90 ? colors.rose : percent >= 70 ? colors.amber : colors.emerald;

  return (
    <div className="flex items-center gap-3">
      <div className="flex-1 h-1.5 rounded-full bg-white/5 overflow-hidden">
        <div
          className={`h-full rounded-full transition-all duration-700 ${barColor}`}
          style={{ width: `${Math.min(percent, 100)}%` }}
        />
      </div>
      <span className="text-xs text-white/40 w-10 text-right">
        {percent?.toFixed(1)}%
      </span>
    </div>
  );
}

function HealthRow({ icon: Icon, label, value, children, loading }) {
  if (loading) {
    return (
      <div className="flex items-center justify-between py-3 border-b border-white/5 last:border-0 animate-pulse">
        <div className="flex items-center gap-3">
          <div className="h-4 w-4 rounded bg-white/5" />
          <div className="h-3 w-24 rounded bg-white/5" />
        </div>
        <div className="h-5 w-16 rounded-full bg-white/5" />
      </div>
    );
  }
  return (
    <div className="py-3 border-b border-white/5 last:border-0">
      <div className="flex items-center justify-between mb-1">
        <div className="flex items-center gap-3">
          <Icon className="h-4 w-4 text-white/40 shrink-0" />
          <span className="text-sm text-white/70">{label}</span>
        </div>
        {value}
      </div>
      {children}
    </div>
  );
}

/**
 * SystemHealthCard — shows live infrastructure metrics.
 *
 * Props:
 *   data    - SystemHealthResponse from /admin/system
 *   loading - boolean
 */
export default function SystemHealthCard({ data, loading = false }) {
  return (
    <div className="rounded-xl border border-white/5 bg-white/[0.03] p-5">
      <div className="flex items-center gap-3 mb-5">
        <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-indigo-500/10 border border-indigo-500/20">
          <Server className="h-4 w-4 text-indigo-400" />
        </div>
        <div>
          <h3 className="text-sm font-semibold text-white">System Health</h3>
          <p className="text-xs text-white/40">Live infrastructure metrics</p>
        </div>
        {data && (
          <span className="ml-auto text-xs text-white/30">
            Uptime {Math.floor((data.uptime_seconds ?? 0) / 3600)}h{" "}
            {Math.floor(((data.uptime_seconds ?? 0) % 3600) / 60)}m
          </span>
        )}
      </div>

      <div className="divide-y divide-white/5">
        <HealthRow icon={Wifi} label="API Server" loading={loading}
          value={<StatusBadge status={data?.api_status ?? "unknown"} />} />

        <HealthRow icon={Database} label="Database" loading={loading}
          value={<StatusBadge status={data?.database_status ?? "unknown"} />} />

        <HealthRow icon={Brain} label="AI Provider" loading={loading}
          value={<StatusBadge status={data?.ai_provider_status ?? "unknown"} />} />

        <HealthRow
          icon={Cpu}
          label="CPU Usage"
          loading={loading}
          value={
            <span className="text-xs text-white/40">
              {data?.cpu_percent?.toFixed(1) ?? "—"}%
            </span>
          }
        >
          {!loading && data && <UsageBar percent={data.cpu_percent} />}
        </HealthRow>

        <HealthRow
          icon={MemoryStick}
          label="Memory"
          loading={loading}
          value={
            <span className="text-xs text-white/40">
              {data
                ? `${data.memory_used_mb?.toFixed(0)} / ${data.memory_total_mb?.toFixed(0)} MB`
                : "—"}
            </span>
          }
        >
          {!loading && data && <UsageBar percent={data.memory_percent} />}
        </HealthRow>

        <HealthRow
          icon={HardDrive}
          label="Disk"
          loading={loading}
          value={
            <span className="text-xs text-white/40">
              {data
                ? `${data.disk_used_gb?.toFixed(1)} / ${data.disk_total_gb?.toFixed(1)} GB`
                : "—"}
            </span>
          }
        >
          {!loading && data && <UsageBar percent={data.disk_percent} />}
        </HealthRow>

        <HealthRow
          icon={HardDrive}
          label="Storage (Uploads)"
          loading={loading}
          value={
            <span className="text-xs text-white/40">
              {data ? `${data.storage_used_mb?.toFixed(1)} MB` : "—"}
            </span>
          }
        />
      </div>
    </div>
  );
}
