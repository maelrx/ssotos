import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { exchangeApi } from '../api/endpoints';

export function useProposals(params?: { state?: string; target_domain?: string }) {
  return useQuery({
    queryKey: ['proposals', params],
    queryFn: () => exchangeApi.listProposals(params),
  });
}

export function useProposal(id: string) {
  return useQuery({
    queryKey: ['proposal', id],
    queryFn: () => exchangeApi.getProposal(id),
    enabled: !!id,
  });
}

export function useApproveProposal() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, note }: { id: string; note?: string }) =>
      exchangeApi.approveProposal(id, note),
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: ['proposal', id] });
      queryClient.invalidateQueries({ queryKey: ['proposals'] });
    },
  });
}

export function useRejectProposal() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, reason }: { id: string; reason: string }) =>
      exchangeApi.rejectProposal(id, reason),
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: ['proposal', id] });
      queryClient.invalidateQueries({ queryKey: ['proposals'] });
    },
  });
}
