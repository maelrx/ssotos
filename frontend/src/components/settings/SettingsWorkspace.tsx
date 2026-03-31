import { PolicyConfig } from './PolicyConfig';

export function SettingsWorkspace() {
  return (
    <div className="p-6">
      <h2 className="text-lg font-semibold mb-6">Settings</h2>
      <div className="max-w-2xl space-y-6">
        <section className="border rounded-lg p-4">
          <h3 className="font-medium mb-2">Policy Configuration</h3>
          <p className="text-sm text-muted-foreground mb-4">
            Manage policy rules that control what operations are allowed in each domain.
          </p>
          <PolicyConfig />
        </section>
      </div>
    </div>
  );
}
