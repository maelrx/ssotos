import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { vaultApi } from '../api/endpoints';
import type { NoteCreateRequest, NoteUpdateRequest } from '../types/note';

export function useNotes(params?: { page?: number; limit?: number; path?: string }) {
  return useQuery({
    queryKey: ['notes', params],
    queryFn: () => vaultApi.listNotes(params),
  });
}

export function useNote(noteId: string) {
  return useQuery({
    queryKey: ['note', noteId],
    queryFn: () => vaultApi.getNote(noteId),
    enabled: !!noteId,
  });
}

export function useNotesByPath(path: string) {
  return useQuery({
    queryKey: ['note', 'path', path],
    queryFn: () => vaultApi.getNoteByPath(path),
  });
}

export function useSearchNotes(query: string) {
  return useQuery({
    queryKey: ['notes', 'search', query],
    queryFn: () => vaultApi.searchNotes(query),
    enabled: query.length > 0,
  });
}

export function useCreateNote() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: NoteCreateRequest) => vaultApi.createNote(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['notes'] });
    },
  });
}

export function useUpdateNote() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ noteId, data }: { noteId: string; data: NoteUpdateRequest }) =>
      vaultApi.updateNote(noteId, data),
    onSuccess: (_, { noteId }) => {
      queryClient.invalidateQueries({ queryKey: ['note', noteId] });
      queryClient.invalidateQueries({ queryKey: ['notes'] });
    },
  });
}

export function useDeleteNote() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (noteId: string) => vaultApi.deleteNote(noteId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['notes'] });
    },
  });
}
