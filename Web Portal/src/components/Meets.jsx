import React, { useEffect, useState } from 'react';
import { getMeets, createMeet, updateMeet, deleteMeet, getMeetEntryStatus } from '../services/api';
import { Calendar, Users, Hash, ArrowLeft, Trash2, Save, Plus, X, Settings } from 'lucide-react';
import CoachMeetDetail from './CoachMeetDetail';

// ─── Create Meet Modal ───────────────────────────────────────────────
function CreateMeetModal({ onClose, onCreated }) {
  const [name, setName] = useState('');
  const [date, setDate] = useState('');
  const [numLanes, setNumLanes] = useState(6);
  const [emptyLanes, setEmptyLanes] = useState(false);
  const [isActive, setIsActive] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    setError('');
    try {
      await createMeet({
        name,
        date: date || null,
        num_lanes: numLanes,
        empty_lanes: emptyLanes,
        is_active: isActive
      });
      onCreated();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to create meet');
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
          <h3 style={{ margin: 0 }}>Create New Meet</h3>
          <button className="btn btn-outline" onClick={onClose} style={{ padding: '0.4rem' }}>
            <X size={18} />
          </button>
        </div>

        {error && <div style={{ padding: '0.75rem 1rem', marginBottom: '1rem', backgroundColor: 'rgba(239,68,68,0.1)', border: '1px solid rgba(239,68,68,0.3)', borderRadius: '8px', color: 'var(--danger-color)', fontSize: '0.875rem' }}>{error}</div>}

        <form onSubmit={handleSubmit}>
          <div className="input-group">
            <label>Meet Name</label>
            <input
              type="text"
              id="create-meet-name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
              placeholder="e.g. June Invitational"
            />
          </div>

          <div className="input-group">
            <label>Date</label>
            <input
              type="date"
              id="create-meet-date"
              value={date}
              onChange={(e) => setDate(e.target.value)}
            />
          </div>

          <div className="input-group">
            <label>Number of Lanes</label>
            <select
              id="create-meet-lanes"
              value={numLanes}
              onChange={(e) => setNumLanes(parseInt(e.target.value))}
            >
              {[4, 5, 6, 7, 8, 9, 10].map(n => (
                <option key={n} value={n}>{n} Lanes</option>
              ))}
            </select>
          </div>

          <div className="toggle-row" style={{ marginBottom: '1rem' }}>
            <div>
              <span style={{ fontWeight: 500, fontSize: '0.875rem' }}>Empty Lanes</span>
              <p style={{ margin: 0, fontSize: '0.8rem' }}>Leave outer lanes empty for smaller heats</p>
            </div>
            <label className="toggle-switch">
              <input type="checkbox" checked={emptyLanes} onChange={(e) => setEmptyLanes(e.target.checked)} />
              <span className="toggle-slider"></span>
            </label>
          </div>

          <div className="toggle-row" style={{ marginBottom: '1.5rem' }}>
            <div>
              <span style={{ fontWeight: 500, fontSize: '0.875rem' }}>Active Meet</span>
              <p style={{ margin: 0, fontSize: '0.8rem' }}>Mark this meet as active for entries</p>
            </div>
            <label className="toggle-switch">
              <input type="checkbox" checked={isActive} onChange={(e) => setIsActive(e.target.checked)} />
              <span className="toggle-slider"></span>
            </label>
          </div>

          <button type="submit" className="btn btn-primary" disabled={saving} style={{ width: '100%' }}>
            <Plus size={18} />
            {saving ? 'Creating...' : 'Create Meet'}
          </button>
        </form>
      </div>
    </div>
  );
}

// ─── Meet Detail / Edit View ─────────────────────────────────────────
function MeetDetail({ meet, onBack, onSaved, onDeleted }) {
  const [name, setName] = useState(meet.name);
  const [date, setDate] = useState(meet.date || '');
  const [numLanes, setNumLanes] = useState(meet.num_lanes);
  const [emptyLanes, setEmptyLanes] = useState(meet.empty_lanes);
  const [isActive, setIsActive] = useState(meet.is_active);
  const [saving, setSaving] = useState(false);
  const [deleting, setDeleting] = useState(false);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const [entryStatus, setEntryStatus] = useState([]);
  const [loadingStatus, setLoadingStatus] = useState(true);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);

  useEffect(() => {
    fetchEntryStatus();
  }, [meet.id]);

  const fetchEntryStatus = async () => {
    try {
      const data = await getMeetEntryStatus(meet.id);
      setEntryStatus(data);
    } catch (err) {
      console.error('Failed to load entry status:', err);
    } finally {
      setLoadingStatus(false);
    }
  };

  const handleSave = async () => {
    setSaving(true);
    setMessage('');
    setError('');
    try {
      await updateMeet(meet.id, {
        name,
        date: date || null,
        num_lanes: numLanes,
        empty_lanes: emptyLanes,
        is_active: isActive
      });
      setMessage('Meet updated successfully.');
      onSaved();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to update meet');
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async () => {
    setDeleting(true);
    try {
      await deleteMeet(meet.id);
      onDeleted();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to delete meet');
      setDeleting(false);
      setShowDeleteConfirm(false);
    }
  };

  return (
    <div className="animate-fade-in">
      <button className="btn btn-outline" onClick={onBack} style={{ marginBottom: '2rem', gap: '0.5rem' }}>
        <ArrowLeft size={18} />
        Back to Meets
      </button>

      <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '2rem' }}>
        <h1 style={{ margin: 0 }}>{meet.name}</h1>
        <span className={`badge ${meet.is_active ? 'badge-active' : 'badge-inactive'}`}>
          {meet.is_active ? 'Active' : 'Inactive'}
        </span>
      </div>

      {message && <div style={{ padding: '0.75rem 1rem', marginBottom: '1rem', backgroundColor: 'rgba(16,185,129,0.1)', border: '1px solid rgba(16,185,129,0.3)', borderRadius: '8px', color: 'var(--success-color)', fontSize: '0.875rem' }}>{message}</div>}
      {error && <div style={{ padding: '0.75rem 1rem', marginBottom: '1rem', backgroundColor: 'rgba(239,68,68,0.1)', border: '1px solid rgba(239,68,68,0.3)', borderRadius: '8px', color: 'var(--danger-color)', fontSize: '0.875rem' }}>{error}</div>}

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '2rem' }}>
        {/* Edit Form */}
        <div className="glass-panel" style={{ padding: '2rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1.5rem' }}>
            <Settings size={20} color="var(--text-muted)" />
            <h3 style={{ margin: 0 }}>Meet Configuration</h3>
          </div>

          <div className="input-group">
            <label>Meet Name</label>
            <input
              type="text"
              id="edit-meet-name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
            />
          </div>

          <div className="input-group">
            <label>Date</label>
            <input
              type="date"
              id="edit-meet-date"
              value={date}
              onChange={(e) => setDate(e.target.value)}
            />
          </div>

          <div className="input-group">
            <label>Number of Lanes</label>
            <select
              id="edit-meet-lanes"
              value={numLanes}
              onChange={(e) => setNumLanes(parseInt(e.target.value))}
            >
              {[4, 5, 6, 7, 8, 9, 10].map(n => (
                <option key={n} value={n}>{n} Lanes</option>
              ))}
            </select>
          </div>

          <div className="toggle-row" style={{ marginBottom: '1rem' }}>
            <div>
              <span style={{ fontWeight: 500, fontSize: '0.875rem' }}>Empty Lanes</span>
              <p style={{ margin: 0, fontSize: '0.8rem' }}>Leave outer lanes empty for smaller heats</p>
            </div>
            <label className="toggle-switch">
              <input type="checkbox" checked={emptyLanes} onChange={(e) => setEmptyLanes(e.target.checked)} />
              <span className="toggle-slider"></span>
            </label>
          </div>

          <div className="toggle-row" style={{ marginBottom: '2rem' }}>
            <div>
              <span style={{ fontWeight: 500, fontSize: '0.875rem' }}>Active Meet</span>
              <p style={{ margin: 0, fontSize: '0.8rem' }}>Mark as active for coach entries</p>
            </div>
            <label className="toggle-switch">
              <input type="checkbox" checked={isActive} onChange={(e) => setIsActive(e.target.checked)} />
              <span className="toggle-slider"></span>
            </label>
          </div>

          <div style={{ display: 'flex', gap: '1rem' }}>
            <button className="btn btn-primary" onClick={handleSave} disabled={saving} style={{ flex: 1 }}>
              <Save size={16} />
              {saving ? 'Saving...' : 'Save Changes'}
            </button>
            <button className="btn btn-outline" onClick={() => setShowDeleteConfirm(true)} style={{ color: 'var(--danger-color)', borderColor: 'var(--danger-color)' }}>
              <Trash2 size={16} />
            </button>
          </div>
        </div>

        {/* Entry Status */}
        <div className="glass-panel" style={{ padding: '2rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1.5rem' }}>
            <Users size={20} color="var(--text-muted)" />
            <h3 style={{ margin: 0 }}>Entry Status by Team</h3>
          </div>

          {loadingStatus ? (
            <p style={{ color: 'var(--text-muted)' }}>Loading entry status...</p>
          ) : entryStatus.length === 0 ? (
            <div style={{ padding: '2rem', textAlign: 'center', color: 'var(--text-muted)', backgroundColor: 'rgba(255,255,255,0.02)', borderRadius: '8px' }}>
              <p style={{ marginBottom: '0.5rem' }}>No teams with swimmers found.</p>
              <p style={{ fontSize: '0.8rem', margin: 0 }}>Add teams and upload rosters in the Admin tab.</p>
            </div>
          ) : (
            <table className="data-table">
              <thead>
                <tr>
                  <th>Team</th>
                  <th>Entries</th>
                  <th>Progress</th>
                </tr>
              </thead>
              <tbody>
                {entryStatus.map((team) => {
                  const pct = team.total_swimmers > 0 ? Math.round((team.entered_swimmers / team.total_swimmers) * 100) : 0;
                  return (
                    <tr key={team.team_id}>
                      <td style={{ fontWeight: 500 }}>{team.team_name}</td>
                      <td>
                        <span style={{ color: pct === 100 ? 'var(--success-color)' : 'var(--text-color)' }}>
                          {team.entered_swimmers}/{team.total_swimmers}
                        </span>
                      </td>
                      <td style={{ minWidth: '120px' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                          <div className="progress-track" style={{ flex: 1 }}>
                            <div className="progress-fill" style={{ width: `${pct}%` }}></div>
                          </div>
                          <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', minWidth: '32px', textAlign: 'right' }}>{pct}%</span>
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          )}
        </div>
      </div>

      {/* Delete Confirmation Modal */}
      {showDeleteConfirm && (
        <div className="modal-overlay" onClick={() => setShowDeleteConfirm(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()} style={{ maxWidth: '400px', textAlign: 'center' }}>
            <Trash2 size={32} color="var(--danger-color)" style={{ marginBottom: '1rem' }} />
            <h3 style={{ marginBottom: '0.5rem' }}>Delete Meet</h3>
            <p style={{ fontSize: '0.9rem' }}>
              Are you sure you want to delete <strong style={{ color: 'var(--text-color)' }}>{meet.name}</strong>? This will permanently remove all associated entries and relay entries.
            </p>
            <div style={{ display: 'flex', gap: '1rem', marginTop: '1.5rem' }}>
              <button className="btn btn-outline" onClick={() => setShowDeleteConfirm(false)} style={{ flex: 1 }}>Cancel</button>
              <button className="btn btn-danger" onClick={handleDelete} disabled={deleting} style={{ flex: 1 }}>
                {deleting ? 'Deleting...' : 'Delete Meet'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

// ─── Main Meets Component ────────────────────────────────────────────
export default function Meets() {
  const [meets, setMeets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [selectedMeet, setSelectedMeet] = useState(null);

  const user = JSON.parse(localStorage.getItem('user') || '{}');
  const isAdmin = user.role === 'admin';

  useEffect(() => {
    fetchMeets();
  }, []);

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

  const handleMeetCreated = () => {
    setShowCreateModal(false);
    fetchMeets();
  };

  const handleMeetSaved = () => {
    fetchMeets();
  };

  const handleMeetDeleted = () => {
    setSelectedMeet(null);
    fetchMeets();
  };

  if (loading) return <div className="animate-fade-in"><p>Loading meets...</p></div>;
  
  if (error) return <div className="animate-fade-in"><div className="glass-panel" style={{ padding: '2rem', color: 'var(--danger-color)' }}>{error}</div></div>;

  // ── Detail View ──
  if (selectedMeet) {
    if (!isAdmin) {
      return (
        <CoachMeetDetail
          meet={selectedMeet}
          onBack={() => setSelectedMeet(null)}
        />
      );
    }
    return (
      <MeetDetail
        meet={selectedMeet}
        onBack={() => setSelectedMeet(null)}
        onSaved={handleMeetSaved}
        onDeleted={handleMeetDeleted}
      />
    );
  }

  // ── List View ──
  return (
    <div className="animate-fade-in">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '3rem' }}>
        <div>
          <h1>Upcoming Meets</h1>
          <p>View and manage all scheduled swim meets.</p>
        </div>
        {isAdmin && (
          <button className="btn btn-primary" id="create-meet-btn" onClick={() => setShowCreateModal(true)}>
            <Plus size={18} />
            Create Meet
          </button>
        )}
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))', gap: '2rem' }}>
        {meets.map((meet) => (
          <div
            key={meet.id}
            className="glass-panel"
            style={{ padding: '1.5rem', transition: 'transform 0.2s ease, box-shadow 0.2s ease', cursor: 'pointer' }}
            onMouseEnter={(e) => { e.currentTarget.style.transform = 'translateY(-4px)'; e.currentTarget.style.boxShadow = '0 8px 30px rgba(0,0,0,0.2)'; }}
            onMouseLeave={(e) => { e.currentTarget.style.transform = 'translateY(0)'; e.currentTarget.style.boxShadow = ''; }}
            onClick={() => setSelectedMeet(meet)}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '1rem' }}>
              <h3 style={{ margin: 0, color: 'var(--text-color)' }}>{meet.name}</h3>
              <span className={`badge ${meet.is_active ? 'badge-active' : 'badge-inactive'}`}>
                {meet.is_active ? 'Active' : 'Inactive'}
              </span>
            </div>
            
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
                {isAdmin ? 'View Details' : 'Manage Entries'}
              </button>
            </div>
          </div>
        ))}
      </div>
      
      {meets.length === 0 && (
        <div className="glass-panel" style={{ padding: '3rem', textAlign: 'center', color: 'var(--text-muted)' }}>
          <Calendar size={48} style={{ marginBottom: '1rem', opacity: 0.4 }} />
          <p style={{ fontSize: '1.1rem', marginBottom: '0.5rem', color: 'var(--text-color)' }}>No meets yet</p>
          <p>Create your first swim meet to get started.</p>
        </div>
      )}

      {showCreateModal && (
        <CreateMeetModal
          onClose={() => setShowCreateModal(false)}
          onCreated={handleMeetCreated}
        />
      )}
    </div>
  );
}
