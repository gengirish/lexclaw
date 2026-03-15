export default function NodesPage() {
  return (
    <section className="card">
      <h1>Node Management</h1>
      <p>Phase 3 node connector endpoints are active in the API.</p>
      <ul>
        <li>Node registration with issued node token</li>
        <li>Heartbeat ingestion and status updates</li>
        <li>Policy pull + entitlement sync endpoints</li>
        <li>Redacted telemetry ingest pipeline</li>
      </ul>
    </section>
  );
}
