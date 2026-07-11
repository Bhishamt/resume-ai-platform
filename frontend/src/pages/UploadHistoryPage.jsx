import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { ArrowLeft, Clock, Loader2, FileText } from "lucide-react";
import { Card } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { EmptyState } from "@/components/ui/EmptyState";
import resumeService from "@/services/resumeService";
import { useToast } from "@/hooks/useToast";
export default function UploadHistoryPage() {
  const { toasts, error, removeToast } = useToast();
  
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadHistory() {
      try {
        const response = await resumeService.getUploadHistory();
        setHistory(response.data);
      } catch {
        error("Failed to load upload history logs.");
      } finally {
        setLoading(false);
      }
    }
    loadHistory();
  }, [error]);

  return (
    <div className="min-h-screen bg-[#050505] text-white">
      <div className="h-24" /> {/* Header spacer */}

        <main className="mx-auto w-full max-w-5xl px-4 py-8 sm:px-6 lg:px-8">
          <div className="mb-8 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Link to="/resumes" className="p-2 rounded-full hover:bg-white/5 transition-colors text-white/55 hover:text-white" aria-label="Back to resumes">
                <ArrowLeft className="h-5 w-5" />
              </Link>
              <div>
                <h1 className="text-3xl font-semibold tracking-tight text-white flex items-center gap-2">
                  Activity Log
                  <Clock className="h-5 w-5 text-white/55" />
                </h1>
                <p className="mt-1 text-sm text-white/55">
                  Audit logs for uploads, updates, replacements, and deletions
                </p>
              </div>
            </div>
          </div>

          {loading ? (
            <Card className="overflow-hidden p-0 border-white/5 bg-white/[0.02]">
              <div className="p-4 border-b border-white/5 flex gap-4">
                <Skeleton className="h-4 w-24" />
                <Skeleton className="h-4 w-48" />
                <Skeleton className="h-4 w-32" />
              </div>
              <div className="p-4 border-b border-white/5 flex gap-4">
                <Skeleton className="h-4 w-24" />
                <Skeleton className="h-4 w-48" />
                <Skeleton className="h-4 w-32" />
              </div>
              <div className="p-4 flex gap-4">
                <Skeleton className="h-4 w-24" />
                <Skeleton className="h-4 w-48" />
                <Skeleton className="h-4 w-32" />
              </div>
            </Card>
          ) : history.length === 0 ? (
            <EmptyState 
              title="No history records"
              description="Actions will be logged here as you manage resumes."
              icon={Clock}
            />
          ) : (
            <Card className="overflow-hidden">
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs border-collapse">
                  <thead>
                    <tr className="border-b border-white/5 bg-white/[0.02] text-white/40 uppercase font-semibold tracking-wider">
                      <th className="px-6 py-4">Action</th>
                      <th className="px-6 py-4">Resume Title</th>
                      <th className="px-6 py-4">Timestamp</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-white/5">
                    {history.map((entry) => {
                      // Action styles map
                      const isUpload = entry.action === "upload";
                      const isDelete = entry.action === "delete";

                      return (
                        <tr key={entry.id} className="hover:bg-white/[0.01] transition-colors">
                          <td className="px-6 py-4 font-medium">
                            <span className={`inline-flex items-center rounded-full px-2 py-0.5 text-[10px] font-semibold border capitalize ${
                              isUpload 
                                ? "bg-green-500/5 text-green-400 border-green-500/10" 
                                : isDelete 
                                ? "bg-red-500/5 text-red-400 border-red-500/10" 
                                : "bg-blue-500/5 text-blue-400 border-blue-500/10"
                            }`}>
                              {entry.action}
                            </span>
                          </td>
                          <td className="px-6 py-4 font-medium text-white/80">
                            {isDelete ? (
                              <span className="text-white/40 line-through">{entry.resume_title}</span>
                            ) : (
                              <Link to={`/resumes/${entry.resume_id}`} className="hover:text-white transition-colors flex items-center gap-1.5">
                                <FileText className="h-3.5 w-3.5 opacity-60" />
                                {entry.resume_title}
                              </Link>
                            )}
                          </td>
                          <td className="px-6 py-4 text-white/50 font-mono">
                            {new Date(entry.timestamp).toLocaleString()}
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            </Card>
          )}
        </main>

      </div>
  );
}
