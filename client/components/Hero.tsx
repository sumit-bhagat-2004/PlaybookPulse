"use client";

import {
  ArrowRight,
  ShieldCheck,
  FileText,
  GitPullRequest,
  Activity,
  CheckCircle2,
  AlertTriangle,
  XCircle,
} from "lucide-react";

export default function Hero() {
  return (
    <div className="relative min-h-screen flex items-center justify-center bg-[#09090b] overflow-hidden">
      <style>{`
        @keyframes slideInUp {
          from {
            opacity: 0;
            transform: translateY(30px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
        @keyframes slideInLeft {
          from {
            opacity: 0;
            transform: translateX(-50px);
          }
          to {
            opacity: 1;
            transform: translateX(0);
          }
        }
        @keyframes slideInRight {
          from {
            opacity: 0;
            transform: translateX(50px);
          }
          to {
            opacity: 1;
            transform: translateX(0);
          }
        }
        @keyframes float {
          0%, 100% {
            transform: translateY(0px);
          }
          50% {
            transform: translateY(-20px);
          }
        }
        @keyframes glow {
          0%, 100% {
            box-shadow: 0 0 20px rgba(59, 130, 246, 0.5);
          }
          50% {
            box-shadow: 0 0 40px rgba(59, 130, 246, 0.8);
          }
        }
        .animate-slide-in-up {
          animation: slideInUp 0.8s ease-out forwards;
        }
        .animate-slide-in-left {
          animation: slideInLeft 0.8s ease-out forwards;
        }
        .animate-slide-in-right {
          animation: slideInRight 0.8s ease-out forwards;
        }
        .animate-float {
          animation: float 3s ease-in-out infinite;
        }
        .animate-glow {
          animation: glow 3s ease-in-out infinite;
        }
        .delay-100 { animation-delay: 0.1s; }
        .delay-200 { animation-delay: 0.2s; }
        .delay-300 { animation-delay: 0.3s; }
        .delay-400 { animation-delay: 0.4s; }
      `}</style>

      {/* Background Gradients & Grid */}
      <div className="absolute inset-0 bg-[linear-gradient(to_right,#ffffff05_1px,transparent_1px),linear-gradient(to_bottom,#ffffff05_1px,transparent_1px)] bg-[size:4rem_4rem] [mask-image:radial-gradient(ellipse_60%_50%_at_50%_0%,#000_70%,transparent_100%)]" />
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-full max-w-3xl h-[400px] bg-blue-600/20 blur-[120px] rounded-full opacity-50 pointer-events-none animate-pulse" />
      <div className="absolute -top-20 right-1/4 w-96 h-96 bg-indigo-600/10 blur-3xl rounded-full opacity-30 pointer-events-none" />
      {/* Background Gradients & Grid */}
      <div className="absolute inset-0 bg-[linear-gradient(to_right,#ffffff05_1px,transparent_1px),linear-gradient(to_bottom,#ffffff05_1px,transparent_1px)] bg-[size:4rem_4rem] [mask-image:radial-gradient(ellipse_60%_50%_at_50%_0%,#000_70%,transparent_100%)]" />
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-full max-w-3xl h-[400px] bg-blue-600/20 blur-[120px] rounded-full opacity-50 pointer-events-none" />

      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col lg:flex-row items-center gap-16 z-10 py-20">
        {/* ── LEFT COLUMN: COPY & CTAS ── */}
        <div className="flex-1 text-center lg:text-left">
          <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-blue-500/10 border border-blue-500/20 text-blue-400 text-sm font-medium mb-6 animate-slide-in-up">
            <Activity className="w-4 h-4" />
            <span>Agentic Security Playbook Compliance Verifier</span>
          </div>

          <h1 className="text-5xl lg:text-7xl font-black tracking-tight text-white mb-6 leading-[1.1] animate-slide-in-up delay-100">
            Prove Your Incident Response. <br className="hidden lg:block" />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-400 via-indigo-400 to-blue-500">
              Automatically.
            </span>
          </h1>

          <p className="text-lg text-neutral-300 mb-8 max-w-2xl mx-auto lg:mx-0 leading-relaxed animate-slide-in-up delay-200">
            PlaybookPulse tells you whether your team actually followed your
            security playbook during an incident — and hands you an
            auditor-ready PDF that proves it. Stop relying on verbal assurances
            for NIST, SOC 2, and ISO 27001.
          </p>

          <div className="flex flex-col sm:flex-row items-center justify-center lg:justify-start gap-4 animate-slide-in-up delay-300">
            <button className="w-full sm:w-auto flex items-center justify-center gap-2 px-7 py-3.5 rounded-lg font-semibold bg-blue-600 text-white hover:bg-blue-500 hover:shadow-[0_0_40px_rgba(37,99,235,0.6)] shadow-[0_0_30px_rgba(37,99,235,0.4)] transition-all duration-300 hover:scale-105 active:scale-95">
              Analyze Incident via Slack
              <ArrowRight className="w-4 h-4" />
            </button>
            <button className="w-full sm:w-auto flex items-center justify-center gap-2 px-7 py-3.5 rounded-lg font-semibold bg-neutral-900 border border-neutral-700 text-white hover:bg-neutral-800 hover:border-neutral-600 hover:shadow-lg shadow-sm transition-all duration-300 hover:scale-105 active:scale-95">
              <FileText className="w-4 h-4 text-blue-400" />
              View Sample PDF
            </button>
          </div>

          <div className="mt-12 flex items-center justify-center lg:justify-start gap-8 text-sm text-neutral-400 font-medium animate-slide-in-up delay-400 flex-wrap">
            <div className="flex items-center gap-2 hover:text-neutral-200 transition-colors">
              <ShieldCheck className="w-4 h-4 text-emerald-500" /> SOC 2 CC7.3
            </div>
            <div className="flex items-center gap-2 hover:text-neutral-200 transition-colors">
              <ShieldCheck className="w-4 h-4 text-emerald-500" /> NIST SP
              800-61
            </div>
            <div className="flex items-center gap-2 hover:text-neutral-200 transition-colors">
              <ShieldCheck className="w-4 h-4 text-emerald-500" /> ISO 27001
              A.16
            </div>
          </div>
        </div>

        {/* ── RIGHT COLUMN: INTERACTIVE VISUAL ── */}
        <div className="flex-1 w-full max-w-lg lg:max-w-none relative animate-slide-in-right">
          <div className="relative rounded-2xl bg-[#0d0d12] border border-white/10 shadow-2xl overflow-hidden backdrop-blur-sm hover:border-white/20 hover:shadow-[0_0_40px_rgba(59,130,246,0.2)] transition-all duration-500">
            {/* Mockup Header */}
            <div className="flex items-center px-4 py-3 border-b border-white/10 bg-white/5">
              <div className="flex gap-1.5">
                <div className="w-3 h-3 rounded-full bg-red-500/80" />
                <div className="w-3 h-3 rounded-full bg-yellow-500/80" />
                <div className="w-3 h-3 rounded-full bg-green-500/80" />
              </div>
              <p className="ml-4 text-xs font-mono text-neutral-400 flex items-center gap-2">
                /playbookpulse #sec-incident-dec-2024
              </p>
            </div>

            {/* Mockup Body: Adherence Grid */}
            <div className="p-6 space-y-4">
              <div className="flex items-center justify-between pb-4 border-b border-white/5">
                <div>
                  <h3 className="text-sm font-semibold text-white">
                    Adherence Report
                  </h3>
                  <p className="text-xs text-neutral-500">
                    Multi-agent analysis complete in 2.4s
                  </p>
                </div>
                <div className="flex -space-x-2">
                  {/* Avatar stack mocking agents */}
                  <div className="w-7 h-7 rounded-full bg-blue-600 border-2 border-[#0d0d12] flex items-center justify-center text-[10px] font-bold text-white z-30">
                    P1
                  </div>
                  <div className="w-7 h-7 rounded-full bg-indigo-600 border-2 border-[#0d0d12] flex items-center justify-center text-[10px] font-bold text-white z-20">
                    A2
                  </div>
                  <div className="w-7 h-7 rounded-full bg-purple-600 border-2 border-[#0d0d12] flex items-center justify-center text-[10px] font-bold text-white z-10">
                    C3
                  </div>
                </div>
              </div>

              {/* Step 1 */}
              <div className="flex items-start gap-4 p-3 rounded-lg bg-white/5 border border-white/5">
                <CheckCircle2 className="w-5 h-5 text-emerald-500 shrink-0 mt-0.5" />
                <div>
                  <p className="text-sm font-medium text-neutral-200">
                    Step 1: Isolate affected endpoints
                  </p>
                  <p className="text-xs text-neutral-500 mt-1">
                    Completed via CrowdStrike at 14:02.
                  </p>
                </div>
              </div>

              {/* Step 4 (Delayed) */}
              <div className="flex items-start gap-4 p-3 rounded-lg bg-yellow-500/10 border border-yellow-500/20">
                <AlertTriangle className="w-5 h-5 text-yellow-500 shrink-0 mt-0.5" />
                <div className="w-full">
                  <div className="flex items-center justify-between">
                    <p className="text-sm font-medium text-yellow-500">
                      Step 4: Rotate compromised credentials
                    </p>
                    <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-yellow-500/20 text-yellow-400">
                      DELAYED
                    </span>
                  </div>
                  <p className="text-xs text-neutral-400 mt-1">
                    Expected 30m. Actual: 2h 15m.
                  </p>
                  <div className="mt-2 text-xs font-mono text-neutral-500 flex items-center gap-1.5">
                    Mapped to:{" "}
                    <span className="text-yellow-600/80 bg-yellow-500/10 px-1.5 py-0.5 rounded">
                      NIST §3.3.1
                    </span>
                  </div>
                </div>
              </div>

              {/* Step 6 (Missed) */}
              <div className="flex items-start gap-4 p-3 rounded-lg bg-red-500/10 border border-red-500/20">
                <XCircle className="w-5 h-5 text-red-500 shrink-0 mt-0.5" />
                <div className="w-full">
                  <div className="flex items-center justify-between">
                    <p className="text-sm font-medium text-red-400">
                      Step 6: Notify internal legal counsel
                    </p>
                    <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-red-500/20 text-red-400">
                      MISSED
                    </span>
                  </div>
                  <p className="text-xs text-neutral-400 mt-1">
                    No mention found in Slack thread.
                  </p>
                </div>
              </div>
            </div>

            {/* Mockup Footer Actions */}
            <div className="p-4 bg-white/[0.02] border-t border-white/5 flex gap-3">
              <button className="flex-1 flex items-center justify-center gap-2 py-2 rounded-md bg-blue-600/10 text-blue-400 hover:bg-blue-600/20 text-xs font-medium transition-colors">
                <FileText className="w-3.5 h-3.5" /> Generate Evidence PDF
              </button>
              <button className="flex-1 flex items-center justify-center gap-2 py-2 rounded-md bg-neutral-800 text-neutral-300 hover:bg-neutral-700 text-xs font-medium transition-colors">
                <GitPullRequest className="w-3.5 h-3.5" /> Open Playbook PR
              </button>
            </div>
          </div>

          {/* Decorative Elements */}
          <div className="absolute -bottom-6 -right-6 w-32 h-32 bg-blue-600/30 blur-3xl rounded-full pointer-events-none" />
          <div className="absolute -top-6 -left-6 w-32 h-32 bg-indigo-600/20 blur-3xl rounded-full pointer-events-none" />
        </div>
      </div>
    </div>
  );
}
