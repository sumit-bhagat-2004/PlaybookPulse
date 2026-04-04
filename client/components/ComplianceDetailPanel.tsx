"use client";

import React from "react";
import { motion } from "framer-motion";
import { 
  X, 
  Clock, 
  Link2, 
  CheckCircle2, 
  MessageSquare,
  Download,
  ExternalLink
} from "lucide-react";
import { cn } from "@/lib/utils";
import { BACKEND_URL } from "@/lib/constants";

interface ComplianceDetailPanelProps {
  step: any;
  onClose: () => void;
}

const ComplianceDetailPanel: React.FC<ComplianceDetailPanelProps> = ({ step, onClose }) => {
  if (!step) return null;

  const handleDownloadPDF = async () => {
    try {
      const incidentId = step.incidentId || "INC-882";
      const response = await fetch(`${BACKEND_URL}/api/report/${incidentId}`);
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      window.open(url, '_blank');
    } catch (error) {
      console.error("PDF Download error:", error);
    }
  };

  const controls = [
    "NIST SP 800-61 §3.3.1",
    "SOC 2 CC7.3",
    "ISO 27001 A.16.1",
    "CIS Control 17"
  ];

  return (
    <motion.aside
      initial={{ x: "100%", opacity: 0 }}
      animate={{ x: 0, opacity: 1 }}
      exit={{ x: "100%", opacity: 0 }}
      transition={{ duration: 0.5, ease: "easeInOut" }}
      className="fixed top-0 right-0 h-full w-[450px] border-l border-slate-800 bg-slate-950/80 backdrop-blur-2xl p-8 z-50 flex flex-col gap-8 shadow-[-20px_0_40px_rgba(0,0,0,0.4)]"
    >
      {step.status === 'FOLLOWED' && (
        <div className="absolute top-6 left-1/2 -translate-x-1/2 bg-emerald-500/10 border border-emerald-500/30 px-3 py-1 rounded-full flex items-center gap-2 backdrop-blur-md shadow-[0_0_15px_rgba(16,185,129,0.1)]">
          <CheckCircle2 className="h-3 w-3 text-emerald-400" />
          <span className="text-[9px] font-black text-emerald-400 uppercase tracking-[0.2em]">Auditor Verified</span>
        </div>
      )}
      {/* Header */}
      <div className="flex items-center justify-between pb-4 border-b border-white/5">
        <div className="flex flex-col gap-1">
          <div className="flex items-center gap-2">
            <span className="text-[10px] font-mono text-cyan-400 uppercase tracking-widest bg-cyan-400/10 px-2 py-0.5 rounded">
              Phase 0{step.id}
            </span>
            <span className={cn(
              "text-[10px] font-bold uppercase px-2 py-0.5 rounded",
              step.status === 'FOLLOWED' ? 'bg-emerald-500/20 text-emerald-400' :
              step.status === 'DELAYED' ? 'bg-amber-500/20 text-amber-400' :
              step.status === 'MISSED' ? 'bg-rose-500/20 text-rose-400' : 'bg-slate-800 text-slate-400'
            )}>
              {step.status}
            </span>
          </div>
          <h2 className="text-2xl font-bold text-white mt-2">{step.label}</h2>
        </div>
        <button 
          onClick={onClose}
          className="p-2 rounded-lg bg-white/5 hover:bg-white/10 text-slate-400 transition-colors"
        >
          <X className="h-5 w-5" />
        </button>
      </div>

      {/* 1. Deviation Summary */}
      <div className="space-y-3">
        <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wider flex items-center gap-2">
          <Clock className="h-4 w-4 text-cyan-500" /> Deviation Summary
        </h3>
        <div className="grid grid-cols-2 gap-4">
          <div className="bg-white/5 border border-white/5 p-4 rounded-xl text-center">
            <p className="text-[10px] font-medium text-slate-500 uppercase tracking-tighter mb-1">Expected Timeline</p>
            <p className="text-xl font-bold text-white">30m</p>
          </div>
          <div className="bg-cyan-500/5 border border-cyan-500/20 p-4 rounded-xl text-center">
            <p className="text-[10px] font-medium text-cyan-500/70 uppercase tracking-tighter mb-1">Actual Event</p>
            <p className="text-xl font-bold text-cyan-400">2h 15m</p>
          </div>
        </div>
      </div>

      {/* 2. Control Mapping */}
      <div className="space-y-3">
        <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wider flex items-center gap-2">
          <Link2 className="h-4 w-4 text-cyan-500" /> Control Mapping
        </h3>
        <div className="flex flex-wrap gap-2">
          {controls.map(control => (
            <span 
              key={control} 
              className="text-[10px] font-mono font-bold text-cyan-400 border border-cyan-400/30 px-3 py-1.5 rounded-lg bg-cyan-400/5 hover:bg-cyan-400/10 cursor-default transition-all"
            >
              {control}
            </span>
          ))}
        </div>
      </div>

      {/* 4. Jira/Slack Snippet (Evidence Trace) */}
      <div className="space-y-3">
        <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wider flex items-center gap-2">
          <MessageSquare className="h-4 w-4 text-cyan-500" /> Evidence Trace
        </h3>
        <div className="bg-slate-900/50 border border-white/5 p-4 rounded-xl font-mono text-xs text-slate-300 leading-relaxed italic">
          <div className="flex items-center gap-2 mb-2 text-[10px] text-slate-500 non-italic">
            <span className="text-amber-500 font-bold uppercase tracking-tighter">Slack</span>
            <span>•</span>
            <span>#incident-war-room</span>
            <span>•</span>
            <span>just now</span>
          </div>
          "{step.summary || "No automated trace available for this event."}"
        </div>
      </div>

      {/* Spacer */}
      <div className="flex-1" />

      {/* Action Buttons */}
      <div className="flex flex-col gap-3">
        {step.pr_url && (
          <a 
            href={step.pr_url} 
            target="_blank" 
            rel="noopener noreferrer"
            className="w-full bg-slate-900 border border-white/10 hover:bg-slate-800 text-white font-semibold py-3 px-6 rounded-xl flex items-center justify-center gap-3 transition-all group"
          >
            <ExternalLink className="h-4 w-4 text-slate-400 group-hover:text-white" />
            View Orchestrator PR
            {step.pr_status === 'Open' && (
              <span className="flex items-center gap-1.5 ml-2 bg-cyan-400/10 px-2 py-0.5 rounded-full border border-cyan-400/20">
                <span className="h-1.5 w-1.5 rounded-full bg-cyan-400 animate-pulse shadow-[0_0_8px_rgba(34,211,238,0.8)]" />
                <span className="text-[9px] font-black text-cyan-400 uppercase tracking-tighter">Live</span>
              </span>
            )}
          </a>
        )}

        <button 
          onClick={handleDownloadPDF}
          className="w-full bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-bold py-4 px-6 rounded-xl flex items-center justify-center gap-3 transition-transform active:scale-[0.98] shadow-[0_0_20px_rgba(6,182,212,0.3)] group"
        >
          <Download className="h-5 w-5 group-hover:animate-bounce" />
          Download Auditor Evidence Package (PDF)
        </button>
      </div>

      <div className="text-[10px] text-slate-600 text-center uppercase font-bold tracking-widest">
        Trace ID: PTR-{Math.random().toString(36).substring(7).toUpperCase()}
      </div>
    </motion.aside>
  );
};

export default ComplianceDetailPanel;
