import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { signUp } from '../services/authService';

interface FormData {
  email: string;
  password: string;
  name: string;
}

const SignupPage: React.FC = () => {
  const [formData, setFormData] = useState<FormData>({ email: '', password: '', name: '' });
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<boolean>(false);

  const navigate = useNavigate();

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      // Call the actual signup function
      const result = await signUp(formData.email, formData.password, formData.name);

      if (result.success) {
        // After successful signup, redirect to chat page
        setSuccess(true);
        setTimeout(() => {
          navigate('/chat');
        }, 1500);
      } else {
        setError(result.error || 'Signup failed');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred during signup');
    } finally {
      setLoading(false);
    }
  };

  if (success) {
    return (
      <div className="auth-success">
        <h2>Account Created!</h2>
        <p>Redirecting to chat...</p>
      </div>
    );
  }

  return (
    <div className="auth-container">
      <div className="auth-form">
        <h2>Create Account</h2>

        {error && <div className="error-message">{error}</div>}

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="name">Full Name</label>
            <input
              type="text"
              id="name"
              name="name"
              value={formData.name}
              onChange={handleChange}
              required
              className="auth-input"
            />
          </div>

          <div className="form-group">
            <label htmlFor="email">Email</label>
            <input
              type="email"
              id="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              required
              className="auth-input"
            />
          </div>

          <div className="form-group">
            <label htmlFor="password">Password</label>
            <input
              type="password"
              id="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              required
              minLength={6}
              className="auth-input"
            />
          </div>

          <button type="submit" disabled={loading} className="auth-button">
            {loading ? 'Creating Account...' : 'Sign Up'}
          </button>
        </form>

        <p className="auth-link">
          Already have an account? <Link to="/login">Log in</Link>
        </p>
      </div>

      <style>{`
        .auth-container {
          min-height: 100vh;
          display: flex;
          align-items: center;
          justify-content: center;
          background: linear-gradient(135deg, #0a0a0f 0%, #12121a 100%);
          padding: 20px;
        }

        .auth-form {
          width: 100%;
          max-width: 400px;
          padding: 2rem;
          background: #12121a;
          border-radius: 12px;
          box-shadow: 0 0 20px rgba(0, 255, 255, 0.2);
        }

        h2 {
          color: #00ffff;
          text-align: center;
          margin-bottom: 1.5rem;
        }

        .form-group {
          margin-bottom: 1rem;
        }

        label {
          display: block;
          margin-bottom: 0.5rem;
          color: #a0a0a0;
        }

        .auth-input {
          width: 100%;
          padding: 12px;
          background: #1a1a25;
          border: 1px solid #2a2a35;
          border-radius: 6px;
          color: #ffffff;
          font-size: 1rem;
        }

        .auth-input:focus {
          outline: none;
          border-color: #00ffff;
          box-shadow: 0 0 10px rgba(0, 255, 255, 0.3);
        }

        .auth-button {
          width: 100%;
          padding: 12px;
          background: linear-gradient(90deg, #00ffff, #00cccc);
          color: #0a0a0f;
          border: none;
          border-radius: 6px;
          font-size: 1rem;
          font-weight: bold;
          cursor: pointer;
          transition: all 0.3s ease;
        }

        .auth-button:hover:not(:disabled) {
          transform: translateY(-2px);
          box-shadow: 0 0 15px rgba(0, 255, 255, 0.4);
        }

        .auth-button:disabled {
          opacity: 0.6;
          cursor: not-allowed;
        }

        .auth-link {
          text-align: center;
          margin-top: 1.5rem;
          color: #a0a0a0;
        }

        .auth-link a {
          color: #00ffff;
          text-decoration: none;
          font-weight: bold;
        }

        .auth-link a:hover {
          text-decoration: underline;
        }

        .error-message {
          background: #ff4444;
          color: white;
          padding: 10px;
          border-radius: 6px;
          margin-bottom: 1rem;
          text-align: center;
        }

        .auth-success {
          min-height: 100vh;
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          background: linear-gradient(135deg, #0a0a0f 0%, #12121a 100%);
          text-align: center;
          color: #00ff88;
        }
      `}</style>
    </div>
  );
};

export default SignupPage;