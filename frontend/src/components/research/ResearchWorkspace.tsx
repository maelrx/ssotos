import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { researchApi } from '../../api/research';
import { JobList } from './JobList';
import { SourceList } from './SourceList';
import { SynthesisViewer } from './SynthesisViewer';

export function ResearchWorkspace() {
  const [selectedJobId, setSelectedJobId] = useState<string | null>(null);
  const [selectedJobQuery, setSelectedJobQuery] = useState<string>('');
  const [activeTab, setActiveTab] = useState<'sources' | 'synthesis' | 'blueprint'>('sources');

  const queryClient = useQueryClient();

  const { data: jobsData, isLoading } = useQuery({
    queryKey: ['research-jobs'],
    queryFn: researchApi.listJobs,
    refetchInterval: 5000,
  });

  const { data: selectedJob } = useQuery({
    queryKey: ['research-job', selectedJobId],
    queryFn: () => researchApi.getJob(selectedJobId!),
    enabled: !!selectedJobId,
    refetchInterval: 3000,
  });

  const cancelMutation = useMutation({
    mutationFn: (jobId: string) => researchApi.cancelJob(jobId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['research-jobs'] });
      queryClient.invalidateQueries({ queryKey: ['research-job', selectedJobId] });
    },
  });

  const retryMutation = useMutation({
    mutationFn: () => researchApi.createBrief({
      query: selectedJobQuery || 'Research',
      goal: 'Retry research',
      questions: [],
      scope: 'web',
      depth: 'surface',
      max_sources: 10,
    }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['research-jobs'] });
    },
  });

  const handleSelect = (id: string) => {
    const job = jobsData?.jobs.find(j => j.id === id);
    setSelectedJobQuery(job?.query ?? '');
    setSelectedJobId(id);
  };

  const jobs = jobsData?.jobs ?? [];
  const status = selectedJob?.status ?? 'pending';
  const resultState = selectedJob?.result_data?.state ?? status;
  const progress = resultState === 'completed' ? 100 :
    resultState === 'synthesizing' ? 80 :
    resultState === 'parsing' ? 60 :
    resultState === 'crawling' ? 40 :
    resultState === 'discovering' ? 20 :
    resultState === 'planning' ? 10 : 0;

  return (
    <div className="flex h-full">
      {/* Job list sidebar */}
      <div className="w-64 border-r p-4 flex flex-col">
        <h2 className="text-lg font-semibold mb-4">Research Jobs</h2>
        {isLoading ? (
          <p className="text-sm text-muted-foreground">Loading...</p>
        ) : (
          <div className="flex-1 overflow-auto">
            <JobList
              jobs={jobs}
              selectedJobId={selectedJobId}
              onSelect={handleSelect}
            />
          </div>
        )}
      </div>

      {/* Main content */}
      <div className="flex-1 overflow-auto p-6">
        {!selectedJobId ? (
          <div className="flex items-center justify-center h-full text-muted-foreground">
            Select a research job to view details
          </div>
        ) : (
          <div className="space-y-6">
            {/* Header */}
            <div className="flex items-center justify-between">
              <h1 className="text-2xl font-bold truncate">{selectedJob?.query ?? 'Research'}</h1>
              <div className="flex gap-2">
                <button
                  onClick={() => retryMutation.mutate()}
                  disabled={retryMutation.isPending}
                  className="px-3 py-1.5 text-sm rounded border hover:bg-muted disabled:opacity-50"
                >
                  Retry
                </button>
                <button
                  onClick={() => cancelMutation.mutate(selectedJobId)}
                  disabled={cancelMutation.isPending || resultState === 'completed' || resultState === 'failed'}
                  className="px-3 py-1.5 text-sm rounded border text-red-500 hover:bg-red-50 disabled:opacity-50"
                >
                  Cancel
                </button>
              </div>
            </div>

            {/* Progress bar */}
            <div className="space-y-1">
              <div className="flex justify-between text-sm">
                <span className="capitalize">{resultState}</span>
                <span>{progress}%</span>
              </div>
              <div className="h-2 bg-muted rounded">
                <div
                  className="h-full bg-primary rounded transition-all"
                  style={{ width: `${progress}%` }}
                />
              </div>
            </div>

            {/* Tabs */}
            <div className="border-b">
              <div className="flex gap-4">
                {(['sources', 'synthesis', 'blueprint'] as const).map(tab => (
                  <button
                    key={tab}
                    onClick={() => setActiveTab(tab)}
                    className={`px-1 py-2 text-sm font-medium border-b-2 transition-colors ${
                      activeTab === tab
                        ? 'border-primary text-primary'
                        : 'border-transparent text-muted-foreground hover:text-foreground'
                    }`}
                  >
                    {tab.charAt(0).toUpperCase() + tab.slice(1)}
                  </button>
                ))}
              </div>
            </div>

            {/* Tab content */}
            <div className="min-h-[200px]">
              {activeTab === 'sources' && (
                <SourceList jobId={selectedJobId} />
              )}
              {activeTab === 'synthesis' && (
                <SynthesisViewer jobId={selectedJobId} />
              )}
              {activeTab === 'blueprint' && (
                <p className="text-sm text-muted-foreground">
                  Blueprint view coming soon.
                </p>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
