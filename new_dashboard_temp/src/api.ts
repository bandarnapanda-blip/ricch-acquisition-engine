/**
 * RI2CH Agency OS — API Layer
 * FILE: src/api.ts
 *
 * This file REPLACES constants.ts as the data source for your React app.
 * All MOCK_* exports are now real fetch calls to your FastAPI backend.
 *
 * HOW TO USE:
 *   In App.tsx, change this ONE line:
 *   FROM: import { MOCK_LEADS, AGENT_STATUSES, MOCK_LOGS, MOCK_TASKS } from './constants';
 *   TO:   import { useLeads, useMetrics, useLogs, useAgents, useTasks, api } from './api';
 *
 * Then replace MOCK_LEADS with leads from the hook:
 *   const { leads, loading, refetch } = useLeads();
 */

// ─── CONFIG ──────────────────────────────────────────────────────────────────

// In development this hits localhost. In production, set VITE_API_URL in your .env
const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8001';

// ─── TYPES (mirrors your types.ts) ───────────────────────────────────────────

export interface Lead {
  id: string;
  businessName: string;
  website: string;
  contactUrl?: string;
  email?: string;
  phone?: string;
  niche: string;
  city: string;
  opportunityScore: number;
  revenueLoss: number;
  revenue?: number;
  monthlyValue: number;
  status: 'New' | 'High Intel Ready' | 'Contacted' | 'Replied' | 'Demo Sent' | 'Closed';
  replyStatus?: 'positive' | 'neutral' | 'negative';
  lastContactedAt?: string;
  speedScore: number;
  seoScore: number;
  mobileScore: number;
  websiteScore?: number;
  websiteRoast?: string;
  demoLink?: string;
  pitchSent?: boolean;
  repliedAt?: string;
  createdAt?: string;
  desktopScreenshotUrl?: string;
  mobileScreenshotUrl?: string;
  domainExpiration?: string;
  previewHtml?: string;
  isApproved?: boolean;
  paymentStatus?: string;
  paymentLink?: string;
  amountPaid?: number;
}

export interface AgentStatus {
  name: string;
  division: string;
  status: 'LIVE' | 'IDLE' | 'DOWN';
  lastActive: string;
}

export interface LogEntry {
  timestamp: string;
  message: string;
  service: string;
}

export interface Task {
  id: string;
  leadId: string;
  title: string;
  description: string;
  status: 'Pending' | 'In Progress' | 'Completed';
  assignee: string;
  dueDate: string;
  createdAt: string;
}

export interface Metrics {
  totalLeads: number;
  whaleLeads: number;
  totalLeakage: number;
  expectedMRR: number;
  actualMRR: number;
  potentialMRR: number;
  replyRate: number;
  totalSent: number;
  totalReplies: number;
  avgScore: number;
  newLeads: number;
  highIntelReady: number;
  funnel: { name: string; count: number }[];
  nicheData: { name: string; value: number }[];
  scoreDistribution: { range: string; count: number }[];
}

// ─── CORE FETCH ───────────────────────────────────────────────────────────────

async function apiFetch<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  });
  if (!res.ok) {
    const err = await res.text();
    throw new Error(`API ${path} failed (${res.status}): ${err}`);
  }
  return res.json();
}

// ─── RAW API CALLS ────────────────────────────────────────────────────────────

export const api = {
  // Leads
  getLeads: (params?: { status?: string; niche?: string; min_score?: number }) => {
    const qs = params ? '?' + new URLSearchParams(
      Object.entries(params)
        .filter(([, v]) => v !== undefined)
        .map(([k, v]) => [k, String(v)])
    ).toString() : '';
    return apiFetch<{ leads: Lead[]; total: number }>(`/api/leads${qs}`);
  },

  getLead: (id: string) =>
    apiFetch<Lead>(`/api/leads/${id}`),

  updateLeadStatus: (id: string, status: string) =>
    apiFetch<{ success: boolean }>(`/api/leads/${id}/status`, {
      method: 'PATCH',
      body: JSON.stringify({ status }),
    }),

  // Metrics
  getMetrics: () =>
    apiFetch<Metrics>('/api/metrics'),

  // Logs
  getLogs: (limit = 50) =>
    apiFetch<{ logs: LogEntry[] }>(`/api/logs?limit=${limit}`),

  // Agents
  getAgents: () =>
    apiFetch<{ agents: AgentStatus[] }>('/api/agents'),

  // Tasks
  getTasks: () =>
    apiFetch<{ tasks: Task[] }>('/api/tasks'),

  createTask: (task: Omit<Task, 'id' | 'createdAt'>) =>
    apiFetch<{ success: boolean }>('/api/tasks', {
      method: 'POST',
      body: JSON.stringify(task),
    }),

  updateTask: (id: string, updates: Partial<Task>) =>
    apiFetch<{ success: boolean }>(`/api/tasks/${id}`, {
      method: 'PATCH',
      body: JSON.stringify(updates),
    }),

  deleteTask: (id: string) =>
    apiFetch<{ success: boolean }>(`/api/tasks/${id}`, { method: 'DELETE' }),

  // Actions
  generateSite: (lead: Pick<Lead, 'id' | 'businessName' | 'niche' | 'city' | 'opportunityScore'>) =>
    apiFetch<{ success: boolean; message: string }>('/api/generate', {
      method: 'POST',
      body: JSON.stringify({
        lead_id: lead.id,
        business_name: lead.businessName,
        niche: lead.niche,
        city: lead.city,
        score: lead.opportunityScore,
      }),
    }),

  fireSilas: (leadId: string) =>
    apiFetch<{ success: boolean; message: string }>(`/api/fire-silas/${leadId}`, {
      method: 'POST',
    }),

  // Worker Chat
  chatWorker: (leadId: string, message: string) =>
    apiFetch<{ response: string; worker: string }>('/api/chat/worker', {
      method: 'POST',
      body: JSON.stringify({ lead_id: leadId, message }),
    }),

  // God View
  getGodView: () =>
    apiFetch<{ events: any[]; liveLeads: any[]; hotLeads: any[] }>('/api/god-view'),

  // Health
  health: () =>
    apiFetch<{ status: string; version: string }>('/api/health'),
};

// ─── REACT HOOKS ─────────────────────────────────────────────────────────────
// Drop-in replacements for your MOCK_* constants. Use these in App.tsx.

import { useState, useEffect, useCallback } from 'react';

/** Replaces MOCK_LEADS — loads real leads and auto-refreshes every 30s */
export function useLeads(params?: { status?: string; niche?: string; min_score?: number }) {
  const [leads, setLeads] = useState<Lead[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetch = useCallback(async () => {
    try {
      const data = await api.getLeads(params);
      setLeads(data.leads);
      setError(null);
    } catch (e: any) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }, [JSON.stringify(params)]);

  useEffect(() => {
    fetch();
    const interval = setInterval(fetch, 180_000); // refresh every 3 minutes
    return () => clearInterval(interval);
  }, [fetch]);

  return { leads, loading, error, refetch: fetch };
}

/** Replaces computed metrics — loads from /api/metrics */
export function useMetrics() {
  const [metrics, setMetrics] = useState<Metrics | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.getMetrics().then(setMetrics).finally(() => setLoading(false));
    const interval = setInterval(() => api.getMetrics().then(setMetrics), 180_000);
    return () => clearInterval(interval);
  }, []);

  return { metrics, loading };
}

/** Replaces MOCK_LOGS — polls every 10s for live terminal feed */
export function useLogs() {
  const [logs, setLogs] = useState<LogEntry[]>([]);

  useEffect(() => {
    const load = () => api.getLogs(50).then(d => setLogs(d.logs));
    load();
    const interval = setInterval(load, 30_000); // 30s for live feel
    return () => clearInterval(interval);
  }, []);

  return logs;
}

/** Replaces AGENT_STATUSES — polls every 15s */
export function useAgents() {
  const [agents, setAgents] = useState<AgentStatus[]>([]);

  useEffect(() => {
    const load = () => api.getAgents().then(d => setAgents(d.agents));
    load();
    const interval = setInterval(load, 120_000);
    return () => clearInterval(interval);
  }, []);

  return agents;
}

/** Replaces MOCK_TASKS */
export function useTasks() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);

  const refetch = useCallback(() => {
    return api.getTasks().then(d => setTasks(d.tasks)).finally(() => setLoading(false));
  }, []);

  useEffect(() => { refetch(); }, []);

  const createTask = async (task: Omit<Task, 'id' | 'createdAt'>) => {
    await api.createTask(task);
    refetch();
  };

  const updateTask = async (id: string, updates: Partial<Task>) => {
    await api.updateTask(id, updates);
    refetch();
  };

  const deleteTask = async (id: string) => {
    await api.deleteTask(id);
    refetch();
  };

  return { tasks, loading, createTask, updateTask, deleteTask, refetch };
}

/** God View hook — polls every 5s for live tracking */
export function useGodView() {
  const [data, setData] = useState<{ events: any[]; liveLeads: any[]; hotLeads: any[] }>({
    events: [], liveLeads: [], hotLeads: []
  });

  useEffect(() => {
    const load = () => api.getGodView().then(setData).catch(() => {});
    load();
    const interval = setInterval(load, 30_000);
    return () => clearInterval(interval);
  }, []);

  return data;
}
