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

export default function CockpitDashboard() {
  const [query, setQuery] = useState('');
  const [asOf, setAsOf] = useState('Day1_2026-11-16T10:00:00+05:30');
  const [loading, setLoading] = useState(false);
  const [answer, setAnswer] = useState<AskResponse | null>(null);
  const [risks, setRisks] = useState<RiskItem[]>([]);
  const [agents, setAgents] = useState<AgentSummary[]>([]);
  const [conflicts, setConflicts] = useState<ConflictItem[]>([]);
  const [activeTab, setActiveTab] = useState<'risks' | 'agents' | 'conflicts' | 'transcripts'>('risks');
  const [selectedCitation, setSelectedCitation] = useState<Citation | null>(null);
  
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
  }, []);

  const fetchRisks = async () => {
    try {
      const res = await fetch('/api/risks');
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
              <span className="text-xs px-2.5 py-0.5 rounded-full bg-blue-500/10 text-blue-400 border border-blue-500/30">
                Day 1 Active
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
              <option value="Day1_2026-11-16T10:00:00+05:30">Day 1 Cutoff (16 Nov 2026 10:00 IST)</option>
              <option value="2026-08-01">Pre-Q2 Historical (01 Aug 2026)</option>
              <option value="2026-04-15">Q1 Historical (15 Apr 2026)</option>
              <option value="2026-11-20">Future Date (20 Nov 2026 - Demo Refusal)</option>
            </select>
          </div>
          <div className="flex items-center space-x-1.5 text-xs text-amber-400 bg-amber-500/10 border border-amber-500/30 px-3 py-1.5 rounded-md">
            <Shield className="w-3.5 h-3.5" />
            <span>Salary Privacy Active</span>
          </div>
        </div>
      </header>

      {/* Main Content Layout */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-6 py-8 space-y-8">
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
              placeholder="Ask any executive question (e.g. 'What is our ARR?', 'What is our monthly burn?', 'Is Atlas v3 on track?')"
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
              'What is our current ARR?',
              'What is our monthly burn rate and runway?',
              'How many employees work at Veloxa?',
              'Is Atlas version 3 on track?',
              'What happened with the Logistics Summit?',
              'What is Vikram Menon\'s salary?',
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
              Ranked Risks ({risks.length})
            </button>
            <button
              onClick={() => setActiveTab('agents')}
              className={`pb-3 font-medium flex items-center gap-2 border-b-2 transition ${
                activeTab === 'agents'
                  ? 'border-blue-500 text-blue-400'
                  : 'border-transparent text-slate-400 hover:text-slate-200'
              }`}
            >
              <Users className="w-4 h-4" />
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

          {/* TAB 2: EMPLOYEE AGENTS */}
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

          {/* TAB 3: SOURCE CONFLICTS */}
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

          {/* TAB 4: TRANSCRIPTION NOTES */}
          {activeTab === 'transcripts' && (
            <div className="bg-slate-900/60 border border-slate-800 rounded-lg p-6 space-y-4">
              <h3 className="text-base font-semibold text-white">MeetNotes AI Audio Transcription Audit (Day 1)</h3>
              <p className="text-xs text-slate-400 leading-relaxed">
                MeetNotes AI auto-summaries exhibit predictable speech-to-text acoustic artifacts.
                All mishearings are treated as hypotheses backed by cross-system corroboration:
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
                      <td className="p-3 font-mono text-amber-400">"Cult Amp"</td>
                      <td className="p-3">T1 CEO Kickoff Call</td>
                      <td className="p-3 font-semibold text-white">Culture Amp</td>
                      <td className="p-3">README manifest lists <code>hr/ Culture Amp pulse</code></td>
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
              Agent initialized with role-grounded facts from Keka HRMS and Day 1 data. Boundary policies apply: salary figures are strictly redacted.
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
