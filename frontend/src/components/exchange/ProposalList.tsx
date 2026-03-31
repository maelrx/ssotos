interface Proposal {
  id: string;
  proposal_type: string;
  state: string;
  actor: string;
  target_path: string;
  created_at: string;
}

interface ProposalListProps {
  proposals: Proposal[];
  selectedId: string | null;
  onSelect: (id: string) => void;
}

export function ProposalList({ proposals, selectedId, onSelect }: ProposalListProps) {
  const stateColors: Record<string, string> = {
    draft: 'bg-gray-100',
    generated: 'bg-blue-100',
    awaiting_review: 'bg-yellow-100',
    approved: 'bg-green-100',
    rejected: 'bg-red-100',
    applied: 'bg-green-200',
    failed: 'bg-red-200',
  };

  return (
    <div className="divide-y">
      {proposals.map(p => (
        <button
          key={p.id}
          onClick={() => onSelect(p.id)}
          className={`w-full text-left p-3 hover:bg-muted transition-colors ${
            selectedId === p.id ? 'bg-muted' : ''
          }`}
        >
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium">{p.target_path?.split('/').pop()}</span>
            <span className={`text-xs px-1.5 py-0.5 rounded ${stateColors[p.state] || ''}`}>
              {p.state}
            </span>
          </div>
          <div className="text-xs text-muted-foreground mt-1">
            by {p.actor} · {new Date(p.created_at).toLocaleDateString()}
          </div>
        </button>
      ))}
    </div>
  );
}
