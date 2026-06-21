import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { signInWithEmailAndPassword } from 'firebase/auth';
import { auth } from '../firebase';
import { Lock, Mail, Activity } from 'lucide-react';

export default function Login() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    const handleSuccess = async (emailToFetch) => {
      try {
        const { getCurrentUser } = await import('../services/api');
        const user = await getCurrentUser(emailToFetch);
        localStorage.setItem('user', JSON.stringify(user));
        navigate('/dashboard');
      } catch (fetchErr) {
        console.error(fetchErr);
        setError('User not found or not authorized.');
      }
    };

    try {

      // In development with dummy keys, we might just bypass this if it fails, 
      // but for now we attempt standard login.
      await signInWithEmailAndPassword(auth, email, password);
      await handleSuccess(email);
    } catch (err) {
      console.error(err);
      // Display the actual error code so we can debug, or bypass if it's a known dummy key issue
      if (err.code === 'auth/invalid-api-key' || err.code === 'auth/api-key-not-valid.-please-pass-a-valid-api-key.' || err.message?.includes('API key not valid')) {
        console.warn("Using dummy Firebase config. Bypassing login for development.");
        // Use the email entered to fetch the user
        await handleSuccess(email);
      } else {
        // Show the actual error to the user for debugging
        setError(`Failed to log in: ${err.code || err.message || 'Unknown error'}`);
      }
    }
    
    setLoading(false);
  };

  return (
    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '100vh', background: 'radial-gradient(circle at top right, var(--bg-color-secondary), var(--bg-color))' }}>
      <div className="glass-panel animate-fade-in" style={{ padding: '3rem', width: '100%', maxWidth: '420px', textAlign: 'center' }}>
        <div style={{ display: 'flex', justifyContent: 'center', marginBottom: '1.5rem' }}>
          <Activity size={48} color="var(--primary-color)" />
        </div>
        <h2 style={{ marginBottom: '0.5rem' }}>Coach Portal</h2>
        <p style={{ marginBottom: '2rem' }}>Sign in to manage your swim meets</p>

        {error && <div style={{ color: 'var(--danger-color)', marginBottom: '1rem', fontSize: '0.875rem' }}>{error}</div>}

        <form onSubmit={handleLogin} style={{ textAlign: 'left' }}>
          <div className="input-group">
            <label>Email</label>
            <div style={{ position: 'relative' }}>
              <Mail size={18} style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
              <input 
                type="email" 
                placeholder="coach@example.com" 
                style={{ width: '100%', paddingLeft: '2.5rem' }}
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
              />
            </div>
          </div>
          
          <div className="input-group">
            <label>Password</label>
            <div style={{ position: 'relative' }}>
              <Lock size={18} style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
              <input 
                type="password" 
                placeholder="••••••••" 
                style={{ width: '100%', paddingLeft: '2.5rem' }}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
              />
            </div>
          </div>

          <button type="submit" className="btn btn-primary" style={{ width: '100%', marginTop: '1rem' }} disabled={loading}>
            {loading ? 'Signing in...' : 'Sign In'}
          </button>
        </form>
      </div>
    </div>
  );
}
