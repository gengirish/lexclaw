export default function RegisterPage() {
  return (
    <section className="card">
      <p className="eyebrow">Onboarding</p>
      <h1>Create owner account</h1>
      <p>Set up your organization owner profile to start configuring billing and skills.</p>
      <div className="grid" style={{ marginTop: 16 }}>
        <label>
          <span className="muted">Full name</span>
          <input type="text" placeholder="Jane Doe" style={{ width: "100%", marginTop: 6, padding: 10 }} />
        </label>
        <label>
          <span className="muted">Work email</span>
          <input type="email" placeholder="owner@firm.com" style={{ width: "100%", marginTop: 6, padding: 10 }} />
        </label>
        <label>
          <span className="muted">Password</span>
          <input type="password" placeholder="Create strong password" style={{ width: "100%", marginTop: 6, padding: 10 }} />
        </label>
        <button style={{ padding: "10px 14px", background: "#0f766e", color: "white", border: 0, borderRadius: 8 }}>
          Create account
        </button>
      </div>
    </section>
  );
}
