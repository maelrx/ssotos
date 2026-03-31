import { useProposals } from '../../hooks/useProposals';
import { ProposalList } from './ProposalList';
import { DiffView } from './DiffView';
import { useState } from 'react';

export function ExchangeWorkspace() {
  const { data, isLoading } = useProposals();
  const [selectedProposalId, setSelectedProposalId] = useState<string | null>(null);

  if (isLoading) {
    return <div className="p-4">Loading...</div>;
  }

  return (
    <div className="flex h-full">
      <div className="w-80 border-r overflow-auto">
        <div className="p-3 border-b">
          <h2 className="font-semibold">Proposals</h2>
          <div className="text-xs text-muted-foreground">
            {data?.proposals.length ?? 0} proposals
          </div>
        </div>
        <ProposalList
          proposals={data?.proposals ?? []}
          selectedId={selectedProposalId}
          onSelect={setSelectedProposalId}
        />
      </div>
      <div className="flex-1 overflow-auto">
        {selectedProposalId ? (
          <DiffView proposalId={selectedProposalId} />
        ) : (
          <div className="flex items-center justify-center h-full text-muted-foreground">
            Select a proposal to review
          </div>
        )}
      </div>
    </div>
  );
}
