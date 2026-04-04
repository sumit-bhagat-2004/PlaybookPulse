"use client";

import { ArrowRight, Zap } from "lucide-react";

export default function CTA() {
  return (
    <section className="relative py-24 bg-black overflow-hidden">
      <style>{`
        @keyframes fadeIn {
          from {
            opacity: 0;
          }
          to {
            opacity: 1;
          }
        }
        @keyframes slideUp {
          from {
            opacity: 0;
            transform: translateY(30px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
        .animate-fade-in {
          animation: fadeIn 1s ease-out forwards;
        }
        .animate-slide-up {
          animation: slideUp 0.8s ease-out forwards;
        }
      `}</style>

      {/* Animated Background */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-full max-w-4xl h-96 bg-gradient-to-b from-blue-600/30 via-indigo-600/20 to-transparent blur-3xl animate-pulse" />
        <div
          className="absolute -bottom-20 left-1/4 w-96 h-96 bg-blue-600/20 blur-3xl rounded-full opacity-40 animate-float"
          style={{ animation: "float 6s ease-in-out infinite" }}
        />
        <div
          className="absolute -bottom-20 right-1/4 w-96 h-96 bg-indigo-600/20 blur-3xl rounded-full opacity-40 animate-float"
          style={{
            animation: "float 8s ease-in-out infinite",
            animationDelay: "-2s",
          }}
        />
      </div>

      <div className="relative max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center z-10">
        <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-blue-500/10 border border-blue-500/20 text-blue-400 text-sm font-medium mb-6 animate-slide-up">
          <Zap className="w-4 h-4" />
          <span>Limited Time Offer</span>
        </div>

        <h2
          className="text-5xl lg:text-6xl font-black text-white mb-6 leading-tight animate-slide-up"
          style={{ animationDelay: "0.1s" }}
        >
          Ready to Prove Your
          <br className="hidden sm:block" />
          <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-400 via-indigo-400 to-blue-500">
            Incident Response?
          </span>
        </h2>

        <p
          className="text-xl text-neutral-300 max-w-2xl mx-auto mb-8 animate-slide-up"
          style={{ animationDelay: "0.2s" }}
        >
          Join security teams that are automating compliance proof and cutting
          incident documentation time by 75%.
        </p>

        <div
          className="flex flex-col sm:flex-row items-center justify-center gap-4 animate-slide-up"
          style={{ animationDelay: "0.3s" }}
        >
          <button className="w-full sm:w-auto flex items-center justify-center gap-2 px-8 py-4 rounded-lg font-bold text-white bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 hover:shadow-[0_0_40px_rgba(59,130,246,0.6)] shadow-[0_0_30px_rgba(59,130,246,0.4)] transition-all duration-300 hover:scale-105 active:scale-95 group">
            Get Started Free
            <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
          </button>
          <button className="w-full sm:w-auto px-8 py-4 rounded-lg font-semibold text-white bg-white/10 border border-white/20 hover:bg-white/20 hover:border-white/30 transition-all duration-300 hover:scale-105 active:scale-95">
            Schedule Demo
          </button>
        </div>

        <p
          className="text-neutral-500 text-sm mt-8 animate-slide-up"
          style={{ animationDelay: "0.4s" }}
        >
          No credit card required. Start analyzing incidents in minutes.
        </p>
      </div>
    </section>
  );
}
