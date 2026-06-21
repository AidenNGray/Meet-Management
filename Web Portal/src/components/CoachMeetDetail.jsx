import React, { useState, useEffect } from 'react';
import { getTeamSwimmers, updateSwimmerEntries, getMeetRelays, createOrUpdateRelay, deleteRelay } from '../services/api';
import { ArrowLeft, Save, Trash2, Plus, Users, Zap } from 'lucide-react';

const EVENT_TYPES = [
  '50 Free','100 Free','200 Free','50 Back','100 Back','50 Breast','100 Breast','50 Fly','100 Fly','200 IM'
];

const RELAY_AGE_GROUPS = ['8 & under','9 & 10','11 & 12','13 & up'];
const RELAY_STROKES = ['medley','free'];
const GENDERS = ['Girls','Boys'];

function getEligibleAges(ageGroup) {
  // Returns [minAge, maxAge] for eligible swimmers (including one group below)
  const idx = RELAY_AGE_GROUPS.indexOf(ageGroup);
  const ranges = [
    [0, 8],   // 8 & under
    [0, 10],  // 9 & 10 + one below = includes 8 & under
    [9, 12],  // 11 & 12 + one below = includes 9 & 10
    [11, 99]  // 13 & up + one below = includes 11 & 12
  ];
  if (idx >= 0) return ranges[idx];
  return [0, 99];
}

// ─── Individual Entries Tab ──────────────────────────────────────────
function EntriesTab({ meet, teamId }) {
  const [swimmers, setSwimmers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState('');

  useEffect(() => { fetchSwimmers(); }, [meet.id, teamId]);

  const fetchSwimmers = async () => {
    setLoading(true);
    try {
      const data = await getTeamSwimmers(teamId, meet.id);
      setSwimmers(data.filter(s => s.is_active !== false));
    } catch (err) { console.error(err); }
    setLoading(false);
  };

  const handleEventToggle = (swimmerId, eventType) => {
    setSwimmers(prev => prev.map(s => {
      if (s.id !== swimmerId) return s;
      const events = s.events || [];
      if (events.includes(eventType)) {
        return { ...s, events: events.filter(e => e !== eventType) };
      } else {
        if (events.length >= 3) { alert('Maximum 3 individual events per swimmer.'); return s; }
        return { ...s, events: [...events, eventType] };
      }
    }));
  };

  const handleSave = async (swimmerId) => {
    const swimmer = swimmers.find(s => s.id === swimmerId);
    try {
      await updateSwimmerEntries(swimmerId, swimmer.events || [], meet.id);
      setMessage(`Entries saved for ${swimmer.first_name} ${swimmer.last_name}`);
      setTimeout(() => setMessage(''), 3000);
    } catch (err) {
      setMessage(`Failed: ${err.response?.data?.detail || err.message}`);
    }
  };

  if (loading) return <p style={{ color: 'var(--text-muted)' }}>Loading swimmers...</p>;

  return (
    <div>
      {message && <div style={{ padding: '0.75rem 1rem', marginBottom: '1rem', backgroundColor: 'var(--bg-color-secondary)', borderRadius: '8px', fontSize: '0.875rem' }}>{message}</div>}
      <div className="glass-panel" style={{ padding: '1.5rem', overflowX: 'auto' }}>
        <table className="data-table">
          <thead>
            <tr>
              <th>Swimmer</th>
              <th>Age</th>
              <th>Events (max 3)</th>
              <th style={{ width: '80px' }}>Save</th>
            </tr>
          </thead>
          <tbody>
            {swimmers.map(swimmer => (
              <tr key={swimmer.id}>
                <td style={{ fontWeight: 500 }}>{swimmer.first_name} {swimmer.last_name}</td>
                <td>{swimmer.age}</td>
                <td>
                  <div style={{ display: 'flex', gap: '0.4rem', flexWrap: 'wrap' }}>
                    {EVENT_TYPES.map(evt => {
                      const key = evt.toLowerCase().replace(' ', '');
                      const checked = (swimmer.events || []).includes(key);
                      return (
                        <label key={evt} style={{ display: 'flex', alignItems: 'center', gap: '0.2rem', fontSize: '0.8rem', cursor: 'pointer', padding: '0.15rem 0.4rem', borderRadius: '4px', backgroundColor: checked ? 'rgba(59,130,246,0.15)' : 'transparent' }}>
                          <input type="checkbox" checked={checked} onChange={() => handleEventToggle(swimmer.id, key)} style={{ accentColor: 'var(--primary-color)' }} />
                          {evt}
                        </label>
                      );
                    })}
                  </div>
                </td>
                <td>
                  <button className="btn btn-outline" style={{ padding: '0.4rem 0.75rem', fontSize: '0.8rem' }} onClick={() => handleSave(swimmer.id)}>
                    <Save size={14} />
                  </button>
                </td>
              </tr>
            ))}
            {swimmers.length === 0 && (
              <tr><td colSpan="4" style={{ padding: '2rem', textAlign: 'center', color: 'var(--text-muted)' }}>No active swimmers. Add swimmers in the Roster tab.</td></tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}

// ─── Relay Assembly Tab ──────────────────────────────────────────────
function RelayTab({ meet, teamId }) {
  const [swimmers, setSwimmers] = useState([]);
  const [relays, setRelays] = useState([]);
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState('');

  useEffect(() => { loadData(); }, [meet.id, teamId]);

  const loadData = async () => {
    setLoading(true);
    try {
      const [swimData, relayData] = await Promise.all([
        getTeamSwimmers(teamId),
        getMeetRelays(meet.id, teamId)
      ]);
      setSwimmers(swimData.filter(s => s.is_active !== false));
      setRelays(relayData);
    } catch (err) { console.error(err); }
    setLoading(false);
  };

  const getEligibleSwimmers = (ageGroup, gender) => {
    const [minAge, maxAge] = getEligibleAges(ageGroup);
    const genderKey = gender === 'Girls' ? ['f','F'] : ['m','M'];
    return swimmers.filter(s => s.age >= minAge && s.age <= maxAge && genderKey.includes(s.gender));
  };

  const findRelay = (ageGroup, gender, stroke, identifier) => {
    return relays.find(r =>
      r.age_group.toLowerCase() === ageGroup.toLowerCase() &&
      r.gender.toLowerCase() === gender.toLowerCase() &&
      r.stroke.toLowerCase() === stroke.toLowerCase() &&
      r.identifier === identifier
    );
  };

  const handleSaveRelay = async (ageGroup, gender, stroke, identifier, s1, s2, s3, s4) => {
    try {
      await createOrUpdateRelay(meet.id, {
        team_id: teamId,
        age_group: ageGroup,
        gender: gender,
        stroke: stroke,
        identifier: identifier,
        swimmer1_id: s1 || null,
        swimmer2_id: s2 || null,
        swimmer3_id: s3 || null,
        swimmer4_id: s4 || null
      });
      setMessage(`${stroke.charAt(0).toUpperCase() + stroke.slice(1)} relay ${identifier} (${gender} ${ageGroup}) saved.`);
      loadData();
      setTimeout(() => setMessage(''), 3000);
    } catch (err) {
      setMessage(`Failed: ${err.response?.data?.detail || err.message}`);
    }
  };

  const handleDeleteRelay = async (relayId) => {
    try {
      await deleteRelay(relayId);
      setMessage('Relay deleted.');
      loadData();
      setTimeout(() => setMessage(''), 3000);
    } catch (err) {
      setMessage(`Failed: ${err.response?.data?.detail || err.message}`);
    }
  };

  if (loading) return <p style={{ color: 'var(--text-muted)' }}>Loading relays...</p>;

  return (
    <div>
      {message && <div style={{ padding: '0.75rem 1rem', marginBottom: '1rem', backgroundColor: 'var(--bg-color-secondary)', borderRadius: '8px', fontSize: '0.875rem' }}>{message}</div>}

      {RELAY_STROKES.map(stroke => (
        <div key={stroke} style={{ marginBottom: '2.5rem' }}>
          <h3 style={{ marginBottom: '1.5rem', textTransform: 'capitalize' }}>
            {stroke === 'medley' ? '🏊 Medley Relay' : '🏊 Free Relay'}
          </h3>

          {RELAY_AGE_GROUPS.map(ageGroup => (
            <div key={ageGroup} style={{ marginBottom: '2rem' }}>
              <h4 style={{ fontSize: '0.95rem', color: 'var(--text-muted)', marginBottom: '1rem' }}>{ageGroup}</h4>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))', gap: '1rem' }}>
                {GENDERS.map(gender => (
                  <RelayCard
                    key={`${stroke}-${ageGroup}-${gender}`}
                    stroke={stroke}
                    ageGroup={ageGroup}
                    gender={gender}
                    eligibleSwimmers={getEligibleSwimmers(ageGroup, gender)}
                    existingRelay={findRelay(ageGroup, gender, stroke, 'A')}
                    onSave={handleSaveRelay}
                    onDelete={handleDeleteRelay}
                  />
                ))}
              </div>
            </div>
          ))}
        </div>
      ))}
    </div>
  );
}

function RelayCard({ stroke, ageGroup, gender, eligibleSwimmers, existingRelay, onSave, onDelete }) {
  const [s1, setS1] = useState(existingRelay?.swimmer1_id || '');
  const [s2, setS2] = useState(existingRelay?.swimmer2_id || '');
  const [s3, setS3] = useState(existingRelay?.swimmer3_id || '');
  const [s4, setS4] = useState(existingRelay?.swimmer4_id || '');
  const [identifier] = useState('A');

  useEffect(() => {
    setS1(existingRelay?.swimmer1_id || '');
    setS2(existingRelay?.swimmer2_id || '');
    setS3(existingRelay?.swimmer3_id || '');
    setS4(existingRelay?.swimmer4_id || '');
  }, [existingRelay]);

  const slots = [
    { label: 'Swimmer 1', value: s1, set: setS1 },
    { label: 'Swimmer 2', value: s2, set: setS2 },
    { label: 'Swimmer 3', value: s3, set: setS3 },
    { label: 'Swimmer 4', value: s4, set: setS4 },
  ];

  return (
    <div className="relay-card">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem' }}>
        <span style={{ fontWeight: 600, fontSize: '0.9rem' }}>{gender} — Team A</span>
        {existingRelay && (
          <button className="btn btn-outline" style={{ padding: '0.3rem', color: 'var(--danger-color)', borderColor: 'var(--danger-color)' }} onClick={() => onDelete(existingRelay.id)} title="Delete relay">
            <Trash2 size={14} />
          </button>
        )}
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', marginBottom: '0.75rem' }}>
        {slots.map((slot, i) => (
          <div key={i}>
            <label style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '0.2rem', display: 'block' }}>{slot.label}</label>
            <select value={slot.value} onChange={e => slot.set(e.target.value)}>
              <option value="">— Select —</option>
              {eligibleSwimmers.map(sw => (
                <option key={sw.id} value={sw.id}>{sw.first_name} {sw.last_name} (age {sw.age})</option>
              ))}
            </select>
          </div>
        ))}
      </div>

      <button
        className="btn btn-primary"
        style={{ width: '100%', padding: '0.5rem', fontSize: '0.85rem' }}
        onClick={() => onSave(ageGroup, gender, stroke, identifier, s1, s2, s3, s4)}
      >
        <Save size={14} /> Save Relay
      </button>
    </div>
  );
}

// ─── Main Coach Meet Detail Component ────────────────────────────────
export default function CoachMeetDetail({ meet, onBack }) {
  const [activeTab, setActiveTab] = useState('entries');
  const user = JSON.parse(localStorage.getItem('user') || '{}');

  return (
    <div className="animate-fade-in">
      <button className="btn btn-outline" onClick={onBack} style={{ marginBottom: '2rem', gap: '0.5rem' }}>
        <ArrowLeft size={18} /> Back to Meets
      </button>

      <div style={{ marginBottom: '1.5rem' }}>
        <h1 style={{ margin: 0 }}>{meet.name}</h1>
        <p>{meet.date || 'Date TBD'} · {meet.num_lanes} lanes</p>
      </div>

      <div className="tab-bar">
        <button className={`tab-btn ${activeTab === 'entries' ? 'active' : ''}`} onClick={() => setActiveTab('entries')}>
          <Users size={16} /> Individual Entries
        </button>
        <button className={`tab-btn ${activeTab === 'relays' ? 'active' : ''}`} onClick={() => setActiveTab('relays')}>
          <Zap size={16} /> Relay Assembly
        </button>
      </div>

      {activeTab === 'entries' && <EntriesTab meet={meet} teamId={user.team_id} />}
      {activeTab === 'relays' && <RelayTab meet={meet} teamId={user.team_id} />}
    </div>
  );
}
