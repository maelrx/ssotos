import { fetchApi } from './client';

export interface NoteExplanationResponse {
  note_id: string;
  markdown: string;
  referenced_headings: string[];
}

export interface NoteSummaryResponse {
  note_id: string;
  markdown: string;
  key_points: string[];
}

export interface LinkSuggestion {
  target_note_path: string;
  target_title: string;
  reason: string;
}

export interface SuggestLinksResponse {
  note_id: string;
  suggestions: LinkSuggestion[];
}

export interface TagSuggestion {
  tag: string;
  confidence: number;
  reason: string;
}

export interface SuggestTagsResponse {
  note_id: string;
  suggestions: TagSuggestion[];
}

export interface StructureIssue {
  type: 'missing_heading' | 'deeply_nested' | 'long_paragraph' | 'logical_gap';
  location: string;
  issue: string;
  suggestion: string;
}

export interface SuggestStructureResponse {
  note_id: string;
  suggestions: StructureIssue[];
}

export interface ProposePatchResponse {
  job_id: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
}

export interface ProposePatchResult {
  note_id: string;
  proposal_id: string;
  diff: string;
}

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
}

export interface ChatResponse {
  note_id: string;
  message: ChatMessage;
}

export const copilotApi = {
  explain: (noteId: string) =>
    fetchApi<NoteExplanationResponse>(`/copilot/explain/${noteId}`, { method: 'POST' }),

  summarize: (noteId: string) =>
    fetchApi<NoteSummaryResponse>(`/copilot/summarize/${noteId}`, { method: 'POST' }),

  suggestLinks: (noteId: string) =>
    fetchApi<SuggestLinksResponse>(`/copilot/suggest-links/${noteId}`, { method: 'POST' }),

  suggestTags: (noteId: string) =>
    fetchApi<SuggestTagsResponse>(`/copilot/suggest-tags/${noteId}`, { method: 'POST' }),

  suggestStructure: (noteId: string) =>
    fetchApi<SuggestStructureResponse>(`/copilot/suggest-structure/${noteId}`, { method: 'POST' }),

  proposePatch: (noteId: string, instruction: string) =>
    fetchApi<ProposePatchResponse>(`/copilot/propose-patch/${noteId}`, {
      method: 'POST',
      body: JSON.stringify({ instruction }),
    }),

  chat: (noteId: string, message: string, history: ChatMessage[]) =>
    fetchApi<ChatResponse>(`/copilot/chat/${noteId}`, {
      method: 'POST',
      body: JSON.stringify({ message, history }),
    }),
};
