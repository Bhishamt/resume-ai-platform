import React, { useState, useEffect, useRef } from "react";
import { useParams, Link, useNavigate } from "react-router-dom";
import {
  User,
  Mail,
  Phone,
  Sparkles,
  ArrowLeft,
  Edit2,
  Check,
  RefreshCw,
  Trash2,
  AlertTriangle,
  Loader2,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { Modal } from "@/components/ui/modal";
import resumeService from "@/services/resumeService";
import { useToast } from "@/hooks/useToast";
import { Toast, ToastClose, ToastDescription, ToastProvider, ToastTitle, ToastViewport } from "@/components/ui/toast";

export default function ResumeDetails() {
  const { id } = useParams();
  const navigate = useNavigate();
  const fileInputRef = useRef(null);
  const { toasts, success, error, removeToast } = useToast();

  const [resume, setResume] = useState(null);
  const [loading, setLoading] = useState(true);

  // Renaming state
  const [isEditingTitle, setIsEditingTitle] = useState(false);
  const [editedTitle, setEditedTitle] = useState("");
  const [updatingTitle, setUpdatingTitle] = useState(false);

  // File replacement state
  const [replacingFile, setReplacingFile] = useState(false);

  // Delete modal state
  const [deleteModalOpen, setDeleteModalOpen] = useState(false);
  const [deleting, setDeleting] = useState(false);

  useEffect(() => {
    async function loadResume() {
      try {
        const response = await resumeService.getResumeById(id);
        setResume(response.data);
        setEditedTitle(response.data.title);
      } catch {
        error("Resume not found or access denied.");
        setTimeout(() => navigate("/resumes"), 2000);
      } finally {
        setLoading(false);
      }
    }
    loadResume();
  }, [id, navigate, error]);

  const handleTitleUpdate = async () => {
    if (!editedTitle.trim()) {
      error("Title cannot be empty.");
      return;
    }
    setUpdatingTitle(true);
    try {
      const response = await resumeService.updateResume(id, editedTitle);
      setResume(response.data);
      setIsEditingTitle(false);
      success("Resume title updated.");
    } catch {
      error("Failed to update title.");
    } finally {
      setUpdatingTitle(false);
    }
  };

  const handleReplaceClick = () => {
    fileInputRef.current.click();
  };

  const handleFileChange = async (e) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      
      // Extension validation client-side
      const ext = file.name.split(".").pop().toLowerCase();
      if (ext !== "pdf" && ext !== "docx") {
        error("Only PDF and DOCX files are allowed.");
        return;
      }

      setReplacingFile(true);
      try {
        const response = await resumeService.replaceResume(id, file);
        setResume(response.data);
        setEditedTitle(response.data.title);
        success("Resume file replaced and re-parsed successfully!");
      } catch (err) {
        const msg = err.response?.data?.message || "File replacement failed.";
        error(msg);
      } finally {
        setReplacingFile(false);
      }
    }
  };

  const handleDelete = async () => {
    setDeleting(true);
    try {
      await resumeService.deleteResume(id);
      success("Resume deleted permanently.");
      setDeleteModalOpen(false);
      setTimeout(() => navigate("/resumes"), 1000);
    } catch {
      error("Failed to delete resume.");
      setDeleting(false);
    }
  };

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-[#050505] text-white">
        <div className="flex flex-col items-center gap-4">
          <Loader2 className="h-8 w-8 animate-spin text-white/50" />
          <p className="text-sm text-white/55">Loading resume details...</p>
        </div>
      </div>
    );
  }

  if (!resume) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-[#050505] text-white">
        <p className="text-sm text-white/55">Redirecting to list...</p>
      </div>
    );
  }

  // Parse details out of parsed_text structure (simple heuristics for details tab)
  const isDocSuccess = resume.upload_status === "success";
  
  // Extract contact fields helper
  const name = resume.parsed_text?.match(/^[^\n]+/)?.[0] || "Unknown Name";
  const email = resume.parsed_text?.match(/[\w.-]+@[\w.-]+\.\w+/)?.[0] || null;
  const phone = resume.parsed_text?.match(/(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}/)?.[0] || null;

  return (
    <ToastProvider>
      <div className="min-h-screen bg-[#050505] text-white">
        <div className="h-24" /> {/* Header spacer */}

        <input
          ref={fileInputRef}
          type="file"
          className="hidden"
          onChange={handleFileChange}
          accept=".pdf,.docx"
        />

        <main className="mx-auto w-full max-w-6xl px-4 py-8 sm:px-6 lg:px-8">
          {/* Header Action Row */}
          <div className="mb-8 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
            <div className="flex items-center gap-3">
              <Link to="/resumes" className="p-2 rounded-full hover:bg-white/5 transition-colors text-white/55 hover:text-white">
                <ArrowLeft className="h-5 w-5" />
              </Link>
              <div>
                <div className="flex items-center gap-2">
                  {isEditingTitle ? (
                    <div className="flex items-center gap-2">
                      <Input
                        type="text"
                        value={editedTitle}
                        onChange={(e) => setEditedTitle(e.target.value)}
                        disabled={updatingTitle}
                        className="h-9 w-64 bg-black/40 text-base font-semibold border-white/10"
                      />
                      <Button
                        size="icon"
                        variant="ghost"
                        onClick={handleTitleUpdate}
                        disabled={updatingTitle}
                        className="h-8 w-8 text-green-400 hover:bg-green-500/10"
                      >
                        <Check className="h-4 w-4" />
                      </Button>
                    </div>
                  ) : (
                    <>
                      <h1 className="text-2xl font-semibold tracking-tight text-white">{resume.title}</h1>
                      <Button
                        size="icon"
                        variant="ghost"
                        onClick={() => setIsEditingTitle(true)}
                        className="h-8 w-8 text-white/40 hover:text-white hover:bg-white/5"
                      >
                        <Edit2 className="h-3.5 w-3.5" />
                      </Button>
                    </>
                  )}
                </div>
                <p className="mt-1 text-xs text-white/45">
                  ID: <code className="text-white/60">{resume.id}</code>
                </p>
              </div>
            </div>

            <div className="flex items-center gap-3">
              <Button
                variant="outline"
                onClick={handleReplaceClick}
                disabled={replacingFile}
                className="rounded-full gap-1.5 text-xs font-semibold"
              >
                {replacingFile ? (
                  <Loader2 className="h-3.5 w-3.5 animate-spin" />
                ) : (
                  <RefreshCw className="h-3.5 w-3.5" />
                )}
                Replace File
              </Button>
              <Button
                variant="danger"
                onClick={() => setDeleteModalOpen(true)}
                className="rounded-full bg-red-500/10 text-red-400 border border-red-500/20 hover:bg-red-500/20 text-xs font-semibold gap-1.5"
              >
                <Trash2 className="h-3.5 w-3.5" />
                Delete
              </Button>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Sidebar Metadata Card */}
            <div className="lg:col-span-1 space-y-6">
              <Card className="p-6">
                <h3 className="text-sm font-semibold text-white mb-4">File Metadata</h3>
                <div className="space-y-4">
                  <div className="flex items-center justify-between text-xs border-b border-white/5 pb-2">
                    <span className="text-white/40">Filename</span>
                    <span className="text-white/80 font-medium truncate max-w-[150px]" title={resume.original_filename}>
                      {resume.original_filename}
                    </span>
                  </div>
                  <div className="flex items-center justify-between text-xs border-b border-white/5 pb-2">
                    <span className="text-white/40">Format type</span>
                    <span className="text-white/80 font-medium truncate max-w-[150px]" title={resume.file_type}>
                      {resume.file_type.split("/")[1]?.toUpperCase() || "Unknown"}
                    </span>
                  </div>
                  <div className="flex items-center justify-between text-xs border-b border-white/5 pb-2">
                    <span className="text-white/40">File size</span>
                    <span className="text-white/80 font-medium">
                      {(resume.file_size / 1024).toFixed(1)} KB
                    </span>
                  </div>
                  <div className="flex items-center justify-between text-xs border-b border-white/5 pb-2">
                    <span className="text-white/40">Uploaded date</span>
                    <span className="text-white/80 font-medium">
                      {new Date(resume.upload_date).toLocaleString()}
                    </span>
                  </div>
                  <div className="flex items-center justify-between text-xs pb-1">
                    <span className="text-white/40">Parse status</span>
                    <span className={`inline-flex items-center rounded-full px-2 py-0.5 text-[10px] font-medium border ${
                      isDocSuccess 
                        ? "bg-green-500/5 text-green-400 border-green-500/10" 
                        : "bg-red-500/5 text-red-400 border-red-500/10"
                    }`}>
                      {resume.upload_status}
                    </span>
                  </div>
                </div>
              </Card>

              {isDocSuccess && (
                <Card className="p-6">
                  <h3 className="text-sm font-semibold text-white mb-4 flex items-center gap-1.5">
                    Contact Information
                    <Sparkles className="h-4 w-4 text-white/50 animate-pulse" />
                  </h3>
                  <div className="space-y-4">
                    <div className="flex items-center gap-3 text-xs">
                      <div className="h-7 w-7 rounded-lg bg-white/5 flex items-center justify-center text-white/50 border border-white/5">
                        <User className="h-3.5 w-3.5" />
                      </div>
                      <div>
                        <p className="text-[10px] text-white/40">Name (Detected)</p>
                        <p className="font-medium text-white mt-0.5">{name}</p>
                      </div>
                    </div>

                    <div className="flex items-center gap-3 text-xs">
                      <div className="h-7 w-7 rounded-lg bg-white/5 flex items-center justify-center text-white/50 border border-white/5">
                        <Mail className="h-3.5 w-3.5" />
                      </div>
                      <div>
                        <p className="text-[10px] text-white/40">Email Address</p>
                        <p className="font-medium text-white mt-0.5">{email || "Not found"}</p>
                      </div>
                    </div>

                    <div className="flex items-center gap-3 text-xs">
                      <div className="h-7 w-7 rounded-lg bg-white/5 flex items-center justify-center text-white/50 border border-white/5">
                        <Phone className="h-3.5 w-3.5" />
                      </div>
                      <div>
                        <p className="text-[10px] text-white/40">Phone Number</p>
                        <p className="font-medium text-white mt-0.5">{phone || "Not found"}</p>
                      </div>
                    </div>
                  </div>
                </Card>
              )}
            </div>

            {/* Main Tabs Content Panel */}
            <div className="lg:col-span-2">
              <Tabs defaultValue="extracted" className="w-full">
                <TabsList className="grid w-full grid-cols-2 bg-white/5 border border-white/5 p-1 rounded-xl">
                  <TabsTrigger value="extracted" className="rounded-lg text-xs font-semibold py-2">
                    Extracted Summary
                  </TabsTrigger>
                  <TabsTrigger value="raw" className="rounded-lg text-xs font-semibold py-2">
                    Raw Parsed Text
                  </TabsTrigger>
                </TabsList>

                {/* Extracted Details View */}
                <TabsContent value="extracted" className="mt-6">
                  <Card className="p-8 space-y-6">
                    {!isDocSuccess ? (
                      <div className="text-center py-10">
                        <AlertTriangle className="h-10 w-10 text-red-400 mx-auto mb-3" />
                        <h4 className="text-sm font-semibold text-white">Parser Failure</h4>
                        <p className="text-xs text-white/50 mt-1 max-w-sm mx-auto leading-relaxed">
                          We were unable to execute the parsing engine on this file. It may be corrupt or encrypted. Try replacing the file.
                        </p>
                      </div>
                    ) : (
                      <div className="space-y-6">
                        <div>
                          <h4 className="text-sm font-semibold text-white mb-3">Extracted Profile Text Description</h4>
                          <p className="text-xs text-white/50 leading-relaxed max-h-[120px] overflow-y-auto pr-2 bg-white/[0.01] p-3 rounded-lg border border-white/5">
                            {resume.parsed_text?.slice(0, 500)}...
                          </p>
                        </div>

                        <div className="border-t border-white/5 pt-4">
                          <h4 className="text-sm font-semibold text-white mb-3">Identified Skill Keywords</h4>
                          <div className="flex flex-wrap gap-2">
                            {/* Dummy filter example based on BaseParser mappings */}
                            {resume.parsed_text?.toLowerCase().includes("python") && (
                              <span className="rounded-full bg-white/5 border border-white/10 px-3 py-1 text-xs text-white/80">Python</span>
                            )}
                            {resume.parsed_text?.toLowerCase().includes("react") && (
                              <span className="rounded-full bg-white/5 border border-white/10 px-3 py-1 text-xs text-white/80">React</span>
                            )}
                            {resume.parsed_text?.toLowerCase().includes("javascript") && (
                              <span className="rounded-full bg-white/5 border border-white/10 px-3 py-1 text-xs text-white/80">Javascript</span>
                            )}
                            {resume.parsed_text?.toLowerCase().includes("docker") && (
                              <span className="rounded-full bg-white/5 border border-white/10 px-3 py-1 text-xs text-white/80">Docker</span>
                            )}
                            {resume.parsed_text?.toLowerCase().includes("sql") && (
                              <span className="rounded-full bg-white/5 border border-white/10 px-3 py-1 text-xs text-white/80">SQL</span>
                            )}
                            {resume.parsed_text?.toLowerCase().includes("fastapi") && (
                              <span className="rounded-full bg-white/5 border border-white/10 px-3 py-1 text-xs text-white/80">FastAPI</span>
                            )}
                            <span className="rounded-full bg-white/5 border border-white/10 px-3 py-1 text-xs text-white/80">Selectable</span>
                          </div>
                        </div>

                        <div className="border-t border-white/5 pt-4">
                          <h4 className="text-sm font-semibold text-white mb-2">Education Section</h4>
                          <p className="text-xs text-white/50 leading-relaxed">
                            {resume.parsed_text?.toLowerCase().includes("university") || resume.parsed_text?.toLowerCase().includes("bachelor")
                              ? "Education sections detected. Check 'Raw Parsed Text' tab to view specific details."
                              : "No prominent education headings detected."}
                          </p>
                        </div>
                      </div>
                    )}
                  </Card>
                </TabsContent>

                {/* Raw Text View */}
                <TabsContent value="raw" className="mt-6">
                  <Card className="p-8">
                    {resume.parsed_text ? (
                      <div className="bg-black/40 border border-white/5 rounded-xl p-6 overflow-y-auto max-h-[500px] text-xs font-mono text-white/70 leading-relaxed whitespace-pre-wrap">
                        {resume.parsed_text}
                      </div>
                    ) : (
                      <p className="text-xs text-white/40 text-center py-10">No parsed text available.</p>
                    )}
                  </Card>
                </TabsContent>
              </Tabs>
            </div>
          </div>
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
                  Are you sure you want to delete this resume? This will permanently delete all metadata and physical files.
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

        {/* Toast Viewport */}
        <ToastViewport />
        {toasts.map(({ id, title, description, variant }) => (
          <Toast key={id} className={variant === "error" ? "border-red-500/20 bg-red-500/10 text-red-400" : "border-green-500/20 bg-green-500/10 text-green-400"}>
            <div className="grid gap-1">
              {title && <ToastTitle>{title}</ToastTitle>}
              {description && <ToastDescription>{description}</ToastDescription>}
            </div>
            <ToastClose onClick={() => removeToast(id)} />
          </Toast>
        ))}
      </div>
    </ToastProvider>
  );
}
