import React, { useState, useEffect, useCallback } from "react";
import { Link } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import { FileText, Plus, Trash2, Calendar, HardDrive, AlertTriangle, ArrowLeft, ArrowRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Modal } from "@/components/ui/modal";
import { Skeleton } from "@/components/ui/skeleton";
import { EmptyState } from "@/components/ui/EmptyState";
import resumeService from "@/services/resumeService";
import { useToast } from "@/hooks/useToast";

export default function ResumeList() {
  const { success, error } = useToast();
  
  const [resumes, setResumes] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [limit] = useState(6);
  const [loading, setLoading] = useState(true);
  
  const [deleteModalOpen, setDeleteModalOpen] = useState(false);
  const [selectedResume, setSelectedResume] = useState(null);
  const [deleting, setDeleting] = useState(false);

  const fetchResumes = useCallback(async (pageNum) => {
    setLoading(true);
    try {
      const response = await resumeService.getResumes(pageNum, limit);
      setResumes(response.data.items);
      setTotal(response.data.total);
      setPage(response.data.page);
    } catch {
      error("Failed to load resumes. Please check your network connection.");
    } finally {
      setLoading(false);
    }
  }, [limit, error]);

  useEffect(() => {
    fetchResumes(1);
  }, [fetchResumes]);

  const openDeleteModal = (resume, e) => {
    e.preventDefault(); // Prevent navigating to details page
    e.stopPropagation();
    setSelectedResume(resume);
    setDeleteModalOpen(true);
  };

  const handleDelete = async () => {
    if (!selectedResume) return;
    setDeleting(true);
    try {
      await resumeService.deleteResume(selectedResume.id);
      success(`Resume "${selectedResume.title}" was deleted.`);
      setDeleteModalOpen(false);
      setSelectedResume(null);
      // Refresh list: if we deleted the last item on the page, go back a page
      const nextTotal = total - 1;
      const totalPages = Math.ceil(nextTotal / limit) || 1;
      const targetPage = page > totalPages ? totalPages : page;
      fetchResumes(targetPage);
    } catch {
      error("Failed to delete the resume. Please try again.");
    } finally {
      setDeleting(false);
    }
  };

  const totalPages = Math.ceil(total / limit) || 1;

  return (
    <div className="min-h-screen bg-[#050505] text-white">
      <div className="h-24" /> {/* Header spacer */}

        <main className="mx-auto w-full max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
          <div className="mb-10 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
            <div>
              <h1 className="text-3xl font-semibold tracking-tight text-white">My Resumes</h1>
              <p className="mt-2 text-sm text-white/55">
                Manage uploaded files and view parsed profile summaries
              </p>
            </div>
            <div className="flex gap-3">
              <Link to="/resumes/history">
                <Button variant="outline" className="rounded-full font-semibold">
                  Activity Log
                </Button>
              </Link>
              <Link to="/resumes/upload">
                <Button variant="default" className="rounded-full font-semibold gap-2">
                  <Plus className="h-4 w-4" />
                  Upload New
                </Button>
              </Link>
            </div>
          </div>

          {loading ? (
            /* Skeleton Loading Grid */
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {[1, 2, 3].map((i) => (
                <Card key={i} className="p-6 space-y-4">
                  <div className="flex items-start justify-between">
                    <Skeleton className="h-10 w-10 rounded-lg" />
                    <Skeleton className="h-8 w-8 rounded-full" />
                  </div>
                  <div className="space-y-2">
                    <Skeleton className="h-5 w-3/4" />
                    <Skeleton className="h-4 w-1/2" />
                  </div>
                  <div className="pt-4 border-t border-white/5 flex gap-4">
                    <Skeleton className="h-4 w-1/3" />
                    <Skeleton className="h-4 w-1/4" />
                  </div>
                </Card>
              ))}
            </div>
          ) : resumes.length === 0 ? (
            /* Empty State */
            <EmptyState 
              title="No resumes found"
              description="Get started by uploading your first resume. We will parse it and index the skills."
              icon={FileText}
              action={
                <Link to="/resumes/upload">
                  <Button className="rounded-full font-semibold">
                    Upload Resume
                  </Button>
                </Link>
              }
            />
          ) : (
            /* Card Grid List */
            <>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                <AnimatePresence mode="popLayout">
                  {resumes.map((resume) => (
                    <motion.div
                      key={resume.id}
                      initial={{ opacity: 0, scale: 0.95 }}
                      animate={{ opacity: 1, scale: 1 }}
                      exit={{ opacity: 0, scale: 0.95 }}
                      transition={{ duration: 0.2 }}
                      className="group"
                    >
                      <Link to={`/resumes/${resume.id}`}>
                        <Card className="p-6 hover:border-white/20 transition-all duration-300 relative overflow-hidden flex flex-col justify-between h-[220px]">
                          <div>
                            <div className="flex items-start justify-between">
                              <div className="h-10 w-10 rounded-lg bg-white/5 flex items-center justify-center text-white/70 border border-white/10 group-hover:bg-white/10 transition-colors">
                                <FileText className="h-5 w-5" />
                              </div>
                              <Button
                                variant="ghost"
                                size="icon"
                                onClick={(e) => openDeleteModal(resume, e)}
                                className="h-8 w-8 rounded-full text-white/40 hover:text-red-400 hover:bg-red-500/10 opacity-0 group-hover:opacity-100 transition-opacity"
                                aria-label="Delete resume"
                              >
                                <Trash2 className="h-4 w-4" />
                              </Button>
                            </div>

                            <CardHeader className="p-0 mt-4">
                              <CardTitle className="text-base font-semibold text-white group-hover:text-white/90 line-clamp-1">
                                {resume.title}
                              </CardTitle>
                              <CardDescription className="text-xs text-white/40 mt-1 line-clamp-1">
                                {resume.original_filename}
                              </CardDescription>
                            </CardHeader>
                          </div>

                          <div className="pt-4 border-t border-white/5 flex items-center justify-between text-xs text-white/40">
                            <span className="flex items-center gap-1.5">
                              <Calendar className="h-3.5 w-3.5" />
                              {new Date(resume.upload_date).toLocaleDateString()}
                            </span>
                            <span className="flex items-center gap-1.5">
                              <HardDrive className="h-3.5 w-3.5" />
                              {(resume.file_size / 1024).toFixed(1)} KB
                            </span>
                            <span className={`inline-flex items-center rounded-full px-2 py-0.5 text-[10px] font-medium border ${
                              resume.upload_status === "success" 
                                ? "bg-green-500/5 text-green-400 border-green-500/10" 
                                : "bg-red-500/5 text-red-400 border-red-500/10"
                            }`}>
                              {resume.upload_status}
                            </span>
                          </div>
                        </Card>
                      </Link>
                    </motion.div>
                  ))}
                </AnimatePresence>
              </div>

              {/* Pagination Controls */}
              {totalPages > 1 && (
                <div className="mt-12 flex items-center justify-center gap-4">
                  <Button
                    variant="outline"
                    size="sm"
                    disabled={page === 1}
                    onClick={() => fetchResumes(page - 1)}
                    className="rounded-full gap-1.5"
                  >
                    <ArrowLeft className="h-4 w-4" />
                    Previous
                  </Button>
                  <span className="text-sm font-medium text-white/50">
                    Page {page} of {totalPages}
                  </span>
                  <Button
                    variant="outline"
                    size="sm"
                    disabled={page === totalPages}
                    onClick={() => fetchResumes(page + 1)}
                    className="rounded-full gap-1.5"
                  >
                    Next
                    <ArrowRight className="h-4 w-4" />
                  </Button>
                </div>
              )}
            </>
          )}
        </main>

        {/* Delete Confirmation Modal */}
        <Modal
          isOpen={deleteModalOpen}
          onClose={() => setDeleteModalOpen(false)}
          title="Delete Resume"
        >
          <div className="space-y-6">
            <div className="flex items-start gap-4 rounded-xl border border-red-500/10 bg-red-500/5 p-4 text-red-400">
              <AlertTriangle className="h-5 w-5 shrink-0 mt-0.5" />
              <div>
                <p className="text-sm font-semibold">Warning: This action is permanent</p>
                <p className="text-xs mt-1 leading-relaxed opacity-85">
                  Are you sure you want to delete "{selectedResume?.title}"? The database metadata and physical storage file will be deleted permanently.
                </p>
              </div>
            </div>
            <div className="flex justify-end gap-3">
              <Button
                variant="ghost"
                onClick={() => setDeleteModalOpen(false)}
                disabled={deleting}
                className="rounded-full"
              >
                Cancel
              </Button>
              <Button
                variant="danger"
                onClick={handleDelete}
                isLoading={deleting}
                className="rounded-full bg-red-500/10 text-red-400 hover:bg-red-500/20 border border-red-500/20"
              >
                Delete Resume
              </Button>
            </div>
          </div>
        </Modal>

      </div>
  );
}
