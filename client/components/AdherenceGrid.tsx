"use client";

import React from "react";
import { motion } from "framer-motion";
import { cn } from "@/lib/utils";

type Status = 'FOLLOWED' | 'DELAYED' | 'MISSED' | 'PENDING';

interface Step {
  id: string | number;
  label: string;
  status: Status;
}

interface AdherenceGridProps {
  steps: Step[];
  selectedStepId?: string | number;
  onStepClick: (step: Step) => void;
}

const AdherenceGrid: React.FC<AdherenceGridProps> = ({ steps, selectedStepId, onStepClick }) => {
  return (
    <div className="flex flex-row gap-3 w-full">
      {steps.map((step) => {
        const isSelected = selectedStepId === step.id;
        const needsGlow = step.status === 'DELAYED' || step.status === 'MISSED';

        let baseStyles = "";
        let borderStyles = "";
        let glowColor = "";

        switch (step.status) {
          case 'FOLLOWED':
            baseStyles = "bg-emerald-500/10";
            borderStyles = "border-emerald-500/50";
            break;
          case 'DELAYED':
            baseStyles = "bg-amber-500/10";
            borderStyles = "border-amber-500/50";
            glowColor = "rgba(245, 158, 11, 0.4)";
            break;
          case 'MISSED':
            baseStyles = "bg-rose-500/10";
            borderStyles = "border-rose-500/50";
            glowColor = "rgba(244, 63, 94, 0.4)";
            break;
          case 'PENDING':
            baseStyles = "bg-slate-800";
            borderStyles = "border-dashed border-slate-700/50";
            break;
        }

        return (
          <motion.div
            key={`${step.id}-${step.status}-${isSelected}`}
            initial={needsGlow ? { scale: 1, boxShadow: `0 0 0px ${glowColor}` } : { scale: 1 }}
            animate={needsGlow ? { 
              boxShadow: [
                `0 0 0px ${glowColor}`, 
                `0 0 30px ${glowColor}`, 
                `0 0 0px ${glowColor}`
              ] 
            } : {}}
            transition={{ duration: 0.5, repeat: needsGlow ? 5 : 0, ease: "easeInOut" }}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.98 }}
            onClick={() => onStepClick(step)}
            className={cn(
              "relative flex aspect-square flex-1 flex-col items-center justify-center rounded-xl border p-3 cursor-pointer transition-all",
              baseStyles,
              borderStyles,
              isSelected ? "ring-2 ring-cyan-400 ring-offset-2 ring-offset-slate-950 border-cyan-400/50 bg-cyan-400/5" : ""
            )}
          >
            {/* Pulsing highlights removed from here, integrated into parent div for better context */}
            
            <div className="text-[9px] uppercase font-bold text-slate-500 mb-1">
              Step 0{step.id}
            </div>
            
            <div className="text-center text-[11px] font-bold text-white leading-tight px-1 mb-2">
              {step.label}
            </div>
            
            <div className={cn(
              "text-[9px] font-mono font-bold tracking-tighter uppercase px-2 py-0.5 rounded-full",
              step.status === 'FOLLOWED' ? 'text-emerald-400 bg-emerald-400/10' : 
              step.status === 'DELAYED' ? 'text-amber-400 bg-amber-400/10' : 
              step.status === 'MISSED' ? 'text-rose-400 bg-rose-400/10' : 'text-slate-500 bg-slate-700/30'
            )}>
              {step.status}
            </div>
          </motion.div>
        );
      })}
    </div>
  );
};

export default AdherenceGrid;
