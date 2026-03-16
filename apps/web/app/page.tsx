export default function DashboardPage() {
  return (
    <div className="grid">
      <section className="card">
        <p className="eyebrow">Overview</p>
        <h1>LexClaw Control Plane</h1>
        <p>
          Manage organization access, billing, skills, node sync, and metadata-only auditing from one
          workspace.
        </p>
      </section>

      <section className="grid two">
        <article className="card">
          <p className="eyebrow">Node Fleet</p>
          <p className="metric">2</p>
          <p className="muted">1 healthy, 1 needs heartbeat</p>
        </article>
        <article className="card">
          <p className="eyebrow">Entitled Skills</p>
          <p className="metric">5</p>
          <p className="muted">3 production skills + 2 stubs</p>
        </article>
      </section>

      <section className="card">
        <p className="eyebrow">Next Actions</p>
        <ul>
          <li>Review node policy pulls and heartbeat timing.</li>
          <li>Verify billing webhook signature key in production environment.</li>
          <li>Enable operator reviews for high-risk skill executions.</li>
        </ul>
      </section>
    </div>
  );
}
