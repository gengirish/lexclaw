export default function NodesPage() {
  return (
    <div className="grid two">
      <section className="card">
        <p className="eyebrow">On-prem runtime</p>
        <h1>Node management</h1>
        <p>Monitor runtime health, sync posture, and policy conformance.</p>
      </section>
      <section className="card">
        <p className="eyebrow">Connector coverage</p>
        <ul>
          <li>Node registration and token issuance</li>
          <li>Heartbeat and runtime version tracking</li>
          <li>Policy pull and entitlement sync</li>
          <li>Redacted telemetry ingestion only</li>
        </ul>
      </section>
    </div>
  );
}
