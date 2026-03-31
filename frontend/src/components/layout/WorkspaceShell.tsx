import { Header } from './Header';
import { Sidebar } from './Sidebar';
import { useUIStore } from '../../stores/uiStore';
import { NoteView } from '../note/NoteView';
import { NoteEditor } from '../editor/NoteEditor';
import { ExchangeWorkspace } from '../exchange/ExchangeWorkspace';
import { ResearchWorkspace } from '../research/ResearchWorkspace';
import { SettingsWorkspace } from '../settings/SettingsWorkspace';

export function WorkspaceShell() {
  const { activeView, selectedNoteId, editorMode } = useUIStore();

  return (
    <div className="h-screen flex flex-col">
      <Header />
      <div className="flex-1 flex overflow-hidden">
        <Sidebar />
        <main className="flex-1 overflow-auto">
          {activeView === 'vault' && selectedNoteId && editorMode === 'view' && (
            <NoteView noteId={selectedNoteId} />
          )}
          {activeView === 'vault' && selectedNoteId && editorMode === 'edit' && (
            <NoteEditor noteId={selectedNoteId} />
          )}
          {activeView === 'vault' && !selectedNoteId && (
            <div className="flex items-center justify-center h-full text-muted-foreground">
              Select a note to view or edit
            </div>
          )}
          {activeView === 'exchange' && <ExchangeWorkspace />}
          {activeView === 'research' && <ResearchWorkspace />}
          {activeView === 'settings' && <SettingsWorkspace />}
        </main>
      </div>
    </div>
  );
}
