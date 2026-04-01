import { useQuery } from '@tanstack/react-query';
import { researchApi, type SourceStatus } from '../../api/research';

interface SourceListProps {
  jobId: string;
}

export function SourceList({ jobId }: SourceListProps) {
  const { data, isLoading } = useQuery({
    queryKey: ['research-sources', jobId],
    queryFn: () => researchApi.getSources(jobId),
    enabled: !!jobId,
    refetchInterval: 5000,
  });

  if (isLoading) return <div className="text-sm text-muted-foreground">Loading sources...</div>;

  const sources: SourceStatus[] = data?.sources ?? [];

  if (sources.length === 0) {
    return <p className="text-sm text-muted-foreground">No sources found.</p>;
  }

  const statusColor = (status: SourceStatus['status']) => {
    switch (status) {
      case 'crawled': return 'text-green-600';
      case 'parsed': return 'text-blue-600';
      case 'failed': return 'text-red-600';
      default: return 'text-muted-foreground';
    }
  };

  return (
    <div className="space-y-2">
      <h3 className="text-sm font-medium">Sources ({sources.length})</h3>
      <div className="space-y-1">
        {sources.map(source => (
          <div key={source.source_id} className="flex items-start gap-2 text-sm">
            <span className={`mt-0.5 ${statusColor(source.status)}`}>
              {source.status === 'crawled' ? '✓' :
               source.status === 'parsed' ? '▣' :
               source.status === 'failed' ? '✗' : '○'}
            </span>
            <div className="flex-1 min-w-0">
              {source.url ? (
                <a
                  href={source.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-blue-600 hover:underline truncate block"
                >
                  {source.url}
                </a>
              ) : (
                <span className="text-muted-foreground truncate block">
                  {source.source_id}
                </span>
              )}
              {source.error && (
                <p className="text-xs text-red-500 mt-0.5">{source.error}</p>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
