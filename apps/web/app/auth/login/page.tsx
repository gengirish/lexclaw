export default function LoginPage() {
  return (
    <section className="card">
      <p className="eyebrow">Authentication</p>
      <h1>Sign in</h1>
      <p>Use your organization credentials to access the control plane.</p>
      <div className="grid" style={{ marginTop: 16 }}>
        <label>
          <span className="muted">Work email</span>
          <input type="email" placeholder="name@firm.com" style={{ width: "100%", marginTop: 6, padding: 10 }} />
        </label>
        <label>
          <span className="muted">Password</span>
          <input type="password" placeholder="••••••••••" style={{ width: "100%", marginTop: 6, padding: 10 }} />
        </label>
        <button style={{ padding: "10px 14px", background: "#1d4ed8", color: "white", border: 0, borderRadius: 8 }}>
          Sign in
        </button>
      </div>
    </section>
  );
}
