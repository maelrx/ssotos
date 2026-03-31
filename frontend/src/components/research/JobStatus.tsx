import type { Job } from '../../types/job';

interface JobStatusProps {
  job: Job;
}

export function JobStatus({ job }: JobStatusProps) {
  const statusColors: Record<string, string> = {
    pending: 'bg-gray-100 text-gray-600',
    running: 'bg-orange-100 text-orange-700',
    completed: 'bg-green-100 text-green-700',
    failed: 'bg-red-100 text-red-700',
  };

  return (
    <div className={`p-3 rounded border ${statusColors[job.status]}`}>
      <div className="flex items-center justify-between">
        <div>
          <span className="font-medium text-sm">{job.job_type}</span>
          <span className="text-xs ml-2 opacity-75">{job.id.slice(0, 8)}</span>
        </div>
        <span className="text-xs">{job.status}</span>
      </div>
      {job.error_message && (
        <p className="text-xs mt-1 opacity-75">{job.error_message}</p>
      )}
      <p className="text-xs mt-1 opacity-50">
        {new Date(job.created_at).toLocaleString()}
      </p>
    </div>
  );
}
