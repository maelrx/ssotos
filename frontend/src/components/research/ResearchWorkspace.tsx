import { useJobs } from '../../hooks/useJobs';
import { JobStatus } from './JobStatus';

export function ResearchWorkspace() {
  const { data, isLoading } = useJobs({});

  const runningJobs = data?.jobs.filter(j => j.status === 'running') ?? [];
  const completedJobs = data?.jobs.filter(j => j.status === 'completed') ?? [];
  const failedJobs = data?.jobs.filter(j => j.status === 'failed') ?? [];

  if (isLoading) {
    return <div className="p-4">Loading...</div>;
  }

  return (
    <div className="p-4">
      <h2 className="text-lg font-semibold mb-4">Research Jobs</h2>

      {runningJobs.length > 0 && (
        <section className="mb-6">
          <h3 className="text-sm font-medium text-orange-600 mb-2">Running ({runningJobs.length})</h3>
          <div className="space-y-2">
            {runningJobs.map(job => (
              <JobStatus key={job.id} job={job} />
            ))}
          </div>
        </section>
      )}

      <section className="mb-6">
        <h3 className="text-sm font-medium mb-2">Completed ({completedJobs.length})</h3>
        <div className="space-y-2">
          {completedJobs.slice(0, 10).map(job => (
            <JobStatus key={job.id} job={job} />
          ))}
        </div>
      </section>

      {failedJobs.length > 0 && (
        <section>
          <h3 className="text-sm font-medium text-red-600 mb-2">Failed ({failedJobs.length})</h3>
          <div className="space-y-2">
            {failedJobs.map(job => (
              <JobStatus key={job.id} job={job} />
            ))}
          </div>
        </section>
      )}
    </div>
  );
}
