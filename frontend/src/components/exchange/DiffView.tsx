import { useState } from 'react';
import { useProposal, useApproveProposal, useRejectProposal } from '../../hooks/useProposals';

interface DiffViewProps {
  proposalId: string;
}

export function DiffView({ proposalId }: DiffViewProps) {
  const { data: proposal, refetch } = useProposal(proposalId);
  const [loading, setLoading] = useState(false);

  const approveMutation = useApproveProposal();
  const rejectMutation = useRejectProposal();

  const handleApprove = async () => {
    setLoading(true);
    try {
      await approveMutation.mutateAsync({ id: proposalId });
      refetch();
    } finally {
      setLoading(false);
    }
  };

  const handleReject = async () => {
    const reason = prompt('Rejection reason:');
    if (!reason) return;
    setLoading(true);
    try {
      await rejectMutation.mutateAsync({ id: proposalId, reason });
      refetch();
    } finally {
      setLoading(false);
    }
  };

  if (!proposal) return <div className="p-4">Loading...</div>;

  return (
    <div className="flex flex-col h-full">
      <div className="border-b p-4 flex items-center justify-between">
        <div>
          <h3 className="font-semibold">{proposal.target_path}</h3>
          <p className="text-sm text-muted-foreground">
            {proposal.proposal_type} · {proposal.state}
          </p>
        </div>
        {proposal.state === 'awaiting_review' && (
          <div className="flex gap-2">
            <button
              onClick={handleReject}
              disabled={loading}
              className="px-3 py-1.5 text-sm rounded border border-red-200 text-red-600 hover:bg-red-50 disabled:opacity-50"
            >
              Reject
            </button>
            <button
              onClick={handleApprove}
              disabled={loading}
              className="px-3 py-1.5 text-sm rounded bg-green-600 text-white hover:bg-green-700 disabled:opacity-50"
            >
              Approve
            </button>
          </div>
        )}
      </div>
      <div className="flex-1 overflow-auto p-4">
        <pre className="text-sm font-mono bg-muted p-4 rounded">
          {JSON.stringify(proposal, null, 2)}
        </pre>
      </div>
    </div>
  );
}
