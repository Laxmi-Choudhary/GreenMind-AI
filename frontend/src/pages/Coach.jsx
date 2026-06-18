import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import { Sparkles, CheckSquare, Lightbulb, Compass, Award } from 'lucide-react';

export const Coach = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchInsights = async () => {
      try {
        const insights = await api.get('/api/coach/insights');
        setData(insights);
      } catch (err) {
        console.error("Failed to load coach insights", err);
      } finally {
        setLoading(false);
      }
    };
    fetchInsights();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-brand-500"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6 max-w-4xl mx-auto animate-slide-up">
      <div className="flex items-center gap-3">
        <div className="p-3 rounded-2xl bg-brand-500/10 text-brand-600 dark:text-brand-400">
          <Sparkles className="w-8 h-8" />
        </div>
        <div>
          <h1 className="text-3xl font-bold text-slate-900 dark:text-white">AI Sustainability Coach</h1>
          <p className="text-slate-500 dark:text-slate-400">Receive custom recommendations, facts, and footprint reduction tips.</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Core Insights */}
        <div className="glass-panel p-6 rounded-3xl md:col-span-2 border border-slate-200/50 dark:border-slate-800/40 space-y-4">
          <div className="flex items-center gap-2 border-b border-slate-200/50 dark:border-slate-800/40 pb-3">
            <Compass className="w-5 h-5 text-brand-600" />
            <h3 className="font-bold text-lg text-slate-800 dark:text-white">Your Carbon Profile Insights</h3>
          </div>

          <div className="space-y-3">
            {data?.insights.map((ins, index) => (
              <div key={index} className="flex items-start gap-3 p-4 bg-white/40 dark:bg-slate-900/20 border border-slate-200/50 dark:border-slate-800/30 rounded-2xl">
                <span className="w-2.5 h-2.5 bg-brand-500 rounded-full flex-shrink-0 mt-1.5" />
                <p className="text-slate-700 dark:text-slate-300 text-sm leading-relaxed">{ins}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Facts & Trivia Sideboard */}
        <div className="glass-panel p-6 rounded-3xl md:col-span-1 border border-slate-200/50 dark:border-slate-800/40 space-y-4">
          <div className="flex items-center gap-2 border-b border-slate-200/50 dark:border-slate-800/40 pb-3">
            <Lightbulb className="w-5 h-5 text-amber-500" />
            <h3 className="font-bold text-lg text-slate-800 dark:text-white">Eco Facts</h3>
          </div>

          <div className="space-y-4">
            {data?.tips.map((tip, index) => (
              <div key={index} className="space-y-1">
                <span className="text-xs font-bold uppercase tracking-wider text-brand-600 dark:text-brand-400">Did you know?</span>
                <p className="text-slate-600 dark:text-slate-400 text-xs leading-relaxed">{tip}</p>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Actionable Reduction Strategies */}
      <div className="glass-panel p-6 rounded-3xl border border-slate-200/50 dark:border-slate-800/40 space-y-4">
        <div className="flex items-center gap-2 border-b border-slate-200/50 dark:border-slate-800/40 pb-3">
          <CheckSquare className="w-5 h-5 text-emerald-500" />
          <h3 className="font-bold text-lg text-slate-800 dark:text-white">Tailored Reduction Strategies</h3>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          {data?.strategies.map((strat, index) => (
            <div key={index} className="p-4 rounded-2xl bg-emerald-500/5 border border-emerald-500/10 text-emerald-900 dark:text-emerald-300 flex items-start gap-3">
              <div className="p-1 rounded-lg bg-emerald-500/10 text-emerald-600 flex-shrink-0 mt-0.5">
                <Award className="w-4 h-4" />
              </div>
              <p className="text-sm font-medium leading-relaxed">{strat}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
export default Coach;
