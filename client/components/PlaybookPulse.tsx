"use client";

import React, { useState, useEffect } from "react";
import { Shield, Activity, Terminal, Zap, AlertCircle } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { cn } from "@/lib/utils";
import AdherenceGrid from "./AdherenceGrid";
import ComplianceDetailPanel from "./ComplianceDetailPanel";
import { WS_URL } from "@/lib/constants";

const PlaybookPulse = () => {
  // --- ANIMATIONS ---
  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1,
        delayChildren: 0.2,
      },
    },
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: {
      opacity: 1,
      y: 0,
      transition: { duration: 0.5, ease: "easeOut" },
    },
  };
  // --- HYDRATION FIX START ---
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);
  // --- HYDRATION FIX END ---

  const [agents, setAgents] = useState([
    { name: "Playbook Parser", active: false },
    { name: "Incident Trail Agent", active: false },
    { name: "Adherence Checker", active: false },
  ]);

  const [selectedStepId, setSelectedStepId] = useState<number | null>(null);

  const [incidentSteps, setIncidentSteps] = useState(
    [
      "Ingestion",
      "Extraction",
      "Correlation",
      "Analysis",
      "Validation",
      "Triage",
      "Remediation",
    ].map((label, i) => ({
      label,
      status: (["FOLLOWED", "DELAYED", "MISSED", "PENDING"] as const)[i % 4],
      id: i + 1,
      timestamp: "14:20:05",
      summary: `Automated ${label.toLowerCase()} phase verification completed with system logs.`,
      pr_url:
        i === 2 || i === 4 ? "https://github.com/org/repo/pull/42" : undefined,
      pr_status: i === 2 ? "Open" : "Merged",
      incidentId: "INC-882",
    })),
  );

  const [isOffline, setIsOffline] = useState(false);

  // --- PERSISTENCE HOOK START ---
  useEffect(() => {
    if (!mounted) return;
    const cached = localStorage.getItem("pp_demo_state");
    if (cached) {
      try {
        const data = JSON.parse(cached);
        if (data.agents) setAgents(data.agents);
        if (data.steps) setIncidentSteps(data.steps);
      } catch (e) {
        console.error("Cache load failed", e);
      }
    }
  }, [mounted]);

  useEffect(() => {
    if (!mounted) return;
    localStorage.setItem(
      "pp_demo_state",
      JSON.stringify({
        agents,
        steps: incidentSteps,
        incidentId: "INC-882",
      }),
    );
  }, [agents, incidentSteps, mounted]);
  // --- PERSISTENCE HOOK END ---

  useEffect(() => {
    if (!mounted) return;
    const socket = new WebSocket(WS_URL);

    socket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.type === "AGENT_STATE") {
          setAgents((prev) =>
            prev.map((a) =>
              a.name === data.agent
                ? { ...a, active: data.state === "active" }
                : a,
            ),
          );
        }
        if (data.type === "STEP_UPDATE") {
          setIncidentSteps((prev) =>
            prev.map((s, i) =>
              i === data.stepIndex ? { ...s, status: data.status } : s,
            ),
          );
        }

        if (data.type === "ADHERENCE_UPDATE") {
          setIncidentSteps((prev) => {
            const updated = prev.map((s) =>
              s.id === data.id
                ? {
                    ...s,
                    status: data.status,
                    timestamp: data.timestamp,
                    summary: data.deviation_reason,
                  }
                : s,
            );

            if (data.status === "DELAYED" || data.status === "MISSED") {
              setSelectedStepId(data.id);
            }
            return updated;
          });
        }
      } catch (e) {
        console.error("WS Error:", e);
      }
    };

    socket.onopen = () => setIsOffline(false);
    socket.onclose = () => setIsOffline(true);
    socket.onerror = () => setIsOffline(true);

    return () => socket.close();
  }, [mounted]);

  const incidents = [
    {
      id: "INC-882",
      severity: "critical",
      type: "DB Injection",
      status: "Active",
    },
    {
      id: "INC-881",
      severity: "high",
      type: "DDoS Attempt",
      status: "Mitigating",
    },
    {
      id: "INC-880",
      severity: "medium",
      type: "Auth Failure",
      status: "Monitoring",
    },
  ];

  const agentLogs = [
    { time: "15:22:10", msg: "Scanning VPC subnet 10.0.1.0/24", type: "info" },
    {
      time: "15:22:15",
      msg: "Potential anomaly detected in node-42",
      type: "warn",
    },
    {
      time: "15:23:02",
      msg: "Updating global firewall rulesets",
      type: "info",
    },
  ];

  const compliance = [
    { name: "SOC 2 Type II", progress: 92 },
    { name: "ISO 27001", progress: 85 },
    { name: "HIPAA Security", progress: 100 },
    { name: "PCI DSS v4.0", progress: 78 },
  ];

  return (
    <div className="relative w-full bg-[#09090b] overflow-hidden py-16 sm:py-20 lg:py-24">
      {/* Background Elements */}
      <div className="absolute inset-0 bg-[linear-gradient(to_right,#ffffff05_1px,transparent_1px),linear-gradient(to_bottom,#ffffff05_1px,transparent_1px)] bg-size-[4rem_4rem] opacity-40 pointer-events-none" />
      <div className="absolute top-20 right-0 w-96 h-96 bg-blue-600/10 blur-3xl rounded-full opacity-40 pointer-events-none" />
      <div className="absolute -bottom-20 left-1/4 w-72 h-72 bg-indigo-600/10 blur-3xl rounded-full opacity-30 pointer-events-none" />

      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <motion.div
          className="mb-12"
          initial={{ opacity: 0, y: -20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
        >
          <div className="flex items-center gap-3 mb-4">
            <Shield className="h-8 w-8 text-blue-400 drop-shadow-[0_0_8px_rgba(59,130,246,0.6)]" />
            <h1 className="text-3xl sm:text-4xl lg:text-5xl font-bold tracking-tight text-white">
              PlaybookPulse
            </h1>
          </div>
          <p className="text-base sm:text-lg text-neutral-400 max-w-2xl">
            Real-time incident response compliance monitoring with AI-powered
            analysis
          </p>
        </motion.div>

        {/* Status Indicators */}
        <motion.div
          className="mb-12 flex flex-col sm:flex-row items-start sm:items-center gap-4"
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6, delay: 0.1 }}
        >
          <div className="flex items-center gap-2">
            <div
              className={`h-3 w-3 rounded-full ${isOffline ? "bg-rose-500" : "bg-emerald-500"} animate-pulse shadow-lg`}
            />
            <span
              className={`text-sm font-medium ${isOffline ? "text-rose-400" : "text-emerald-400"}`}
            >
              {isOffline ? "Offline - Viewing Cached Data" : "Live Monitoring"}
            </span>
          </div>
        </motion.div>

        {/* Main Grid Layout */}
        <motion.div
          className="grid grid-cols-1 lg:grid-cols-3 gap-6 lg:gap-8"
          variants={containerVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true }}
        >
          {/* Left Column: Incidents & Agents */}
          <div className="lg:col-span-1 space-y-6">
            {/* Active Incidents Card */}
            <motion.section
              className="rounded-2xl border border-white/10 bg-white/2 backdrop-blur-sm p-6 hover:border-white/20 hover:bg-white/5 transition-all duration-300 hover:shadow-lg hover:shadow-blue-600/10"
              variants={itemVariants}
            >
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-sm font-semibold uppercase tracking-wider text-white flex items-center gap-2">
                  <AlertCircle className="h-4 w-4 text-blue-400" />
                  Active Incidents
                </h2>
                <span className="flex h-2 w-2 rounded-full bg-blue-400 animate-pulse" />
              </div>
              <div className="space-y-3">
                {incidents.map((inc) => (
                  <div
                    key={inc.id}
                    className="group relative rounded-lg border border-white/5 bg-white/5 p-3 backdrop-blur-sm transition-all hover:bg-white/8 hover:border-white/10"
                  >
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-xs font-mono text-blue-400">
                        {inc.id}
                      </span>
                      <span
                        className={`text-[10px] font-bold uppercase ${
                          inc.severity === "critical"
                            ? "text-red-400"
                            : "text-amber-400"
                        }`}
                      >
                        {inc.severity}
                      </span>
                    </div>
                    <div className="text-sm font-medium text-white mb-1">
                      {inc.type}
                    </div>
                    <div className="text-[11px] text-neutral-400">
                      {inc.status} • Just now
                    </div>
                  </div>
                ))}
              </div>
            </motion.section>

            {/* System Agents Card */}
            <motion.section
              className="rounded-2xl border border-white/10 bg-white/2 backdrop-blur-sm p-6 hover:border-white/20 hover:bg-white/5 transition-all duration-300 hover:shadow-lg hover:shadow-blue-600/10"
              variants={itemVariants}
            >
              <h2 className="text-sm font-semibold uppercase tracking-wider text-white mb-4">
                System Agents
              </h2>
              <div className="space-y-3">
                {agents.map((agent) => (
                  <div
                    key={agent.name}
                    className={`rounded-lg border p-3 backdrop-blur-sm transition-all duration-500 ${
                      agent.active
                        ? "border-blue-400/50 bg-blue-400/5 shadow-[0_0_15px_rgba(59,130,246,0.2)]"
                        : "border-white/5 bg-white/5"
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium text-white">
                        {agent.name}
                      </span>
                      <div
                        className={`h-1.5 w-1.5 rounded-full transition-all ${agent.active ? "bg-blue-400 shadow-[0_0_8px_rgba(59,130,246,0.8)]" : "bg-slate-600"}`}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </motion.section>
          </div>

          {/* Right Column: Main Content */}
          <div className="lg:col-span-2 space-y-6">
            {/* Live Agent Feed Card */}
            <motion.section
              className="rounded-2xl border border-white/10 bg-white/2 backdrop-blur-sm p-6 hover:border-white/20 hover:bg-white/5 transition-all duration-300 hover:shadow-lg hover:shadow-blue-600/10"
              variants={itemVariants}
            >
              <div className="flex items-center gap-2 mb-4 text-white">
                <Terminal className="h-4 w-4 text-blue-400" />
                <h2 className="text-sm font-semibold uppercase tracking-widest">
                  Live Agent Feed
                </h2>
              </div>
              <div className="relative rounded-lg border border-white/5 bg-white/5 p-4 overflow-hidden">
                <div className="absolute inset-0 bg-linear-to-t from-slate-950/20 to-transparent pointer-events-none" />
                <div className="flex flex-col gap-2 font-mono text-xs max-h-48 overflow-y-auto custom-scrollbar">
                  {agentLogs.map((log, i) => (
                    <div key={i} className="flex gap-4 text-neutral-400">
                      <span className="text-neutral-600 shrink-0">
                        [{log.time}]
                      </span>
                      <span className="text-neutral-500 shrink-0">SYSTEM:</span>
                      <span
                        className={
                          log.type === "warn"
                            ? "text-amber-400"
                            : "text-blue-400/80"
                        }
                      >
                        {log.msg}
                      </span>
                    </div>
                  ))}
                  <div className="flex gap-4 text-neutral-400 animate-pulse">
                    <span className="text-neutral-600 shrink-0">
                      [
                      {mounted
                        ? new Date().toLocaleTimeString("en-GB")
                        : "00:00:00"}
                      ]
                    </span>
                    <span className="text-neutral-500 shrink-0">SYSTEM:</span>
                    <span className="text-blue-400">
                      Ready for incoming telemetry...
                    </span>
                  </div>
                </div>
              </div>
            </motion.section>

            {/* Adherence Grid Card */}
            <motion.section
              className="rounded-2xl border border-white/10 bg-white/2 backdrop-blur-sm p-6 hover:border-white/20 hover:bg-white/5 transition-all duration-300 hover:shadow-lg hover:shadow-blue-600/10"
              variants={itemVariants}
            >
              <div className="flex items-center gap-2 mb-4 text-white">
                <Activity className="h-4 w-4 text-blue-400" />
                <h2 className="text-sm font-semibold uppercase tracking-widest">
                  Adherence Grid
                </h2>
              </div>
              <div className="overflow-x-auto">
                <AdherenceGrid
                  steps={incidentSteps}
                  selectedStepId={selectedStepId || undefined}
                  onStepClick={(step) => setSelectedStepId(step.id as number)}
                />
              </div>
            </motion.section>
          </div>
        </motion.div>

        {/* Compliance Mapping Section */}
        <motion.section
          className="mt-8 rounded-2xl border border-white/10 bg-white/2 backdrop-blur-sm p-6 hover:border-white/20 hover:bg-white/5 transition-all duration-300 hover:shadow-lg hover:shadow-blue-600/10"
          variants={itemVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true }}
          transition={{ duration: 0.5, delay: 0.5 }}
        >
          <div className="flex items-center gap-2 mb-6 text-white">
            <Zap className="h-4 w-4 text-blue-400" />
            <h2 className="text-sm font-semibold uppercase tracking-widest">
              Compliance Mapping
            </h2>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {compliance.map((item, i) => (
              <motion.div
                key={i}
                className="space-y-3"
                initial={{ opacity: 0 }}
                whileInView={{ opacity: 1 }}
                viewport={{ once: true }}
                transition={{ duration: 0.5, delay: i * 0.1 }}
              >
                <div className="flex justify-between items-center">
                  <span className="font-medium text-white text-sm">
                    {item.name}
                  </span>
                  <span className="text-blue-400 font-mono text-xs">
                    {item.progress}%
                  </span>
                </div>
                <div className="h-2 w-full bg-neutral-800 rounded-full overflow-hidden">
                  <motion.div
                    className="h-full bg-linear-to-r from-blue-400 to-blue-600 shadow-[0_0_10px_rgba(59,130,246,0.4)]"
                    initial={{ width: 0 }}
                    whileInView={{ width: `${item.progress}%` }}
                    viewport={{ once: true }}
                    transition={{ duration: 1, delay: i * 0.1 + 0.2 }}
                  />
                </div>
              </motion.div>
            ))}
          </div>
        </motion.section>
      </div>

      <AnimatePresence>
        {selectedStepId && (
          <ComplianceDetailPanel
            step={incidentSteps.find((s) => s.id === selectedStepId)}
            onClose={() => setSelectedStepId(null)}
          />
        )}
      </AnimatePresence>

      <style jsx global>{`
        .custom-scrollbar::-webkit-scrollbar {
          width: 5px;
          height: 5px;
        }
        .custom-scrollbar::-webkit-scrollbar-track {
          background: transparent;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb {
          background: rgba(59, 130, 246, 0.2);
          border-radius: 10px;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb:hover {
          background: rgba(59, 130, 246, 0.3);
        }
      `}</style>
    </div>
  );
};

export default PlaybookPulse;
