import type { Note } from '../../types/note';

interface MetadataPanelProps {
  note: Note;
}

export function MetadataPanel({ note }: MetadataPanelProps) {
  const fm = note.frontmatter;

  return (
    <aside className="w-64 border-l p-4 overflow-auto">
      <h3 className="text-xs font-semibold text-muted-foreground uppercase mb-3">Metadata</h3>

      <dl className="space-y-3 text-sm">
        <div>
          <dt className="text-muted-foreground">Kind</dt>
          <dd className="font-medium">{fm.kind}</dd>
        </div>
        <div>
          <dt className="text-muted-foreground">Status</dt>
          <dd className="font-medium">{fm.status}</dd>
        </div>
        {fm.tags.length > 0 && (
          <div>
            <dt className="text-muted-foreground">Tags</dt>
            <dd className="flex flex-wrap gap-1 mt-1">
              {fm.tags.map(tag => (
                <span key={tag} className="px-1.5 py-0.5 bg-muted rounded text-xs">{tag}</span>
              ))}
            </dd>
          </div>
        )}
        {fm.links.length > 0 && (
          <div>
            <dt className="text-muted-foreground">Links</dt>
            <dd className="flex flex-wrap gap-1 mt-1">
              {fm.links.map(link => (
                <span key={link} className="px-1.5 py-0.5 bg-muted rounded text-xs">{link}</span>
              ))}
            </dd>
          </div>
        )}
        <div>
          <dt className="text-muted-foreground">Path</dt>
          <dd className="font-mono text-xs">{note.path}</dd>
        </div>
        <div>
          <dt className="text-muted-foreground">Updated</dt>
          <dd>{new Date(note.updated_at).toLocaleString()}</dd>
        </div>
      </dl>
    </aside>
  );
}
