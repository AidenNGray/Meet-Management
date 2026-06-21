import React from 'react';
import { Outlet, NavLink, useNavigate } from 'react-router-dom';
import { Calendar, FileText, Users, LogOut, Activity } from 'lucide-react';
import { auth } from '../firebase';

export default function Dashboard() {
  const navigate = useNavigate();

  const handleLogout = async () => {
    try {
      await auth.signOut();
      navigate('/login');
    } catch (error) {
      console.error('Error logging out:', error);
      navigate('/login');
    }
  };

  const navLinkStyle = ({ isActive }) => ({
    display: 'flex',
    alignItems: 'center',
    padding: '0.75rem 1rem',
    borderRadius: '8px',
    color: isActive ? 'var(--text-color)' : 'var(--text-muted)',
    backgroundColor: isActive ? 'var(--bg-color-secondary)' : 'transparent',
    textDecoration: 'none',
    fontWeight: 500,
    gap: '0.75rem',
    transition: 'all 0.2s',
    marginBottom: '0.5rem',
  });

  return (
    <div style={{ display: 'flex', minHeight: '100vh', backgroundColor: 'var(--bg-color)' }}>
      {/* Sidebar */}
      <div className="glass-panel" style={{ width: '260px', padding: '2rem 1rem', display: 'flex', flexDirection: 'column', borderRight: '1px solid var(--border-color)', borderRadius: '0', borderLeft: 'none', borderTop: 'none', borderBottom: 'none' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', padding: '0 1rem', marginBottom: '3rem' }}>
          <Activity size={32} color="var(--primary-color)" />
          <h2 style={{ fontSize: '1.25rem', margin: 0, fontWeight: 700 }}>Coach Portal</h2>
        </div>

        <nav style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
          <NavLink to="/dashboard/meets" style={navLinkStyle}>
            <Calendar size={20} />
            Meets
          </NavLink>
          <NavLink to="/dashboard/generate" style={navLinkStyle}>
            <FileText size={20} />
            Heat Sheets
          </NavLink>
          <NavLink to="/dashboard/rosters" style={navLinkStyle}>
            <Users size={20} />
            Rosters
          </NavLink>
        </nav>

        <button onClick={handleLogout} className="btn btn-outline" style={{ display: 'flex', justifyContent: 'flex-start', color: 'var(--text-muted)', border: 'none' }}>
          <LogOut size={20} />
          Sign Out
        </button>
      </div>

      {/* Main Content Area */}
      <div style={{ flex: 1, padding: '3rem 4rem', overflowY: 'auto' }}>
        <Outlet />
      </div>
    </div>
  );
}
