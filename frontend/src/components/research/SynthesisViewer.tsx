import { useQuery } from '@tanstack/react-query';
import { researchApi } from '../../api/research';

interface SynthesisViewerProps {
  jobId: string;
}

export function SynthesisViewer({ jobId }: SynthesisViewerProps) {
  const { data, isLoading } = useQuery({
    queryKey: ['research-synthesis', jobId],
    queryFn: () => researchApi.getSynthesis(jobId),
    enabled: !!jobId,
    retry: false,
  });

  if (isLoading) return <div className="text-sm text-muted-foreground">Loading synthesis...</div>;
  if (!data?.content) return <p className="text-sm text-muted-foreground">No synthesis available yet.</p>;

  return (
    <div className="prose prose-sm max-w-none">
      <div dangerouslySetInnerHTML={{ __html: data.content.replace(/\n/g, '<br>') }} />
    </div>
  );
}
