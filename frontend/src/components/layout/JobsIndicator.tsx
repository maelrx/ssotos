import { useJobs } from '../../hooks/useJobs';

export function JobsIndicator() {
  const { data: jobsData } = useJobs();

  const running = jobsData?.jobs.filter(j => j.status === 'running').length ?? 0;

  return (
    <button className="flex items-center gap-1.5 px-2 py-1 rounded hover:bg-muted">
      <span className="relative">
        <span className="text-xs">Jobs</span>
        {running > 0 && (
          <span className="absolute -top-1 -right-2 w-2 h-2 bg-orange-500 rounded-full" />
        )}
      </span>
      {running > 0 && <span className="text-xs text-orange-600">{running}</span>}
    </button>
  );
}
