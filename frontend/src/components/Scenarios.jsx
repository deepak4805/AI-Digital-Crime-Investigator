function Scenarios() {
  const scams = [
    {
      icon: "🏦",
      title: "Fake Bank & KYC Warnings",
      desc: "Messages claiming your bank account or SIM card will be blocked unless you verify immediately.",
      clues: "Finds fake links, spoofed sender IDs, and extracted bank accounts.",
    },
    {
      icon: "💳",
      title: "UPI & QR Code Money Scams",
      desc: "Fraudulent collect requests or fake prize winnings asking you to enter your UPI PIN.",
      clues: "Extracts suspicious UPI IDs (@okaxis, @ybl) and demanded amounts.",
    },
    {
      icon: "🔗",
      title: "Fake Websites & Phishing Links",
      desc: "Cloned login pages disguised as banks, government portals, or utility bills.",
      clues: "Flags suspicious web domains (.xyz, .top) and unverified links.",
    },
    {
      icon: "👮",
      title: "Police & Official Impersonation",
      desc: "Threatening messages pretending to be from police, CBI, or courier customs demanding money.",
      clues: "Highlights fake officer names, coercive language, and intimidation flags.",
    },
  ];

  return (
    <section id="scams" className="section-container">
      <div className="section-title-box">
        <p className="sub-heading">WHAT WE CATCH</p>
        <h2>Common Online Crimes AIDCI Detects</h2>
        <p className="sub-text">
          Our AI is trained to recognize the tricks and patterns used by digital scammers.
        </p>
      </div>

      <div className="scams-grid">
        {scams.map((item, index) => (
          <div className="scam-card" key={index}>
            <div className="scam-icon">{item.icon}</div>
            <h3>{item.title}</h3>
            <p className="scam-desc">{item.desc}</p>
            <div className="scam-clues">
              <strong>🔍 What AI Extracts:</strong> {item.clues}
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}

export default Scenarios;
