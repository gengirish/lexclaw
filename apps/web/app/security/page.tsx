export default function SecurityPage() {
  return (
    <div className="grid two">
      <section className="card">
        <p className="eyebrow">Security</p>
        <h1>Controls and key lifecycle</h1>
        <p>Manage JWT signing materials, webhook secrets, and node token rotation practices.</p>
      </section>
      <section className="card">
        <p className="eyebrow">Hardening checklist</p>
        <ul>
          <li>Rotate signing and webhook keys on schedule</li>
          <li>Enforce least-privilege role assignments</li>
          <li>Verify no cloud legal-content persistence</li>
        </ul>
      </section>
    </div>
  );
}
