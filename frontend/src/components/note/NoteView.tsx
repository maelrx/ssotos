import ReactMarkdown from 'react-markdown';
import { Sparkles } from 'lucide-react';
import { useNote } from '../../hooks/useNotes';
import { MetadataPanel } from './MetadataPanel';
import { CopilotPanel } from '../copilot/CopilotPanel';
import { useUIStore } from '../../stores/uiStore';

interface NoteViewProps {
  noteId: string;
}

export function NoteView({ noteId }: NoteViewProps) {
  const { data: note, isLoading } = useNote(noteId);
  const { setEditorMode, copilotPanelOpen, toggleCopilotPanel } = useUIStore();

  if (isLoading) {
    return <div className="p-4">Loading...</div>;
  }

  if (!note) {
    return <div className="p-4">Note not found</div>;
  }

  return (
    <div className="flex h-full">
      <div className="flex-1 overflow-auto p-6">
        <div className="max-w-3xl mx-auto">
          <div className="flex items-start justify-between mb-6">
            <h1 className="text-2xl font-bold">{note.title || note.path.split('/').pop()}</h1>
            <div className="flex items-center gap-2">
              <button
                onClick={toggleCopilotPanel}
                title="Open Copilot"
                className="p-2 hover:bg-muted rounded"
              >
                <Sparkles className="w-4 h-4" />
              </button>
              <button
                onClick={() => setEditorMode('edit')}
                className="px-3 py-1.5 text-sm rounded border hover:bg-muted"
              >
                Edit
              </button>
            </div>
          </div>
          <article className="prose prose-slate max-w-none">
            <ReactMarkdown>{note.content}</ReactMarkdown>
          </article>
        </div>
      </div>
      <MetadataPanel note={note} />
      {copilotPanelOpen && <CopilotPanel noteId={noteId} />}
    </div>
  );
}
