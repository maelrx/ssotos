import { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { copilotApi, SuggestLinksResponse, SuggestTagsResponse, SuggestStructureResponse, NoteExplanationResponse, NoteSummaryResponse } from '../../api/copilot';
import { Lightbulb, Link2, Tags, LayoutList, FileText } from 'lucide-react';

interface CopilotSuggestionsProps {
  noteId: string;
}

type Result =
  | { kind: 'explanation'; data: NoteExplanationResponse }
  | { kind: 'summary'; data: NoteSummaryResponse }
  | { kind: 'links'; data: SuggestLinksResponse }
  | { kind: 'tags'; data: SuggestTagsResponse }
  | { kind: 'structure'; data: SuggestStructureResponse };

export function CopilotSuggestions({ noteId }: CopilotSuggestionsProps) {
  const [result, setResult] = useState<Result | null>(null);

  const explainMutation = useMutation({
    mutationFn: () => copilotApi.explain(noteId),
    onSuccess: (data) => setResult({ kind: 'explanation', data }),
  });

  const summarizeMutation = useMutation({
    mutationFn: () => copilotApi.summarize(noteId),
    onSuccess: (data) => setResult({ kind: 'summary', data }),
  });

  const linksMutation = useMutation({
    mutationFn: () => copilotApi.suggestLinks(noteId),
    onSuccess: (data) => setResult({ kind: 'links', data }),
  });

  const tagsMutation = useMutation({
    mutationFn: () => copilotApi.suggestTags(noteId),
    onSuccess: (data) => setResult({ kind: 'tags', data }),
  });

  const structureMutation = useMutation({
    mutationFn: () => copilotApi.suggestStructure(noteId),
    onSuccess: (data) => setResult({ kind: 'structure', data }),
  });

  const actions = [
    { key: 'explain', label: 'Explain', icon: FileText, mutation: explainMutation },
    { key: 'summarize', label: 'Summarize', icon: FileText, mutation: summarizeMutation },
    { key: 'links', label: 'Suggest Links', icon: Link2, mutation: linksMutation },
    { key: 'tags', label: 'Suggest Tags', icon: Tags, mutation: tagsMutation },
    { key: 'structure', label: 'Suggest Structure', icon: LayoutList, mutation: structureMutation },
  ];

  const isLoading = actions.some((a) => a.mutation.isPending);

  return (
    <div className="p-4 space-y-4">
      {/* Action buttons grid */}
      <div className="grid grid-cols-2 gap-2">
        {actions.map((action) => (
          <button
            key={action.key}
            onClick={() => action.mutation.mutate()}
            disabled={isLoading}
            className="flex items-center gap-2 px-3 py-2 text-xs rounded border hover:bg-muted disabled:opacity-50 transition-colors"
          >
            <action.icon className="w-3.5 h-3.5" />
            {action.label}
          </button>
        ))}
      </div>

      {/* Result card */}
      {result && (
        <div className="border rounded-lg p-4 space-y-3">
          <div className="flex items-center gap-2 text-xs font-medium text-muted-foreground">
            <Lightbulb className="w-3.5 h-3.5" />
            Result
          </div>
          {result.kind === 'explanation' && (
            <div className="prose prose-sm max-w-none">{result.data.markdown}</div>
          )}
          {result.kind === 'summary' && (
            <div>
              <div className="prose prose-sm max-w-none">{result.data.markdown}</div>
              {result.data.key_points.length > 0 && (
                <ul className="mt-2 space-y-1 text-sm">
                  {result.data.key_points.map((p, i) => (
                    <li key={i} className="text-muted-foreground">• {p}</li>
                  ))}
                </ul>
              )}
            </div>
          )}
          {result.kind === 'links' && (
            <ul className="space-y-2 text-sm">
              {result.data.suggestions.map((s, i) => (
                <li key={i} className="border rounded p-2">
                  <div className="font-medium">{s.target_title}</div>
                  <div className="text-xs text-muted-foreground">{s.target_note_path}</div>
                  <div className="text-xs text-muted-foreground mt-1">{s.reason}</div>
                </li>
              ))}
            </ul>
          )}
          {result.kind === 'tags' && (
            <ul className="space-y-2 text-sm">
              {result.data.suggestions.map((s, i) => (
                <li key={i} className="flex items-center gap-2">
                  <span className="px-1.5 py-0.5 bg-muted rounded text-xs">{s.tag}</span>
                  <span className="text-xs text-muted-foreground">
                    {s.confidence.toFixed(0)}% — {s.reason}
                  </span>
                </li>
              ))}
            </ul>
          )}
          {result.kind === 'structure' && (
            <ul className="space-y-2 text-sm">
              {result.data.suggestions.map((s, i) => (
                <li key={i} className="border rounded p-2">
                  <div className="flex items-center gap-2">
                    <span className="px-1.5 py-0.5 bg-muted rounded text-xs">{s.type.replace('_', ' ')}</span>
                    <span className="text-xs text-muted-foreground">{s.location}</span>
                  </div>
                  <div className="mt-1 text-xs">{s.issue}</div>
                  <div className="mt-1 text-xs text-muted-foreground">→ {s.suggestion}</div>
                </li>
              ))}
            </ul>
          )}
        </div>
      )}

      {result && (
        <button
          onClick={() => setResult(null)}
          className="w-full text-xs text-muted-foreground hover:text-foreground"
        >
          Clear result
        </button>
      )}
    </div>
  );
}
