import { QueryClientProvider } from '@tanstack/react-query';
import { queryClient } from './api/client';
import { WorkspaceShell } from './components/layout/WorkspaceShell';

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <WorkspaceShell />
    </QueryClientProvider>
  );
}
