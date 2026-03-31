interface NoteViewProps {
  noteId: string;
}

export function NoteView({ noteId }: NoteViewProps) {
  return (
    <div className="flex h-full">
      <div className="flex-1 overflow-auto p-6">
        <div className="max-w-3xl mx-auto">
          <div className="text-muted-foreground">Loading note {noteId}...</div>
        </div>
      </div>
    </div>
  );
}
