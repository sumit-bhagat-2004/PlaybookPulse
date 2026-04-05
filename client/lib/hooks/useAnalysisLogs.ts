import { useState, useEffect, useRef, useCallback } from "react";

export interface LogEntry {
  type: "log";
  analysis_id: string;
  timestamp: string;
  level: "DEBUG" | "INFO" | "WARN" | "ERROR";
  logger: string;
  agent_name: string;
  message: string;
}

export function useAnalysisLogs() {
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [filteredLevel, setFilteredLevel] = useState<LogEntry["level"] | "ALL">(
    "ALL",
  );
  const logsEndRef = useRef<HTMLDivElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to latest log unless user scrolled up
  useEffect(() => {
    if (logsEndRef.current && containerRef.current) {
      const { scrollTop, scrollHeight, clientHeight } = containerRef.current;
      // Only auto-scroll if we're already at the bottom
      if (scrollHeight - scrollTop - clientHeight < 50) {
        logsEndRef.current.scrollIntoView({ behavior: "smooth" });
      }
    }
  }, [logs]);

  const addLog = useCallback((log: LogEntry) => {
    setLogs((prev) => {
      const updated = [...prev, log];
      // Keep only last 100 logs
      return updated.length > 100 ? updated.slice(-100) : updated;
    });
  }, []);

  const clearLogs = useCallback(() => {
    setLogs([]);
  }, []);

  const getFilteredLogs = useCallback(() => {
    if (filteredLevel === "ALL") return logs;
    return logs.filter((log) => log.level === filteredLevel);
  }, [logs, filteredLevel]);

  return {
    logs,
    filteredLogs: getFilteredLogs(),
    filteredLevel,
    setFilteredLevel,
    addLog,
    clearLogs,
    logsEndRef,
    containerRef,
  };
}
