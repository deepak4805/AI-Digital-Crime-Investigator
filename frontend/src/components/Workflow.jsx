function Workflow() {
  const steps = [
    {
      step: "1",
      icon: "📁",
      title: "Create a Case",
      description: "Give your investigation a simple name, like 'KYC WhatsApp Fraud'.",
    },
    {
      step: "2",
      icon: "📥",
      title: "Upload Evidence",
      description: "Drop screenshots, photos, PDFs, or paste suspicious chat messages.",
    },
    {
      step: "3",
      icon: "🧠",
      title: "AI Scans & Finds Clues",
      description: "AI reads the text, calculates risk score, and spots phones, UPI IDs, and scam tricks.",
    },
    {
      step: "4",
      icon: "📄",
      title: "Download PDF Report",
      description: "Get a formal, ready-to-print investigation report with one click.",
    },
  ];

  return (
    <section id="how-it-works" className="section-container">
      <div className="section-title-box">
        <p className="sub-heading">SIMPLE & FAST</p>
        <h2>How It Works in 4 Easy Steps</h2>
        <p className="sub-text">
          No complex tools needed. Anyone can start an investigation in seconds.
        </p>
      </div>

      <div className="steps-grid">
        {steps.map((item, index) => (
          <div className="step-card" key={index}>
            <div className="step-badge">{item.step}</div>
            <div className="step-icon">{item.icon}</div>
            <h3>{item.title}</h3>
            <p>{item.description}</p>
          </div>
        ))}
      </div>
    </section>
  );
}

export default Workflow;
