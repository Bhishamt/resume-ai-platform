import React from "react";
import { TrendingUp, TrendingDown, Minus } from "lucide-react";

/**
 * StatsCard — displays a single metric with optional trend indicator.
 *
 * Props:
 *   title     - string label
 *   value     - number | string
 *   icon      - Lucide icon component
 *   trend     - "up" | "down" | "neutral" (optional)
 *   trendVal  - string, e.g. "+12%" (optional)
 *   subtitle  - secondary description string (optional)
 *   color     - Tailwind colour prefix: "indigo" | "emerald" | "rose" | "amber"
 *   loading   - boolean (shows skeleton)
 */
export default function StatsCard({
  title,
  value,
  icon: Icon,
  trend,
  trendVal,
  subtitle,
  color = "indigo",
  loading = false,
}) {
  const colorMap = {
    indigo: {
      bg: "bg-indigo-500/10",
      border: "border-indigo-500/20",
      icon: "text-indigo-400",
      glow: "shadow-indigo-500/5",
    },
    emerald: {
      bg: "bg-emerald-500/10",
      border: "border-emerald-500/20",
      icon: "text-emerald-400",
      glow: "shadow-emerald-500/5",
    },
    rose: {
      bg: "bg-rose-500/10",
      border: "border-rose-500/20",
      icon: "text-rose-400",
      glow: "shadow-rose-500/5",
    },
    amber: {
      bg: "bg-amber-500/10",
      border: "border-amber-500/20",
      icon: "text-amber-400",
      glow: "shadow-amber-500/5",
    },
    violet: {
      bg: "bg-violet-500/10",
      border: "border-violet-500/20",
      icon: "text-violet-400",
      glow: "shadow-violet-500/5",
    },
    sky: {
      bg: "bg-sky-500/10",
      border: "border-sky-500/20",
      icon: "text-sky-400",
      glow: "shadow-sky-500/5",
    },
  };

  const c = colorMap[color] ?? colorMap.indigo;

  const TrendIcon =
    trend === "up" ? TrendingUp : trend === "down" ? TrendingDown : Minus;
  const trendColor =
    trend === "up"
      ? "text-emerald-400"
      : trend === "down"
      ? "text-rose-400"
      : "text-white/40";

  if (loading) {
    return (
      <div className="rounded-xl border border-white/5 bg-white/[0.03] p-5 animate-pulse">
        <div className="flex items-center justify-between mb-4">
          <div className="h-4 w-24 rounded bg-white/5" />
          <div className="h-9 w-9 rounded-lg bg-white/5" />
        </div>
        <div className="h-8 w-20 rounded bg-white/5 mb-2" />
        <div className="h-3 w-16 rounded bg-white/5" />
      </div>
    );
  }

  return (
    <div
      className={`relative rounded-xl border border-white/5 bg-white/[0.03] p-5 transition-all duration-200 hover:border-white/10 hover:bg-white/[0.05] shadow-lg ${c.glow}`}
    >
      <div className="flex items-start justify-between mb-4">
        <p className="text-sm font-medium text-white/50">{title}</p>
        <div className={`flex h-9 w-9 items-center justify-center rounded-lg border ${c.bg} ${c.border}`}>
          {Icon && <Icon className={`h-4 w-4 ${c.icon}`} />}
        </div>
      </div>

      <p className="text-3xl font-bold text-white tracking-tight">
        {value !== undefined && value !== null
          ? typeof value === "number"
            ? value.toLocaleString()
            : value
          : "—"}
      </p>

      <div className="mt-2 flex items-center gap-2">
        {trend && trendVal && (
          <div className={`flex items-center gap-1 text-xs font-medium ${trendColor}`}>
            <TrendIcon className="h-3 w-3" />
            <span>{trendVal}</span>
          </div>
        )}
        {subtitle && (
          <p className="text-xs text-white/30">{subtitle}</p>
        )}
      </div>
    </div>
  );
}
