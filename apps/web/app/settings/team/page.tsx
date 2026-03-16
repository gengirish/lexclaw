export default function TeamPage() {
  return (
    <div className="grid two">
      <section className="card">
        <p className="eyebrow">Team</p>
        <h1>Members and roles</h1>
        <p>Control Owner, Admin, and Operator permissions across cloud and on-prem workflows.</p>
      </section>
      <section className="card">
        <p className="eyebrow">Recommended model</p>
        <ul>
          <li>Owner: billing, keys, policy exceptions.</li>
          <li>Admin: skills, node operations, user management.</li>
          <li>Operator: runbooks, approvals, and monitoring.</li>
        </ul>
      </section>
    </div>
  );
}
