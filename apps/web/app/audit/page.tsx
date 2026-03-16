export default function AuditPage() {
  return (
    <div className="grid two">
      <section className="card">
        <p className="eyebrow">Audit</p>
        <h1>Metadata chain viewer</h1>
        <p>Inspect immutable, hash-linked audit metadata for executions and node actions.</p>
      </section>
      <section className="card">
        <p className="eyebrow">Chain endpoints</p>
        <ul>
          <li>Node ingest: <code>/v1/nodes/audit-events</code></li>
          <li>Org view: <code>/v1/orgs/{'{org_id}'}/audit-events</code></li>
          <li>Hash chain continuity verification</li>
        </ul>
      </section>
    </div>
  );
}
