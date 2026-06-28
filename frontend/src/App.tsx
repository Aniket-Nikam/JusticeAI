import React, { useState, useEffect } from 'react';
import { Scale, AlertCircle, Loader2, History, Trash2, CheckCircle, ShieldAlert, BarChart3, ChevronDown, ChevronUp } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, Legend, ResponsiveContainer, Cell } from 'recharts';

interface CaseHistory {
  id: str;
  jurisdiction: string;
  crime_type: string;
  submitted_at: string;
  verdict: string;
  confidence: number;
}

interface AnalysisResult {
  id: string;
  case_id: string;
  verdict_classification: string;
  confidence_score: number;
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
  const [analysis, setAnalysis] = useState<AnalysisResult | null>(null);
  const [history, setHistory] = useState<CaseHistory[]>([]);
  const [error, setError] = useState('');
  const [expandedLayer, setExpandedLayer] = useState<string | null>('layer1_result');
  const [challengeText, setChallengeText] = useState('');
  const [submittingChallenge, setSubmittingChallenge] = useState<string | null>(null);

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
    if (!description || !jurisdiction || !crimeType) return;
    
    setLoading(true);
    setError('');
    
    try {
      const res = await fetch('http://localhost:8000/api/v1/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          jurisdiction,
          crime_type: crimeType,
          defendant_profile: profile,
          description,
          counts: [] // Simplified for MVP form
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
      setLoading(false);
    }
  };

  const handleChallenge = async (layerKey: string, layerNum: int) => {
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

  const getVerdictColor = (verdict: string) => {
    switch(verdict) {
      case 'CONSISTENT': return 'text-emerald-400 border-emerald-400/30 bg-emerald-400/10';
      case 'LENIENT': 
      case 'SIGNIFICANTLY LENIENT': return 'text-amber-400 border-amber-400/30 bg-amber-400/10';
      case 'HARSH': 
      case 'SIGNIFICANTLY HARSH': return 'text-rose-400 border-rose-400/30 bg-rose-400/10';
      default: return 'text-gray-400 border-gray-400/30 bg-gray-400/10';
    }
  };

  const renderLayer = (key: string, title: string) => {
    if (!analysis) return null;
    const layer = (analysis as any)[key];
    if (!layer) return null;
    
    const isExpanded = expandedLayer === key;
    const layerNum = parseInt(key.replace('layer', '').replace('_result', ''));
    
    return (
      <div className="border border-slate-700/50 rounded-lg mb-4 bg-slate-800/30 overflow-hidden">
        <button 
          onClick={() => setExpandedLayer(isExpanded ? null : key)}
          className="w-full flex justify-between items-center p-4 hover:bg-slate-700/30 transition-colors"
        >
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-full bg-indigo-500/20 text-indigo-400 flex items-center justify-center font-bold">
              {layerNum}
            </div>
            <h3 className="font-semibold text-lg">{title}</h3>
          </div>
          {isExpanded ? <ChevronUp size={20} /> : <ChevronDown size={20} />}
        </button>
        
        {isExpanded && (
          <div className="p-4 border-t border-slate-700/50 bg-slate-800/50">
            <div className="mb-3">
              <span className="text-xs uppercase tracking-wider text-slate-400 font-semibold block mb-1">Status / Finding</span>
              <div className="inline-block px-3 py-1 rounded-full bg-slate-700 text-sm font-medium mb-2">
                {layer.status || (layer.bias_detected !== undefined ? (layer.bias_detected ? 'BIAS DETECTED' : 'NO BIAS') : 'EVALUATED')}
              </div>
            </div>
            <p className="text-slate-300 leading-relaxed mb-4">{layer.finding}</p>
            
            <div className="mt-4 p-3 bg-slate-900/50 border border-indigo-500/20 rounded-md">
              <span className="text-xs font-bold text-indigo-400 uppercase tracking-wider mb-2 block">Agentic Memory (Challenge Error)</span>
              <div className="flex gap-2">
                <input 
                  type="text"
                  value={expandedLayer === key ? challengeText : ''}
                  onChange={e => setChallengeText(e.target.value)}
                  placeholder="Spot an error? Explain it here to update the AI's future memory..."
                  className="flex-1 bg-slate-800 border border-slate-700 rounded p-2 text-xs focus:border-indigo-500 focus:outline-none"
                />
                <button 
                  onClick={() => handleChallenge(key, layerNum)}
                  disabled={submittingChallenge === key || !challengeText}
                  className="bg-indigo-600/80 hover:bg-indigo-500 text-xs px-3 rounded text-white font-medium"
                >
                  {submittingChallenge === key ? 'Saving...' : 'Challenge'}
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-[#0a0f1c] text-slate-200 font-sans flex">
      
      {/* Sidebar */}
      <div className="w-80 bg-slate-900/80 border-r border-slate-800 p-6 flex flex-col h-screen overflow-y-auto shrink-0">
        <div className="flex items-center gap-3 mb-8">
          <Scale className="text-indigo-400" size={32} />
          <h1 className="text-2xl font-bold tracking-tight bg-gradient-to-r from-indigo-400 to-purple-400 bg-clip-text text-transparent">
            JusticeAI
          </h1>
        </div>
        
        <div className="flex items-center gap-2 mb-4 text-slate-400 uppercase text-xs font-bold tracking-wider">
          <History size={14} />
          <span>Recent Analyses</span>
        </div>
        
        <div className="flex-1 overflow-y-auto space-y-3 mb-6 pr-2 custom-scrollbar">
          {history.length === 0 ? (
            <p className="text-slate-500 text-sm italic">No case history.</p>
          ) : (
            history.map((h, i) => (
              <div key={i} className="p-3 bg-slate-800/50 rounded-lg border border-slate-700/50 hover:border-indigo-500/30 transition-colors cursor-pointer group relative">
                <div className="flex justify-between items-start mb-1">
                  <span className={`text-[10px] uppercase font-bold px-1.5 py-0.5 rounded ${getVerdictColor(h.verdict)}`}>
                    {h.verdict.substring(0, 10)}
                  </span>
                  <span className="text-xs text-slate-500">{new Date(h.submitted_at).toLocaleDateString()}</span>
                </div>
                <h4 className="text-sm font-medium text-slate-300 truncate">{h.crime_type}</h4>
                <p className="text-xs text-slate-500 truncate">{h.jurisdiction}</p>
              </div>
            ))
          )}
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col h-screen overflow-hidden">
        
        {/* Top Navbar / Form Header */}
        <div className="bg-slate-900/50 border-b border-slate-800 p-6 shadow-sm backdrop-blur-sm z-10">
          <form onSubmit={handleSubmit} className="max-w-6xl mx-auto">
            <div className="grid grid-cols-3 gap-4 mb-4">
              <div>
                <label className="block text-xs font-semibold text-slate-400 mb-1">Jurisdiction</label>
                <input 
                  type="text" 
                  value={jurisdiction}
                  onChange={e => setJurisdiction(e.target.value)}
                  placeholder="e.g. California, Federal" 
                  className="w-full bg-slate-800 border border-slate-700 rounded-md p-2.5 text-sm focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-all outline-none"
                />
              </div>
              <div>
                <label className="block text-xs font-semibold text-slate-400 mb-1">Crime Type</label>
                <input 
                  type="text" 
                  value={crimeType}
                  onChange={e => setCrimeType(e.target.value)}
                  placeholder="e.g. Sexual Assault" 
                  className="w-full bg-slate-800 border border-slate-700 rounded-md p-2.5 text-sm focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-all outline-none"
                />
              </div>
              <div>
                <label className="block text-xs font-semibold text-slate-400 mb-1">Defendant Profile</label>
                <input 
                  type="text" 
                  value={profile}
                  onChange={e => setProfile(e.target.value)}
                  placeholder="e.g. 19yo male, no prior record" 
                  className="w-full bg-slate-800 border border-slate-700 rounded-md p-2.5 text-sm focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-all outline-none"
                />
              </div>
            </div>
            
            <div className="flex gap-4">
              <textarea 
                value={description}
                onChange={e => setDescription(e.target.value)}
                placeholder="Paste the factual case description and actual sentence here..." 
                className="flex-1 bg-slate-800 border border-slate-700 rounded-md p-3 text-sm focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-all outline-none resize-none h-14 custom-scrollbar"
              ></textarea>
              <button 
                type="submit" 
                disabled={loading || !description}
                className="bg-indigo-600 hover:bg-indigo-500 disabled:bg-slate-700 disabled:text-slate-500 text-white px-6 rounded-md font-medium transition-colors flex items-center justify-center min-w-[140px]"
              >
                {loading ? <Loader2 className="animate-spin" size={20} /> : 'Analyze Case'}
              </button>
            </div>
          </form>
        </div>
        
        {/* Results Area */}
        <div className="flex-1 overflow-y-auto p-8 custom-scrollbar">
          <div className="max-w-6xl mx-auto">
            {error && (
              <div className="bg-rose-500/10 border border-rose-500/30 text-rose-400 p-4 rounded-lg flex items-start gap-3 mb-8">
                <AlertCircle className="shrink-0 mt-0.5" size={20} />
                <p>{error}</p>
              </div>
            )}
            
            {!analysis && !loading && !error && (
              <div className="h-full flex flex-col items-center justify-center text-slate-500 mt-20">
                <Scale size={64} className="mb-4 opacity-20" />
                <h2 className="text-xl font-medium mb-2">Ready for Analysis</h2>
                <p className="max-w-md text-center">Enter the case details above. JusticeAI will automatically fetch live statutes and precedents before generating a verdict.</p>
              </div>
            )}
            
            {analysis && (
              <div className="animate-fade-in pb-20">
                
                {/* Hero Stats */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                  <div className={`col-span-2 p-6 rounded-xl border ${getVerdictColor(analysis.verdict_classification)} flex flex-col justify-center relative overflow-hidden group`}>
                    <div className="absolute top-0 right-0 p-4 opacity-10 scale-150 transform transition-transform group-hover:scale-[2]">
                      <Scale size={100} />
                    </div>
                    <span className="text-sm font-bold uppercase tracking-widest opacity-80 mb-2">Verdict Classification</span>
                    <h2 className="text-4xl font-black tracking-tight">{analysis.verdict_classification}</h2>
                  </div>
                  
                  <div className="p-6 rounded-xl border border-indigo-500/30 bg-indigo-500/10 flex flex-col items-center justify-center">
                    <span className="text-sm font-bold uppercase tracking-widest text-indigo-400 mb-2">Confidence Score</span>
                    <div className="flex items-baseline gap-1">
                      <h2 className="text-5xl font-black text-indigo-300">{analysis.confidence_score}</h2>
                      <span className="text-indigo-500/50 font-bold">/100</span>
                    </div>
                  </div>
                </div>
                
                <div className="grid grid-cols-1 xl:grid-cols-3 gap-8">
                  {/* Left Column: Layers */}
                  <div className="xl:col-span-2">
                    <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
                      <ShieldAlert className="text-indigo-400" size={20} />
                      Reasoning Layers
                    </h2>
                    
                    {renderLayer('layer1_result', 'Legal Compliance')}
                    {renderLayer('layer2_result', 'Sentencing Consistency')}
                    {renderLayer('layer3_result', 'Factor Analysis & Bias')}
                    {renderLayer('layer4_result', 'Cross-Jurisdictional Precedent')}
                    {renderLayer('layer5_result', 'Defendant Profile Context')}
                    
                    <div className="mt-8 p-6 bg-slate-800/30 border border-slate-700/50 rounded-xl">
                      <h3 className="text-lg font-bold mb-3">AI Executive Summary</h3>
                      <p className="text-slate-300 leading-relaxed">{analysis.summary}</p>
                    </div>
                  </div>
                  
                  {/* Right Column: Data & Citations */}
                  <div className="space-y-8">
                    <div className="p-6 bg-slate-800/30 border border-slate-700/50 rounded-xl">
                      <h3 className="text-lg font-bold mb-4 flex items-center gap-2">
                        <BarChart3 className="text-indigo-400" size={20} />
                        Sentence Bounds
                      </h3>
                      
                      <div className="h-[200px] w-full">
                        <ResponsiveContainer width="100%" height="100%">
                          <BarChart data={[
                            { name: 'Min', value: analysis.recommended_range_min_months },
                            { name: 'Max', value: analysis.recommended_range_max_months }
                          ]} layout="vertical" margin={{ top: 0, right: 20, left: 0, bottom: 0 }}>
                            <XAxis type="number" />
                            <YAxis dataKey="name" type="category" width={40} tick={{fill: '#94a3b8'}} />
                            <Tooltip cursor={{fill: '#1e293b'}} contentStyle={{backgroundColor: '#0f172a', borderColor: '#334155'}} />
                            <Bar dataKey="value" fill="#6366f1" radius={[0, 4, 4, 0]}>
                              {
                                [
                                  { name: 'Min', value: analysis.recommended_range_min_months },
                                  { name: 'Max', value: analysis.recommended_range_max_months }
                                ].map((entry, index) => (
                                  <Cell key={`cell-${index}`} fill={index === 0 ? '#818cf8' : '#4f46e5'} />
                                ))
                              }
                            </Bar>
                          </BarChart>
                        </ResponsiveContainer>
                      </div>
                      <p className="text-xs text-center text-slate-500 mt-2">Recommended Range (Months)</p>
                    </div>
                    
                    <div className="p-6 bg-slate-800/30 border border-slate-700/50 rounded-xl">
                      <h3 className="text-lg font-bold mb-4 flex items-center gap-2">
                        <CheckCircle className="text-indigo-400" size={20} />
                        Verified Citations
                      </h3>
                      <div className="space-y-4 max-h-[400px] overflow-y-auto custom-scrollbar pr-2">
                        {analysis.citations.map((c, i) => (
                          <div key={i} className="text-sm border-l-2 border-slate-600 pl-3">
                            <span className="inline-block px-1.5 py-0.5 bg-slate-700 text-[10px] font-bold rounded text-slate-300 mb-1 mr-2">L{c.layer}</span>
                            <span className="text-indigo-300 font-medium">{c.source_type}</span>
                            <a href={c.source_url || '#'} target="_blank" rel="noreferrer" className="block text-slate-400 hover:text-indigo-400 truncate mt-1">
                              {c.source_title || 'View Source'}
                            </a>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                </div>
                
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
