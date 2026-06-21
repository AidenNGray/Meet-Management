import React, { useEffect, useState } from 'react';
import { getMeets } from '../services/api';
import { Calendar, Users, Hash } from 'lucide-react';

export default function Meets() {
  const [meets, setMeets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchMeets = async () => {
      try {
        const data = await getMeets();
        setMeets(data);
      } catch (err) {
        console.error("Failed to fetch meets:", err);
        setError('Failed to load meets from server. Make sure the backend is running.');
      } finally {
        setLoading(false);
      }
    };
    fetchMeets();
  }, []);

  if (loading) return <div className="animate-fade-in"><p>Loading meets...</p></div>;
  
  if (error) return <div className="animate-fade-in"><div className="glass-panel" style={{ padding: '2rem', color: 'var(--danger-color)' }}>{error}</div></div>;

  return (
    <div className="animate-fade-in">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '3rem' }}>
        <div>
          <h1>Upcoming Meets</h1>
          <p>View and manage all scheduled swim meets.</p>
        </div>
        <button className="btn btn-primary">
          + Create Meet
        </button>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))', gap: '2rem' }}>
        {meets.map((meet) => (
          <div key={meet.id} className="glass-panel" style={{ padding: '1.5rem', transition: 'transform 0.2s ease', cursor: 'pointer' }} onMouseEnter={(e) => e.currentTarget.style.transform = 'translateY(-4px)'} onMouseLeave={(e) => e.currentTarget.style.transform = 'translateY(0)'}>
            <h3 style={{ marginBottom: '1rem', color: 'var(--text-color)' }}>{meet.name}</h3>
            
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--text-muted)', fontSize: '0.875rem', marginBottom: '0.5rem' }}>
              <Hash size={16} />
              <span>Meet ID: {meet.id}</span>
            </div>
            
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--text-muted)', fontSize: '0.875rem', marginBottom: '0.5rem' }}>
              <Calendar size={16} />
              <span>{meet.date ? meet.date : 'Date TBD'}</span>
            </div>
            
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--text-muted)', fontSize: '0.875rem', marginBottom: '1.5rem' }}>
              <Users size={16} />
              <span>{meet.num_lanes} Lanes</span>
            </div>
            
            <div style={{ borderTop: '1px solid var(--border-color)', paddingTop: '1rem', display: 'flex', justifyContent: 'flex-end' }}>
              <button className="btn btn-outline" style={{ padding: '0.5rem 1rem', fontSize: '0.875rem' }}>
                View Details
              </button>
            </div>
          </div>
        ))}
      </div>
      
      {meets.length === 0 && (
        <div className="glass-panel" style={{ padding: '3rem', textAlign: 'center', color: 'var(--text-muted)' }}>
          <p>No meets found. Try creating one!</p>
        </div>
      )}
    </div>
  );
}
