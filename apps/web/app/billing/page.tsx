export default function BillingPage() {
  return (
    <div className="grid two">
      <section className="card">
        <p className="eyebrow">Billing</p>
        <h1>Subscription and invoices</h1>
        <p>Track plan status, upcoming renewal date, and invoice metadata.</p>
      </section>
      <section className="card">
        <p className="eyebrow">Integration status</p>
        <ul>
          <li>Checkout session API ready</li>
          <li>Webhook signature verification enabled</li>
          <li>Idempotent event dedupe enabled</li>
        </ul>
      </section>
    </div>
  );
}
