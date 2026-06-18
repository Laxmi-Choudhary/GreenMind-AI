import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { api } from '../services/api';
import { useAuth } from '../context/AuthContext';
import { 
  TrendingDown, 
  Leaf, 
  Zap, 
  Calendar, 
  Scale, 
  AlertCircle,
  Plus,
  Trophy,
  ChevronRight
} from 'lucide-react';
import { 
  ResponsiveContainer, 
  PieChart, 
  Pie, 
  Cell, 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  Tooltip, 
  Legend, 
  LineChart, 
  Line 
} from 'recharts';

export const Dashboard = () => {
  const { user } = useAuth();
  const [history, setHistory] = useState([]);
  const [scoreData, setScoreData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const hist = await api.get('/api/calculator/history');
        const score = await api.get('/api/score');
        setHistory(hist);
        setScoreData(score);
      } catch (err) {
        console.error("Error loading dashboard data:", err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-brand-500"></div>
      </div>
    );
  }

  // Fallback default state if no history exists
  const hasHistory = history.length > 0;
  const latestLog = hasHistory ? history[0] : null;

  // 1. Pie Chart data (Category Distribution)
  const COLORS = ['#22c55e', '#3b82f6', '#f59e0b', '#ec4899', '#8b5cf6'];
  const pieData = latestLog 
    ? [
        { name: 'Travel', value: latestLog.breakdown.travel },
        { name: 'Energy', value: latestLog.breakdown.energy },
        { name: 'Food', value: latestLog.breakdown.food },
        { name: 'Shopping', value: latestLog.breakdown.shopping },
        { name: 'Waste', value: latestLog.breakdown.waste }
      ].filter(item => item.value > 0)
    : [
        { name: 'Travel', value: 20.0 },
        { name: 'Energy', value: 15.0 },
        { name: 'Food', value: 3.8 },
        { name: 'Shopping', value: 5.0 },
        { name: 'Waste', value: 2.5 }
      ];

  // 2. Line Chart data (Weekly trends - last 7 entries)
  const lineData = hasHistory 
    ? [...history].reverse().slice(-7).map(log => ({
        date: log.date.slice(5), // MM-DD
        emissions: log.daily_emissions
      }))
    : [
        { date: '06-12', emissions: 45.3 },
        { date: '06-13', emissions: 42.1 },
        { date: '06-14', emissions: 39.8 },
        { date: '06-15', emissions: 48.0 },
        { date: '06-16', emissions: 44.5 },
        { date: '06-17', emissions: 35.2 },
        { date: '06-18', emissions: latestLog ? latestLog.daily_emissions : 46.3 }
      ];

  // 3. Bar Chart data (Comparison)
  const barData = latestLog
    ? [
        { name: 'Your Footprint', value: latestLog.daily_emissions },
        { name: 'Global Average', value: 16.0 },
        { name: 'Eco Target', value: 8.0 }
      ]
    : [
        { name: 'Estimate', value: 46.3 },
        { name: 'Global Average', value: 16.0 },
        { name: 'Eco Target', value: 8.0 }
      ];

  return (
    <div className="space-y-6 animate-slide-up">
      {/* Welcome & Action Header */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold text-slate-900 dark:text-white">Hello, {user?.username}</h1>
          <p className="text-slate-500 dark:text-slate-400">Here's your environmental footprint and impact analysis today.</p>
        </div>
        <Link 
          to="/calculator" 
          className="flex items-center gap-2 px-5 py-3 rounded-2xl bg-brand-600 hover:bg-brand-500 text-white font-semibold shadow-md shadow-brand-500/10 hover:shadow-lg transition-all cursor-pointer"
        >
          <Plus className="w-5 h-5" />
          <span>Log Daily Footprint</span>
        </Link>
      </div>

      {!hasHistory && (
        <div className="p-6 rounded-3xl bg-amber-500/10 border border-amber-500/20 text-amber-800 dark:text-amber-300 flex items-start gap-4 shadow-sm">
          <AlertCircle className="w-6 h-6 flex-shrink-0 mt-0.5 text-amber-500" />
          <div>
            <h4 className="font-bold text-base">Get Started by Logging Your Footprint</h4>
            <p className="text-sm mt-1">We are showing estimated dashboard statistics. Log your transit, meals, and utilities to unlock tailored insights and personalized goals.</p>
          </div>
        </div>
      )}

      {/* Main Metrics Row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        <div className="glass-card p-5 rounded-3xl">
          <div className="flex justify-between items-start">
            <span className="text-slate-500 dark:text-slate-400 text-sm font-medium">Daily Carbon Footprint</span>
            <div className="p-2 rounded-xl bg-brand-500/10 text-brand-600 dark:text-brand-400">
              <Leaf className="w-5 h-5" />
            </div>
          </div>
          <div className="mt-3">
            <span className="text-3xl font-bold text-slate-900 dark:text-white">
              {latestLog ? latestLog.daily_emissions : '46.3'}
            </span>
            <span className="text-slate-500 text-sm font-medium ml-1">kg CO₂</span>
          </div>
          <div className="mt-2 text-xs font-semibold text-brand-600 dark:text-brand-400 flex items-center gap-1">
            <TrendingDown className="w-3.5 h-3.5" />
            <span>Target: 8.0 kg CO₂</span>
          </div>
        </div>

        <div className="glass-card p-5 rounded-3xl">
          <div className="flex justify-between items-start">
            <span className="text-slate-500 dark:text-slate-400 text-sm font-medium">Monthly Projection</span>
            <div className="p-2 rounded-xl bg-blue-500/10 text-blue-600 dark:text-blue-400">
              <Calendar className="w-5 h-5" />
            </div>
          </div>
          <div className="mt-3">
            <span className="text-3xl font-bold text-slate-900 dark:text-white">
              {latestLog ? latestLog.monthly_emissions : '1,389.0'}
            </span>
            <span className="text-slate-500 text-sm font-medium ml-1">kg CO₂</span>
          </div>
          <div className="mt-2 text-xs text-slate-500 dark:text-slate-400">
            Based on your latest daily entries
          </div>
        </div>

        <div className="glass-card p-5 rounded-3xl">
          <div className="flex justify-between items-start">
            <span className="text-slate-500 dark:text-slate-400 text-sm font-medium">Annualized Footprint</span>
            <div className="p-2 rounded-xl bg-pink-500/10 text-pink-600 dark:text-pink-400">
              <Scale className="w-5 h-5" />
            </div>
          </div>
          <div className="mt-3">
            <span className="text-3xl font-bold text-slate-900 dark:text-white">
              {latestLog ? latestLog.annual_emissions.toLocaleString() : '16,899.5'}
            </span>
            <span className="text-slate-500 text-sm font-medium ml-1">kg CO₂</span>
          </div>
          <div className="mt-2 text-xs text-slate-500 dark:text-slate-400">
            Equivalent to ~{latestLog ? Math.round(latestLog.annual_emissions / 1000) : '17'} metric tons
          </div>
        </div>

        <div className="glass-card p-5 rounded-3xl">
          <div className="flex justify-between items-start">
            <span className="text-slate-500 dark:text-slate-400 text-sm font-medium">Sustainability Score</span>
            <div className="p-2 rounded-xl bg-amber-500/10 text-amber-600 dark:text-amber-400">
              <Trophy className="w-5 h-5" />
            </div>
          </div>
          <div className="mt-3">
            <span className="text-3xl font-bold text-slate-900 dark:text-white">
              {scoreData ? scoreData.overall : '56'}
            </span>
            <span className="text-slate-500 text-sm font-medium ml-1">/ 100</span>
          </div>
          <div className="mt-2 text-xs font-semibold text-amber-600 dark:text-amber-400 flex items-center gap-1">
            <span>Grade: {scoreData?.overall >= 80 ? 'Excellent' : (scoreData?.overall >= 60 ? 'Average' : 'Needs Optimization')}</span>
          </div>
        </div>
      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Category Breakdown Pie Chart */}
        <div className="glass-panel p-5 rounded-3xl lg:col-span-1 border border-slate-200/50 dark:border-slate-800/40">
          <h3 className="text-lg font-bold text-slate-800 dark:text-white mb-4">Emissions Share</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={pieData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={80}
                  paddingAngle={5}
                  dataKey="value"
                >
                  {pieData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip 
                  formatter={(value) => [`${value} kg CO₂`, 'Emissions']}
                  contentStyle={{ borderRadius: '12px', border: 'none', background: 'rgba(15,23,42,0.85)', color: 'white' }}
                />
                <Legend layout="horizontal" verticalAlign="bottom" align="center" iconType="circle" />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Weekly Trend Line Chart */}
        <div className="glass-panel p-5 rounded-3xl lg:col-span-2 border border-slate-200/50 dark:border-slate-800/40">
          <h3 className="text-lg font-bold text-slate-800 dark:text-white mb-4">Carbon Footprint Trend</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={lineData}>
                <XAxis dataKey="date" stroke="#94a3b8" fontSize={11} tickLine={false} />
                <YAxis stroke="#94a3b8" fontSize={11} tickLine={false} />
                <Tooltip contentStyle={{ borderRadius: '12px', border: 'none', background: 'rgba(15,23,42,0.85)', color: 'white' }} />
                <Line 
                  type="monotone" 
                  dataKey="emissions" 
                  stroke="#22c55e" 
                  strokeWidth={3} 
                  activeDot={{ r: 8 }} 
                  dot={{ stroke: '#22c55e', strokeWidth: 2, r: 4 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Comparisons and Suggestions */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Score Breakdown Bars */}
        <div className="glass-panel p-5 rounded-3xl lg:col-span-1 border border-slate-200/50 dark:border-slate-800/40">
          <h3 className="text-lg font-bold text-slate-800 dark:text-white mb-4">Emissions Comparison</h3>
          <div className="h-56">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={barData}>
                <XAxis dataKey="name" stroke="#94a3b8" fontSize={11} tickLine={false} />
                <YAxis stroke="#94a3b8" fontSize={11} tickLine={false} />
                <Tooltip contentStyle={{ borderRadius: '12px', border: 'none', background: 'rgba(15,23,42,0.85)', color: 'white' }} />
                <Bar dataKey="value" radius={[10, 10, 0, 0]}>
                  {barData.map((entry, index) => (
                    <Cell 
                      key={`cell-${index}`} 
                      fill={index === 0 ? '#ef4444' : (index === 1 ? '#94a3b8' : '#22c55e')} 
                    />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* AI Action Suggestions */}
        <div className="glass-panel p-5 rounded-3xl lg:col-span-2 border border-slate-200/50 dark:border-slate-800/40 flex flex-col justify-between">
          <div>
            <h3 className="text-lg font-bold text-slate-800 dark:text-white mb-3">Improvement Suggestions</h3>
            <div className="space-y-3">
              {scoreData?.suggestions.slice(0, 3).map((sug, idx) => (
                <div key={idx} className="flex gap-3 p-3.5 rounded-2xl bg-white/40 dark:bg-slate-950/20 border border-slate-200/50 dark:border-slate-800/30">
                  <div className="w-8 h-8 rounded-xl bg-brand-500/10 text-brand-600 dark:text-brand-400 flex items-center justify-center flex-shrink-0 font-bold text-sm">
                    {idx + 1}
                  </div>
                  <div>
                    <h5 className="font-semibold text-sm text-slate-800 dark:text-white">{sug.category} Suggestion</h5>
                    <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">{sug.text}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
          <div className="mt-4 pt-3 border-t border-slate-200/50 dark:border-slate-800/40 flex justify-end">
            <Link 
              to="/coach" 
              className="flex items-center gap-1.5 text-sm font-semibold text-brand-600 hover:text-brand-500 dark:text-brand-400 hover:gap-2 transition-all"
            >
              <span>View Full AI Coaching Report</span>
              <ChevronRight className="w-4 h-4" />
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
};
export default Dashboard;
