"use client";

import { Zap, Brain, Shield, BarChart3, Clock, FileCheck } from "lucide-react";

const features = [
  {
    icon: Zap,
    title: "Instant Analysis",
    description: "Multi-agent analysis completes in seconds, not hours.",
    color: "from-yellow-400 to-orange-500",
  },
  {
    icon: Brain,
    title: "AI-Powered Agents",
    description: "Specialized agents for each compliance framework.",
    color: "from-purple-400 to-pink-500",
  },
  {
    icon: Shield,
    title: "Compliance Ready",
    description: "Audit-ready reports for NIST, SOC 2, and ISO 27001.",
    color: "from-emerald-400 to-teal-500",
  },
  {
    icon: BarChart3,
    title: "Real-time Insights",
    description: "Track incident response metrics and adherence rates.",
    color: "from-cyan-400 to-blue-500",
  },
  {
    icon: Clock,
    title: "Timeline Tracking",
    description: "Automically map incident timeline to playbook steps.",
    color: "from-indigo-400 to-blue-500",
  },
  {
    icon: FileCheck,
    title: "PDF Generation",
    description: "Generate auditor-ready PDF evidence reports instantly.",
    color: "from-red-400 to-pink-500",
  },
];

export default function Features() {
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

      {/* Background Elements */}
      <div className="absolute inset-0 bg-[linear-gradient(to_right,#ffffff05_1px,transparent_1px),linear-gradient(to_bottom,#ffffff05_1px,transparent_1px)] bg-[size:4rem_4rem] opacity-40" />
      <div className="absolute top-20 right-0 w-96 h-96 bg-blue-600/10 blur-3xl rounded-full opacity-40 pointer-events-none" />

      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <h2 className="text-4xl lg:text-5xl font-bold text-white mb-4 animate-fade-in-up">
            Powerful Features
          </h2>
          <p
            className="text-lg text-neutral-400 max-w-2xl mx-auto animate-fade-in-up"
            style={{ animationDelay: "0.1s" }}
          >
            Everything you need to prove incident response compliance
          </p>
        </div>

        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {features.map((feature, idx) => {
            const Icon = feature.icon;
            return (
              <div
                key={idx}
                className="group relative p-6 rounded-xl border border-white/10 bg-white/[0.02] hover:bg-white/[0.05] backdrop-blur-sm transition-all duration-300 hover:border-white/20 hover:shadow-lg hover:shadow-blue-600/10 animate-fade-in-up"
                style={{ animationDelay: `${idx * 0.1}s` }}
              >
                {/* Gradient Background on Hover */}
                <div
                  className={`absolute inset-0 rounded-xl opacity-0 group-hover:opacity-10 bg-gradient-to-br ${feature.color} transition-opacity duration-300 pointer-events-none`}
                />

                <div className="relative z-10">
                  <div
                    className={`w-12 h-12 rounded-lg bg-gradient-to-br ${feature.color} flex items-center justify-center mb-4 group-hover:scale-110 transition-transform duration-300`}
                  >
                    <Icon className="w-6 h-6 text-white" />
                  </div>
                  <h3 className="text-lg font-semibold text-white mb-2">
                    {feature.title}
                  </h3>
                  <p className="text-neutral-400 text-sm leading-relaxed">
                    {feature.description}
                  </p>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
}
