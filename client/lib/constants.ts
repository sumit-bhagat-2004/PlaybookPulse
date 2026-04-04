// Backend Integration API (port 8000)
export const BACKEND_URL =
  process.env.REACT_APP_BACKEND_URL || "http://localhost:8000";
export const WS_URL = BACKEND_URL.replace(/^http/, "ws") + "/ws";

// Agents API (port 8001)
export const AGENTS_API =
  process.env.REACT_APP_AGENTS_API || "http://localhost:8001/api/v1";
export const AGENTS_WS = AGENTS_API.replace(/^http/, "ws");

// API Endpoints
export const API_ENDPOINTS = {
  // Agents API
  ANALYSIS_START: `${AGENTS_API}/analysis/start`,
  ANALYSIS_GET: (id: string) => `${AGENTS_API}/analysis/${id}`,
  ANALYSIS_LIST: `${AGENTS_API}/analysis`,
  ANALYSIS_REPORT: (id: string) => `${AGENTS_API}/analysis/${id}/report`,
  HEALTH: `${AGENTS_API}/health`,

  // Backend API
  BACKEND_ANALYZE: `${BACKEND_URL}/analyze`,
  BACKEND_PLAYBOOKS: `${BACKEND_URL}/playbooks`,
  BACKEND_PLAYBOOK_GET: (id: string) => `${BACKEND_URL}/playbooks/${id}`,
};
