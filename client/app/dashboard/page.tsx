"use client";

import React, { useState, useEffect } from "react";
import {
  Shield,
  Activity,
  AlertCircle,
  CheckCircle2,
  Clock,
  TrendingUp,
  Zap,
  Download,
  Play,
  RefreshCw,
  ExternalLink,
} from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import AdherenceGrid from "@/components/AdherenceGrid";
import ComplianceDetailPanel from "@/components/ComplianceDetailPanel";
import LogsPanel from "@/components/LogsPanel";
import SlackPanel from "@/components/SlackPanel";
import { listAnalyses, checkHealth, downloadReport } from "@/lib/api";
import { AGENTS_WS } from "@/lib/constants";
import { useAnalysisLogs, type LogEntry } from "@/lib/hooks/useAnalysisLogs";

interface Analysis {
  analysis_id: string;
  status: string;
  playbook_steps?: Array<{
    step_id: string;
    phase: string;
    description: string;
  }>;
  adherence_checks?: Array<{
    step_id: string;
    adherence_level: string;
    evidence: string[];
    gaps: string[];
    recommendations: string[];
  }>;
  compliance_mappings?: Array<{
    framework: string;
    control_id: string;
    control_title: string;
    adherence_level: string;
    supporting_evidence: string[];
  }>;
  overall_score?: number;
  created_at?: string;
  slack_thread_id?: string;
  slack_messages?: Array<{
    user: string;
    username?: string;
    ts: string;
    text: string;
    reactions?: string[];
  }>;
}

type TabType = "compliance" | "logs" | "slack";

const DashboardPage = () => {
  const [mounted, setMounted] = useState(false);
  const [analyses, setAnalyses] = useState<Analysis[]>([]);
  const [selectedAnalysis, setSelectedAnalysis] = useState<Analysis | null>(
    null,
  );
  const [selectedStep, setSelectedStep] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isOnline, setIsOnline] = useState(false);
  const [activeTab, setActiveTab] = useState<TabType>("compliance");

  // Log management
  const {
    logs,
    filteredLogs,
    filteredLevel,
    setFilteredLevel,
    addLog,
    clearLogs,
    logsEndRef,
    containerRef,
  } = useAnalysisLogs();

  // Slack data state
  const [slackMessages, setSlackMessages] = useState<
    Analysis["slack_messages"]
  >([]);
  const [slackLoading, setSlackLoading] = useState(false);
  const [slackParticipantCount, setSlackParticipantCount] = useState(0);

  // Hydration fix
  useEffect(() => {
    setMounted(true);
  }, []);

  // Health check
  useEffect(() => {
    if (!mounted) return;

    const checkApiHealth = async () => {
      const healthy = await checkHealth();
      setIsOnline(healthy);
    };

    checkApiHealth();
    const interval = setInterval(checkApiHealth, 5000);
    return () => clearInterval(interval);
  }, [mounted]);

  // Fetch analyses
  const fetchAnalyses = async () => {
    if (!mounted) return;
    setLoading(true);
    setError(null);

    try {
      const data = await listAnalyses(10, 0);
      const analysisArray = Array.isArray(data) ? data : data?.data || [];
      setAnalyses(analysisArray);
      if (analysisArray.length > 0) {
        setSelectedAnalysis(analysisArray[0]);
      }
    } catch (err) {
      setError((err as Error).message);
      setAnalyses([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (mounted) {
      fetchAnalyses();
      const interval = setInterval(fetchAnalyses, 10000);
      return () => clearInterval(interval);
    }
  }, [mounted]);

  // Download report handler
  const handleDownloadReport = async () => {
    if (!selectedAnalysis) return;
    try {
      const blob = await downloadReport(selectedAnalysis.analysis_id, "pdf");
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `analysis-${selectedAnalysis.analysis_id}.pdf`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err) {
      console.error("Failed to download report:", err);
      alert("Failed to download report");
    }
  };

  // WebSocket connection for real-time updates
  useEffect(() => {
    if (!mounted || !selectedAnalysis) return;

    const clientId = `client-${Math.random().toString(36).substr(2, 9)}`;
    const ws = new WebSocket(`${AGENTS_WS}/ws/${clientId}`);

    const handleMessage = (event: MessageEvent) => {
      try {
        const message = JSON.parse(event.data);

        // Handle log messages
        if (
          message.type === "log" &&
          message.analysis_id === selectedAnalysis.analysis_id
        ) {
          addLog(message as LogEntry);
        }

        // Handle Slack messages
        if (
          message.type === "slack_messages" &&
          message.analysis_id === selectedAnalysis.analysis_id
        ) {
          setSlackMessages(message.messages || []);
          setSlackParticipantCount(message.participant_count || 0);
          setSlackLoading(false);
        }

        // Handle analysis updates
        if (message.analysis_id === selectedAnalysis.analysis_id) {
          setSelectedAnalysis((prev) =>
            prev
              ? {
                  ...prev,
                  status: message.status || prev.status,
                  adherence_checks:
                    message.adherence_checks || prev.adherence_checks,
                  compliance_mappings:
                    message.compliance_mappings || prev.compliance_mappings,
                  overall_score: message.overall_score || prev.overall_score,
                }
              : null,
          );
        }
      } catch (e) {
        console.error("WS parse error:", e);
      }
    };

    ws.onopen = () => {
      console.log("WS connected");
      // Subscribe to analysis updates and logs
      ws.send(
        JSON.stringify({
          type: "subscribe",
          analysis_id: selectedAnalysis.analysis_id,
        }),
      );
      // Request Slack messages
      setSlackLoading(true);
      ws.send(
        JSON.stringify({
          type: "get_slack_messages",
          analysis_id: selectedAnalysis.analysis_id,
        }),
      );
    };

    ws.onmessage = handleMessage;
    ws.onerror = (err) => console.error("WS error:", err);
    ws.onclose = () => console.log("WS closed");

    return () => {
      ws.send(JSON.stringify({ type: "unsubscribe" }));
      ws.close();
    };
  }, [mounted, selectedAnalysis?.analysis_id, addLog]);

  // Clear logs when changing analysis
  useEffect(() => {
    if (selectedAnalysis?.analysis_id) {
      clearLogs();
      setSlackMessages([]);
      setSlackParticipantCount(0);
    }
  }, [selectedAnalysis?.analysis_id, clearLogs]);

  if (!mounted) return null;

  // Transform adherence checks to grid format
  const adherenceSteps =
    selectedAnalysis?.adherence_checks?.map((check, i) => ({
      id: i + 1,
      label: selectedAnalysis.playbook_steps?.[i]?.phase || `Step ${i + 1}`,
      status:
        (
          {
            full: "FOLLOWED",
            partial: "DELAYED",
            none: "MISSED",
          } as Record<string, "FOLLOWED" | "DELAYED" | "MISSED">
        )[check.adherence_level] || "PENDING",
      step_id: check.step_id,
      evidence: check.evidence,
      gaps: check.gaps,
      recommendations: check.recommendations,
    })) || [];

  // Find selected step by id
  const selectedStepData =
    selectedStep && adherenceSteps.find((s) => s.id === selectedStep.id);

  const complianceFrameworks =
    selectedAnalysis?.compliance_mappings?.reduce(
      (acc, mapping) => {
        if (!acc[mapping.framework]) {
          acc[mapping.framework] = {
            controls: [],
            adherenceLevel: mapping.adherence_level,
          };
        }
        acc[mapping.framework].controls.push({
          id: mapping.control_id,
          title: mapping.control_title,
          adherenceLevel: mapping.adherence_level,
          evidence: mapping.supporting_evidence,
        });
        return acc;
      },
      {} as Record<
        string,
        {
          controls: Array<{
            id: string;
            title: string;
            adherenceLevel: string;
            evidence: string[];
          }>;
          adherenceLevel: string;
        }
      >,
    ) || {};

  return (
    <div className="relative w-full min-h-screen bg-[#09090b] overflow-hidden py-16">
      {/* Background */}
      <div className="absolute inset-0 bg-[linear-gradient(to_right,#ffffff05_1px,transparent_1px),linear-gradient(to_bottom,#ffffff05_1px,transparent_1px)] bg-size-[4rem_4rem] opacity-40 pointer-events-none" />
      <div className="absolute top-20 right-0 w-96 h-96 bg-blue-600/10 blur-3xl rounded-full opacity-40 pointer-events-none" />
      <div className="absolute -bottom-20 left-1/4 w-72 h-72 bg-indigo-600/10 blur-3xl rounded-full opacity-30 pointer-events-none" />

      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8 flex items-center justify-between">
          <div>
            <div className="flex items-center gap-3 mb-4">
              <Shield className="h-8 w-8 text-blue-400" />
              <h1 className="text-3xl sm:text-4xl lg:text-5xl font-bold text-white">
                Incident Analysis Dashboard
              </h1>
            </div>
            <p className="text-neutral-400">
              Real-time compliance monitoring with AI-powered analysis
            </p>
          </div>

          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
              <div
                className={`h-3 w-3 rounded-full ${isOnline ? "bg-emerald-500" : "bg-rose-500"} animate-pulse`}
              />
              <span
                className={
                  isOnline
                    ? "text-emerald-400 text-sm"
                    : "text-rose-400 text-sm"
                }
              >
                {isOnline ? "Live" : "Offline"}
              </span>
            </div>
            <button
              onClick={fetchAnalyses}
              disabled={loading}
              className="p-2 rounded-lg bg-white/5 hover:bg-white/10 transition disabled:opacity-50"
            >
              <RefreshCw
                className={`h-5 w-5 text-white ${loading ? "animate-spin" : ""}`}
              />
            </button>
          </div>
        </div>

        {/* Error State */}
        {error && (
          <div className="mb-6 p-4 bg-rose-500/10 border border-rose-500/30 rounded-lg text-rose-400">
            {error}
          </div>
        )}

        {loading && !analyses.length ? (
          <div className="flex items-center justify-center py-12">
            <div className="animate-spin">
              <Activity className="h-8 w-8 text-blue-400" />
            </div>
          </div>
        ) : analyses.length === 0 ? (
          <div className="text-center py-12">
            <AlertCircle className="h-12 w-12 text-slate-500 mx-auto mb-4" />
            <p className="text-slate-400">
              No analyses found. Start a new analysis to begin.
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
            {/* Analyses List */}
            <div className="lg:col-span-1">
              <div className="rounded-lg border border-white/10 bg-white/5 p-4 space-y-2 max-h-[600px] overflow-y-auto">
                <h2 className="text-sm font-semibold text-white mb-4">
                  Analyses ({analyses.length})
                </h2>
                {analyses.map((analysis) => (
                  <button
                    key={analysis.analysis_id}
                    onClick={() => {
                      setSelectedAnalysis(analysis);
                      setSelectedStep(null);
                      setActiveTab("compliance");
                    }}
                    className={`w-full p-3 text-left rounded-lg border transition-all ${
                      selectedAnalysis?.analysis_id === analysis.analysis_id
                        ? "border-blue-500/50 bg-blue-500/10"
                        : "border-white/10 hover:border-white/20 bg-white/5"
                    }`}
                  >
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-xs font-mono text-blue-400">
                        {analysis.analysis_id.slice(0, 8)}...
                      </span>
                      <span
                        className={`text-[10px] font-bold ${
                          analysis.status === "completed"
                            ? "text-emerald-400"
                            : analysis.status === "in_progress"
                              ? "text-amber-400"
                              : "text-slate-400"
                        }`}
                      >
                        {analysis.status}
                      </span>
                    </div>
                    <p className="text-[11px] text-slate-400">
                      {new Date(analysis.created_at || "").toLocaleDateString()}
                    </p>
                  </button>
                ))}
              </div>
            </div>

            {/* Main Analysis View */}
            {selectedAnalysis && (
              <div className="lg:col-span-3 space-y-6">
                {/* Tabs */}
                <div className="flex gap-2">
                  {(["compliance", "logs", "slack"] as const).map((tab) => (
                    <button
                      key={tab}
                      onClick={() => setActiveTab(tab)}
                      className={`px-4 py-2 rounded-lg font-medium transition ${
                        activeTab === tab
                          ? "bg-blue-500/30 border border-blue-500/50 text-blue-300"
                          : "bg-white/5 border border-white/10 text-gray-400 hover:bg-white/10"
                      }`}
                    >
                      {tab.charAt(0).toUpperCase() + tab.slice(1)}
                    </button>
                  ))}
                </div>

                {/* Tab Content */}
                {activeTab === "compliance" && (
                  <div className="space-y-6">
                    {/* Score Card */}
                    <motion.div
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      className="rounded-lg border border-white/10 bg-white/5 p-6"
                    >
                      <div className="flex items-center justify-between mb-4">
                        <h2 className="text-lg font-semibold text-white flex items-center gap-2">
                          <TrendingUp className="h-5 w-5 text-blue-400" />
                          Compliance Score
                        </h2>
                        <div className="flex items-center gap-4">
                          {selectedAnalysis.overall_score && (
                            <div className="text-4xl font-bold text-emerald-400">
                              {(selectedAnalysis.overall_score * 100).toFixed(
                                0,
                              )}
                              %
                            </div>
                          )}
                          <button
                            onClick={handleDownloadReport}
                            disabled={selectedAnalysis.status !== "completed"}
                            className="p-2 rounded-lg bg-blue-500/20 hover:bg-blue-500/30 disabled:opacity-50 transition"
                            title="Download PDF Report"
                          >
                            <Download className="h-5 w-5 text-blue-400" />
                          </button>
                        </div>
                      </div>
                      <div className="w-full bg-white/10 rounded-full h-2 overflow-hidden">
                        <div
                          className="h-full bg-gradient-to-r from-emerald-500 to-blue-500 transition-all"
                          style={{
                            width: `${(selectedAnalysis.overall_score || 0) * 100}%`,
                          }}
                        />
                      </div>
                    </motion.div>

                    {/* Adherence Steps */}
                    {adherenceSteps.length > 0 && (
                      <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.1 }}
                        className="rounded-lg border border-white/10 bg-white/5 p-6"
                      >
                        <h2 className="text-lg font-semibold text-white mb-4">
                          Adherence Tracking
                        </h2>
                        <AdherenceGrid
                          steps={adherenceSteps}
                          selectedStepId={selectedStep?.id}
                          onStepClick={setSelectedStep}
                        />
                      </motion.div>
                    )}

                    {/* Compliance Frameworks */}
                    {Object.entries(complianceFrameworks).length > 0 && (
                      <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.2 }}
                        className="rounded-lg border border-white/10 bg-white/5 p-6"
                      >
                        <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                          <Shield className="h-5 w-5 text-blue-400" />
                          Compliance Frameworks
                        </h2>
                        <div className="space-y-4">
                          {Object.entries(complianceFrameworks).map(
                            ([framework, data]) => (
                              <div
                                key={framework}
                                className="border border-white/10 rounded-lg p-4"
                              >
                                <div className="flex items-center justify-between mb-3">
                                  <h3 className="font-semibold text-white capitalize">
                                    {framework.replace(/_/g, " ")}
                                  </h3>
                                  <span
                                    className={`text-sm font-bold px-3 py-1 rounded ${
                                      data.adherenceLevel === "full"
                                        ? "bg-emerald-500/20 text-emerald-400"
                                        : data.adherenceLevel === "partial"
                                          ? "bg-amber-500/20 text-amber-400"
                                          : "bg-rose-500/20 text-rose-400"
                                    }`}
                                  >
                                    {data.adherenceLevel.toUpperCase()}
                                  </span>
                                </div>
                                <div className="space-y-2">
                                  {data.controls.slice(0, 3).map((control) => (
                                    <div
                                      key={control.id}
                                      className="text-sm p-2 bg-white/5 rounded"
                                    >
                                      <div className="flex items-center justify-between mb-1">
                                        <span className="font-mono text-cyan-400 text-xs">
                                          {control.id}
                                        </span>
                                        <CheckCircle2 className="h-4 w-4 text-emerald-400" />
                                      </div>
                                      <p className="text-slate-300 text-xs">
                                        {control.title}
                                      </p>
                                    </div>
                                  ))}
                                  {data.controls.length > 3 && (
                                    <p className="text-xs text-slate-500 pt-2">
                                      +{data.controls.length - 3} more controls
                                    </p>
                                  )}
                                </div>
                              </div>
                            ),
                          )}
                        </div>
                      </motion.div>
                    )}
                  </div>
                )}

                {activeTab === "logs" && (
                  <LogsPanel
                    logs={filteredLogs}
                    filteredLevel={filteredLevel}
                    onFilterChange={setFilteredLevel}
                    onClear={clearLogs}
                    containerRef={containerRef}
                    logsEndRef={logsEndRef}
                  />
                )}

                {activeTab === "slack" && (
                  <SlackPanel
                    messages={slackMessages}
                    participantCount={slackParticipantCount}
                    threadId={selectedAnalysis.slack_thread_id}
                    loading={slackLoading}
                  />
                )}
              </div>
            )}
          </div>
        )}
      </div>

      {/* Detail Panel */}
      <AnimatePresence>
        {selectedStepData && (
          <ComplianceDetailPanel
            step={selectedStepData}
            onClose={() => setSelectedStep(null)}
          />
        )}
      </AnimatePresence>
    </div>
  );
};

export default DashboardPage;
