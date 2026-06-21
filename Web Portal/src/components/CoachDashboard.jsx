import React, { useState, useEffect } from 'react';
import { getTeamSwimmers, addSwimmer, toggleSwimmerStatus } from '../services/api';
import { UserPlus, UserX, UserCheck, Plus, X } from 'lucide-react';

export default function CoachDashboard() {
  const [swimmers, setSwimmers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState('');
  const [showAddForm, setShowAddForm] = useState(false);
  const [newFirstName, setNewFirstName] = useState('');
  const [newLastName, setNewLastName] = useState('');
  const [newAge, setNewAge] = useState('');
  const [newGender, setNewGender] = useState('M');
  const [adding, setAdding] = useState(false);

  const user = JSON.parse(localStorage.getItem('user') || '{}');

  useEffect(() => {
    if (user.team_id) {
      fetchSwimmers();
    } else {
      setLoading(false);
    }
  }, [user.team_id]);

  const fetchSwimmers = async () => {
    try {
      const data = await getTeamSwimmers(user.team_id);
      setSwimmers(data);
    } catch (err) {
      console.error(err);
      setMessage('Failed to load roster.');
    }
    setLoading(false);
  };

  const handleToggleStatus = async (swimmerId, swimmerName) => {
    try {
      const res = await toggleSwimmerStatus(swimmerId);
      setMessage(`${swimmerName} ${res.is_active ? 'activated' : 'deactivated'}.`);
      fetchSwimmers();
    } catch (err) {
      setMessage(`Failed to update status: ${err.response?.data?.detail || err.message}`);
    }
  };

  const handleAddSwimmer = async (e) => {
    e.preventDefault();
    setAdding(true);
    try {
      await addSwimmer(user.team_id, {
        first_name: newFirstName,
        last_name: newLastName,
        age: parseInt(newAge),
        gender: newGender
      });
      setMessage(`${newFirstName} ${newLastName} added to the roster.`);
      setNewFirstName('');
      setNewLastName('');
      setNewAge('');
      setNewGender('M');
      setShowAddForm(false);
      fetchSwimmers();
    } catch (err) {
      setMessage(`Failed to add swimmer: ${err.response?.data?.detail || err.message}`);
    } finally {
      setAdding(false);
    }
  };

  if (!user.team_id) {
    return <div className="animate-fade-in"><h2>Roster</h2><p>You are not assigned to a team.</p></div>;
  }

  if (loading) return <div className="animate-fade-in"><p>Loading roster...</p></div>;

  const activeSwimmers = swimmers.filter(s => s.is_active !== false);
  const inactiveSwimmers = swimmers.filter(s => s.is_active === false);

  return (
    <div className="animate-fade-in">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
        <div>
          <h1>Team Roster</h1>
          <p>Manage your team's swimmers.</p>
        </div>
        <button className="btn btn-primary" onClick={() => setShowAddForm(!showAddForm)}>
          {showAddForm ? <><X size={18} /> Cancel</> : <><UserPlus size={18} /> Add Swimmer</>}
        </button>
      </div>

      {message && (
        <div style={{ padding: '0.75rem 1rem', marginBottom: '1rem', backgroundColor: 'var(--bg-color-secondary)', borderRadius: '8px', fontSize: '0.9rem' }}>
          {message}
        </div>
      )}

      {/* Add Swimmer Form */}
      {showAddForm && (
        <div className="glass-panel" style={{ padding: '1.5rem', marginBottom: '2rem' }}>
          <h3 style={{ marginBottom: '1rem', fontSize: '1.1rem' }}>Add New Swimmer</h3>
          <form onSubmit={handleAddSwimmer} style={{ display: 'flex', gap: '1rem', alignItems: 'flex-end', flexWrap: 'wrap' }}>
            <div className="input-group" style={{ margin: 0, flex: '1 1 150px' }}>
              <label>First Name</label>
              <input type="text" value={newFirstName} onChange={e => setNewFirstName(e.target.value)} required placeholder="First" />
            </div>
            <div className="input-group" style={{ margin: 0, flex: '1 1 150px' }}>
              <label>Last Name</label>
              <input type="text" value={newLastName} onChange={e => setNewLastName(e.target.value)} required placeholder="Last" />
            </div>
            <div className="input-group" style={{ margin: 0, flex: '0 1 80px' }}>
              <label>Age</label>
              <input type="number" min="4" max="18" value={newAge} onChange={e => setNewAge(e.target.value)} required />
            </div>
            <div className="input-group" style={{ margin: 0, flex: '0 1 100px' }}>
              <label>Gender</label>
              <select value={newGender} onChange={e => setNewGender(e.target.value)}>
                <option value="M">Male</option>
                <option value="F">Female</option>
              </select>
            </div>
            <button type="submit" className="btn btn-primary" disabled={adding} style={{ alignSelf: 'flex-end' }}>
              <Plus size={16} />
              {adding ? 'Adding...' : 'Add'}
            </button>
          </form>
        </div>
      )}

      {/* Active Swimmers */}
      <div className="glass-panel" style={{ padding: '2rem', overflowX: 'auto', marginBottom: '2rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1rem' }}>
          <UserCheck size={18} color="var(--success-color)" />
          <h3 style={{ margin: 0, fontSize: '1rem' }}>Active Swimmers ({activeSwimmers.length})</h3>
        </div>
        <table className="data-table">
          <thead>
            <tr>
              <th>Status</th>
              <th>Name</th>
              <th>Age</th>
              <th>Gender</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            {activeSwimmers.map(swimmer => (
              <tr key={swimmer.id}>
                <td><span className="status-dot active"></span></td>
                <td style={{ fontWeight: 500 }}>{swimmer.first_name} {swimmer.last_name}</td>
                <td>{swimmer.age}</td>
                <td>{swimmer.gender === 'M' || swimmer.gender === 'm' ? 'Male' : 'Female'}</td>
                <td>
                  <button
                    className="btn btn-outline"
                    style={{ padding: '0.4rem 0.75rem', fontSize: '0.8rem', color: 'var(--danger-color)', borderColor: 'var(--danger-color)' }}
                    onClick={() => handleToggleStatus(swimmer.id, `${swimmer.first_name} ${swimmer.last_name}`)}
                    title="Deactivate swimmer"
                  >
                    <UserX size={14} /> Deactivate
                  </button>
                </td>
              </tr>
            ))}
            {activeSwimmers.length === 0 && (
              <tr><td colSpan="5" style={{ padding: '2rem', textAlign: 'center', color: 'var(--text-muted)' }}>No active swimmers. Add swimmers or reactivate inactive ones.</td></tr>
            )}
          </tbody>
        </table>
      </div>

      {/* Inactive Swimmers */}
      {inactiveSwimmers.length > 0 && (
        <div className="glass-panel" style={{ padding: '2rem', overflowX: 'auto' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1rem' }}>
            <UserX size={18} color="var(--text-muted)" />
            <h3 style={{ margin: 0, fontSize: '1rem', color: 'var(--text-muted)' }}>Inactive Swimmers ({inactiveSwimmers.length})</h3>
          </div>
          <table className="data-table">
            <thead>
              <tr>
                <th>Status</th>
                <th>Name</th>
                <th>Age</th>
                <th>Gender</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {inactiveSwimmers.map(swimmer => (
                <tr key={swimmer.id} className="row-inactive">
                  <td><span className="status-dot inactive"></span></td>
                  <td>{swimmer.first_name} {swimmer.last_name}</td>
                  <td>{swimmer.age}</td>
                  <td>{swimmer.gender === 'M' || swimmer.gender === 'm' ? 'Male' : 'Female'}</td>
                  <td>
                    <button
                      className="btn btn-outline"
                      style={{ padding: '0.4rem 0.75rem', fontSize: '0.8rem', color: 'var(--success-color)', borderColor: 'var(--success-color)' }}
                      onClick={() => handleToggleStatus(swimmer.id, `${swimmer.first_name} ${swimmer.last_name}`)}
                      title="Reactivate swimmer"
                    >
                      <UserCheck size={14} /> Activate
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
