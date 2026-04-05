"use client";

import React from "react";
import { Trash2, Filter } from "lucide-react";
import { LogEntry } from "@/lib/hooks/useAnalysisLogs";

interface LogsPanelProps {
  logs: LogEntry[];
  filteredLevel: string;
  onFilterChange: (level: string) => void;
  onClear: () => void;
  containerRef: React.RefObject<HTMLDivElement>;
  logsEndRef: React.RefObject<HTMLDivElement>;
}

const LogsPanel: React.FC<LogsPanelProps> = ({
  logs,
  filteredLevel,
  onFilterChange,
  onClear,
  containerRef,
  logsEndRef,
}) => {
  const getLevelColor = (level: string) => {
    switch (level) {
      case "DEBUG":
        return "text-blue-400";
      case "INFO":
        return "text-gray-400";
      case "WARN":
        return "text-amber-400";
      case "ERROR":
        return "text-rose-400";
      default:
        return "text-gray-400";
    }
  };

  const getLevelBgColor = (level: string) => {
    switch (level) {
      case "DEBUG":
        return "bg-blue-500/10";
      case "INFO":
        return "bg-gray-500/10";
      case "WARN":
        return "bg-amber-500/10";
      case "ERROR":
        return "bg-rose-500/10";
      default:
        return "bg-gray-500/10";
    }
  };

  return (
    <div className="rounded-lg border border-white/10 bg-white/5 p-6 flex flex-col h-full">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold text-white flex items-center gap-2">
          Backend Logs ({logs.length})
        </h2>
        <div className="flex items-center gap-2">
          {/* Filter */}
          <select
            value={filteredLevel}
            onChange={(e) => onFilterChange(e.target.value)}
            className="px-3 py-1 text-sm rounded bg-white/10 border border-white/20 text-white hover:bg-white/20 transition"
          >
            <option value="ALL">All Levels</option>
            <option value="DEBUG">DEBUG</option>
            <option value="INFO">INFO</option>
            <option value="WARN">WARN</option>
            <option value="ERROR">ERROR</option>
          </select>

          {/* Clear button */}
          <button
            onClick={onClear}
            disabled={logs.length === 0}
            className="p-2 rounded-lg bg-white/5 hover:bg-white/10 transition disabled:opacity-30 disabled:cursor-not-allowed"
            title="Clear logs"
          >
            <Trash2 className="h-4 w-4 text-white" />
          </button>
        </div>
      </div>

      {/* Logs Container */}
      <div
        ref={containerRef}
        className="flex-1 overflow-y-auto space-y-1 font-mono text-xs bg-black/30 rounded p-3 border border-white/5"
      >
        {logs.length === 0 ? (
          <div className="text-gray-500 text-center py-8">
            No logs yet. Logs will appear here as the analysis runs.
          </div>
        ) : (
          logs.map((log, i) => (
            <div
              key={i}
              className={`flex gap-3 py-1 px-2 rounded ${getLevelBgColor(log.level)}`}
            >
              <span className="text-gray-500 flex-shrink-0 w-24">
                {new Date(log.timestamp).toLocaleTimeString()}
              </span>
              <span
                className={`font-bold flex-shrink-0 w-12 ${getLevelColor(log.level)}`}
              >
                {log.level}
              </span>
              <span className="text-cyan-400 flex-shrink-0 w-40 truncate">
                {log.agent_name}
              </span>
              <span className="text-gray-300 flex-grow">{log.message}</span>
            </div>
          ))
        )}
        <div ref={logsEndRef} />
      </div>

      {/* Stats Footer */}
      <div className="mt-3 text-xs text-gray-500 text-right">
        Showing {logs.length} log(s)
        {filteredLevel !== "ALL" && ` (filtered by ${filteredLevel})`}
      </div>
    </div>
  );
};

export default LogsPanel;
