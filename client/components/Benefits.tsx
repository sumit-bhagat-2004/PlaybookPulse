"use client";

import { CheckCircle, TrendingUp, Lock, Users, Zap, Award } from "lucide-react";

const benefits = [
  {
    icon: TrendingUp,
    title: "Speed Up Compliance",
    description:
      "Reduce incident response documentation time from hours to minutes.",
  },
  {
    icon: Lock,
    title: "Risk Reduction",
    description: "Identify playbook gaps before auditors do.",
  },
  {
    icon: Users,
    title: "Team Alignment",
    description:
      "Ensure your entire team follows incident response procedures.",
  },
  {
    icon: Award,
    title: "Audit Confidence",
    description: "Walk into audits with irrefutable compliance evidence.",
  },
];

export default function Benefits() {
  return (
    <section className="relative py-24 bg-[#09090b] overflow-hidden">
      <style>{`
        @keyframes fadeInUp {
          from {
            opacity: 0;
            transform: translateY(40px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
        .animate-fade-in-up {
          animation: fadeInUp 0.8s ease-out forwards;
        }
      `}</style>

      {/* Background */}
      <div className="absolute bottom-0 right-0 w-96 h-96 bg-emerald-600/10 blur-3xl rounded-full opacity-40 pointer-events-none" />
      <div className="absolute top-1/2 left-0 w-96 h-96 bg-blue-600/10 blur-3xl rounded-full opacity-40 pointer-events-none" />

      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid lg:grid-cols-2 gap-16 items-center">
          {/* Left Side */}
          <div>
            <h2 className="text-4xl lg:text-5xl font-bold text-white mb-8 animate-fade-in-up">
              Why Teams Choose <br className="hidden lg:block" />
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-indigo-500">
                PlaybookPulse
              </span>
            </h2>

            <div className="space-y-6">
              {benefits.map((benefit, idx) => {
                const Icon = benefit.icon;
                return (
                  <div
                    key={idx}
                    className="flex gap-4 animate-fade-in-up"
                    style={{ animationDelay: `${(idx + 1) * 0.1}s` }}
                  >
                    <div className="flex-shrink-0">
                      <div className="flex items-center justify-center h-12 w-12 rounded-lg bg-gradient-to-br from-blue-600 to-indigo-600">
                        <Icon className="h-6 w-6 text-white" />
                      </div>
                    </div>
                    <div>
                      <h3 className="text-lg font-semibold text-white">
                        {benefit.title}
                      </h3>
                      <p className="text-neutral-400 text-sm mt-1">
                        {benefit.description}
                      </p>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Right Side - Visual Stats */}
          <div
            className="space-y-6 animate-fade-in-up"
            style={{ animationDelay: "0.3s" }}
          >
            <div className="group relative p-8 rounded-2xl border border-blue-500/20 bg-gradient-to-br from-blue-600/10 to-indigo-600/10 hover:border-blue-500/40 hover:shadow-lg hover:shadow-blue-600/20 transition-all duration-300">
              <div className="absolute top-0 right-0 w-32 h-32 bg-blue-600/20 blur-3xl opacity-0 group-hover:opacity-100 transition-opacity duration-300 rounded-full" />
              <div className="relative z-10">
                <p className="text-5xl font-black text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-indigo-500 mb-2">
                  2.4s
                </p>
                <p className="text-neutral-300 font-semibold">
                  Average Analysis Time
                </p>
                <p className="text-neutral-500 text-sm mt-1">
                  Multi-agent analysis completes 60x faster than manual review
                </p>
              </div>
            </div>

            <div className="group relative p-8 rounded-2xl border border-emerald-500/20 bg-gradient-to-br from-emerald-600/10 to-teal-600/10 hover:border-emerald-500/40 hover:shadow-lg hover:shadow-emerald-600/20 transition-all duration-300">
              <div className="absolute top-0 right-0 w-32 h-32 bg-emerald-600/20 blur-3xl opacity-0 group-hover:opacity-100 transition-opacity duration-300 rounded-full" />
              <div className="relative z-10">
                <p className="text-5xl font-black text-transparent bg-clip-text bg-gradient-to-r from-emerald-400 to-teal-400 mb-2">
                  100%
                </p>
                <p className="text-neutral-300 font-semibold">
                  Audit-Ready Reports
                </p>
                <p className="text-neutral-500 text-sm mt-1">
                  Compliance-focused PDF evidence for all major frameworks
                </p>
              </div>
            </div>

            <div className="group relative p-8 rounded-2xl border border-purple-500/20 bg-gradient-to-br from-purple-600/10 to-pink-600/10 hover:border-purple-500/40 hover:shadow-lg hover:shadow-purple-600/20 transition-all duration-300">
              <div className="absolute top-0 right-0 w-32 h-32 bg-purple-600/20 blur-3xl opacity-0 group-hover:opacity-100 transition-opacity duration-300 rounded-full" />
              <div className="relative z-10">
                <p className="text-5xl font-black text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-pink-400 mb-2">
                  3x
                </p>
                <p className="text-neutral-300 font-semibold">
                  Faster Incident Documentation
                </p>
                <p className="text-neutral-500 text-sm mt-1">
                  Automated compliance mapping saves hours per incident
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
