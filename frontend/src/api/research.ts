import { fetchApi } from './client';

export interface ResearchJob {
  id: string;
  query: string;
  status: string;
  result_data?: {
    state?: string;
    sources?: Array<{ source_id: string; url?: string; status: string }>;
    [key: string]: unknown;
  };
  created_at: string;
  started_at?: string;
  completed_at?: string;
}

export interface SourceStatus {
  source_id: string;
  url: string | null;
  status: 'pending' | 'crawled' | 'parsed' | 'failed';
  content_hash: string | null;
  error: string | null;
}

export interface CreateBriefRequest {
  query: string;
  goal: string;
  questions: string[];
  scope: string;
  depth: string;
  max_sources: number;
}

export const researchApi = {
  listJobs: () => fetchApi<{ jobs: ResearchJob[] }>('/research/jobs'),

  getJob: (jobId: string) =>
    fetchApi<ResearchJob>(`/research/jobs/${jobId}`),

  getSources: (jobId: string) =>
    fetchApi<{ sources: SourceStatus[] }>(`/research/jobs/${jobId}/sources`),

  createBrief: (data: CreateBriefRequest) =>
    fetchApi<{ job_id: string; message: string }>('/research/briefs', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  cancelJob: (jobId: string) =>
    fetchApi<{ success: boolean; message: string }>(`/research/jobs/${jobId}/cancel`, {
      method: 'POST',
    }),

  getBlueprint: (jobId: string) =>
    fetchApi<{ content: string }>(`/research/jobs/${jobId}/blueprint`),

  getSynthesis: (jobId: string) =>
    fetchApi<{ content: string }>(`/research/jobs/${jobId}/synthesis`),
};
