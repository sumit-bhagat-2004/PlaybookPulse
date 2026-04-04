/**
 * API utilities for agents and backend integrations
 */
import { API_ENDPOINTS } from "./constants";

// Type definitions
export interface AnalysisRequest {
  playbook_content: string;
  slack_thread_id?: string;
  jira_ticket_id?: string;
  github_repo?: string;
  compliance_frameworks?: string[];
}

export interface PlaybookStep {
  step_id: string;
  phase: string;
  description: string;
  required_actions: string[];
  responsible_roles: string[];
}

export interface AdherenceCheck {
  step_id: string;
  adherence_level: "full" | "partial" | "none";
  evidence: string[];
  gaps: string[];
  recommendations: string[];
}

export interface ComplianceMapping {
  framework: string;
  control_id: string;
  control_title: string;
  adherence_level: "full" | "partial" | "none";
  supporting_evidence: string[];
}

export interface AnalysisResult {
  analysis_id: string;
  status: string;
  playbook_steps: PlaybookStep[];
  adherence_checks: AdherenceCheck[];
  compliance_mappings: ComplianceMapping[];
  overall_score?: number;
  created_at: string;
  updated_at: string;
  completed_at?: string;
}

// API Calls to Agents API

/**
 * Check health status of agents API
 */
export async function checkHealth() {
  try {
    const response = await fetch(API_ENDPOINTS.HEALTH);
    return response.ok;
  } catch (error) {
    return false;
  }
}

/**
 * Start a new analysis
 */
export async function startAnalysis(request: AnalysisRequest) {
  const response = await fetch(API_ENDPOINTS.ANALYSIS_START, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    throw new Error(`Failed to start analysis: ${response.statusText}`);
  }

  return response.json();
}

/**
 * Get analysis by ID
 */
export async function getAnalysis(id: string) {
  const response = await fetch(API_ENDPOINTS.ANALYSIS_GET(id));

  if (!response.ok) {
    if (response.status === 404) {
      throw new Error("Analysis not found");
    }
    throw new Error(`Failed to fetch analysis: ${response.statusText}`);
  }

  return response.json();
}

/**
 * List all analyses
 */
export async function listAnalyses(limit: number = 10, offset: number = 0) {
  const response = await fetch(
    `${API_ENDPOINTS.ANALYSIS_LIST}?limit=${limit}&offset=${offset}`,
  );

  if (!response.ok) {
    throw new Error(`Failed to list analyses: ${response.statusText}`);
  }

  return response.json();
}

/**
 * Download analysis report
 */
export async function downloadReport(
  id: string,
  format: "pdf" | "json" | "html" = "pdf",
) {
  const response = await fetch(API_ENDPOINTS.ANALYSIS_REPORT(id), {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ format }),
  });

  if (!response.ok) {
    throw new Error(`Failed to download report: ${response.statusText}`);
  }

  return response.blob();
}

// API Calls to Backend Integration API

/**
 * Run quick analysis via backend
 */
export async function quickAnalysis(params: {
  playbook_content?: string;
  use_sample_playbook?: boolean;
  compliance_frameworks?: string[];
  slack_thread_data?: Record<string, unknown>;
  jira_ticket_data?: Record<string, unknown>;
  github_events?: Array<Record<string, unknown>>;
}) {
  const response = await fetch(API_ENDPOINTS.BACKEND_ANALYZE, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(params),
  });

  if (!response.ok) {
    throw new Error(`Analysis failed: ${response.statusText}`);
  }

  return response.json();
}

/**
 * List available playbooks
 */
export async function listPlaybooks() {
  const response = await fetch(API_ENDPOINTS.BACKEND_PLAYBOOKS);

  if (!response.ok) {
    throw new Error(`Failed to fetch playbooks: ${response.statusText}`);
  }

  return response.json();
}

/**
 * Get playbook content
 */
export async function getPlaybook(id: string) {
  const response = await fetch(API_ENDPOINTS.BACKEND_PLAYBOOK_GET(id));

  if (!response.ok) {
    throw new Error(`Failed to fetch playbook: ${response.statusText}`);
  }

  return response.json();
}
