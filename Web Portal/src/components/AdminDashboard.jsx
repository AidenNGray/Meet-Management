import React, { useState, useEffect } from 'react';
import { getTeams, uploadRoster, createCoach, createTeam, updateTeam, deleteTeam } from '../services/api';
import { Edit2, Trash2, Check, X } from 'lucide-react';

export default function AdminDashboard() {
  const [teams, setTeams] = useState([]);
  const [coachEmail, setCoachEmail] = useState('');
  const [selectedTeamForCoach, setSelectedTeamForCoach] = useState('');
  const [message, setMessage] = useState('');

  const [newTeamName, setNewTeamName] = useState('');
  const [newTeamShortId, setNewTeamShortId] = useState('');

  const [editingTeamId, setEditingTeamId] = useState(null);
  const [editTeamName, setEditTeamName] = useState('');
  const [editTeamShortId, setEditTeamShortId] = useState('');

  useEffect(() => {
    fetchTeams();
  }, []);

  const fetchTeams = async () => {
    try {
      const data = await getTeams();
      setTeams(data);
      if (data.length > 0) setSelectedTeamForCoach(data[0].id);
    } catch (err) {
      console.error(err);
    }
  };

  const handleFileUpload = async (e, teamId) => {
    const file = e.target.files[0];
    if (!file) return;
    try {
      const res = await uploadRoster(teamId, file);
      setMessage(res.message);
    } catch (err) {
      setMessage(err.response?.data?.detail || 'Failed to upload roster');
    }
  };

  const handleCreateCoach = async (e) => {
    e.preventDefault();
    try {
      await createCoach({ email: coachEmail, team_id: selectedTeamForCoach });
      setMessage(`Coach ${coachEmail} created successfully.`);
      setCoachEmail('');
    } catch (err) {
      setMessage(err.response?.data?.detail || 'Failed to create coach');
    }
  };

  const handleCreateTeam = async (e) => {
    e.preventDefault();
    try {
      await createTeam({ name: newTeamName, short_id: newTeamShortId });
      setMessage(`Team ${newTeamName} created successfully.`);
      setNewTeamName('');
      setNewTeamShortId('');
      fetchTeams(); // Refresh the list of teams
    } catch (err) {
      setMessage(err.response?.data?.detail || 'Failed to create team');
    }
  };

  const handleStartEdit = (team) => {
    setEditingTeamId(team.id);
    setEditTeamName(team.name);
    setEditTeamShortId(team.short_id);
  };

  const handleCancelEdit = () => {
    setEditingTeamId(null);
    setEditTeamName('');
    setEditTeamShortId('');
  };

  const handleSaveEdit = async (teamId) => {
    try {
      await updateTeam(teamId, { name: editTeamName, short_id: editTeamShortId });
      setMessage(`Team updated successfully.`);
      setEditingTeamId(null);
      fetchTeams();
    } catch (err) {
      setMessage(err.response?.data?.detail || 'Failed to update team');
    }
  };

  const handleDeleteTeam = async (teamId) => {
    if (!window.confirm("Are you sure you want to delete this team? This will remove all associated coaches and swimmers.")) return;
    try {
      await deleteTeam(teamId);
      setMessage(`Team deleted successfully.`);
      fetchTeams();
    } catch (err) {
      setMessage(err.response?.data?.detail || 'Failed to delete team');
    }
  };

  return (
    <div className="animate-fade-in">
      <h2>Admin Portal</h2>
      {message && <div style={{ padding: '1rem', marginBottom: '1rem', backgroundColor: 'var(--bg-color-secondary)', borderRadius: '8px' }}>{message}</div>}

      <div style={{ display: 'flex', gap: '2rem', flexWrap: 'wrap' }}>
        <div className="glass-panel" style={{ flex: 1, minWidth: '300px', padding: '2rem' }}>
          <h3>Teams & Rosters</h3>
          <p style={{ color: 'var(--text-muted)', marginBottom: '1rem' }}>Upload Excel roster files for each team.</p>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            {teams.map(team => (
              <div key={team.id} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '1rem', backgroundColor: 'rgba(255,255,255,0.02)', borderRadius: '8px', flexWrap: 'wrap', gap: '1rem' }}>
                {editingTeamId === team.id ? (
                  <div style={{ display: 'flex', gap: '0.5rem', flex: 1 }}>
                    <input type="text" value={editTeamName} onChange={e => setEditTeamName(e.target.value)} placeholder="Team Name" style={{ flex: 2 }} />
                    <input type="text" value={editTeamShortId} onChange={e => setEditTeamShortId(e.target.value)} placeholder="Short ID" style={{ flex: 1 }} />
                  </div>
                ) : (
                  <span style={{ fontWeight: 'bold' }}>{team.name} ({team.short_id})</span>
                )}
                
                <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
                  {editingTeamId === team.id ? (
                    <>
                      <button className="btn btn-primary" onClick={() => handleSaveEdit(team.id)} style={{ padding: '0.5rem' }}><Check size={16} /></button>
                      <button className="btn btn-outline" onClick={handleCancelEdit} style={{ padding: '0.5rem' }}><X size={16} /></button>
                    </>
                  ) : (
                    <>
                      <label className="btn btn-outline" style={{ cursor: 'pointer', margin: 0 }}>
                        Upload Roster
                        <input type="file" accept=".xlsx" style={{ display: 'none' }} onChange={(e) => handleFileUpload(e, team.id)} />
                      </label>
                      <button className="btn btn-outline" onClick={() => handleStartEdit(team)} style={{ padding: '0.5rem' }}><Edit2 size={16} /></button>
                      <button className="btn btn-outline" onClick={() => handleDeleteTeam(team.id)} style={{ padding: '0.5rem', color: 'var(--danger-color)' }}><Trash2 size={16} /></button>
                    </>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="glass-panel" style={{ flex: 1, minWidth: '300px', padding: '2rem', alignSelf: 'flex-start' }}>
          <h3>Create Coach</h3>
          <p style={{ color: 'var(--text-muted)', marginBottom: '1rem' }}>Assign a coach to a team.</p>
          <form onSubmit={handleCreateCoach} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            <div className="input-group">
              <label>Coach Email</label>
              <input type="email" value={coachEmail} onChange={e => setCoachEmail(e.target.value)} required placeholder="coach@example.com" />
            </div>
            <div className="input-group">
              <label>Select Team</label>
              <select value={selectedTeamForCoach} onChange={e => setSelectedTeamForCoach(e.target.value)} required>
                {teams.map(team => (
                  <option key={team.id} value={team.id}>{team.name}</option>
                ))}
              </select>
            </div>
            <button type="submit" className="btn btn-primary">Create Coach Access</button>
          </form>
        </div>

        <div className="glass-panel" style={{ flex: 1, minWidth: '300px', padding: '2rem', alignSelf: 'flex-start' }}>
          <h3>Create New Team</h3>
          <p style={{ color: 'var(--text-muted)', marginBottom: '1rem' }}>Add a new team to the league.</p>
          <form onSubmit={handleCreateTeam} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            <div className="input-group">
              <label>Team Name</label>
              <input type="text" value={newTeamName} onChange={e => setNewTeamName(e.target.value)} required placeholder="e.g. Savannah Swim Team" />
            </div>
            <div className="input-group">
              <label>Short ID</label>
              <input type="text" value={newTeamShortId} onChange={e => setNewTeamShortId(e.target.value)} required placeholder="e.g. sav" />
            </div>
            <button type="submit" className="btn btn-primary">Create Team</button>
          </form>
        </div>
      </div>
    </div>
  );
}
