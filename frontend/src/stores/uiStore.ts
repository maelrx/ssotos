import { create } from 'zustand';

interface UIState {
  // Sidebar
  sidebarOpen: boolean;
  toggleSidebar: () => void;

  // Active view
  activeView: 'vault' | 'exchange' | 'research' | 'settings';
  setActiveView: (view: UIState['activeView']) => void;

  // Selected note
  selectedNoteId: string | null;
  setSelectedNoteId: (id: string | null) => void;

  // Editor mode
  editorMode: 'edit' | 'view';
  setEditorMode: (mode: UIState['editorMode']) => void;

  // Jobs indicator
  activeJobCount: number;
  setActiveJobCount: (count: number) => void;

  // Copilot panel
  copilotPanelOpen: boolean;
  copilotActiveTab: 'chat' | 'suggestions' | 'proposal';
  toggleCopilotPanel: () => void;
  setCopilotActiveTab: (tab: UIState['copilotActiveTab']) => void;
}

export const useUIStore = create<UIState>((set) => ({
  sidebarOpen: true,
  toggleSidebar: () => set((s) => ({ sidebarOpen: !s.sidebarOpen })),

  activeView: 'vault',
  setActiveView: (view) => set({ activeView: view }),

  selectedNoteId: null,
  setSelectedNoteId: (id) => set({ selectedNoteId: id }),

  editorMode: 'view',
  setEditorMode: (mode) => set({ editorMode: mode }),

  activeJobCount: 0,
  setActiveJobCount: (count) => set({ activeJobCount: count }),

  copilotPanelOpen: false,
  copilotActiveTab: 'suggestions',
  toggleCopilotPanel: () => set((s) => ({ copilotPanelOpen: !s.copilotPanelOpen })),
  setCopilotActiveTab: (tab) => set({ copilotActiveTab: tab }),
}));
