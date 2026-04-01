import { useUIStore } from '../../stores/uiStore';
import { CopilotChat } from './CopilotChat';
import { CopilotSuggestions } from './CopilotSuggestions';
import { CopilotProposal } from './CopilotProposal';
import { MessageSquare, Lightbulb, FileDiff } from 'lucide-react';

interface CopilotPanelProps {
  noteId: string;
}

export function CopilotPanel({ noteId }: CopilotPanelProps) {
  const { copilotActiveTab, setCopilotActiveTab } = useUIStore();

  const tabs = [
    { id: 'chat' as const, label: 'Chat', icon: MessageSquare },
    { id: 'suggestions' as const, label: 'Suggestions', icon: Lightbulb },
    { id: 'proposal' as const, label: 'Proposal', icon: FileDiff },
  ];

  return (
    <aside className="w-80 border-l bg-background flex flex-col h-full">
      {/* Header with tabs */}
      <div className="flex border-b">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setCopilotActiveTab(tab.id)}
            className={`flex-1 flex items-center justify-center gap-1.5 py-2.5 text-xs font-medium transition-colors ${
              copilotActiveTab === tab.id
                ? 'border-b-2 border-primary text-primary'
                : 'text-muted-foreground hover:text-foreground'
            }`}
          >
            <tab.icon className="w-3.5 h-3.5" />
            {tab.label}
          </button>
        ))}
      </div>

      {/* Tab content */}
      <div className="flex-1 overflow-auto">
        {copilotActiveTab === 'chat' && <CopilotChat noteId={noteId} />}
        {copilotActiveTab === 'suggestions' && <CopilotSuggestions noteId={noteId} />}
        {copilotActiveTab === 'proposal' && <CopilotProposal noteId={noteId} />}
      </div>
    </aside>
  );
}
