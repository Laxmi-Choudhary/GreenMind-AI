import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import { useAuth } from '../context/AuthContext';
import {
  FileText,
  Download,
  RefreshCw,
  Loader2,
  TrendingUp,
  CalendarCheck,
  Sparkles,
  ChevronDown,
  ChevronUp,
  Award,
  AlertCircle
} from 'lucide-react';

export const Reports = () => {
  const { user, refreshUser } = useAuth();
  const [reports, setReports] = useState([]);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [expandedId, setExpandedId] = useState(null);

  useEffect(() => {
    fetchReports();
  }, []);

  const fetchReports = async () => {
    try {
      const data = await api.get('/api/reports');
      setReports(data);
    } catch (err) {
      console.error('Failed to load reports:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleGenerate = async () => {
    setGenerating(true);
    try {
      const newReport = await api.post('/api/reports/generate', {});
      setReports(prev => [newReport, ...prev]);
      setExpandedId(newReport.id);
      await refreshUser();
    } catch (err) {
      console.error('Failed to generate report:', err);
    } finally {
      setGenerating(false);
    }
  };

  const handleDownload = async (reportId) => {
    try {
      const token = localStorage.getItem('greenmind_token');
      const res = await fetch(`http://localhost:8000/api/reports/${reportId}/download`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      const text = await res.text();
      const blob = new Blob([text], { type: 'text/plain' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `greenmind_report_${reportId.slice(0, 8)}.txt`;
      a.click();
      URL.revokeObjectURL(url);
    } catch (err) {
      console.error('Failed to download report:', err);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-brand-500"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6 animate-slide-up max-w-4xl mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold text-slate-900 dark:text-white">Weekly AI Reports</h1>
          <p className="text-slate-500 dark:text-slate-400 mt-1">
            AI-generated sustainability reports based on your logged footprint data.
          </p>
        </div>
        <button
          onClick={handleGenerate}
          disabled={generating}
          className="flex items-center gap-2 px-5 py-3 rounded-2xl bg-brand-600 hover:bg-brand-500 text-white font-semibold shadow-md shadow-brand-500/10 hover:shadow-lg transition-all disabled:opacity-50 cursor-pointer"
        >
          {generating ? (
            <Loader2 className="w-5 h-5 animate-spin" />
          ) : (
            <RefreshCw className="w-5 h-5" />
          )}
          <span>{generating ? 'Generating...' : 'Generate New Report'}</span>
        </button>
      </div>

      {/* Info callout */}
      <div className="p-5 rounded-3xl bg-brand-500/5 border border-brand-500/15 text-brand-800 dark:text-brand-300 flex items-start gap-4">
        <Sparkles className="w-6 h-6 flex-shrink-0 mt-0.5 text-brand-500" />
        <div>
          <h4 className="font-bold text-sm">How Reports Work</h4>
          <p className="text-xs mt-1 text-brand-700 dark:text-brand-400">
            Each report analyzes your recent footprint logs and provides AI-driven summaries, trend analysis,
            carbon savings estimates, and personalized recommendations. Generating a report earns you <strong>+15 Points</strong>.
          </p>
        </div>
      </div>

      {/* Reports list */}
      {reports.length === 0 ? (
        <div className="glass-panel p-12 rounded-3xl border border-slate-200/50 dark:border-slate-800/40 text-center">
          <AlertCircle className="w-12 h-12 text-slate-300 dark:text-slate-600 mx-auto mb-4" />
          <h3 className="text-lg font-bold text-slate-700 dark:text-slate-300">No Reports Yet</h3>
          <p className="text-sm text-slate-500 dark:text-slate-400 mt-2 max-w-md mx-auto">
            Click "Generate New Report" above to create your first AI sustainability report.
            Make sure to log a few footprint entries first for the best insights!
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          {reports.map((report, idx) => {
            const isExpanded = expandedId === report.id;
            const dateStr = report.created_at
              ? new Date(report.created_at).toLocaleDateString('en-US', {
                  weekday: 'short',
                  year: 'numeric',
                  month: 'short',
                  day: 'numeric',
                })
              : 'Unknown date';

            return (
              <div
                key={report.id || idx}
                className="glass-panel rounded-3xl border border-slate-200/50 dark:border-slate-800/40 overflow-hidden transition-all"
              >
                {/* Report Header (Collapsible) */}
                <button
                  onClick={() => setExpandedId(isExpanded ? null : report.id)}
                  className="w-full flex items-center justify-between p-5 text-left hover:bg-slate-50/50 dark:hover:bg-slate-900/20 transition-colors cursor-pointer"
                >
                  <div className="flex items-center gap-4">
                    <div className="p-2.5 rounded-xl bg-brand-500/10 text-brand-600 dark:text-brand-400">
                      <FileText className="w-5 h-5" />
                    </div>
                    <div>
                      <h3 className="font-bold text-slate-800 dark:text-white text-sm">
                        Sustainability Report
                      </h3>
                      <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5 flex items-center gap-2">
                        <CalendarCheck className="w-3.5 h-3.5" />
                        {dateStr}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    {report.score_change !== undefined && (
                      <span
                        className={`text-xs font-bold px-2 py-1 rounded-lg ${
                          report.score_change >= 0
                            ? 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-400'
                            : 'bg-rose-500/10 text-rose-600 dark:text-rose-400'
                        }`}
                      >
                        {report.score_change >= 0 ? '+' : ''}
                        {report.score_change} pts
                      </span>
                    )}
                    {isExpanded ? (
                      <ChevronUp className="w-5 h-5 text-slate-400" />
                    ) : (
                      <ChevronDown className="w-5 h-5 text-slate-400" />
                    )}
                  </div>
                </button>

                {/* Expanded Content */}
                {isExpanded && (
                  <div className="px-5 pb-5 border-t border-slate-200/50 dark:border-slate-800/40 space-y-5 pt-5 animate-slide-up">
                    {/* Summary */}
                    <div className="p-4 rounded-2xl bg-white/40 dark:bg-slate-950/20 border border-slate-200/50 dark:border-slate-800/30">
                      <h4 className="text-xs font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider mb-2">
                        Summary
                      </h4>
                      <p className="text-sm text-slate-700 dark:text-slate-300 leading-relaxed">
                        {report.summary}
                      </p>
                    </div>

                    {/* Trends & Savings */}
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                      <div className="p-4 rounded-2xl bg-white/40 dark:bg-slate-950/20 border border-slate-200/50 dark:border-slate-800/30">
                        <div className="flex items-center gap-2 mb-2">
                          <TrendingUp className="w-4 h-4 text-blue-500" />
                          <h4 className="text-xs font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider">
                            Trends
                          </h4>
                        </div>
                        <p className="text-sm text-slate-700 dark:text-slate-300">{report.trends}</p>
                      </div>
                      <div className="p-4 rounded-2xl bg-white/40 dark:bg-slate-950/20 border border-slate-200/50 dark:border-slate-800/30">
                        <div className="flex items-center gap-2 mb-2">
                          <Award className="w-4 h-4 text-amber-500" />
                          <h4 className="text-xs font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider">
                            Carbon Savings
                          </h4>
                        </div>
                        <p className="text-lg font-bold text-brand-600 dark:text-brand-400">
                          {report.savings}
                        </p>
                      </div>
                    </div>

                    {/* Recommendations */}
                    <div>
                      <h4 className="text-xs font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider mb-3">
                        AI Recommendations
                      </h4>
                      <div className="space-y-2">
                        {report.recommendations?.map((rec, rIdx) => (
                          <div
                            key={rIdx}
                            className="flex gap-3 p-3 rounded-xl bg-white/40 dark:bg-slate-950/20 border border-slate-200/50 dark:border-slate-800/30"
                          >
                            <div className="w-6 h-6 rounded-lg bg-brand-500/10 text-brand-600 dark:text-brand-400 flex items-center justify-center flex-shrink-0 text-xs font-bold">
                              {rIdx + 1}
                            </div>
                            <p className="text-sm text-slate-700 dark:text-slate-300">{rec}</p>
                          </div>
                        ))}
                      </div>
                    </div>

                    {/* Download button */}
                    <div className="flex justify-end pt-2">
                      <button
                        onClick={() => handleDownload(report.id)}
                        className="flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-semibold text-brand-600 dark:text-brand-400 border border-brand-500/20 hover:bg-brand-500/5 transition-colors cursor-pointer"
                      >
                        <Download className="w-4 h-4" />
                        Download Report
                      </button>
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};

export default Reports;
