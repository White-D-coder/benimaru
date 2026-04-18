"use client";

import { useState } from "react";
import axios from "axios";
import { Upload, MessageSquare, BarChart3, ChevronRight, FileText, Loader2, Play } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

const API_BASE_URL = "http://localhost:8000";

export default function Home() {
  const [file, setFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [dataProfile, setDataProfile] = useState<any>(null);
  const [query, setQuery] = useState("");
  const [isProcessing, setIsProcessing] = useState(false);
  const [analysisResult, setAnalysisResult] = useState<any>(null);

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const uploadedFile = e.target.files?.[0];
    if (!uploadedFile) return;

    setFile(uploadedFile);
    setIsUploading(true);

    const formData = new FormData();
    formData.append("file", uploadedFile);

    try {
      const response = await axios.post(`${API_BASE_URL}/upload`, formData);
      setDataProfile(response.data.data_profile);
    } catch (error) {
      console.error("Upload failed", error);
      alert("Failed to upload dataset.");
    } finally {
      setIsUploading(false);
    }
  };

  const handleQuerySubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query || !file) return;

    setIsProcessing(true);
    setAnalysisResult(null);

    try {
      const response = await axios.post(`${API_BASE_URL}/query`, {
        filename: file.name,
        query: query,
      });
      setAnalysisResult(response.data);
    } catch (error) {
      console.error("Query failed", error);
      alert("Failed to process query.");
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <main className="min-h-screen bg-slate-950 text-slate-50 p-6 md:p-12">
      <div className="max-w-6xl mx-auto space-y-12">
        {/* Header */}
        <header className="space-y-4">
          <motion.div 
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-blue-500/10 border border-blue-500/20 text-blue-400 text-sm font-medium"
          >
            <BarChart3 size={14} />
            <span>AI-Powered Intelligence</span>
          </motion.div>
          <motion.h1 
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="text-4xl md:text-6xl font-bold tracking-tight"
          >
            Data Analyst <span className="text-blue-500">Assistant</span>
          </motion.h1>
          <motion.p 
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="text-slate-400 text-lg max-w-2xl"
          >
            Upload your dataset and ask any question. Get instant code, charts, and human-readable insights.
          </motion.p>
        </header>

        <section className="grid grid-cols-1 lg:grid-cols-12 gap-8">
          {/* Left Column: Upload & Profile */}
          <div className="lg:col-span-4 space-y-6">
            {!dataProfile ? (
              <motion.div 
                whileHover={{ scale: 1.01 }}
                className="relative group cursor-pointer"
              >
                <input
                  type="file"
                  onChange={handleFileUpload}
                  className="absolute inset-0 opacity-0 cursor-pointer z-10"
                  accept=".csv,.xlsx,.xls"
                />
                <div className="p-8 rounded-2xl border-2 border-dashed border-slate-800 group-hover:border-blue-500/50 bg-slate-900/50 transition-all text-center space-y-4">
                  <div className="w-12 h-12 rounded-xl bg-slate-800 flex items-center justify-center mx-auto group-hover:bg-blue-500/20 group-hover:text-blue-400 transition-colors">
                    {isUploading ? <Loader2 className="animate-spin" /> : <Upload />}
                  </div>
                  <div>
                    <p className="font-medium">Drop your dataset here</p>
                    <p className="text-sm text-slate-500">CSV or Excel up to 50MB</p>
                  </div>
                </div>
              </motion.div>
            ) : (
              <motion.div 
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                className="p-6 rounded-2xl border border-slate-800 bg-slate-900/50 space-y-4"
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <div className="p-2 rounded-lg bg-emerald-500/10 text-emerald-500">
                      <FileText size={18} />
                    </div>
                    <div>
                      <p className="font-medium text-sm truncate max-w-[150px]">{file?.name}</p>
                      <p className="text-xs text-slate-500">{dataProfile.row_count} rows • {dataProfile.column_count} columns</p>
                    </div>
                  </div>
                  <button 
                    onClick={() => setDataProfile(null)}
                    className="text-xs text-slate-500 hover:text-slate-300 transition-colors"
                  >
                    Change
                  </button>
                </div>
                
                <div className="space-y-2">
                  <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Available Columns</p>
                  <div className="flex flex-wrap gap-2">
                    {dataProfile.columns.map((col: any) => (
                      <span key={col.name} className="px-2 py-1 rounded bg-slate-800 text-[10px] text-slate-300 border border-slate-700">
                        {col.name}
                      </span>
                    ))}
                  </div>
                </div>
              </motion.div>
            )}
          </div>

          {/* Right Column: Chat & Analysis */}
          <div className="lg:col-span-8 space-y-6">
            <div className={`p-6 rounded-2xl border border-slate-800 bg-slate-900/50 min-h-[400px] flex flex-col ${!dataProfile && 'opacity-50 pointer-events-none'}`}>
              <div className="flex-1 space-y-8 overflow-y-auto pb-4">
                {analysisResult ? (
                  <motion.div 
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="space-y-6"
                  >
                    {/* Explanation */}
                    <div className="flex items-start space-x-4">
                      <div className="w-8 h-8 rounded-full bg-blue-600 flex items-center justify-center flex-shrink-0">
                        <MessageSquare size={16} />
                      </div>
                      <div className="space-y-2">
                        <p className="text-slate-200 leading-relaxed">{analysisResult.explanation}</p>
                      </div>
                    </div>

                    {/* Chart */}
                    {analysisResult.chart && (
                      <div className="ml-12 p-4 rounded-xl border border-slate-800 bg-black/40">
                        <img src={analysisResult.chart} alt="Analysis Chart" className="w-full h-auto rounded-lg" />
                      </div>
                    )}

                    {/* Data Table Preview */}
                    {analysisResult.data && (
                      <div className="ml-12 overflow-x-auto rounded-xl border border-slate-800">
                        <table className="w-full text-left text-sm">
                          <thead className="bg-slate-800/50 text-slate-400">
                            <tr>
                              {Object.keys(analysisResult.data[0]).map((key) => (
                                <th key={key} className="px-4 py-2 font-medium">{key}</th>
                              ))}
                            </tr>
                          </thead>
                          <tbody className="divide-y divide-slate-800">
                            {analysisResult.data.map((row: any, i: number) => (
                              <tr key={i} className="hover:bg-slate-800/20 transition-colors">
                                {Object.values(row).map((val: any, j: number) => (
                                  <th key={j} className="px-4 py-2 font-normal text-slate-300">{String(val)}</th>
                                ))}
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    )}
                  </motion.div>
                ) : (
                  <div className="h-full flex flex-col items-center justify-center text-slate-500 space-y-4">
                    <div className="p-4 rounded-full bg-slate-900 border border-slate-800">
                      <MessageSquare size={32} />
                    </div>
                    <p className="text-center">
                      {dataProfile 
                        ? "Dataset ready. Ask me anything about your data!" 
                        : "Upload a dataset to start the conversation."}
                    </p>
                  </div>
                )}
              </div>

              {/* Chat Input */}
              <form onSubmit={handleQuerySubmit} className="relative group">
                <input
                  type="text"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  placeholder="Ask a question (e.g., 'What are the top 5 sales by region?')"
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl py-4 pl-4 pr-16 focus:outline-none focus:border-blue-500 transition-all placeholder:text-slate-600 shadow-2xl"
                />
                <button
                  type="submit"
                  disabled={isProcessing || !query}
                  className="absolute right-2 top-2 h-10 w-10 rounded-lg bg-blue-600 flex items-center justify-center text-white disabled:bg-slate-800 disabled:text-slate-600 transition-all"
                >
                  {isProcessing ? <Loader2 className="animate-spin" size={18} /> : <Play size={18} />}
                </button>
              </form>
            </div>
          </div>
        </section>
      </div>
    </main>
  );
}
