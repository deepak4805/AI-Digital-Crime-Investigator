function Footer() {
  return (
    <footer className="footer">
      <div className="footer-inner">
        <div className="footer-brand">
          <div className="footer-logo">
            <span>🛡️</span> AIDCI
          </div>
          <p>
            AI Digital Crime Investigator — A simple, powerful tool to analyze digital evidence, uncover scams, and generate investigation reports.
          </p>
        </div>

        <div className="footer-links">
          <h4>Quick Links</h4>
          <a href="#how-it-works">How It Works</a>
          <a href="#features">Features</a>
          <a href="#scams">What We Detect</a>
          <a href="/login">Investigator Login</a>
        </div>
      </div>

      <div className="footer-bottom">
        <p>© 2026 AI Digital Crime Investigator (AIDCI). Easy & Smart Digital Forensics.</p>
      </div>
    </footer>
  );
}

export default Footer;
