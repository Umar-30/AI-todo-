import { Link } from 'react-router-dom';

const LandingPage = () => {
  return (
    <div className="landing-page">
      <div className="landing-container">
        {/* Large App Name Heading */}
        <header className="landing-header">
          <h1 className="app-title neon-text">AI Todo Chatbot</h1>
        </header>

        <main className="landing-main">
          {/* Hero Section: Smart Task Manager text beside Chat Mockup */}
          <div className="hero-row">
            <div className="hero-text">
              <h2 className="smart-title">
                <span className="neon-text">Smart Task Manager</span>
              </h2>
              <p className="hero-subtitle subtle-text">Powered by AI</p>
              <p className="hero-description">
                Transform the way you manage tasks with our intelligent AI-powered chatbot.
                Simply speak or type your tasks naturally, and let our AI handle the rest.
              </p>
            </div>

            <div className="hero-visual">
              <div className="mockup-container">
                <div className="chat-mockup">
                  <div className="mockup-header">
                    <div className="mockup-dots">
                      <span className="dot red"></span>
                      <span className="dot yellow"></span>
                      <span className="dot green"></span>
                    </div>
                  </div>
                  <div className="mockup-content">
                    <div className="message ai-message">
                      "Hello! I'm your AI task assistant. What would you like to do today?"
                    </div>
                    <div className="message user-message">
                      "Add a meeting with John at 3 PM tomorrow"
                    </div>
                    <div className="message ai-message">
                      "✓ Added: Meeting with John on [date] at 3:00 PM"
                    </div>
                    <div className="input-bar">
                      <div className="voice-input">🎤</div>
                      <div className="text-input">Type or speak your task...</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Features Section with Get Started button on one side */}
          <div className="features-section">
            <div className="features-grid">
              <div className="feature-card">
                <div className="feature-icon">🎤</div>
                <h3>Voice Commands</h3>
                <p>Talk to your AI assistant to manage tasks hands-free</p>
              </div>

              <div className="feature-card">
                <div className="feature-icon">💬</div>
                <h3>Natural Language</h3>
                <p>Speak naturally - our AI understands context and intent</p>
              </div>

              <div className="feature-card">
                <div className="feature-icon">✅</div>
                <h3>Smart Organization</h3>
                <p>Automatically categorizes and prioritizes your tasks</p>
              </div>

              <div className="feature-card">
                <div className="feature-icon">📱</div>
                <h3>Fully Responsive</h3>
                <p>Works seamlessly on desktop, tablet, and mobile devices</p>
              </div>
            </div>

            <div className="cta-section">
              <Link to="/signup" className="cta-button primary">
                Get Started
                <span className="arrow">→</span>
              </Link>
              <p className="login-link">
                Already have an account? <Link to="/login">Sign in</Link>
              </p>
            </div>
          </div>
        </main>

        <footer className="landing-footer">
          <p>© 2026 AI Todo Chatbot. Simplify your productivity.</p>
        </footer>
      </div>
    </div>
  );
};

export default LandingPage;