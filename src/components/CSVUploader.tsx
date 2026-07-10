import { useState, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Upload, FileText, CheckCircle, AlertCircle, X, Database, Shield, Info, Copy, Check, ChevronDown, FileCode } from "lucide-react";

interface CSVUploaderProps {
  onDataLoaded: (data: any) => void;
  uploadRef: React.RefObject<HTMLDivElement>;
}

const REQUIRED_COLUMNS = [
  "date",
  "model_decision",
  "human_decision",
  "confidence_note",
];

export const CSVUploader = ({ onDataLoaded, uploadRef }: CSVUploaderProps) => {
  const [isDragging, setIsDragging] = useState(false);
  const [uploadState, setUploadState] = useState<
    "idle" | "loading" | "success" | "error"
  >("idle");
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [fileName, setFileName] = useState<string | null>(null);
  const [isGuideOpen, setIsGuideOpen] = useState(false);
  const [copied, setCopied] = useState(false);

  const copyTemplate = () => {
    const csvString = `date,model_decision,human_decision,confidence_note,ground_truth,department
2024-01-01,shortlist,shortlist,Model seems accurate for this candidate,shortlist,Finance
2024-01-02,shortlist,reject,Overriding due to lack of real-world experience,reject,Finance
2024-01-03,reject,reject,AI correctly flagged missing qualifications,reject,HR`;

    navigator.clipboard.writeText(csvString).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    });
  };

  // ── Upload CSV → Backend ──
  const uploadToBackend = async (file: File) => {
    setUploadState("loading");
    setProgress(0);
    setError(null);
    setFileName(file.name);

    let current = 0;
    const interval = setInterval(() => {
      current += Math.random() * 12;
      setProgress(Math.min(current, 95));
    }, 120);

    try {
      const formData = new FormData();
      formData.append("file", file);

      // Use the environment variable if provided (for Vercel), otherwise fallback to local/relative
      const apiUrl = import.meta.env.VITE_API_URL 
        ? import.meta.env.VITE_API_URL
        : import.meta.env.DEV 
          ? "http://127.0.0.1:8000/analyze" 
          : "/analyze";

      const res = await fetch(apiUrl, {
        method: "POST",
        body: formData,
      });

      if (!res.ok) throw new Error("Backend error");

      const data = await res.json();

      clearInterval(interval);
      setProgress(100);
      setUploadState("success");

      setTimeout(() => {
        onDataLoaded(data);
      }, 600);
    } catch (err) {
      clearInterval(interval);
      setError("Failed to connect to backend. Is the server running?");
      setUploadState("error");
    }
  };

  // ── File Handling ──
  const handleFile = useCallback((file: File) => {
    if (!file.name.endsWith(".csv")) {
      setError("Please upload a CSV file");
      setUploadState("error");
      return;
    }
    uploadToBackend(file);
  }, []);

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setIsDragging(false);
      const file = e.dataTransfer.files[0];
      if (file) handleFile(file);
    },
    [handleFile]
  );

  const handleFileInput = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const file = e.target.files?.[0];
      if (file) handleFile(file);
    },
    [handleFile]
  );

  const reset = () => {
    setUploadState("idle");
    setProgress(0);
    setError(null);
    setFileName(null);
  };

  const loadDemoData = (withGroundTruth: boolean) => {
    let csvContent = "";
    if (withGroundTruth) {
      csvContent =
`date,model_decision,human_decision,confidence_note,ground_truth,department
2024-01-01,shortlist,shortlist,Model seems accurate for this candidate,shortlist,Finance
2024-01-02,shortlist,reject,Overriding due to lack of real-world experience,reject,Finance
2024-01-03,reject,reject,AI correctly flagged missing qualifications,reject,HR
2024-01-04,shortlist,shortlist,Trusting the system recommendation,shortlist,HR
2024-01-05,shortlist,reject,Model missed important context from resume,reject,Engineering
2024-01-06,reject,shortlist,Using human judgment over AI output,reject,Engineering
2024-01-07,shortlist,shortlist,Decision aligned with role expectations,shortlist,Finance
2024-01-08,reject,reject,Model recommendation seems reliable,reject,HR
2024-01-09,shortlist,reject,Not fully convinced by AI confidence,reject,Engineering
2024-01-10,shortlist,reject,Model seems wrong based on past hiring experience,shortlist,Finance
2024-01-11,reject,reject,Clear mismatch with job requirements,reject,Engineering
2024-01-12,shortlist,shortlist,AI assessment appears correct,shortlist,Operations
2024-01-13,shortlist,reject,Manual review required due to edge case,reject,Operations
2024-01-14,reject,shortlist,Context mismatch AI missed role nuances,shortlist,Finance
2024-01-15,shortlist,reject,Prefer human judgment in this situation,reject,Engineering
2024-01-16,shortlist,shortlist,Strong alignment between AI and human review,shortlist,HR
2024-01-17,reject,reject,Low confidence signals correctly identified,reject,Operations
2024-01-18,shortlist,reject,Recommendation not aligned with team needs,reject,Engineering
2024-01-19,reject,shortlist,AI confidence seems low here,shortlist,Finance
2024-01-20,shortlist,shortlist,Trusting model output for efficiency,shortlist,HR`;
    } else {
      csvContent =
`date,model_decision,human_decision,confidence_note,department
2024-01-01,shortlist,shortlist,Model seems accurate for this candidate,Finance
2024-01-02,shortlist,reject,Overriding due to lack of real-world experience,Finance
2024-01-03,reject,reject,AI correctly flagged missing qualifications,HR
2024-01-04,shortlist,shortlist,Trusting the system recommendation,HR
2024-01-05,shortlist,reject,Model missed important context from resume,Engineering
2024-01-06,reject,shortlist,Using human judgment over AI output,Engineering
2024-01-07,shortlist,shortlist,Decision aligned with role expectations,Finance
2024-01-08,reject,reject,Model recommendation seems reliable,HR
2024-01-09,shortlist,reject,Not fully convinced by AI confidence,Engineering
2024-01-10,shortlist,reject,Model seems wrong based on past hiring experience,Finance
2024-01-11,reject,reject,Clear mismatch with job requirements,Engineering
2024-01-12,shortlist,shortlist,AI assessment appears correct,Operations
2024-01-13,shortlist,reject,Manual review required due to edge case,Operations
2024-01-14,reject,shortlist,Context mismatch AI missed role nuances,Finance
2024-01-15,shortlist,reject,Prefer human judgment in this situation,Engineering
2024-01-16,shortlist,shortlist,Strong alignment between AI and human review,HR
2024-01-17,reject,reject,Low confidence signals correctly identified,Operations
2024-01-18,shortlist,reject,Recommendation not aligned with team needs,Engineering
2024-01-19,reject,shortlist,AI confidence seems low here,Finance
2024-01-20,shortlist,shortlist,Trusting model output for efficiency,HR`;
    }

    const filename = withGroundTruth ? "demo_ground_truth.csv" : "demo_standard.csv";
    const blob = new Blob([csvContent], { type: "text/csv" });
    const file = new File([blob], filename, { type: "text/csv" });
    uploadToBackend(file);
  };

  // ── UI ──
  return (
    <section ref={uploadRef} className="relative py-28 overflow-hidden">
      <div className="max-w-7xl mx-auto px-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-80px" }}
          transition={{ duration: 0.5 }}
          className="text-center mb-12"
        >
          <h2 className="font-display text-3xl md:text-4xl font-bold mb-4 text-white">
            Upload <span className="gradient-text">Your Data</span>
          </h2>
          <p className="text-white/40 text-base max-w-xl mx-auto leading-relaxed">
            Drop a CSV file or select a demo dataset to explore
          </p>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, scale: 0.98 }}
          whileInView={{ opacity: 1, scale: 1 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5, delay: 0.15 }}
          className="max-w-xl mx-auto"
        >
          {/* Drop Zone */}
          <div
            onDragOver={(e) => {
              e.preventDefault();
              setIsDragging(true);
            }}
            onDragLeave={() => setIsDragging(false)}
            onDrop={handleDrop}
            className={`
              relative rounded-xl transition-all duration-200
              ${isDragging
                ? "border-indigo-light/50 shadow-glow-indigo"
                : "hover:border-white/12"
              }
              ${uploadState === "success" ? "border-emerald/30" : ""}
              ${uploadState === "error" ? "border-red/30" : ""}
            `}
            style={{
              background: isDragging
                ? "linear-gradient(145deg, rgba(99,102,241,0.1), rgba(99,102,241,0.03))"
                : "linear-gradient(145deg, rgba(255,255,255,0.06), rgba(255,255,255,0.02))",
              border: `1px solid ${
                isDragging ? "rgba(99,102,241,0.4)" :
                uploadState === "success" ? "rgba(34,197,94,0.3)" :
                uploadState === "error" ? "rgba(239,68,68,0.3)" :
                "rgba(255,255,255,0.06)"
              }`,
              padding: "3rem 2rem",
            }}
          >
            <AnimatePresence mode="wait">
              {uploadState === "idle" && (
                <motion.div
                  key="idle"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  className="text-center"
                >
                  <div
                    className="inline-flex items-center justify-center w-14 h-14 rounded-xl mb-5"
                    style={{
                      background: "linear-gradient(135deg, rgba(99,102,241,0.15), rgba(124,58,237,0.08))",
                    }}
                  >
                    <Upload className="w-6 h-6 text-indigo-light" />
                  </div>
                  <h3 className="text-base font-semibold mb-1.5 text-white">
                    Drop your CSV file here
                  </h3>
                  <p className="text-sm text-white/35 mb-5">
                    or click to browse
                  </p>
                  <input
                    type="file"
                    accept=".csv"
                    onChange={handleFileInput}
                    className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                  />
                  <div className="flex flex-wrap justify-center gap-2">
                    {REQUIRED_COLUMNS.map((c) => (
                      <span
                        key={c}
                        className="text-[11px] px-2.5 py-1 rounded-md text-white/30 font-mono"
                        style={{ background: "rgba(255,255,255,0.04)" }}
                      >
                        {c}
                      </span>
                    ))}
                  </div>
                </motion.div>
              )}

              {uploadState === "loading" && (
                <motion.div
                  key="loading"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  className="text-center"
                >
                  <div
                    className="inline-flex items-center justify-center w-14 h-14 rounded-xl mb-5"
                    style={{
                      background: "linear-gradient(135deg, rgba(99,102,241,0.15), rgba(124,58,237,0.08))",
                    }}
                  >
                    <FileText className="w-6 h-6 text-indigo-light animate-pulse" />
                  </div>
                  <h3 className="text-base font-semibold mb-1 text-white">
                    {fileName}
                  </h3>
                  <p className="text-sm text-white/35 mb-5">
                    Running ensemble analysis…
                  </p>

                  {/* Progress bar */}
                  <div className="w-full h-1.5 bg-white/5 rounded-full overflow-hidden">
                    <motion.div
                      animate={{ width: `${progress}%` }}
                      className="h-full rounded-full"
                      style={{ background: "var(--gradient-brand)" }}
                    />
                  </div>
                  <p className="mt-2.5 text-xs text-white/30 font-mono tabular-nums">
                    {Math.round(progress)}%
                  </p>
                </motion.div>
              )}

              {uploadState === "success" && (
                <motion.div
                  key="success"
                  initial={{ opacity: 0, scale: 0.96 }}
                  animate={{ opacity: 1, scale: 1 }}
                  exit={{ opacity: 0 }}
                  className="text-center"
                >
                  <div className="inline-flex items-center justify-center w-14 h-14 rounded-xl mb-5"
                    style={{ background: "rgba(34,197,94,0.12)" }}
                  >
                    <CheckCircle className="w-6 h-6 text-emerald-bright" />
                  </div>
                  <h3 className="text-base font-semibold mb-1 text-emerald-bright">
                    Analysis Complete
                  </h3>
                  <p className="text-sm text-white/35">
                    Scroll down for your dashboard
                  </p>
                </motion.div>
              )}

              {uploadState === "error" && (
                <motion.div
                  key="error"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  className="text-center"
                >
                  <div className="inline-flex items-center justify-center w-14 h-14 rounded-xl mb-5"
                    style={{ background: "rgba(239,68,68,0.12)" }}
                  >
                    <AlertCircle className="w-6 h-6 text-red" />
                  </div>
                  <h3 className="text-base font-semibold mb-1 text-red">
                    Upload Failed
                  </h3>
                  <p className="text-sm text-white/35 mb-4">{error}</p>
                  <button
                    onClick={reset}
                    className="inline-flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium text-white/60 hover:text-white transition-colors"
                    style={{
                      background: "rgba(255,255,255,0.06)",
                      border: "1px solid rgba(255,255,255,0.08)",
                    }}
                  >
                    <X className="w-3.5 h-3.5" />
                    Try Again
                  </button>
                </motion.div>
              )}
            </AnimatePresence>
          </div>

          {/* Demo buttons */}
          {uploadState === "idle" && (
            <>
              <motion.div
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.3, duration: 0.4 }}
                className="flex flex-col sm:flex-row items-center justify-center gap-3 mt-6"
              >
                <button
                  onClick={() => loadDemoData(false)}
                  className="w-full sm:w-auto px-5 py-2.5 rounded-lg text-[13px] font-medium text-white/60 hover:text-white transition-all duration-200 flex items-center justify-center gap-2"
                  style={{
                    background: "linear-gradient(145deg, rgba(255,255,255,0.06), rgba(255,255,255,0.02))",
                    border: "1px solid rgba(255,255,255,0.06)",
                  }}
                >
                  <Database className="w-3.5 h-3.5" />
                  Standard Demo
                </button>
                <button
                  onClick={() => loadDemoData(true)}
                  className="w-full sm:w-auto px-5 py-2.5 rounded-lg text-[13px] font-medium text-white/60 hover:text-white transition-all duration-200 flex items-center justify-center gap-2"
                  style={{
                    background: "linear-gradient(145deg, rgba(255,255,255,0.06), rgba(255,255,255,0.02))",
                    border: "1px solid rgba(255,255,255,0.06)",
                  }}
                >
                  <Shield className="w-3.5 h-3.5" />
                  Ground Truth Demo
                </button>
              </motion.div>

              {/* CSV Format Guidelines Toggle */}
              <motion.div
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.4, duration: 0.4 }}
                className="mt-6"
              >
                <button
                  onClick={() => setIsGuideOpen(!isGuideOpen)}
                  className="w-full py-3 px-4 rounded-xl flex items-center justify-between text-sm font-medium transition-all duration-200"
                  style={{
                    background: "linear-gradient(145deg, rgba(255,255,255,0.03), rgba(255,255,255,0.01))",
                    border: "1px solid rgba(255,255,255,0.05)",
                  }}
                >
                  <div className="flex items-center gap-2 text-white/70 hover:text-white transition-colors">
                    <Info className="w-4 h-4 text-indigo-light" />
                    <span>CSV Data Format Guidelines</span>
                  </div>
                  <ChevronDown
                    className={`w-4 h-4 text-white/40 transition-transform duration-200 ${
                      isGuideOpen ? "rotate-180 text-indigo-light" : ""
                    }`}
                  />
                </button>

                <AnimatePresence>
                  {isGuideOpen && (
                    <motion.div
                      initial={{ height: 0, opacity: 0, marginTop: 0 }}
                      animate={{ height: "auto", opacity: 1, marginTop: 12 }}
                      exit={{ height: 0, opacity: 0, marginTop: 0 }}
                      transition={{ duration: 0.3, ease: "easeInOut" }}
                      className="overflow-hidden"
                    >
                      <div
                        className="rounded-xl p-5 text-left border border-white/5 space-y-5"
                        style={{
                          background: "linear-gradient(145deg, rgba(255,255,255,0.03), rgba(255,255,255,0.01))",
                          backdropFilter: "blur(10px)",
                        }}
                      >
                        <div>
                          <h4 className="text-sm font-semibold text-white/90 mb-3 flex items-center gap-2">
                            <span className="w-1.5 h-1.5 rounded-full bg-indigo-light" />
                            Required Columns
                          </h4>
                          <div className="grid grid-cols-1 gap-2.5">
                            {[
                              { name: "date", desc: "Timestamp or date of human-AI decision (e.g. YYYY-MM-DD)", type: "Date" },
                              { name: "model_decision", desc: "The recommendation/prediction generated by the AI model", type: "shortlist | reject" },
                              { name: "human_decision", desc: "The final decision made by the human operator", type: "shortlist | reject" },
                              { name: "confidence_note", desc: "Human feedback, comments or reasoning for the decision", type: "Text (String)" },
                            ].map((col) => (
                              <div key={col.name} className="flex flex-col sm:flex-row sm:items-center justify-between p-2.5 rounded-lg border border-white/5 bg-white/[0.01] gap-2">
                                <div className="flex items-center gap-2">
                                  <code className="text-xs text-indigo-light font-mono font-bold bg-indigo-light/10 px-2 py-0.5 rounded">
                                    {col.name}
                                  </code>
                                  <span className="text-[10px] text-white/40 font-mono">({col.type})</span>
                                </div>
                                <span className="text-xs text-white/50">{col.desc}</span>
                              </div>
                            ))}
                          </div>
                        </div>

                        <div>
                          <h4 className="text-sm font-semibold text-white/90 mb-3 flex items-center gap-2">
                            <span className="w-1.5 h-1.5 rounded-full bg-emerald-bright" />
                            Optional Columns (Unlocks Advanced Analytics)
                          </h4>
                          <div className="grid grid-cols-1 gap-2.5">
                            {[
                              { name: "ground_truth", desc: "The actual correct decision. Unlocks Accuracy, Justified/Unjustified Overrides, and Missed Overrides metrics.", type: "shortlist | reject" },
                              { name: "department", desc: "The department or team tag. Unlocks Fairness Monitor & Department-wise Trust Score analysis.", type: "Finance | HR | Engineering | ..." },
                            ].map((col) => (
                              <div key={col.name} className="flex flex-col sm:flex-row sm:items-center justify-between p-2.5 rounded-lg border border-white/5 bg-white/[0.01] gap-2">
                                <div className="flex items-center gap-2">
                                  <code className="text-xs text-emerald-bright font-mono font-bold bg-emerald-bright/10 px-2 py-0.5 rounded">
                                    {col.name}
                                  </code>
                                  <span className="text-[10px] text-white/40 font-mono">({col.type})</span>
                                </div>
                                <span className="text-xs text-white/50">{col.desc}</span>
                              </div>
                            ))}
                          </div>
                        </div>

                        <div>
                          <div className="flex items-center justify-between mb-2">
                            <h4 className="text-sm font-semibold text-white/90 flex items-center gap-2">
                              <FileCode className="w-4 h-4 text-indigo-light" />
                              Sample CSV Template
                            </h4>
                            <button
                              onClick={copyTemplate}
                              className="flex items-center gap-1.5 px-2.5 py-1 rounded text-xs font-medium text-white/60 hover:text-white border border-white/5 bg-white/[0.02] active:scale-95 transition-all duration-200"
                            >
                              {copied ? (
                                <>
                                  <Check className="w-3.5 h-3.5 text-emerald-bright" />
                                  <span className="text-emerald-bright font-medium">Copied!</span>
                                </>
                              ) : (
                                <>
                                  <Copy className="w-3.5 h-3.5" />
                                  <span>Copy CSV</span>
                                </>
                              )}
                            </button>
                          </div>
                          <pre className="text-xs text-white/60 font-mono p-3.5 rounded-lg bg-black/40 border border-white/5 overflow-x-auto whitespace-pre leading-relaxed select-all">
{`date,model_decision,human_decision,confidence_note,ground_truth,department
2024-01-01,shortlist,shortlist,Model seems accurate for this candidate,shortlist,Finance
2024-01-02,shortlist,reject,Overriding due to lack of real-world experience,reject,Finance
2024-01-03,reject,reject,AI correctly flagged missing qualifications,reject,HR`}
                          </pre>
                        </div>
                      </div>
                    </motion.div>
                  )}
                </AnimatePresence>
              </motion.div>
            </>
          )}
        </motion.div>
      </div>
    </section>
  );
};
