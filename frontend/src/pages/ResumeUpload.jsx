import React, { useState, useRef } from "react";
import { Link, useNavigate } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import { Upload, FileText, CheckCircle2, AlertTriangle, ArrowLeft, Loader2, Sparkles } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card } from "@/components/ui/card";
import resumeService from "@/services/resumeService";

const MAX_SIZE = 10 * 1024 * 1024; // 10MB
const ALLOWED_EXTS = ["pdf", "docx"];

export default function ResumeUpload() {
  const navigate = useNavigate();
  const fileInputRef = useRef(null);
  
  const [file, setFile] = useState(null);
  const [title, setTitle] = useState("");
  const [dragActive, setDragActive] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState("");
  const [successMsg, setSuccessMsg] = useState("");

  const validateFile = (selectedFile) => {
    setError("");
    setSuccessMsg("");
    
    if (!selectedFile) return false;

    const ext = selectedFile.name.split(".").pop().toLowerCase();
    if (!ALLOWED_EXTS.includes(ext)) {
      setError("Unsupported file format. Only PDF and DOCX files are allowed.");
      return false;
    }

    if (selectedFile.size > MAX_SIZE) {
      setError("File exceeds the 10 MB limit.");
      return false;
    }

    return true;
  };

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const droppedFile = e.dataTransfer.files[0];
      if (validateFile(droppedFile)) {
        setFile(droppedFile);
        setTitle(droppedFile.name.replace(/\.[^/.]+$/, ""));
      }
    }
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      const selectedFile = e.target.files[0];
      if (validateFile(selectedFile)) {
        setFile(selectedFile);
        setTitle(selectedFile.name.replace(/\.[^/.]+$/, ""));
      }
    }
  };

  const onButtonClick = () => {
    fileInputRef.current.click();
  };

  const handleUploadSubmit = async (e) => {
    e.preventDefault();
    if (!file) return;

    setUploading(true);
    setError("");
    setProgress(10); // Initial fake progress

    // Simulate progress bar increase
    const interval = setInterval(() => {
      setProgress((prev) => (prev < 80 ? prev + 15 : prev));
    }, 150);

    try {
      const response = await resumeService.uploadResume(file, title);
      clearInterval(interval);
      setProgress(100);
      setSuccessMsg("Resume uploaded and parsed successfully!");
      
      // Automatically redirect to resume details page after 1.5 seconds
      setTimeout(() => {
        navigate(`/resumes/${response.data.id}`);
      }, 1500);
    } catch (err) {
      clearInterval(interval);
      setProgress(0);
      const msg = err.response?.data?.message || "Upload failed. Please try again.";
      setError(msg);
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#050505] text-white flex flex-col justify-between">
      <div className="h-24" /> {/* Header spacer */}
      
      <main className="flex-grow mx-auto w-full max-w-4xl px-4 py-8 sm:px-6 lg:px-8">
        <div className="mb-8 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Link to="/profile" className="p-2 rounded-full hover:bg-white/5 transition-colors text-white/55 hover:text-white">
              <ArrowLeft className="h-5 w-5" />
            </Link>
            <div>
              <h1 className="text-3xl font-semibold tracking-tight text-white flex items-center gap-2">
                Upload Resume
                <Sparkles className="h-5 w-5 text-white/70" />
              </h1>
              <p className="mt-1.5 text-sm text-white/55">
                Support PDF and DOCX formats up to 10 MB.
              </p>
            </div>
          </div>
          <Link to="/resumes">
            <Button variant="outline" className="rounded-full text-xs font-semibold">
              View All Resumes
            </Button>
          </Link>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {/* Main Upload Dropzone */}
          <div className="md:col-span-2 space-y-6">
            <Card className="p-8 relative overflow-hidden">
              <form onSubmit={handleUploadSubmit} className="space-y-6">
                <div
                  onDragEnter={handleDrag}
                  onDragOver={handleDrag}
                  onDragLeave={handleDrag}
                  onDrop={handleDrop}
                  className={`relative flex flex-col items-center justify-center border-2 border-dashed rounded-xl p-12 transition-all duration-300 min-h-[300px] text-center cursor-pointer ${
                    dragActive 
                      ? "border-white bg-white/5 scale-[0.99]" 
                      : "border-white/10 bg-white/[0.01] hover:border-white/20 hover:bg-white/[0.02]"
                  }`}
                  onClick={onButtonClick}
                >
                  <input
                    ref={fileInputRef}
                    type="file"
                    className="hidden"
                    onChange={handleFileChange}
                    accept=".pdf,.docx"
                    disabled={uploading}
                  />

                  {file ? (
                    <div className="space-y-4">
                      <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-xl bg-white/5 border border-white/10 text-white">
                        <FileText className="h-8 w-8" />
                      </div>
                      <div>
                        <p className="font-semibold text-white truncate max-w-xs sm:max-w-md">
                          {file.name}
                        </p>
                        <p className="text-xs text-white/40 mt-1">
                          {(file.size / (1024 * 1024)).toFixed(2)} MB
                        </p>
                      </div>
                    </div>
                  ) : (
                    <div className="space-y-4">
                      <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-xl bg-white/[0.02] border border-white/5 text-white/50">
                        <Upload className="h-8 w-8" />
                      </div>
                      <div>
                        <p className="font-semibold text-white text-base">
                          Drag and drop your file here
                        </p>
                        <p className="text-xs text-white/40 mt-2">
                          or click to browse from files
                        </p>
                      </div>
                    </div>
                  )}

                  {/* Drag overlays */}
                  {dragActive && (
                    <div className="absolute inset-0 rounded-xl bg-white/5 backdrop-blur-[2px] pointer-events-none flex items-center justify-center">
                      <p className="text-sm font-semibold text-white">Drop to upload your resume</p>
                    </div>
                  )}
                </div>

                {file && (
                  <motion.div
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="space-y-4"
                  >
                    <div className="space-y-2">
                      <label htmlFor="resume-title" className="text-sm font-medium text-white/75">
                        Resume Title
                      </label>
                      <Input
                        id="resume-title"
                        type="text"
                        value={title}
                        onChange={(e) => setTitle(e.target.value)}
                        placeholder="e.g. Senior Software Engineer Resume"
                        disabled={uploading}
                        className="bg-black/40 border-white/10 focus-visible:ring-white/30"
                      />
                    </div>

                    <div className="flex gap-4">
                      <Button
                        type="submit"
                        disabled={uploading || !file}
                        className="flex-grow rounded-full font-semibold"
                        isLoading={uploading}
                      >
                        Upload & Parse Resume
                      </Button>
                      <Button
                        type="button"
                        variant="outline"
                        disabled={uploading}
                        onClick={() => {
                          setFile(null);
                          setTitle("");
                        }}
                        className="rounded-full font-semibold"
                      >
                        Clear
                      </Button>
                    </div>
                  </motion.div>
                )}
              </form>
            </Card>
          </div>

          {/* Guidelines Sidebar */}
          <div className="md:col-span-1 space-y-6">
            {/* Status alerts */}
            <AnimatePresence mode="wait">
              {error && (
                <motion.div
                  initial={{ opacity: 0, y: -10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -10 }}
                  className="flex items-start gap-3 rounded-xl border border-red-500/20 bg-red-500/5 p-4 text-red-400"
                >
                  <AlertTriangle className="h-5 w-5 shrink-0 mt-0.5" />
                  <div>
                    <h4 className="text-sm font-semibold">Upload failed</h4>
                    <p className="text-xs mt-1 leading-relaxed opacity-85">{error}</p>
                  </div>
                </motion.div>
              )}

              {successMsg && (
                <motion.div
                  initial={{ opacity: 0, y: -10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -10 }}
                  className="flex items-start gap-3 rounded-xl border border-green-500/20 bg-green-500/5 p-4 text-green-400"
                >
                  <CheckCircle2 className="h-5 w-5 shrink-0 mt-0.5" />
                  <div>
                    <h4 className="text-sm font-semibold">Success</h4>
                    <p className="text-xs mt-1 leading-relaxed opacity-85">{successMsg}</p>
                    {progress === 100 && (
                      <p className="text-[10px] mt-2 flex items-center gap-1.5 opacity-60">
                        <Loader2 className="h-3 w-3 animate-spin" />
                        Redirecting to details...
                      </p>
                    )}
                  </div>
                </motion.div>
              )}
            </AnimatePresence>

            {uploading && (
              <Card className="p-6 space-y-4">
                <h4 className="text-sm font-semibold text-white flex items-center justify-between">
                  <span>Uploading & Parsing</span>
                  <span className="text-xs text-white/50">{progress}%</span>
                </h4>
                <div className="h-1.5 w-full bg-white/5 rounded-full overflow-hidden">
                  <div 
                    className="h-full bg-white rounded-full transition-all duration-300"
                    style={{ width: `${progress}%` }}
                  />
                </div>
                <p className="text-xs text-white/40 leading-relaxed">
                  We are securely uploading your file and executing the parsing engine to map raw profile sections. This may take a few seconds.
                </p>
              </Card>
            )}

            <Card className="p-6 space-y-4">
              <h4 className="text-sm font-semibold text-white">Guidelines</h4>
              <ul className="space-y-2.5 text-xs text-white/50 leading-relaxed list-disc list-inside">
                <li>Make sure the text inside the file is selectable (not an scanned image PDF).</li>
                <li>Verify your contact details (email and phone) are present on the header.</li>
                <li>State your work history, skills, and certifications clearly.</li>
                <li>Files exceeding 10 MB limit will be rejected.</li>
              </ul>
            </Card>
          </div>
        </div>
      </main>
    </div>
  );
}
