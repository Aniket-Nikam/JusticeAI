import React, { useState, useEffect } from 'react';
import axios from 'axios';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Scale, ArrowLeft, AlertCircle, Loader2, Clock, History, Trash2 } from 'lucide-react';
import './index.css';

interface CaseHistory {
  id: number;
  description: string;
  report: string;
  timestamp: string;
}

function App() {
  const [caseDetails, setCaseDetails] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [report, setReport] = useState('');
  const [error, setError] = useState('');
  const [history, setHistory] = useState<CaseHistory[]>([]);

  useEffect(() => {
    fetchHistory();
  }, []);

  const fetchHistory = async () => {
    try {
      const response = await axios.get(`${import.meta.env.VITE_API_URL || ''}/api/v1/cases?limit=20`);
      setHistory(response.data);
    } catch (err) {
      console.error("Failed to fetch history", err);
    }
  };

  const handleAnalyze = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!caseDetails.trim()) return;

    setIsLoading(true);
    setError('');

    try {
      const response = await axios.post(`${import.meta.env.VITE_API_URL || ''}/api/v1/analyze`, {
        description: caseDetails
      });
      setReport(response.data.report);
      fetchHistory(); // Refresh history
    } catch (err: any) {
      console.error("Analysis Error:", err);
      if (err.response?.status === 422) {
        setError("Input validation failed: Case description must be between 10 and 10,000 characters.");
      } else {
        setError(err.response?.data?.detail || "An internal server error occurred. Please try again later.");
      }
    } finally {
      setIsLoading(false);
    }
  };

  const loadHistoricalCase = (hist: CaseHistory) => {
    setCaseDetails(hist.description);
    setReport(hist.report);
    setError('');
  };

  const handleDelete = async (e: React.MouseEvent, id: number) => {
    e.stopPropagation();
    try {
      await axios.delete(`${import.meta.env.VITE_API_URL || ''}/api/v1/cases/${id}`);
      fetchHistory();
    } catch (err) {
      console.error("Failed to delete case", err);
    }
  };

  const handleReset = () => {
    setReport('');
    setCaseDetails('');
    setError('');
  };

  return (
    <div className="layout-wrapper">
      <aside className="sidebar">
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1.5rem' }}>
          <History size={24} style={{ color: 'var(--accent-color)' }} />
          <h3 style={{ margin: 0 }}>System Memory</h3>
        </div>
        <div className="history-list">
          {history.length === 0 ? (
            <p style={{ fontSize: '0.9rem', color: 'var(--text-secondary)' }}>No prior cases found.</p>
          ) : (
            history.map((hist) => (
              <div key={hist.id} className="history-item" onClick={() => loadHistoricalCase(hist)} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                <div style={{ flex: 1, paddingRight: '1rem', overflow: 'hidden' }}>
                  <div className="history-date">
                    <Clock size={12} />
                    <span>{new Date(hist.timestamp).toLocaleString()}</span>
                  </div>
                  <div className="history-desc">{hist.description}</div>
                </div>
                <button 
                  onClick={(e) => handleDelete(e, hist.id)}
                  style={{ background: 'none', border: 'none', color: 'var(--text-secondary)', cursor: 'pointer', padding: '0.25rem' }}
                  onMouseEnter={(e) => e.currentTarget.style.color = 'var(--danger-color)'}
                  onMouseLeave={(e) => e.currentTarget.style.color = 'var(--text-secondary)'}
                  title="Delete case"
                >
                  <Trash2 size={16} />
                </button>
              </div>
            ))
          )}
        </div>
      </aside>

      <main className="main-content">
        <div className="app-container">
          <header className="header">
            <h1>JusticeAI</h1>
            <p>Autonomous Legal Reasoning & Judicial Analysis</p>
          </header>

          <div className="glass-card">
            {error && (
              <div className="error-message">
                <AlertCircle size={20} />
                <span>{error}</span>
              </div>
            )}

            {!isLoading && !report && (
              <form onSubmit={handleAnalyze}>
                <div className="form-group">
                  <label htmlFor="caseDetails" className="form-label">
                    Provide Case Context & Details
                  </label>
                  <textarea
                    id="caseDetails"
                    className="form-textarea"
                    placeholder="Enter case facts, defendant profile, jurisdiction, and the sentence given..."
                    value={caseDetails}
                    onChange={(e) => setCaseDetails(e.target.value)}
                    required
                    minLength={10}
                    maxLength={10000}
                  />
                </div>
                <button 
                  type="submit" 
                  className="btn-primary"
                  disabled={!caseDetails.trim() || isLoading}
                >
                  <Scale size={20} />
                  <span>Initiate Autonomous Analysis</span>
                </button>
              </form>
            )}

            {isLoading && (
              <div className="loading-container">
                <Loader2 className="spinner" />
                <h3 className="loading-text">
                  Judicial Reasoning (Llama)
                </h3>
                <p className="loading-subtext">
                  Applying Master Prompt constraints across 6 dimensions...
                </p>
              </div>
            )}

            {report && !isLoading && (
              <div className="report-container">
                <div className="report-header">
                  <h2>Analysis Report</h2>
                  <button onClick={handleReset} className="btn-secondary">
                    <ArrowLeft size={16} />
                    <span>New Case</span>
                  </button>
                </div>
                <div className="markdown-body">
                  <ReactMarkdown remarkPlugins={[remarkGfm]}>{report}</ReactMarkdown>
                </div>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}

export default App;
