import { useEffect, useRef } from 'react';
import { EditorView, basicSetup } from 'codemirror';
import { ViewUpdate } from '@codemirror/view';
import { markdown } from '@codemirror/lang-markdown';
import { oneDark } from '@codemirror/theme-one-dark';
import { EditorState } from '@codemirror/state';
import { useNote, useUpdateNote } from '../../hooks/useNotes';
import { useUIStore } from '../../stores/uiStore';

interface NoteEditorProps {
  noteId: string;
}

export function NoteEditor({ noteId }: NoteEditorProps) {
  const editorRef = useRef<HTMLDivElement>(null);
  const viewRef = useRef<EditorView | null>(null);
  const { data: note, isLoading } = useNote(noteId);
  const { setEditorMode } = useUIStore();
  const updateNote = useUpdateNote();

  useEffect(() => {
    if (!editorRef.current || !note) return;

    // Destroy previous editor
    if (viewRef.current) {
      viewRef.current.destroy();
    }

    const state = EditorState.create({
      doc: note.content,
      extensions: [
        basicSetup,
        markdown(),
        oneDark,
        EditorView.updateListener.of((update: ViewUpdate) => {
          if (update.docChanged) {
            // Could implement auto-save here
          }
        }),
      ],
    });

    viewRef.current = new EditorView({
      state,
      parent: editorRef.current,
    });

    return () => {
      viewRef.current?.destroy();
    };
  }, [note]);

  const handleSave = () => {
    if (!viewRef.current || !note) return;
    const content = viewRef.current.state.doc.toString();
    updateNote.mutate(
      { noteId, data: { content } },
      {
        onSuccess: () => setEditorMode('view'),
      }
    );
  };

  if (isLoading) {
    return <div className="p-4">Loading...</div>;
  }

  return (
    <div className="flex flex-col h-full">
      <div className="flex-1 overflow-auto">
        <div ref={editorRef} className="h-full" />
      </div>
      <div className="border-t p-2 flex justify-end gap-2">
        <button
          onClick={() => setEditorMode('view')}
          className="px-3 py-1.5 text-sm rounded border hover:bg-muted"
        >
          Cancel
        </button>
        <button
          onClick={handleSave}
          className="px-3 py-1.5 text-sm rounded bg-primary text-primary-foreground hover:bg-primary/90"
        >
          Save
        </button>
      </div>
    </div>
  );
}
