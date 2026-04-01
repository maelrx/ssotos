import type { ResearchJob } from '../../api/research';

interface JobListProps {
  jobs: ResearchJob[];
  selectedJobId: string | null;
  onSelect: (id: string) => void;
}

export function JobList({ jobs, selectedJobId, onSelect }: JobListProps) {
  if (jobs.length === 0) {
    return (
      <p className="text-sm text-muted-foreground">No research jobs yet.</p>
    );
  }

  return (
    <div className="space-y-1">
      {jobs.map(job => (
        <button
          key={job.id}
          onClick={() => onSelect(job.id)}
          className={`w-full text-left px-3 py-2 rounded text-sm transition-colors ${
            selectedJobId === job.id
              ? 'bg-primary text-primary-foreground'
              : 'hover:bg-muted'
          }`}
        >
          <div className="truncate font-medium">{job.query}</div>
          <div className="flex items-center gap-2 mt-1">
            <span className={`text-xs px-1.5 py-0.5 rounded ${
              job.status === 'completed' ? 'bg-green-100 text-green-700' :
              job.status === 'failed' ? 'bg-red-100 text-red-700' :
              job.status === 'running' || job.status === 'crawling' || job.status === 'synthesizing' ? 'bg-orange-100 text-orange-700' :
              'bg-gray-100 text-gray-600'
            }`}>
              {job.status}
            </span>
          </div>
        </button>
      ))}
    </div>
  );
}
