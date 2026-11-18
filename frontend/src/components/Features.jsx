function Features() {
  const features = [
    {
      icon: "📷",
      title: "Automatic Image Text Reader (OCR)",
      desc: "Takes screenshots or photos and reads the text automatically. You never have to re-type long messages.",
    },
    {
      icon: "🧠",
      title: "Smart Scam & Fraud Detector",
      desc: "Powered by Google Gemini AI to catch fake bank notices, urgent threats, and trick messages.",
    },
    {
      icon: "🔗",
      title: "Find Connected Clues",
      desc: "Automatically shows if the same phone number or UPI ID was used in multiple different cases.",
    },
    {
      icon: "⏱️",
      title: "Timeline of Events",
      desc: "Arranges all evidence and messages into a clean timeline so you can see exactly when everything happened.",
    },
    {
      icon: "📄",
      title: "Instant Formal PDF Reports",
      desc: "Generates clean, professional investigation reports with evidence lists, risk scores, and findings.",
    },
    {
      icon: "🔒",
      title: "Safe & Private Storage",
      desc: "All evidence is securely hashed with SHA-256 and safely stored in your private investigation account.",
    },
  ];

  return (
    <section id="features" className="section-container bg-panel">
      <div className="section-title-box">
        <p className="sub-heading">POWERFUL TOOLS</p>
        <h2>Everything You Need to Solve Digital Crimes</h2>
        <p className="sub-text">
          Designed to be simple for beginners while having professional tools for investigators.
        </p>
      </div>

      <div className="features-grid">
        {features.map((f, i) => (
          <div className="feature-box" key={i}>
            <div className="feature-icon">{f.icon}</div>
            <h3>{f.title}</h3>
            <p>{f.desc}</p>
          </div>
        ))}
      </div>
    </section>
  );
}

export default Features;
