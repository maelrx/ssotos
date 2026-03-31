import { JobsIndicator } from './JobsIndicator';

export function Header() {
  return (
    <header className="h-14 border-b flex items-center px-4 gap-4">
      <span className="font-semibold">Knowledge OS</span>
      <div className="flex-1">
        <input
          type="search"
          placeholder="Search notes..."
          className="w-full max-w-md px-3 py-1.5 rounded border"
        />
      </div>
      <JobsIndicator />
    </header>
  );
}
