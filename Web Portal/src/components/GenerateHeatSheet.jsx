import React, { useState, useEffect } from 'react';
import { getMeets, generateHeatSheet } from '../services/api';
import { FileDown, Loader2 } from 'lucide-react';

export default function GenerateHeatSheet() {
  const [meets, setMeets] = useState([]);
  const [selectedMeetId, setSelectedMeetId] = useState('');
  const [loading, setLoading] = useState(false);
  const [fetchingMeets, setFetchingMeets] = useState(true);
  const [error, setError] = useState('');
  const [pdfUrl, setPdfUrl] = useState(null);

  useEffect(() => {
    const fetchMeets = async () => {
      try {
        const data = await getMeets();
        setMeets(data);
        if (data.length > 0) {
          setSelectedMeetId(data[0].id);
        }
      } catch (err) {
        console.error(err);
        setError('Failed to load meets.');
      } finally {
        setFetchingMeets(false);
      }
    };
    fetchMeets();
  }, []);

  const handleGenerate = async (e) => {
    e.preventDefault();
    if (!selectedMeetId) return;

    setError('');
    setLoading(true);
    setPdfUrl(null);

    try {
      const blob = await generateHeatSheet(selectedMeetId);
      // Create a URL for the blob
      const url = window.URL.createObjectURL(blob);
      setPdfUrl(url);
    } catch (err) {
      console.error(err);
      setError('Failed to generate heat sheet. Make sure the backend is running and the meet ID is valid.');
    } finally {
      setLoading(false);
    }
  };

  if (fetchingMeets) return <div className="animate-fade-in"><p>Loading meets...</p></div>;

  return (
    <div className="animate-fade-in" style={{ display: 'flex', gap: '2rem', height: '100%' }}>
      <div style={{ flex: '1', maxWidth: '400px' }}>
        <h1 style={{ marginBottom: '1rem' }}>Heat Sheets</h1>
        <p style={{ marginBottom: '3rem' }}>Generate PDF heat sheets for upcoming meets with a single click.</p>

        <div className="glass-panel" style={{ padding: '2rem' }}>
          <form onSubmit={handleGenerate}>
            <div className="input-group">
              <label>Select Meet</label>
              <select 
                value={selectedMeetId}
                onChange={(e) => setSelectedMeetId(e.target.value)}
                required
              >
                {meets.map(m => (
                  <option key={m.id} value={m.id}>{m.name} ({m.id})</option>
                ))}
              </select>
            </div>

            <button type="submit" className="btn btn-primary" style={{ width: '100%', marginTop: '1rem' }} disabled={loading}>
              {loading ? (
                <>
                  <Loader2 size={18} className="animate-spin" style={{ animation: 'spin 1s linear infinite' }} />
                  Generating...
                </>
              ) : (
                <>
                  <FileDown size={18} />
                  Generate PDF
                </>
              )}
            </button>
            {error && <p style={{ color: 'var(--danger-color)', marginTop: '1rem', fontSize: '0.875rem' }}>{error}</p>}
          </form>
        </div>
      </div>

      <div style={{ flex: '2', height: '100%' }}>
        {pdfUrl ? (
          <div className="glass-panel animate-fade-in" style={{ height: 'calc(100vh - 6rem)', padding: '1rem', display: 'flex', flexDirection: 'column' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
              <h3 style={{ margin: 0 }}>Generated Heat Sheet</h3>
              <a href={pdfUrl} download={`heat_sheet_${selectedMeetId}.pdf`} className="btn btn-primary" style={{ padding: '0.5rem 1rem' }}>
                Download PDF
              </a>
            </div>
            <iframe 
              src={pdfUrl} 
              style={{ width: '100%', flex: 1, border: 'none', borderRadius: '8px', backgroundColor: '#fff' }} 
              title="PDF Preview"
            />
          </div>
        ) : (
           <div className="glass-panel" style={{ height: 'calc(100vh - 6rem)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--text-muted)' }}>
              <div style={{ textAlign: 'center' }}>
                <FileDown size={48} style={{ opacity: 0.5, marginBottom: '1rem' }} />
                <p>Select a meet and generate a heat sheet to preview it here.</p>
              </div>
           </div>
        )}
      </div>
      <style dangerouslySetInnerHTML={{__html: `
        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
      `}} />
    </div>
  );
}
