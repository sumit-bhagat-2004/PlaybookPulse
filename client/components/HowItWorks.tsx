"use client";

import {
  ArrowRight,
  MessageCircle,
  Zap,
  FileText,
  CheckCircle,
} from "lucide-react";

const steps = [
  {
    number: 1,
    icon: MessageCircle,
    title: "Start in Slack",
    description: "Trigger incident analysis directly from your Slack channel",
  },
  {
    number: 2,
    icon: Zap,
    title: "Multi-Agent Analysis",
    description:
      "Specialized agents analyze incident response against playbooks",
  },
  {
    number: 3,
    icon: FileText,
    title: "Generate Report",
    description: "Get audit-ready PDF with compliance mapping and evidence",
  },
  {
    number: 4,
    icon: CheckCircle,
    title: "Compliance Verified",
    description: "Prove adherence to NIST, SOC2, and ISO 27001 requirements",
  },
];

export default function HowItWorks() {
  return (
    <section className="relative py-24 bg-black overflow-hidden">
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
        @keyframes slideInRight {
          from {
            opacity: 0;
            transform: translateX(30px);
          }
          to {
            opacity: 1;
            transform: translateX(0);
          }
        }
        .animate-fade-in-up {
          animation: fadeInUp 0.8s ease-out forwards;
        }
        .animate-slide-in-right {
          animation: slideInRight 0.8s ease-out forwards;
        }
      `}</style>

      {/* Background */}
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-full max-w-2xl h-96 bg-indigo-600/15 blur-3xl rounded-full opacity-50 pointer-events-none" />

      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <h2 className="text-4xl lg:text-5xl font-bold text-white mb-4 animate-fade-in-up">
            How It Works
          </h2>
          <p
            className="text-lg text-neutral-400 max-w-2xl mx-auto animate-fade-in-up"
            style={{ animationDelay: "0.1s" }}
          >
            From incident to compliance proof in minutes
          </p>
        </div>

        <div className="relative">
          {/* Connection Line */}
          <div className="absolute hidden lg:block top-24 left-0 right-0 h-1 bg-gradient-to-r from-blue-600/0 via-blue-600/50 to-blue-600/0" />

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            {steps.map((step, idx) => {
              const Icon = step.icon;
              return (
                <div
                  key={idx}
                  className="relative animate-fade-in-up"
                  style={{ animationDelay: `${idx * 0.15}s` }}
                >
                  {/* Step Number Badge */}
                  <div className="flex items-center justify-center mb-6">
                    <div className="relative">
                      <div className="absolute inset-0 bg-gradient-to-br from-blue-600 to-indigo-600 rounded-full blur opacity-75 group-hover:opacity-100 transition duration-300" />
                      <div className="relative w-16 h-16 bg-black rounded-full flex items-center justify-center border border-blue-600/50">
                        <div className="absolute inset-0 bg-gradient-to-br from-blue-600/20 to-indigo-600/20 rounded-full" />
                        <Icon className="w-8 h-8 text-blue-400 relative z-10" />
                      </div>
                    </div>
                    {idx < steps.length - 1 && (
                      <div className="hidden lg:block absolute left-20 top-1/2 -translate-y-1/2 w-8">
                        <ArrowRight className="w-6 h-6 text-blue-600/50" />
                      </div>
                    )}
                  </div>

                  <div className="text-center">
                    <h3 className="text-xl font-semibold text-white mb-2">
                      {step.title}
                    </h3>
                    <p className="text-neutral-400 text-sm leading-relaxed">
                      {step.description}
                    </p>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </section>
  );
}
