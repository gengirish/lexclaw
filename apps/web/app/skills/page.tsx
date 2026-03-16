export default function SkillsPage() {
  return (
    <div className="grid two">
      <section className="card">
        <p className="eyebrow">Marketplace</p>
        <h1>Skills catalog</h1>
        <p>Purchase and manage premium legal skills by organization entitlement.</p>
      </section>
      <section className="card">
        <p className="eyebrow">Current capabilities</p>
        <ul>
          <li>Catalog list/detail APIs</li>
          <li>Entitlement issuance on purchase</li>
          <li>License issue/rotate/validate endpoints</li>
        </ul>
      </section>
    </div>
  );
}
