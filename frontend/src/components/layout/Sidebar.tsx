import { useUIStore } from '../../stores/uiStore';
import { useNotes } from '../../hooks/useNotes';

const NAV_ITEMS = [
  { id: 'vault' as const, label: 'Vault', icon: '📁' },
  { id: 'exchange' as const, label: 'Exchange', icon: '🔄' },
  { id: 'research' as const, label: 'Research', icon: '🔬' },
  { id: 'settings' as const, label: 'Settings', icon: '⚙️' },
];

export function Sidebar() {
  const { activeView, setActiveView, sidebarOpen, setSelectedNoteId } = useUIStore();
  const { data: notesData } = useNotes({ limit: 100 });

  if (!sidebarOpen) return null;

  return (
    <aside className="w-56 border-r flex flex-col">
      {/* Navigation tabs */}
      <nav className="flex border-b">
        {NAV_ITEMS.map(item => (
          <button
            key={item.id}
            onClick={() => setActiveView(item.id)}
            className={`flex-1 py-2 text-xs flex flex-col items-center gap-0.5 ${
              activeView === item.id ? 'border-b-2 border-primary' : ''
            }`}
          >
            <span>{item.icon}</span>
            <span>{item.label}</span>
          </button>
        ))}
      </nav>

      {/* Vault tree (when on vault view) */}
      {activeView === 'vault' && (
        <div className="flex-1 overflow-auto p-2">
          <div className="text-xs font-semibold text-muted-foreground mb-1">Notes</div>
          <div className="space-y-0.5">
            {notesData?.notes.map(note => (
              <div
                key={note.id}
                className="text-sm px-2 py-1 rounded hover:bg-muted cursor-pointer truncate"
                title={note.path}
                onClick={() => setSelectedNoteId(note.id)}
              >
                {note.title || note.path.split('/').pop()}
              </div>
            ))}
          </div>
        </div>
      )}
    </aside>
  );
}
