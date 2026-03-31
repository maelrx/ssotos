import { fetchApi } from './client';
import type { Note, NoteCreateRequest, NoteUpdateRequest } from '../types/note';
import type { Job, JobEvent } from '../types/job';
import type { Proposal } from '../types/proposal';

// Vault endpoints
export const vaultApi = {
  listNotes: (params?: { page?: number; limit?: number; path?: string }) =>
    fetchApi<{ notes: Note[]; total: number }>(`/vault/notes?${new URLSearchParams(params as any)}`),

  getNote: (noteId: string) =>
    fetchApi<Note>(`/vault/notes/${noteId}`),

  getNoteByPath: (path: string) =>
    fetchApi<Note>(`/vault/notes/path/${encodeURIComponent(path)}`),

  createNote: (data: NoteCreateRequest) =>
    fetchApi<Note>('/vault/notes', { method: 'POST', body: JSON.stringify(data) }),

  updateNote: (noteId: string, data: NoteUpdateRequest) =>
    fetchApi<Note>(`/vault/notes/${noteId}`, { method: 'PUT', body: JSON.stringify(data) }),

  deleteNote: (noteId: string) =>
    fetchApi<{ success: boolean }>(`/vault/notes/${noteId}`, { method: 'DELETE' }),

  searchNotes: (q: string) =>
    fetchApi<{ notes: Note[] }>(`/vault/search?q=${encodeURIComponent(q)}`),
};

// Jobs endpoints
export const jobsApi = {
  listJobs: (params?: { page?: number; limit?: number }) =>
    fetchApi<{ jobs: Job[]; total: number }>(`/jobs?${new URLSearchParams(params as any)}`),

  getJob: (jobId: string) =>
    fetchApi<Job>(`/jobs/${jobId}`),

  createJob: (data: { job_type: string; priority?: number; input_data?: Record<string, unknown> }) =>
    fetchApi<Job>('/jobs', { method: 'POST', body: JSON.stringify(data) }),

  cancelJob: (jobId: string) =>
    fetchApi<Job>(`/jobs/${jobId}/cancel`, { method: 'POST' }),

  retryJob: (jobId: string) =>
    fetchApi<Job>(`/jobs/${jobId}/retry`, { method: 'POST' }),

  getJobEvents: (jobId: string) =>
    fetchApi<{ events: JobEvent[] }>(`/jobs/${jobId}/events`),
};

// Exchange endpoints
export const exchangeApi = {
  listProposals: (params?: { state?: string; target_domain?: string }) =>
    fetchApi<{ proposals: Proposal[]; total: number; states: Record<string, number> }>(
      `/exchange/proposals?${new URLSearchParams(params as any)}`
    ),
  getProposal: (id: string) =>
    fetchApi<Proposal>(`/exchange/proposals/${id}`),
  approveProposal: (id: string, note?: string) =>
    fetchApi(`/exchange/proposals/${id}/approve`, { method: 'POST', body: JSON.stringify({ review_note: note }) }),
  rejectProposal: (id: string, reason: string) =>
    fetchApi(`/exchange/proposals/${id}/reject`, { method: 'POST', body: JSON.stringify({ reason }) }),
};
