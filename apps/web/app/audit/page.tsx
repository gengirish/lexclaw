export default function AuditPage() {
  return (
    <section className="card">
      <h1>Audit Metadata Viewer</h1>
      <p>Phase 4 audit chain endpoints are active in the API.</p>
      <ul>
        <li>Node audit metadata ingestion (`/v1/nodes/audit-events`)</li>
        <li>Org audit event listing (`/v1/orgs/{'{org_id}'}/audit-events`)</li>
        <li>Hash-linked chain verification metadata</li>
      </ul>
    </section>
  );
}
