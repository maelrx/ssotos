export interface NoteFrontmatter {
  id: string;
  kind: string;
  status: string;
  title: string;
  tags: string[];
  links: string[];
  source?: string;
  policy?: Record<string, unknown>;
}

export interface Note {
  id: string;
  path: string;
  kind: string;
  title: string;
  tags: string[];
  links: string[];
  frontmatter: NoteFrontmatter;
  content: string;
  created_at: string;
  updated_at: string;
}

export interface NoteCreateRequest {
  path: string;
  content: string;
  frontmatter: NoteFrontmatter;
  actor?: string;
}

export interface NoteUpdateRequest {
  content?: string;
  frontmatter?: Partial<NoteFrontmatter>;
  actor?: string;
}
