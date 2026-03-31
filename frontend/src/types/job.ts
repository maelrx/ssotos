export type JobType =
  | 'index_note'
  | 'reindex_scope'
  | 'generate_embeddings'
  | 'research_job'
  | 'parse_source'
  | 'apply_patch_bundle'
  | 'reflect_agent'
  | 'consolidate_memory';

export type JobStatus = 'pending' | 'running' | 'completed' | 'failed';

export interface Job {
  id: string;
  job_type: JobType;
  status: JobStatus;
  priority: number;
  input_data: Record<string, unknown>;
  result_data?: Record<string, unknown>;
  error_message?: string;
  attempt_count: number;
  max_attempts: number;
  created_at: string;
  started_at?: string;
  completed_at?: string;
}

export interface JobEvent {
  id: string;
  job_id: string;
  event_type: string;
  message?: string;
  metadata: Record<string, unknown>;
  created_at: string;
}
