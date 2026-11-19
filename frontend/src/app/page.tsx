'use client';

import React, { useState, useEffect } from 'react';
import {
  ShieldAlert,
  Search,
  AlertTriangle,
  FileText,
  Users,
  Building2,
  Clock,
  Send,
  X,
  ExternalLink,
  ChevronRight,
  Shield,
  Layers,
  HelpCircle,
  TrendingDown,
  TrendingUp,
  CheckCircle,
  Lock,
  Briefcase,
  ChevronDown,
  ChevronUp,
} from 'lucide-react';

interface Citation {
  ref: string;
  source_file: string;
  sheet_or_page?: string;
  row_or_line?: string;
  fact_text: string;
  confidence: string;
}

interface AskResponse {
  query: string;
  answer: string;
  citations: Citation[];
  confidence: string;
  status: string;
  refusal_reason?: string;
  conflict_detected: boolean;
  conflict_details?: string;
  as_of: string;
}

interface RiskItem {
  rank: number;
  risk_id: string;
  title: string;
  category: string;
  severity: string;
  summary: string;
  evidence_refs: string[];
  recommended_mitigation: string;
}

interface AgentSummary {
  emp_id: string;
  full_name: string;
  title: string;
  department: string;
  location: string;
  status: string;
}

interface ConflictItem {
  conflict_id: string;
  topic: string;
  description: string;
  competing_sources: string;
  proposed_interpretation: string;
  confidence: string;
  what_would_change: string;
  impact_level: string;
  human_status: string;
}

interface TeamEngagement {
  team: string;
  department: string;
  team_size: number;
  respondents: number;
  prior_score: number;
  latest_score: number;
  change: number;
  comments_status: string;
}

interface RequisitionItem {
  req_id: string;
  role: string;
  team: string;
  hiring_manager: string;
  opened_date?: string;
  status: string;
  status_date?: string;
  pipeline_count: number;
  notes?: string;
}

interface HRInsightsResponse {
  as_of: string;
  team_engagement: TeamEngagement[];
  requisitions: RequisitionItem[];
  privacy_safeguards: string[];
}

export default function CockpitDashboard() {
  const [query, setQuery] = useState('');
  const [asOf, setAsOf] = useState('Day4_2026-11-19T10:00:00+05:30');
  const [loading, setLoading] = useState(false);
  const [answer, setAnswer] = useState<AskResponse | null>(null);
  const [risks, setRisks] = useState<RiskItem[]>([]);
  const [agents, setAgents] = useState<AgentSummary[]>([]);
  const [conflicts, setConflicts] = useState<ConflictItem[]>([]);
  const [hrInsights, setHrInsights] = useState<HRInsightsResponse | null>(null);
  const [activeTab, setActiveTab] = useState<'risks' | 'hr' | 'agents' | 'conflicts' | 'transcripts'>('risks');
  const [selectedCitation, setSelectedCitation] = useState<Citation | null>(null);
  const [showAllRisks, setShowAllRisks] = useState(false);
  
  // Agent chat state
  const [selectedAgent, setSelectedAgent] = useState<AgentSummary | null>(null);
  const [agentMessage, setAgentMessage] = useState('');
  const [chatHistory, setChatHistory] = useState<{ sender: 'user' | 'agent'; text: string; citations?: Citation[] }[]>([]);
  const [agentLoading, setAgentLoading] = useState(false);

  useEffect(() => {
    // Initial fetch
    fetchRisks();
    fetchAgents();
    fetchConflicts();
    fetchHRInsights();
  }, [asOf]);

  const fetchRisks = async () => {
    try {
      const res = await fetch(`/api/risks?as_of=${encodeURIComponent(asOf)}`);
      if (res.ok) {
        const data = await res.json();
        setRisks(data.risks || []);
      }
    } catch (e) {
      console.error(e);
    }
  };

  const fetchAgents = async () => {
    try {
      const res = await fetch('/api/agents');
      if (res.ok) {
        const data = await res.json();
        setAgents(data || []);
      }
    } catch (e) {
      console.error(e);
    }
  };

  const fetchConflicts = async () => {
    try {
      const res = await fetch('/api/conflicts');
      if (res.ok) {
        const data = await res.json();
        setConflicts(data || []);
      }
    } catch (e) {
      console.error(e);
    }
  };

  const fetchHRInsights = async () => {
    try {
      const res = await fetch(`/api/hr-insights?as_of=${encodeURIComponent(asOf)}`);
      if (res.ok) {
        const data = await res.json();
        setHrInsights(data);
      }
    } catch (e) {
      console.error(e);
    }
  };

  const handleAsk = async (textToAsk?: string) => {
    const q = textToAsk || query;
    if (!q.trim()) return;
    setLoading(true);
    try {
      const res = await fetch('/api/ask', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: q, as_of: asOf }),
      });
      if (res.ok) {
        const data = await res.json();
        setAnswer(data);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const handleAgentChat = async () => {
    if (!selectedAgent || !agentMessage.trim()) return;
    const msg = agentMessage.trim();
    setChatHistory((prev) => [...prev, { sender: 'user', text: msg }]);
    setAgentMessage('');
    setAgentLoading(true);

    try {
      const res = await fetch(`/api/agents/${selectedAgent.emp_id}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: msg, as_of: asOf }),
      });
      if (res.ok) {
        const data = await res.json();
        setChatHistory((prev) => [
          ...prev,
          { sender: 'agent', text: data.reply, citations: data.citations },
        ]);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setAgentLoading(false);
    }
  };

  const topThreeRisks = risks.slice(0, 3);

  return (
    <div className="min-h-screen bg-[#0B0F17] text-slate-100 flex flex-col">
      {/* Top Header */}
      <header className="border-b border-slate-800 bg-[#0F172A]/80 backdrop-blur sticky top-0 z-30 px-6 py-4 flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 rounded-lg bg-blue-600 flex items-center justify-center font-bold text-xl text-white shadow-lg shadow-blue-500/20">
            VX
          </div>
          <div>
            <h1 className="text-xl font-bold tracking-tight text-white flex items-center gap-2">
              VELOXA CXO COCKPIT
              <span className="text-xs px-2.5 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
                Day 4 Active (19 Nov 2026)
              </span>
            </h1>
            <p className="text-xs text-slate-400">Grounded Multi-Source Executive Intelligence & Governance</p>
          </div>
        </div>

        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2 text-xs bg-slate-800/80 px-3 py-1.5 rounded-md border border-slate-700 text-slate-300">
            <Clock className="w-3.5 h-3.5 text-blue-400" />
            <label htmlFor="as-of-select" className="text-slate-400">As-Of:</label>
            <select
              id="as-of-select"
              value={asOf}
              onChange={(e) => {
                setAsOf(e.target.value);
                setAnswer(null);
              }}
              className="bg-slate-900 text-white font-medium text-xs rounded px-2 py-0.5 border border-slate-600 focus:outline-none focus:ring-1 focus:ring-blue-500 cursor-pointer"
            >
              <option value="Day4_2026-11-19T10:00:00+05:30">Day 4 Active (19 Nov 2026 10:00 IST)</option>
              <option value="2026-11-19T09:59:59+05:30">Pre-Day 4 Cutoff (09:59:59 - Demo Refusal)</option>
              <option value="Day3_2026-11-18T10:00:00+05:30">Day 3 Active (18 Nov 2026 10:00 IST)</option>
              <option value="2026-11-18T09:59:59+05:30">Pre-Day 3 Cutoff (09:59:59 - Demo Refusal)</option>
              <option value="Day2_2026-11-17T10:00:00+05:30">Day 2 Active (17 Nov 2026 10:00 IST)</option>
              <option value="2026-11-17T09:59:59+05:30">Pre-Day 2 Cutoff (09:59:59 - Demo Refusal)</option>
              <option value="Day1_2026-11-16T10:00:00+05:30">Day 1 Cutoff (16 Nov 2026 10:00 IST)</option>
              <option value="2026-08-01">Pre-Q2 Historical (01 Aug 2026)</option>
              <option value="2026-11-20">Future Date (20 Nov 2026 - Demo Refusal)</option>
            </select>
          </div>
          <div className="flex items-center space-x-1.5 text-xs text-amber-400 bg-amber-500/10 border border-amber-500/30 px-3 py-1.5 rounded-md">
            <Shield className="w-3.5 h-3.5" />
            <span>Salary & Survey Privacy Active</span>
          </div>
        </div>
      </header>

      {/* Main Content Layout */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-6 py-8 space-y-8">
        
        {/* T6a EXECUTIVE MORNING BRIEFING: TOP 3 RISKS ("What to worry about") */}
        <section className="bg-slate-900/80 border border-blue-500/40 rounded-xl p-6 shadow-xl backdrop-blur relative overflow-hidden">
          <div className="absolute top-0 right-0 bg-blue-500/10 border-l border-b border-blue-500/30 px-3 py-1 text-[11px] text-blue-300 rounded-bl-lg font-mono">
            T6a View • Decision: APPROVED: ACCEPT WITH SCOPE (Ratified by Candidate)
          </div>
          <div className="flex items-center justify-between mb-4">
            <div>
              <div className="flex items-center gap-2">
                <ShieldAlert className="w-5 h-5 text-red-400" />
                <h2 className="text-base font-bold text-white tracking-tight">
                  CEO Morning Briefing — Top 3 Risks ("What to worry about")
                </h2>
              </div>
              <p className="text-xs text-slate-400 mt-1">
                Default zero-click executive risk assessment answering CEO voice note T6a. Backed strictly by SQLite evidence.
              </p>
            </div>
            <button
              onClick={() => {
                setActiveTab('risks');
                setShowAllRisks(!showAllRisks);
              }}
              className="text-xs bg-slate-800 hover:bg-slate-700 text-blue-300 border border-slate-700 px-3 py-1.5 rounded flex items-center gap-1.5 transition"
            >
              <span>{showAllRisks ? 'Collapse List' : `View All (${risks.length}) Risks`}</span>
              {showAllRisks ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
            </button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {topThreeRisks.map((r) => (
              <div
                key={r.risk_id}
                className="bg-slate-950/70 border border-slate-800 rounded-lg p-4 flex flex-col justify-between hover:border-blue-500/50 transition shadow-md"
              >
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="w-6 h-6 rounded-full bg-blue-600/20 text-blue-400 font-bold text-xs flex items-center justify-center border border-blue-500/30">
                      #{r.rank}
                    </span>
                    <span
                      className={`text-[10px] font-bold px-2 py-0.5 rounded ${
                        r.severity === 'CRITICAL'
                          ? 'bg-red-500/20 text-red-300 border border-red-500/40'
                          : r.severity === 'HIGH'
                          ? 'bg-orange-500/20 text-orange-300 border border-orange-500/40'
                          : 'bg-yellow-500/20 text-yellow-300 border border-yellow-500/40'
                      }`}
                    >
                      {r.severity}
                    </span>
                  </div>

                  <h3 className="text-sm font-semibold text-white leading-snug mb-1">
                    {r.title}
                  </h3>
                  <div className="text-[11px] text-blue-400 mb-2 font-medium">Category: {r.category}</div>

                  <p className="text-xs text-slate-300 leading-relaxed mb-3">
                    {r.summary}
                  </p>
                </div>

                <div className="pt-3 border-t border-slate-800 space-y-2">
                  <div className="text-[11px] text-emerald-300 bg-emerald-950/30 p-2 rounded border border-emerald-500/20">
                    <strong>Recommended Action:</strong> {r.recommended_mitigation}
                  </div>
                  <div className="flex items-center justify-between text-[11px] text-slate-400 pt-1">
                    <span>Evidence ({r.evidence_refs.length}):</span>
                    <div className="flex gap-1">
                      {r.evidence_refs.slice(0, 3).map((ref) => (
                        <span key={ref} className="bg-slate-800 text-blue-300 px-1.5 py-0.5 rounded text-[10px] border border-slate-700">
                          {ref}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* CEO Ask Section */}
        <section className="bg-slate-900/60 border border-slate-800 rounded-xl p-6 shadow-xl backdrop-blur">
          <div className="flex items-center justify-between mb-3">
            <h2 className="text-sm font-semibold tracking-wider uppercase text-blue-400 flex items-center gap-2">
              <Search className="w-4 h-4" /> CEO Decision Query
            </h2>
            <span className="text-xs text-slate-400">Deterministic Evidence Retrieval • Strict Zero-Hallucination</span>
          </div>

          <div className="flex gap-2">
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleAsk()}
              placeholder="Ask any executive question (e.g. 'What is our engineering pulse score?', 'Which requisitions are paused?')"
              className="flex-1 bg-slate-950 border border-slate-700 rounded-lg px-4 py-3 text-sm text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <button
              onClick={() => handleAsk()}
              disabled={loading}
              className="bg-blue-600 hover:bg-blue-500 text-white font-medium px-6 py-3 rounded-lg text-sm transition flex items-center gap-2 shadow-lg shadow-blue-600/30"
            >
              {loading ? 'Evaluating...' : 'Query Cockpit'}
            </button>
          </div>

          {/* Quick Query Pills */}
          <div className="flex flex-wrap gap-2 mt-3 pt-2">
            <span className="text-xs text-slate-400 self-center">Quick queries:</span>
            {[
              'What is our engineering engagement pulse score?',
              'Which requisitions did Meera Iyer pause and has the funding round closed?',
              'Can you show me the qualitative comments from the engineering pulse survey?',
              'What is our company attrition rate based on Deepa\'s call?',
              'Why did Priya Nair take personal leave in September and is she experiencing burnout?',
              'Did Siddharth Mehta resign and has the product launch kit been handed over?',
              'What is our current ARR?',
              'What is our monthly burn rate and runway?',
            ].map((p, i) => (
              <button
                key={i}
                onClick={() => {
                  setQuery(p);
                  handleAsk(p);
                }}
                className="text-xs bg-slate-800/80 hover:bg-slate-700 text-slate-300 hover:text-white px-3 py-1 rounded-full border border-slate-700 transition"
              >
                {p}
              </button>
            ))}
          </div>

          {/* Answer Card */}
          {answer && (
            <div className="mt-6 border border-slate-700/80 bg-slate-950/80 rounded-lg p-5 space-y-4">
              <div className="flex items-center justify-between border-b border-slate-800 pb-3">
                <div className="flex items-center gap-2">
                  <span
                    className={`text-xs font-semibold px-2.5 py-0.5 rounded-full ${
                      answer.status === 'ANSWERED'
                        ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30'
                        : answer.status === 'REFUSAL'
                        ? 'bg-rose-500/10 text-rose-400 border border-rose-500/30'
                        : 'bg-amber-500/10 text-amber-400 border border-amber-500/30'
                    }`}
                  >
                    STATUS: {answer.status}
                  </span>
                  <span className="text-xs text-slate-400">Confidence: <strong className="text-white">{answer.confidence}</strong></span>
                </div>
                {answer.conflict_detected && (
                  <span className="text-xs bg-amber-500/10 text-amber-400 border border-amber-500/30 px-2.5 py-0.5 rounded-full flex items-center gap-1">
                    <AlertTriangle className="w-3 h-3" /> Source Conflict Detected
                  </span>
                )}
              </div>

              <div className="text-sm leading-relaxed text-slate-200">
                {answer.answer}
              </div>

              {answer.conflict_details && (
                <div className="bg-amber-950/30 border border-amber-500/40 rounded p-3 text-xs text-amber-200">
                  <strong>Conflict Note:</strong> {answer.conflict_details}
                </div>
              )}

              {/* Citations list */}
              {answer.citations.length > 0 && (
                <div className="space-y-2 pt-2 border-t border-slate-800/80">
                  <span className="text-xs font-medium text-slate-400 flex items-center gap-1.5">
                    <FileText className="w-3.5 h-3.5 text-blue-400" /> Evidence Citations ({answer.citations.length}):
                  </span>
                  <div className="flex flex-wrap gap-2">
                    {answer.citations.map((c, i) => (
                      <button
                        key={i}
                        onClick={() => setSelectedCitation(c)}
                        className="text-xs bg-slate-800 hover:bg-slate-700 text-blue-300 border border-blue-500/30 px-3 py-1.5 rounded flex items-center gap-1.5 transition"
                      >
                        <span className="font-semibold">{c.ref}</span>
                        <span className="text-slate-400 text-[11px] truncate max-w-xs">{c.source_file}</span>
                      </button>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </section>

        {/* Dashboard Tabs */}
        <section className="space-y-4">
          <div className="flex border-b border-slate-800 space-x-6 text-sm">
            <button
              onClick={() => setActiveTab('risks')}
              className={`pb-3 font-medium flex items-center gap-2 border-b-2 transition ${
                activeTab === 'risks'
                  ? 'border-blue-500 text-blue-400'
                  : 'border-transparent text-slate-400 hover:text-slate-200'
              }`}
            >
              <ShieldAlert className="w-4 h-4" />
              Ranked Enterprise Risks ({risks.length})
            </button>
            <button
              onClick={() => setActiveTab('hr')}
              className={`pb-3 font-medium flex items-center gap-2 border-b-2 transition ${
                activeTab === 'hr'
                  ? 'border-blue-500 text-blue-400'
                  : 'border-transparent text-slate-400 hover:text-slate-200'
              }`}
            >
              <Users className="w-4 h-4" />
              HR & People Insights (Culture Amp & Hiring)
            </button>
            <button
              onClick={() => setActiveTab('agents')}
              className={`pb-3 font-medium flex items-center gap-2 border-b-2 transition ${
                activeTab === 'agents'
                  ? 'border-blue-500 text-blue-400'
                  : 'border-transparent text-slate-400 hover:text-slate-200'
              }`}
            >
              <Building2 className="w-4 h-4" />
              Employee Agents ({agents.length})
            </button>
            <button
              onClick={() => setActiveTab('conflicts')}
              className={`pb-3 font-medium flex items-center gap-2 border-b-2 transition ${
                activeTab === 'conflicts'
                  ? 'border-blue-500 text-blue-400'
                  : 'border-transparent text-slate-400 hover:text-slate-200'
              }`}
            >
              <AlertTriangle className="w-4 h-4" />
              Source Conflicts ({conflicts.length})
            </button>
            <button
              onClick={() => setActiveTab('transcripts')}
              className={`pb-3 font-medium flex items-center gap-2 border-b-2 transition ${
                activeTab === 'transcripts'
                  ? 'border-blue-500 text-blue-400'
                  : 'border-transparent text-slate-400 hover:text-slate-200'
              }`}
            >
              <Layers className="w-4 h-4" />
              Transcription Notes & Audits
            </button>
          </div>

          {/* TAB 1: RANKED RISKS */}
          {activeTab === 'risks' && (
            <div className="grid grid-cols-1 gap-4">
              {risks.map((r) => (
                <div
                  key={r.risk_id}
                  className="bg-slate-900/60 border border-slate-800 rounded-lg p-5 hover:border-slate-700 transition"
                >
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex items-center gap-3">
                      <span className="w-7 h-7 rounded-full bg-slate-800 text-slate-300 font-bold text-xs flex items-center justify-center border border-slate-700">
                        #{r.rank}
                      </span>
                      <div>
                        <h3 className="text-base font-semibold text-white">{r.title}</h3>
                        <div className="flex items-center gap-2 mt-1">
                          <span
                            className={`text-[11px] font-semibold px-2 py-0.5 rounded ${
                              r.severity === 'CRITICAL'
                                ? 'bg-red-500/10 text-red-400 border border-red-500/30'
                                : r.severity === 'HIGH'
                                ? 'bg-orange-500/10 text-orange-400 border border-orange-500/30'
                                : 'bg-yellow-500/10 text-yellow-400 border border-yellow-500/30'
                            }`}
                          >
                            {r.severity}
                          </span>
                          <span className="text-xs text-slate-400">Category: {r.category}</span>
                        </div>
                      </div>
                    </div>

                    <div className="flex gap-1.5">
                      {r.evidence_refs.map((ref) => (
                        <span key={ref} className="text-[11px] bg-slate-800 text-blue-400 px-2 py-1 rounded border border-slate-700">
                          {ref}
                        </span>
                      ))}
                    </div>
                  </div>

                  <p className="mt-3 text-sm text-slate-300 leading-relaxed">{r.summary}</p>
                  
                  <div className="mt-3 pt-3 border-t border-slate-800/80 text-xs text-emerald-400 flex items-start gap-2">
                    <strong className="text-slate-400">Recommended Action:</strong> {r.recommended_mitigation}
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* TAB 2: HR & PEOPLE INSIGHTS */}
          {activeTab === 'hr' && (
            <div className="space-y-6">
              {/* Culture Amp Pulse Survey Section */}
              <div className="bg-slate-900/60 border border-slate-800 rounded-lg p-5 space-y-4">
                <div className="flex items-center justify-between border-b border-slate-800 pb-3">
                  <div>
                    <h3 className="text-base font-semibold text-white flex items-center gap-2">
                      Culture Amp Quarterly Pulse Survey (Jul - Sep 2026)
                    </h3>
                    <p className="text-xs text-slate-400">Quarter-over-quarter engagement trends across departments (Scale 1-5)</p>
                  </div>
                  <span className="text-xs bg-rose-500/10 text-rose-300 border border-rose-500/30 px-3 py-1 rounded-full flex items-center gap-1.5">
                    <Lock className="w-3 h-3" />
                    Qualitative Comments Withheld (&lt; 6 members)
                  </span>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  {hrInsights?.team_engagement.map((t) => (
                    <div
                      key={t.team}
                      className={`p-4 rounded-lg border ${
                        t.change <= -0.5
                          ? 'bg-red-950/20 border-red-500/40'
                          : t.change < 0
                          ? 'bg-amber-950/20 border-amber-500/30'
                          : 'bg-slate-950 border-slate-800'
                      }`}
                    >
                      <div className="flex items-center justify-between">
                        <h4 className="font-semibold text-white text-sm">{t.team}</h4>
                        <span
                          className={`text-xs font-bold px-2 py-0.5 rounded flex items-center gap-1 ${
                            t.change < 0
                              ? 'text-red-400 bg-red-500/10'
                              : t.change > 0
                              ? 'text-emerald-400 bg-emerald-500/10'
                              : 'text-slate-400 bg-slate-800'
                          }`}
                        >
                          {t.change < 0 ? <TrendingDown className="w-3 h-3" /> : <TrendingUp className="w-3 h-3" />}
                          {t.change > 0 ? `+${t.change}` : t.change}
                        </span>
                      </div>

                      <div className="mt-3 flex items-baseline gap-2">
                        <span className="text-2xl font-bold text-white">{t.latest_score.toFixed(1)}</span>
                        <span className="text-xs text-slate-400">from {t.prior_score.toFixed(1)} (Apr-Jun)</span>
                      </div>

                      <div className="mt-2 text-[11px] text-slate-400 flex items-center justify-between">
                        <span>Participation: {t.respondents} / {t.team_size} responded</span>
                        <span className="font-mono text-[10px] text-amber-400">{t.comments_status}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Keka Hire Requisitions Section */}
              <div className="bg-slate-900/60 border border-slate-800 rounded-lg p-5 space-y-4">
                <div className="flex items-center justify-between border-b border-slate-800 pb-3">
                  <div>
                    <h3 className="text-base font-semibold text-white flex items-center gap-2">
                      <Briefcase className="w-4 h-4 text-blue-400" />
                      Keka Hire Requisition Tracker (Export 31-Oct-2026)
                    </h3>
                    <p className="text-xs text-slate-400">Active, on-hold, and filled positions across departments</p>
                  </div>
                  <div className="text-xs text-amber-300 bg-amber-500/10 border border-amber-500/30 px-3 py-1 rounded">
                    <strong>Hiring Pause Directive:</strong> Paused by Meera (06.eml) until round closes
                  </div>
                </div>

                <div className="overflow-x-auto">
                  <table className="w-full text-left text-xs border border-slate-800">
                    <thead className="bg-slate-950 text-slate-400 uppercase tracking-wider">
                      <tr>
                        <th className="p-3 border-b border-slate-800">Req ID</th>
                        <th className="p-3 border-b border-slate-800">Role</th>
                        <th className="p-3 border-b border-slate-800">Team</th>
                        <th className="p-3 border-b border-slate-800">Status</th>
                        <th className="p-3 border-b border-slate-800">Pipeline</th>
                        <th className="p-3 border-b border-slate-800">Status Date</th>
                        <th className="p-3 border-b border-slate-800">Governance Notes</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-800 text-slate-300">
                      {hrInsights?.requisitions.map((req) => (
                        <tr key={req.req_id} className="hover:bg-slate-800/40">
                          <td className="p-3 font-mono text-blue-400 font-bold">{req.req_id}</td>
                          <td className="p-3 font-medium text-white">{req.role}</td>
                          <td className="p-3 text-slate-300">{req.team}</td>
                          <td className="p-3">
                            <span
                              className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                                req.status === 'On hold'
                                  ? 'bg-amber-500/20 text-amber-300 border border-amber-500/40'
                                  : req.status === 'Open'
                                  ? 'bg-blue-500/20 text-blue-300 border border-blue-500/40'
                                  : req.status === 'Filled'
                                  ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/40'
                                  : 'bg-slate-800 text-slate-400'
                              }`}
                            >
                              {req.status}
                            </span>
                          </td>
                          <td className="p-3 font-mono text-white font-bold">{req.pipeline_count}</td>
                          <td className="p-3 text-slate-400">{req.status_date || req.opened_date || '—'}</td>
                          <td className="p-3 text-slate-400 max-w-xs truncate">{req.notes || '—'}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>

              {/* Privacy Safeguards Banner */}
              <div className="bg-slate-950 border border-slate-800 rounded-lg p-4 space-y-2">
                <h4 className="text-xs font-bold text-slate-300 flex items-center gap-1.5 uppercase tracking-wider">
                  <Shield className="w-3.5 h-3.5 text-blue-400" />
                  Service-Layer Privacy & Confidentiality Safeguards Active
                </h4>
                <ul className="text-xs text-slate-400 space-y-1 list-disc list-inside">
                  {hrInsights?.privacy_safeguards.map((s, idx) => (
                    <li key={idx}>{s}</li>
                  ))}
                </ul>
              </div>
            </div>
          )}

          {/* TAB 3: EMPLOYEE AGENTS */}
          {activeTab === 'agents' && (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {agents.map((a) => (
                <div
                  key={a.emp_id}
                  className="bg-slate-900/60 border border-slate-800 rounded-lg p-5 flex flex-col justify-between hover:border-slate-700 transition"
                >
                  <div>
                    <div className="flex items-start justify-between">
                      <div>
                        <h4 className="font-semibold text-white text-base">{a.full_name}</h4>
                        <p className="text-xs text-blue-400 font-medium">{a.title}</p>
                      </div>
                      <span className="text-xs font-mono bg-slate-800 text-slate-300 px-2 py-0.5 rounded border border-slate-700">
                        {a.emp_id}
                      </span>
                    </div>

                    <div className="mt-3 space-y-1 text-xs text-slate-400">
                      <div>Department: <strong className="text-slate-300">{a.department}</strong></div>
                      <div>Location: <span className="text-slate-300">{a.location}</span></div>
                      <div>Status: <span className="text-emerald-400 font-medium">{a.status}</span></div>
                    </div>
                  </div>

                  <button
                    onClick={() => {
                      setSelectedAgent(a);
                      setChatHistory([]);
                    }}
                    className="mt-4 w-full bg-slate-800 hover:bg-slate-700 text-xs font-medium text-white py-2 rounded border border-slate-700 flex items-center justify-center gap-1.5 transition"
                  >
                    <span>Interview Agent</span>
                    <ChevronRight className="w-3.5 h-3.5" />
                  </button>
                </div>
              ))}
            </div>
          )}

          {/* TAB 4: SOURCE CONFLICTS */}
          {activeTab === 'conflicts' && (
            <div className="space-y-4">
              <div className="bg-amber-500/10 border border-amber-500/30 rounded-lg p-4 text-xs text-amber-300">
                <strong>Mandatory Governance Policy:</strong> Per hackathon rules, all factual discrepancies are recorded as proposed interpretations with explicit confidence and reversal conditions. Decisions remain <strong>UNRESOLVED</strong> pending executive human confirmation.
              </div>

              {conflicts.map((c) => (
                <div key={c.conflict_id} className="bg-slate-900/60 border border-slate-800 rounded-lg p-5 space-y-3">
                  <div className="flex items-center justify-between">
                    <h3 className="text-base font-semibold text-white flex items-center gap-2">
                      <span className="font-mono text-xs bg-slate-800 text-blue-400 px-2 py-1 rounded border border-slate-700">
                        {c.conflict_id}
                      </span>
                      {c.topic}
                    </h3>
                    <span className="text-xs font-bold px-2.5 py-0.5 rounded bg-amber-500/20 text-amber-300 border border-amber-500/40">
                      STATUS: {c.human_status}
                    </span>
                  </div>

                  <p className="text-sm text-slate-300">{c.description}</p>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs pt-2">
                    <div className="bg-slate-950 p-3 rounded border border-slate-800">
                      <div className="text-slate-400 font-medium mb-1">Competing Sources:</div>
                      <div className="text-slate-200">{c.competing_sources}</div>
                    </div>
                    <div className="bg-slate-950 p-3 rounded border border-slate-800">
                      <div className="text-blue-400 font-medium mb-1">Proposed Interpretation (Confidence: {c.confidence}):</div>
                      <div className="text-slate-200">{c.proposed_interpretation}</div>
                    </div>
                  </div>

                  <div className="text-xs text-slate-400 pt-1">
                    <strong className="text-slate-300">What would change this conclusion:</strong> {c.what_would_change}
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* TAB 5: TRANSCRIPTION NOTES */}
          {activeTab === 'transcripts' && (
            <div className="bg-slate-900/60 border border-slate-800 rounded-lg p-6 space-y-4">
              <h3 className="text-base font-semibold text-white">MeetNotes AI Audio Transcription Audit (Day 1 & Day 2)</h3>
              <p className="text-xs text-slate-400 leading-relaxed">
                MeetNotes AI auto-summaries exhibit predictable speech-to-text acoustic artifacts and human verbal ambiguities.
                All mishearings are treated as hypotheses backed by cross-system corroboration, preserving unresolved ambiguity:
              </p>

              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs border border-slate-800">
                  <thead className="bg-slate-950 text-slate-400 uppercase tracking-wider">
                    <tr>
                      <th className="p-3 border-b border-slate-800">Transcript Phrase</th>
                      <th className="p-3 border-b border-slate-800">Source Audio Context</th>
                      <th className="p-3 border-b border-slate-800">Hypothesized Entity</th>
                      <th className="p-3 border-b border-slate-800">Grounding Evidence</th>
                      <th className="p-3 border-b border-slate-800">Confidence</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800 text-slate-300">
                    <tr>
                      <td className="p-3 font-mono text-amber-400">"Cult Amp"</td>
                      <td className="p-3">T1 & T3 (Deepa J.)</td>
                      <td className="p-3 font-semibold text-white">Culture Amp</td>
                      <td className="p-3">Pulse_Survey.xlsx export header</td>
                      <td className="p-3 text-emerald-400 font-bold">HIGH</td>
                    </tr>
                    <tr>
                      <td className="p-3 font-mono text-amber-400">"Liver"</td>
                      <td className="p-3">T3 (Rohan B.)</td>
                      <td className="p-3 font-semibold text-white">Keka Hire / Lever</td>
                      <td className="p-3">Hiring_Tracker.xlsx header: "Keka Hire"</td>
                      <td className="p-3 text-emerald-400 font-bold">HIGH</td>
                    </tr>
                    <tr>
                      <td className="p-3 font-mono text-amber-400">"Kekka"</td>
                      <td className="p-3">T3 (Rohan B.)</td>
                      <td className="p-3 font-semibold text-white">Keka HRMS</td>
                      <td className="p-3">HRMS master database</td>
                      <td className="p-3 text-emerald-400 font-bold">HIGH</td>
                    </tr>
                    <tr>
                      <td className="p-3 font-mono text-amber-400">"about twelve"</td>
                      <td className="p-3">T3 (Deepa J.)</td>
                      <td className="p-3 font-semibold text-white">Undefined Metric (12% vs 12 headcount)</td>
                      <td className="p-3">Kept as UNRESOLVED conflict CONF-006</td>
                      <td className="p-3 text-amber-400 font-bold">LOW</td>
                    </tr>
                    <tr>
                      <td className="p-3 font-mono text-amber-400">"twenty-two open roles... lost six"</td>
                      <td className="p-3">T3 (Rohan B.)</td>
                      <td className="p-3 font-semibold text-white">Uncorroborated Hiring Metrics</td>
                      <td className="p-3">Formal Hiring Tracker lists only 6 requisitions</td>
                      <td className="p-3 text-amber-400 font-bold">LOW</td>
                    </tr>
                    <tr>
                      <td className="p-3 font-mono text-amber-400">"Jeera board"</td>
                      <td className="p-3">T1 CEO Kickoff Call</td>
                      <td className="p-3 font-semibold text-white">Jira</td>
                      <td className="p-3">README manifest lists <code>engineering/ Jira (ATLAS)</code></td>
                      <td className="p-3 text-emerald-400 font-bold">HIGH</td>
                    </tr>
                    <tr>
                      <td className="p-3 font-mono text-amber-400">"Joho books"</td>
                      <td className="p-3">T2 CFO Call (Meera)</td>
                      <td className="p-3 font-semibold text-white">Zoho Books</td>
                      <td className="p-3">GL Export header: "General ledger export, Zoho Books"</td>
                      <td className="p-3 text-emerald-400 font-bold">HIGH</td>
                    </tr>
                    <tr>
                      <td className="p-3 font-mono text-amber-400">"Kayka"</td>
                      <td className="p-3">T2 CFO Call (Meera)</td>
                      <td className="p-3 font-semibold text-white">Keka HRMS</td>
                      <td className="p-3">Employee Master header: "Keka HRMS export"</td>
                      <td className="p-3 text-emerald-400 font-bold">HIGH</td>
                    </tr>
                    <tr>
                      <td className="p-3 font-mono text-amber-400">"one-eighty, give or take"</td>
                      <td className="p-3">T1 CEO Kickoff Call</td>
                      <td className="p-3 font-semibold text-white">18 people or Contractor pool</td>
                      <td className="p-3">Employee master lists exactly 19 employees (contractors excluded)</td>
                      <td className="p-3 text-amber-400 font-bold">MEDIUM</td>
                    </tr>
                    <tr>
                      <td className="p-3 font-mono text-amber-400">"two point two lakhs" burn</td>
                      <td className="p-3">T2 CFO Call</td>
                      <td className="p-3 font-semibold text-white">Net Burn or 42.5 L misheard</td>
                      <td className="p-3">GL Payroll is 31.75 L alone; Board reports 44 L gross burn</td>
                      <td className="p-3 text-amber-400 font-bold">MEDIUM</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </section>
      </main>

      {/* Evidence Drawer Modal */}
      {selectedCitation && (
        <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-700 rounded-xl max-w-2xl w-full p-6 space-y-4 shadow-2xl animate-in fade-in zoom-in-95">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <div className="flex items-center gap-2">
                <span className="font-mono text-xs bg-blue-500/20 text-blue-400 px-2.5 py-1 rounded border border-blue-500/40">
                  {selectedCitation.ref}
                </span>
                <h3 className="font-semibold text-white text-sm truncate">{selectedCitation.source_file}</h3>
              </div>
              <button
                onClick={() => setSelectedCitation(null)}
                className="text-slate-400 hover:text-white p-1 rounded hover:bg-slate-800 transition"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="space-y-3 text-sm">
              <div className="grid grid-cols-2 gap-2 text-xs text-slate-400 bg-slate-950 p-3 rounded border border-slate-800">
                <div>Location: <strong className="text-slate-200">{selectedCitation.sheet_or_page || 'N/A'}, {selectedCitation.row_or_line || 'N/A'}</strong></div>
                <div>Confidence: <strong className="text-emerald-400">{selectedCitation.confidence}</strong></div>
              </div>

              <div>
                <span className="text-xs text-slate-400 block mb-1">Grounded Fact Text:</span>
                <div className="bg-slate-950 p-4 rounded border border-slate-800 text-slate-200 leading-relaxed font-mono text-xs">
                  {selectedCitation.fact_text}
                </div>
              </div>
            </div>

            <div className="flex justify-end pt-2">
              <button
                onClick={() => setSelectedCitation(null)}
                className="bg-slate-800 hover:bg-slate-700 text-white text-xs px-4 py-2 rounded transition"
              >
                Close Inspector
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Agent Interview Drawer */}
      {selectedAgent && (
        <div className="fixed inset-y-0 right-0 z-50 w-full max-w-md bg-slate-900 border-l border-slate-800 shadow-2xl flex flex-col animate-in slide-in-from-right">
          <div className="p-4 border-b border-slate-800 flex items-center justify-between bg-slate-950">
            <div>
              <h3 className="font-bold text-white text-base">{selectedAgent.full_name}</h3>
              <p className="text-xs text-blue-400">{selectedAgent.title} • {selectedAgent.department}</p>
            </div>
            <button
              onClick={() => setSelectedAgent(null)}
              className="text-slate-400 hover:text-white p-1 rounded hover:bg-slate-800 transition"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          <div className="flex-1 overflow-y-auto p-4 space-y-3 text-xs">
            <div className="bg-blue-500/10 border border-blue-500/20 rounded p-3 text-blue-300">
              Agent initialized with role-grounded facts from Keka HRMS and Day 1 & Day 2 data. Boundary policies apply: salary figures and unapproved comments are strictly redacted.
            </div>

            {chatHistory.length === 0 && (
              <div className="text-center text-slate-500 py-8">
                Ask {selectedAgent.full_name} about their role, projects, or team operations.
              </div>
            )}

            {chatHistory.map((item, idx) => (
              <div
                key={idx}
                className={`p-3 rounded-lg max-w-[85%] ${
                  item.sender === 'user'
                    ? 'ml-auto bg-blue-600 text-white'
                    : 'mr-auto bg-slate-950 text-slate-200 border border-slate-800'
                }`}
              >
                <div className="leading-relaxed">{item.text}</div>
                {item.citations && item.citations.length > 0 && (
                  <div className="mt-2 pt-2 border-t border-slate-800 flex flex-wrap gap-1">
                    {item.citations.map((c, ci) => (
                      <span key={ci} className="text-[10px] bg-slate-800 text-blue-300 px-1.5 py-0.5 rounded">
                        {c.ref}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            ))}
            {agentLoading && (
              <div className="text-slate-400 text-xs italic">Thinking...</div>
            )}
          </div>

          <div className="p-4 border-t border-slate-800 bg-slate-950 flex gap-2">
            <input
              type="text"
              value={agentMessage}
              onChange={(e) => setAgentMessage(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleAgentChat()}
              placeholder={`Message ${selectedAgent.full_name}...`}
              className="flex-1 bg-slate-900 border border-slate-700 rounded px-3 py-2 text-xs text-white placeholder-slate-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
            />
            <button
              onClick={handleAgentChat}
              disabled={agentLoading}
              className="bg-blue-600 hover:bg-blue-500 text-white p-2 rounded transition"
            >
              <Send className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
