import { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { copilotApi, ProposePatchResponse } from '../../api/copilot';
import { FileDiff } from 'lucide-react';

interface CopilotProposalProps {
  noteId: string;
}

export function CopilotProposal({ noteId }: CopilotProposalProps) {
  const [instruction, setInstruction] = useState('');
  const [proposal, setProposal] = useState<ProposePatchResponse | null>(null);

  const patchMutation = useMutation({
    mutationFn: (instruction: string) => copilotApi.proposePatch(noteId, instruction),
    onSuccess: (data) => setProposal(data),
  });

  return (
    <div className="p-4 space-y-4">
      {!proposal ? (
        <>
          {/* Instruction input */}
          <div className="space-y-2">
            <label className="text-xs font-medium text-muted-foreground">
              Describe the change you'd like to propose
            </label>
            <textarea
              value={instruction}
              onChange={(e) => setInstruction(e.target.value)}
              placeholder="e.g., Add a section about deployment best practices..."
              className="w-full resize-none rounded border p-3 text-sm min-h-[80px]"
            />
          </div>

          {/* Generate button */}
          <button
            onClick={() => patchMutation.mutate(instruction)}
            disabled={!instruction.trim() || patchMutation.isPending}
            className="w-full flex items-center justify-center gap-2 px-4 py-2 rounded bg-primary text-primary-foreground hover:bg-primary/90 disabled:opacity-50 text-sm font-medium transition-colors"
          >
            <FileDiff className="w-4 h-4" />
            {patchMutation.isPending ? 'Generating patch...' : 'Generate Patch'}
          </button>

          {patchMutation.isError && (
            <div className="bg-destructive/10 text-destructive rounded-lg p-3 text-sm">
              Couldn't generate patch. Try again.
            </div>
          )}
        </>
      ) : (
        <>
          {/* Diff viewer */}
          <div className="space-y-2">
            <div className="text-xs font-medium text-muted-foreground flex items-center gap-1">
              <FileDiff className="w-3.5 h-3.5" />
              Generated Diff
            </div>
            <pre className="bg-muted rounded p-3 text-xs overflow-auto max-h-64 font-mono whitespace-pre-wrap">
              {proposal.diff}
            </pre>
          </div>

          {/* Submit CTA */}
          <div className="border rounded-lg p-4 space-y-3">
            <p className="text-xs text-muted-foreground">
              This patch proposal was submitted to the Exchange Zone for your review.
            </p>
            <button
              onClick={() => setProposal(null)}
              className="w-full flex items-center justify-center gap-2 px-4 py-2 rounded border hover:bg-muted text-sm transition-colors"
            >
              Done
            </button>
          </div>

          {/* Proposal ID */}
          <p className="text-xs text-muted-foreground text-center">
            Proposal created: {proposal.proposal_id}
          </p>
        </>
      )}
    </div>
  );
}
