import React, { useState, useEffect, useRef } from 'react';
import { Scale, ShieldAlert, History, UploadCloud, FileSignature, ChevronDown, ChevronUp, AlertCircle, Trash2, BarChart3, ArrowLeft, Activity, Gavel, ChevronRight, BookOpen, Download, Printer } from 'lucide-react';
import { Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer as RadarResponsiveContainer } from 'recharts';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts';

interface CaseHistory {
  id: string;
  jurisdiction: string;
  crime_type: string;
  crime_description?: string;
  submitted_at: string;
  verdict: string;
  confidence: number;
}

interface AnalysisResult {
  id: string;
  case_id: string;
  verdict_classification: string;
  confidence_score: number;
  confidence_breakdown?: {
    legal_compliance: number;
    precedent_match: number;
    absence_of_bias: number;
  };
  recommended_range_min_months: number;
  recommended_range_max_months: number;
  summary: string;
  layer1_result: any;
  layer2_result: any;
  layer3_result: any;
  layer4_result: any;
  layer5_result: any;
  full_reasoning_chain: string;
  citations: any[];
}

function App() {
  const [jurisdiction, setJurisdiction] = useState('');
  const [crimeType, setCrimeType] = useState('');
  const [profile, setProfile] = useState('');
  const [description, setDescription] = useState('');
  const [loading, setLoading] = useState(false);
  const [loadingStep, setLoadingStep] = useState(0);
  const [dragActive, setDragActive] = useState(false);
  const [selectedCaseId, setSelectedCaseId] = useState<string | null>(null);
  const [showOptionalFields, setShowOptionalFields] = useState(false);
  
  const [analysis, setAnalysis] = useState<AnalysisResult | null>(null);
  const [history, setHistory] = useState<CaseHistory[]>([]);
  const [error, setError] = useState('');
  const [expandedLayer, setExpandedLayer] = useState<string | null>('layer1_result');
  const [challengeText, setChallengeText] = useState('');
  const [submittingChallenge, setSubmittingChallenge] = useState<string | null>(null);
  const [uploadingPdf, setUploadingPdf] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const loadingStepsText = [
    "Initializing multi-layer reasoning pipeline...",
    "Layer 1 — Assessing legal compliance guidelines...",
    "Layer 2 — Evaluating sentencing consistency precedents...",
    "Layer 3 — Running factor analysis & bias detection...",
    "Layer 4 — Cross-jurisdictional precedent evaluation...",
    "Layer 5 — Defendant profile context analysis...",
    "Compiling executive summary and sentence boundaries..."
  ];

  useEffect(() => {
    fetchHistory();
  }, []);

  const fetchHistory = async () => {
    try {
      const res = await fetch('http://localhost:8000/api/v1/cases');
      if (res.ok) {
        const data = await res.json();
        setHistory(data);
      }
    } catch (err) {
      console.error("Failed to fetch history", err);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!description) return;
    
    setLoading(true);
    setLoadingStep(0);
    setError('');
    setAnalysis(null);
    setSelectedCaseId(null);

    const timer = setInterval(() => {
      setLoadingStep(prev => prev < 6 ? prev + 1 : prev);
    }, 1300);
    
    try {
      const res = await fetch('http://localhost:8000/api/v1/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          jurisdiction: jurisdiction || 'Not specified',
          crime_type: crimeType || 'Not specified',
          defendant_profile: profile || 'Not specified',
          description,
          counts: [] 
        })
      });
      
      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || 'Analysis failed');
      }
      
      const data = await res.json();
      setAnalysis(data);
      fetchHistory();
    } catch (err: any) {
      setError(err.message);
    } finally {
      clearInterval(timer);
      setLoading(false);
    }
  };

  const handleChallenge = async (layerKey: string, layerNum: number) => {
    if (!analysis || !challengeText) return;
    
    setSubmittingChallenge(layerKey);
    try {
      const res = await fetch(`http://localhost:8000/api/v1/analyses/${analysis.id}/challenge`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          layer_challenged: layerNum,
          challenge_text: challengeText
        })
      });
      if (res.ok) {
        alert("Challenge submitted! The Agentic Memory has been updated.");
        setChallengeText('');
      }
    } catch (err) {
      console.error(err);
    } finally {
      setSubmittingChallenge(null);
    }
  };

  const uploadPdfFile = async (file: File) => {
    setUploadingPdf(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await fetch('http://localhost:8000/api/v1/extract-case-pdf', {
        method: 'POST',
        body: formData
      });
      if (!res.ok) throw new Error("Failed to extract PDF");
      const data = await res.json();
      
      setDescription(data.description || description);
      setJurisdiction(data.jurisdiction || jurisdiction);
      setCrimeType(data.crime_type || crimeType);
      setProfile(data.defendant_profile || profile);
      if (data.jurisdiction || data.crime_type || data.defendant_profile) {
        setShowOptionalFields(true);
      }
      
      alert("PDF successfully extracted and form auto-filled!");
    } catch (err) {
      console.error(err);
      alert("Error extracting PDF.");
    } finally {
      setUploadingPdf(false);
    }
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    await uploadPdfFile(file);
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = async (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const file = e.dataTransfer.files[0];
      if (file.type !== "application/pdf" && !file.name.endsWith('.pdf')) {
        alert("Please upload a PDF file.");
        return;
      }
      await uploadPdfFile(file);
    }
  };

  const handleSelectCase = async (caseId: string) => {
    setSelectedCaseId(caseId);
    setLoading(true);
    setError('');
    setAnalysis(null);
    try {
      const res = await fetch(`http://localhost:8000/api/v1/cases/${caseId}/analysis`);
      if (!res.ok) throw new Error("Failed to retrieve analysis.");
      const data = await res.json();
      setAnalysis(data);
      
      const hItem = history.find(h => h.id === caseId);
      if (hItem) {
        setJurisdiction(hItem.jurisdiction);
        setCrimeType(hItem.crime_type);
      }
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteCase = async (e: React.MouseEvent, id: string) => {
    e.stopPropagation();
    if (!confirm("Delete this case and its analysis?")) return;
    try {
      const res = await fetch(`http://localhost:8000/api/v1/cases/${id}`, { method: 'DELETE' });
      if (res.ok) {
        if (analysis && analysis.case_id === id) {
          setAnalysis(null);
          setSelectedCaseId(null);
        }
        fetchHistory();
      }
    } catch (err) {
      console.error("Failed to delete case", err);
    }
  };

  const handleNewAnalysis = () => {
    setAnalysis(null);
    setSelectedCaseId(null);
    setJurisdiction('');
    setCrimeType('');
    setProfile('');
    setDescription('');
    setError('');
  };

  const exportToText = () => {
    if (!analysis) return;
    const content = `JUSTICE AI - SENTENCING ANALYSIS REPORT
=======================================

Case Jurisdiction: ${jurisdiction || 'Not specified'}
Crime Type: ${crimeType || 'Not specified'}
Defendant Profile: ${profile || 'Not specified'}

CASE DESCRIPTION:
${description}

VERDICT: ${analysis.verdict_classification}
CONFIDENCE: ${analysis.confidence_score}%
RECOMMENDED RANGE: ${analysis.recommended_range_min_months} to ${analysis.recommended_range_max_months} months

SUMMARY:
${analysis.summary}

REASONING CHAIN:
${analysis.full_reasoning_chain}
`;
    const blob = new Blob([content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `justiceai-report-${Date.now()}.txt`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const getVerdictClass = (verdict: string) => {
    switch(verdict) {
      case 'CONSISTENT': return 'verdict-consistent';
      case 'LENIENT': case 'SIGNIFICANTLY LENIENT': return 'verdict-lenient';
      case 'HARSH': case 'SIGNIFICANTLY HARSH': return 'verdict-harsh';
      default: return '';
    }
  };
  
  const getVerdictBadgeClass = (verdict: string) => {
    switch(verdict) {
      case 'CONSISTENT': return 'verdict-consistent-tag';
      case 'LENIENT': case 'SIGNIFICANTLY LENIENT': return 'verdict-lenient-tag';
      case 'HARSH': case 'SIGNIFICANTLY HARSH': return 'verdict-harsh-tag';
      default: return 'verdict-neutral-tag';
    }
  };

  const renderLayer = (key: string, title: string) => {
    if (!analysis) return null;
    const layer = (analysis as any)[key];
    if (!layer) return null;
    
    const isExpanded = expandedLayer === key;
    const layerNum = parseInt(key.replace('layer', '').replace('_result', ''));
    const statusText = layer.status || (layer.bias_detected !== undefined ? (layer.bias_detected ? 'BIAS DETECTED' : 'NO BIAS') : 'EVALUATED');
    
    return (
      <div key={key} className={`timeline-item ${isExpanded ? 'expanded' : ''}`}>
        <div className="timeline-left">
          <div className="timeline-dot">{layerNum}</div>
          <div className="timeline-line"></div>
        </div>
        <div className="timeline-right">
          <div className="timeline-card">
            <button 
              onClick={() => setExpandedLayer(isExpanded ? null : key)}
              className="timeline-header-btn"
            >
              <div className="timeline-header-info">
                <span className="timeline-card-title">{title}</span>
                <span className="timeline-card-status">{statusText}</span>
              </div>
              {isExpanded ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
            </button>
            
            {isExpanded && (
              <div className="timeline-body">
                <p className="timeline-finding">{layer.finding}</p>
                
                <div className="challenge-box">
                  <span className="challenge-label">Agentic Memory — Challenge This Finding</span>
                  <div className="challenge-form-row">
                    <input 
                      type="text"
                      value={challengeText}
                      onChange={e => setChallengeText(e.target.value)}
                      placeholder="Spot an error? Override the AI's future reasoning..."
                      className="challenge-input"
                    />
                    <button 
                      onClick={() => handleChallenge(key, layerNum)}
                      disabled={submittingChallenge === key || !challengeText}
                      className="btn-challenge"
                    >
                      {submittingChallenge === key ? 'Saving...' : 'Challenge'}
                    </button>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="layout-wrapper">
      
      {/* ── Sidebar ── */}
      <div className="sidebar">
        <div className="sidebar-brand">
          <Scale className="sidebar-logo" size={24} />
          <span className="sidebar-title">JusticeAI</span>
        </div>
        
        <div className="sidebar-section-title">
          <History size={11} />
          <span>Case History</span>
        </div>
        
        <div className="history-list custom-scrollbar">
          {history.length === 0 ? (
            <p className="sidebar-empty">No cases analyzed yet.</p>
          ) : (
            history.map((h) => (
              <div 
                key={h.id} 
                onClick={() => handleSelectCase(h.id)}
                className={`history-item ${selectedCaseId === h.id ? 'active' : ''}`}
              >
                <div className="history-header">
                  <span className={`history-badge ${getVerdictBadgeClass(h.verdict)}`}>
                    {h.verdict.replace('SIGNIFICANTLY ', '')}
                  </span>
                  <span className="history-date">
                    {new Date(h.submitted_at).toLocaleDateString(undefined, {month: 'short', day: 'numeric'})}
                  </span>
                </div>
                <div className="history-crime">
                  {h.crime_type && h.crime_type !== 'Not specified' ? h.crime_type : 'Case Analysis'}
                </div>
                <div className="history-jurisdiction">
                  {h.jurisdiction && h.jurisdiction !== 'Not specified' ? h.jurisdiction : 
                   (h.crime_description ? (h.crime_description.substring(0, 40) + (h.crime_description.length > 40 ? '...' : '')) : '—')}
                </div>
                <button 
                  className="history-delete-btn"
                  onClick={(e) => handleDeleteCase(e, h.id)}
                  title="Delete case"
                >
                  <Trash2 size={12} />
                </button>
              </div>
            ))
          )}
        </div>
      </div>

      {/* ── Main Content ── */}
      <div className="main-content custom-scrollbar">
        <div className="app-container">
          
          {error && (
            <div className="toast-alert">
              <AlertCircle size={16} />
              <p>{error}</p>
            </div>
          )}
          
          {/* ── Form View ── */}
          {!analysis && !loading && (
            <div className="animate-fade-in">
              <div className="header">
                <div className="header-icon">
                  <Gavel size={24} />
                </div>
                <h1>Sentencing Analysis</h1>
                <p>Paste case facts below or upload a court document. Our multi-agent pipeline evaluates sentencing against statutes, precedents, and bias indicators.</p>
              </div>
              
              <div className="glass-card">
                <h2 className="glass-card-title">
                  <FileSignature size={18} />
                  New Case Submission
                </h2>

                {/* Upload zone */}
                <div 
                  className={`upload-zone ${dragActive ? 'drag-active' : ''}`}
                  onDragEnter={handleDrag}
                  onDragOver={handleDrag}
                  onDragLeave={handleDrag}
                  onDrop={handleDrop}
                  onClick={() => fileInputRef.current?.click()}
                >
                  <input 
                    type="file" 
                    accept=".pdf" 
                    className="hidden" 
                    ref={fileInputRef}
                    onChange={handleFileUpload}
                    style={{ display: 'none' }}
                  />
                  <UploadCloud className="upload-icon" size={32} />
                  <h3 className="upload-title">
                    {uploadingPdf ? "Extracting document..." : "Upload Court Document"}
                  </h3>
                  <p className="upload-subtitle">
                    Drop a PDF here or click to browse — fields auto-fill via OCR
                  </p>
                </div>

                {/* Main Form */}
                <form onSubmit={handleSubmit}>
                  {/* Hero: Case Description */}
                  <div className="form-group">
                    <label className="form-label">
                      Case Description & Factual Circumstances
                    </label>
                    <textarea 
                      value={description} 
                      onChange={e => setDescription(e.target.value)} 
                      className="form-textarea-hero" 
                      placeholder={"Describe the case facts, charges, and actual sentence imposed (if known).\n\nExample: \"Defendant, a 22-year-old first-time offender, was convicted of aggravated assault in Los Angeles County Superior Court. The incident involved a bar altercation resulting in a broken jaw. Judge imposed 4 years state prison. Prosecution sought 6 years; defense argued for probation citing no prior record and provocation.\""}
                      required
                    ></textarea>
                  </div>

                  {/* Optional Fields Toggle */}
                  <button 
                    type="button"
                    className="optional-fields-toggle"
                    onClick={() => setShowOptionalFields(!showOptionalFields)}
                  >
                    <ChevronRight size={13} style={{ transform: showOptionalFields ? 'rotate(90deg)' : 'none' }} />
                    <span>Additional details (optional)</span>
                  </button>

                  {showOptionalFields && (
                    <div className="optional-fields">
                      <div className="form-group">
                        <label className="form-label">
                          Jurisdiction
                          <span className="form-label-hint">optional</span>
                        </label>
                        <input 
                          type="text" 
                          value={jurisdiction} 
                          onChange={e => setJurisdiction(e.target.value)} 
                          className="form-input" 
                          placeholder="e.g. California, Federal"
                        />
                      </div>
                      <div className="form-group">
                        <label className="form-label">
                          Crime Type
                          <span className="form-label-hint">optional</span>
                        </label>
                        <input 
                          type="text" 
                          value={crimeType} 
                          onChange={e => setCrimeType(e.target.value)} 
                          className="form-input" 
                          placeholder="e.g. Aggravated Assault"
                        />
                      </div>
                      <div className="form-group">
                        <label className="form-label">
                          Defendant Profile
                          <span className="form-label-hint">optional</span>
                        </label>
                        <input 
                          type="text" 
                          value={profile} 
                          onChange={e => setProfile(e.target.value)} 
                          className="form-input" 
                          placeholder="e.g. 22yo, no prior record"
                        />
                      </div>
                    </div>
                  )}
                  
                  <button type="submit" className="btn-submit" disabled={!description.trim() || uploadingPdf}>
                    <Scale size={16} />
                    Analyze Case
                  </button>
                </form>
              </div>
            </div>
          )}

          {/* ── Loading State ── */}
          {loading && (
            <div className="glass-card animate-fade-in">
              <div className="loading-box">
                <div className="loading-scales">
                  <Scale size={64} />
                </div>
                <h2 className="loading-box-title">Analyzing Case</h2>
                <p className="loading-box-desc">
                  Running multi-agent reasoning pipeline against statutes and precedents...
                </p>
                
                <div className="loading-steps">
                  {loadingStepsText.map((text, index) => {
                    let stepClass = "loading-step";
                    if (index < loadingStep) stepClass += " completed";
                    else if (index === loadingStep) stepClass += " active";
                    
                    return (
                      <div key={index} className={stepClass}>
                        <div className="step-indicator-dot"></div>
                        <span>{text}</span>
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>
          )}
          
          {/* ── Analysis Results ── */}
          {analysis && !loading && (
            <div className="animate-fade-in" style={{ paddingBottom: '3rem' }}>
              
              <div className="action-bar no-print">
                <button onClick={handleNewAnalysis} className="btn-back">
                  <ArrowLeft size={13} />
                  <span>New Analysis</span>
                </button>
                <div className="export-group">
                  <button onClick={() => window.print()} className="btn-export">
                    <Printer size={13} />
                    <span>Print / PDF</span>
                  </button>
                  <button onClick={exportToText} className="btn-export">
                    <Download size={13} />
                    <span>Export Text</span>
                  </button>
                </div>
              </div>

              {/* Verdict Hero */}
              <div className={`verdict-banner ${getVerdictClass(analysis.verdict_classification)}`}>
                <div className="verdict-banner-bg-icon">
                  <Scale />
                </div>
                <div className="verdict-banner-lbl">Verdict Classification</div>
                <h2 className="verdict-banner-title">{analysis.verdict_classification}</h2>
                <span className="verdict-banner-confidence">
                  <Activity size={12} />
                  Confidence: {analysis.confidence_score}%
                </span>
                <p className="verdict-banner-desc">
                  Classification computed relative to applicable statutes, historical sentencing data, and cross-jurisdictional precedents.
                </p>
              </div>

              {/* Charts */}
              <div className="dashboard-grid">
                <div className="chart-card">
                  <div className="chart-card-title">
                    <Activity size={13} />
                    <span>Confidence Breakdown</span>
                  </div>
                  {analysis.confidence_breakdown ? (
                    <div className="chart-container">
                      <RadarResponsiveContainer width="100%" height="100%">
                        <RadarChart cx="50%" cy="50%" outerRadius="75%" data={[
                          { subject: 'Legal Compliance', A: analysis.confidence_breakdown.legal_compliance, fullMark: 100 },
                          { subject: 'Precedent Match', A: analysis.confidence_breakdown.precedent_match, fullMark: 100 },
                          { subject: 'Absence of Bias', A: analysis.confidence_breakdown.absence_of_bias, fullMark: 100 }
                        ]}>
                          <PolarGrid stroke="rgba(201, 168, 76, 0.08)" />
                          <PolarAngleAxis dataKey="subject" tick={{ fill: '#94a3b8', fontSize: 9, fontWeight: 500 }} />
                          <PolarRadiusAxis angle={30} domain={[0, 100]} tick={false} axisLine={false} />
                          <Radar name="Confidence" dataKey="A" stroke="#c9a84c" fill="#c9a84c" fillOpacity={0.2} />
                        </RadarChart>
                      </RadarResponsiveContainer>
                    </div>
                  ) : (
                    <p style={{ color: 'var(--text-muted)', fontSize: '0.8rem', margin: 'auto' }}>No breakdown available.</p>
                  )}
                </div>

                <div className="chart-card">
                  <div className="chart-card-title">
                    <BarChart3 size={13} />
                    <span>Recommended Range (Months & Years)</span>
                  </div>
                  <div className="chart-container">
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart 
                        data={[
                          { name: 'Minimum', value: analysis.recommended_range_min_months },
                          { name: 'Maximum', value: analysis.recommended_range_max_months }
                        ]} 
                        layout="vertical" 
                        margin={{ top: 15, right: 15, left: 5, bottom: 5 }}
                      >
                        <XAxis type="number" stroke="#334155" tick={{ fill: '#94a3b8', fontSize: 9 }} />
                        <YAxis dataKey="name" type="category" width={70} stroke="#334155" tick={{ fill: '#94a3b8', fontSize: 9 }} />
                        <Tooltip 
                          formatter={(value: number) => [`${value} months (${(value / 12).toFixed(1)} years)`, 'Duration']}
                          cursor={{ fill: 'rgba(255,255,255,0.01)' }} 
                          contentStyle={{ backgroundColor: '#0c0e18', borderColor: 'rgba(255,255,255,0.06)', borderRadius: '8px', fontSize: '11px' }} 
                        />
                        <Bar dataKey="value" radius={[0, 4, 4, 0]} barSize={20}>
                          <Cell fill="#c9a84c" />
                          <Cell fill="#a68936" />
                        </Bar>
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                </div>
              </div>

              {/* Reasoning Layers */}
              <h3 className="reasoning-section-title">
                <ShieldAlert size={16} />
                <span>Reasoning Audit Trail</span>
              </h3>
              
              <div className="timeline">
                {renderLayer('layer1_result', 'Legal Compliance')}
                {renderLayer('layer2_result', 'Sentencing Consistency')}
                {renderLayer('layer3_result', 'Aggravating Factors & Bias')}
                {renderLayer('layer4_result', 'Cross-Jurisdictional Precedent')}
                {renderLayer('layer5_result', 'Defendant Profile Context')}
              </div>

              {/* Summary & Citations */}
              <div className="details-split">
                <div className="summary-card">
                  <h3 className="summary-title">
                    <BookOpen size={15} />
                    Executive Summary
                  </h3>
                  <div className="summary-text">{analysis.summary}</div>
                </div>

                <div className="citations-card">
                  <h3 className="citations-title">
                    <Gavel size={15} />
                    Verified Citations
                  </h3>
                  <div className="citations-list custom-scrollbar">
                    {analysis.citations && analysis.citations.length > 0 ? (
                      analysis.citations.map((c, i) => (
                        <div key={i} className="citation-item">
                          <div className="citation-badge-row">
                            <span className="citation-badge">L{c.layer}</span>
                            <span className="citation-type">{c.source_type}</span>
                          </div>
                          <a 
                            href={c.source_url || '#'} 
                            target="_blank" 
                            rel="noreferrer" 
                            className="citation-link" 
                            title={c.source_title || 'View Source'}
                          >
                            {c.source_title || 'View Citation'}
                          </a>
                        </div>
                      ))
                    ) : (
                      <p style={{ color: 'var(--text-muted)', fontSize: '0.78rem', fontStyle: 'italic' }}>No citations listed.</p>
                    )}
                  </div>
                </div>
              </div>

            </div>
          )}

        </div>
      </div>

    </div>
  );
}

export default App;
