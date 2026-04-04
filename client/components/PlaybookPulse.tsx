"use client";

import React, { useState, useEffect } from "react";
import { 
  Shield, 
  Activity, 
  Terminal, 
  Zap
} from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { cn } from "@/lib/utils";
import AdherenceGrid from "./AdherenceGrid";
import ComplianceDetailPanel from "./ComplianceDetailPanel";
import { WS_URL } from "@/lib/constants";

const PlaybookPulse = () => {
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
    ["Ingestion", "Extraction", "Correlation", "Analysis", "Validation", "Triage", "Remediation"].map((label, i) => ({
      label,
      status: (['FOLLOWED', 'DELAYED', 'MISSED', 'PENDING'] as const)[i % 4],
      id: i + 1,
      timestamp: "14:20:05",
      summary: `Automated ${label.toLowerCase()} phase verification completed with system logs.`,
      pr_url: i === 2 || i === 4 ? "https://github.com/org/repo/pull/42" : undefined,
      pr_status: i === 2 ? "Open" : "Merged",
      incidentId: "INC-882"
    }))
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
    localStorage.setItem("pp_demo_state", JSON.stringify({ 
      agents, 
      steps: incidentSteps,
      incidentId: "INC-882"
    }));
  }, [agents, incidentSteps, mounted]);
  // --- PERSISTENCE HOOK END ---

  useEffect(() => {
    if (!mounted) return;
    const socket = new WebSocket(WS_URL);
    
    socket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.type === "AGENT_STATE") {
          setAgents(prev => prev.map(a => 
            a.name === data.agent ? { ...a, active: data.state === "active" } : a
          ));
        }
        if (data.type === "STEP_UPDATE") {
          setIncidentSteps(prev => prev.map((s, i) => 
            i === data.stepIndex ? { ...s, status: data.status } : s
          ));
        }

        if (data.type === "ADHERENCE_UPDATE") {
          setIncidentSteps(prev => {
            const updated = prev.map(s => 
              s.id === data.id 
                ? { ...s, status: data.status, timestamp: data.timestamp, summary: data.deviation_reason } 
                : s
            );
            
            if (data.status === 'DELAYED' || data.status === 'MISSED') {
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
    { id: "INC-882", severity: "critical", type: "DB Injection", status: "Active" },
    { id: "INC-881", severity: "high", type: "DDoS Attempt", status: "Mitigating" },
    { id: "INC-880", severity: "medium", type: "Auth Failure", status: "Monitoring" },
  ];

  const agentLogs = [
    { time: "15:22:10", msg: "Scanning VPC subnet 10.0.1.0/24", type: "info" },
    { time: "15:22:15", msg: "Potential anomaly detected in node-42", type: "warn" },
    { time: "15:23:02", msg: "Updating global firewall rulesets", type: "info" },
  ];

  const compliance = [
    { name: "SOC 2 Type II", progress: 92 },
    { name: "ISO 27001", progress: 85 },
    { name: "HIPAA Security", progress: 100 },
    { name: "PCI DSS v4.0", progress: 78 },
  ];

  return (
    <div className="flex h-screen w-full overflow-hidden bg-slate-950 font-sans text-slate-100">
      {/* Sidebar: Active Incidents */}
      <aside className="w-80 border-r border-slate-800 bg-slate-950 p-6 flex flex-col gap-6">
        <div className="flex items-center gap-3">
          <Shield className="h-6 w-6 text-cyan-400 drop-shadow-[0_0_8px_rgba(34,211,238,0.6)]" />
          <h1 className="text-xl font-bold tracking-tight text-white">PlaybookPulse</h1>
        </div>

        <section className="flex flex-col gap-4">
          <div className="flex items-center justify-between">
            <h2 className="text-sm font-semibold uppercase tracking-wider text-slate-400">Active Incidents</h2>
            <span className="flex h-2 w-2 rounded-full bg-cyan-400 animate-pulse" />
          </div>
          <div className="flex flex-col gap-3">
            {incidents.map((inc) => (
              <div 
                key={inc.id} 
                className="group relative flex flex-col gap-2 rounded-lg border border-white/5 bg-white/5 p-3 backdrop-blur-md transition-all hover:bg-white/[0.08]"
              >
                <div className="flex items-center justify-between">
                  <span className="text-xs font-mono text-cyan-400">{inc.id}</span>
                  <span className={`text-[10px] font-bold uppercase ${
                    inc.severity === 'critical' ? 'text-red-400' : 'text-amber-400'
                  }`}>{inc.severity}</span>
                </div>
                <div className="text-sm font-medium">{inc.type}</div>
                <div className="text-[11px] text-slate-400">{inc.status} • Just now</div>
              </div>
            ))}
          </div>
        </section>

        <section className="flex flex-col gap-4">
          <h2 className="text-sm font-semibold uppercase tracking-wider text-slate-400">System Agents</h2>
          <div className="flex flex-col gap-3">
            {agents.map((agent) => (
              <div 
                key={agent.name}
                className={`rounded-lg border p-3 backdrop-blur-md transition-all duration-500 ${
                  agent.active 
                    ? "border-cyan-400/50 bg-cyan-400/5 shadow-[0_0_15px_rgba(34,211,238,0.2)] animate-pulse" 
                    : "border-white/5 bg-white/5"
                }`}
              >
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium text-slate-200">{agent.name}</span>
                  <div className={`h-1.5 w-1.5 rounded-full ${agent.active ? 'bg-cyan-400 shadow-[0_0_8px_rgba(34,211,238,0.8)]' : 'bg-slate-600'}`} />
                </div>
              </div>
            ))}
          </div>
        </section>
      </aside>

      {/* Main Content Area */}
      <main className="flex-1 overflow-y-auto p-8 flex flex-col gap-8 custom-scrollbar">
        {/* Top: Live Agent Feed */}
        <section className="flex flex-col gap-4">
          <div className="flex items-center gap-2 text-slate-400">
            <Terminal className="h-4 w-4" />
            <h2 className="text-xs font-semibold uppercase tracking-widest">Live Agent Feed</h2>
          </div>
          <div className="h-48 overflow-hidden rounded-xl border border-white/5 bg-white/5 p-4 backdrop-blur-md relative">
            <div className="absolute inset-0 bg-gradient-to-t from-slate-950/20 to-transparent pointer-events-none" />
            <div className="flex flex-col gap-2 font-mono text-xs">
              {agentLogs.map((log, i) => (
                <div key={i} className="flex gap-4">
                  <span className="text-slate-500">[{log.time}]</span>
                  <span className="text-slate-400">SYSTEM:</span>
                  <span className={log.type === 'warn' ? 'text-amber-400' : 'text-cyan-400/80'}>{log.msg}</span>
                </div>
              ))}
              <div className="flex gap-4 animate-pulse">
                <span className="text-slate-500">
                  [{mounted ? new Date().toLocaleTimeString('en-GB') : "00:00:00"}]
                </span>
                <span className="text-slate-400">SYSTEM:</span>
                <span className="text-cyan-400">Ready for incoming telemetry...</span>
              </div>
            </div>
          </div>
        </section>

        {/* Middle: Adherence Grid */}
        <section className="flex flex-col gap-4">
          <div className="flex items-center gap-2 text-slate-400">
            <Activity className="h-4 w-4" />
            <h2 className="text-xs font-semibold uppercase tracking-widest">Adherence Grid</h2>
          </div>
          <AdherenceGrid 
            steps={incidentSteps} 
            selectedStepId={selectedStepId || undefined} 
            onStepClick={(step) => setSelectedStepId(step.id as number)} 
          />
        </section>

        {/* Bottom: Compliance Mapping */}
        <section className="flex flex-col gap-4">
          <div className="flex items-center gap-2 text-slate-400">
            <Zap className="h-4 w-4" />
            <h2 className="text-xs font-semibold uppercase tracking-widest">Compliance Mapping</h2>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 p-6 rounded-2xl border border-white/5 bg-white/5 backdrop-blur-md">
            {compliance.map((item, i) => (
              <div key={i} className="space-y-3">
                <div className="flex justify-between items-center text-sm">
                  <span className="font-medium text-slate-300">{item.name}</span>
                  <span className="text-cyan-400 font-mono text-xs">{item.progress}%</span>
                </div>
                <div className="h-1.5 w-full bg-slate-800 rounded-full overflow-hidden">
                  <div 
                    className="h-full bg-cyan-400 shadow-[0_0_10px_rgba(34,211,238,0.4)] transition-all duration-1000" 
                    style={{ width: `${item.progress}%` }} 
                  />
                </div>
              </div>
            ))}
          </div>
        </section>
      </main>

      <AnimatePresence>
        {selectedStepId && (
          <ComplianceDetailPanel 
            step={incidentSteps.find(s => s.id === selectedStepId)} 
            onClose={() => setSelectedStepId(null)} 
          />
        )}
      </AnimatePresence>

      <AnimatePresence>
        {isOffline && (
          <motion.div 
            initial={{ opacity: 0, scale: 0.9, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.9, y: 20 }}
            className="fixed bottom-8 left-8 z-[100] flex items-center gap-3 bg-slate-900/80 border border-rose-500/30 px-5 py-3 rounded-2xl backdrop-blur-xl shadow-2xl shadow-rose-950/20"
          >
            <div className="h-2 w-2 rounded-full bg-rose-500 animate-pulse shadow-[0_0_8px_rgba(244,63,94,0.8)]" />
            <span className="text-[10px] font-black text-rose-400 uppercase tracking-[0.2em]">Offline - Viewing Cached Data</span>
          </motion.div>
        )}
      </AnimatePresence>

      {process.env.NODE_ENV === 'development' && (
        <button 
          onClick={() => { localStorage.removeItem("pp_demo_state"); window.location.reload(); }}
          className="fixed bottom-8 right-8 z-[100] p-2 rounded bg-slate-800/50 hover:bg-rose-500/20 text-slate-500 hover:text-rose-400 transition-all opacity-0 hover:opacity-100 text-[9px] font-black uppercase tracking-widest border border-transparent hover:border-rose-500/30"
        >
          Reset Demo State
        </button>
      )}

      <style jsx global>{`
        .custom-scrollbar::-webkit-scrollbar {
          width: 5px;
        }
        .custom-scrollbar::-webkit-scrollbar-track {
          background: transparent;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb {
          background: rgba(148, 163, 184, 0.1);
          border-radius: 10px;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb:hover {
          background: rgba(148, 163, 184, 0.2);
        }
      `}</style>
    </div>
  );
};

export default PlaybookPulse;