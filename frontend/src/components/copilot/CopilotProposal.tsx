import { useState } from 'react';
import { useMutation, useQuery } from '@tanstack/react-query';
import { copilotApi, ProposePatchResult } from '../../api/copilot';
import { jobsApi } from '../../api/endpoints';
import { FileDiff } from 'lucide-react';

interface CopilotProposalProps {
  noteId: string;
}

export function CopilotProposal({ noteId }: CopilotProposalProps) {
  const [instruction, setInstruction] = useState('');
  const [proposalResult, setProposalResult] = useState<ProposePatchResult | null>(null);

  const patchMutation = useMutation({
    mutationFn: (instruction: string) => copilotApi.proposePatch(noteId, instruction),
  });

  // Poll for job status when we have a job_id
  const jobId = patchMutation.data?.job_id;

  const jobQuery = useQuery({
    queryKey: ['jobs', jobId],
    queryFn: () => jobsApi.getJob(jobId!),
    enabled: !!jobId && patchMutation.isSuccess,
    refetchInterval: (query) => {
      const status = query.state.data?.status;
      return status === 'completed' || status === 'failed' ? false : 1000;
    },
  });

  // When job completes, extract result_data and set proposal result
  const jobStatus = jobQuery.data?.status;
  if (jobStatus === 'completed' && jobQuery.data?.result_data && !proposalResult) {
    const result = jobQuery.data.result_data as unknown as ProposePatchResult;
    setProposalResult(result);
  }

  return (
    <div className="p-4 space-y-4">
      {!proposalResult ? (
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
            {patchMutation.isPending ? 'Enqueuing...' : jobQuery.isFetching ? 'Generating patch...' : 'Generate Patch'}
          </button>

          {patchMutation.isError && (
            <div className="bg-destructive/10 text-destructive rounded-lg p-3 text-sm">
              Couldn't enqueue patch job. Try again.
            </div>
          )}

          {jobQuery.isError && (
            <div className="bg-destructive/10 text-destructive rounded-lg p-3 text-sm">
              Failed to check job status. Try again.
            </div>
          )}

          {jobStatus === 'failed' && (
            <div className="bg-destructive/10 text-destructive rounded-lg p-3 text-sm">
              Job failed: {jobQuery.data?.error_message || 'Unknown error'}
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
              {proposalResult.diff}
            </pre>
          </div>

          {/* Submit CTA */}
          <div className="border rounded-lg p-4 space-y-3">
            <p className="text-xs text-muted-foreground">
              This patch proposal was submitted to the Exchange Zone for your review.
            </p>
            <button
              onClick={() => setProposalResult(null)}
              className="w-full flex items-center justify-center gap-2 px-4 py-2 rounded border hover:bg-muted text-sm transition-colors"
            >
              Done
            </button>
          </div>

          {/* Proposal ID */}
          <p className="text-xs text-muted-foreground text-center">
            Proposal created: {proposalResult.proposal_id}
          </p>
        </>
      )}
    </div>
  );
}
