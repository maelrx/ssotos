export interface Proposal {
  id: string;
  proposal_type: string;
  state: string;
  actor: string;
  target_path: string;
  source_domain: string;
  target_domain: string;
  created_at: string;
  updated_at?: string;
  branch_name?: string;
  worktree_path?: string;
  content?: string;
  review_note?: string;
}
