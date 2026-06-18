import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import { 
  GitBranch, 
  TrendingDown, 
  DollarSign, 
  TreePine, 
  HelpCircle,
  Zap,
  Car,
  Utensils,
  ShoppingBag
} from 'lucide-react';
import { 
  ResponsiveContainer, 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  Tooltip, 
  Cell 
} from 'recharts';

export const Simulators = () => {
  // Simulator View tabs: 'twin' or 'whatif'
  const [tab, setTab] = useState('twin');

  // Twin Simulator state
  const [twinData, setTwinData] = useState(null);
  
  // What-If Simulator state (Sliders)
  const [transitShift, setTransitShift] = useState(0);
  const [acReduction, setAcReduction] = useState(0);
  const [meatlessDays, setMeatlessDays] = useState(0);
  const [shoppingReduction, setShoppingReduction] = useState(0);
  const [whatIfData, setWhatIfData] = useState(null);

  const [loading, setLoading] = useState(true);

  // Load Carbon Twin on mount
  useEffect(() => {
    const fetchTwin = async () => {
      try {
        const data = await api.post('/api/simulator/twin', {});
        setTwinData(data);
      } catch (err) {
        console.error("Error loading Carbon Twin", err);
      } finally {
        setLoading(false);
      }
    };
    fetchTwin();
  }, []);

  // Update What-If Scenario when sliders modify
  useEffect(() => {
    const fetchWhatIf = async () => {
      const payload = {
        transit_shift_pct: Number(transitShift),
        ac_reduction_hours: Number(acReduction),
        meatless_days_per_week: Number(meatlessDays),
        shopping_reduction_pct: Number(shoppingReduction)
      };
      try {
        const data = await api.post('/api/simulator/what-if', payload);
        setWhatIfData(data);
      } catch (err) {
        console.error("Error loading What-If outcome", err);
      }
    };

    // debounce or run instantly for snappy calculations
    fetchWhatIf();
  }, [transitShift, acReduction, meatlessDays, shoppingReduction]);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-brand-500"></div>
      </div>
    );
  }

  // Format Recharts data for Carbon Twin
  const twinChartData = twinData 
    ? [
        { name: 'Current', emissions: twinData.current.annual_emissions },
        { name: 'Optimized Eco', emissions: twinData.eco.annual_emissions }
      ]
    : [];

  return (
    <div className="space-y-6 max-w-5xl mx-auto animate-slide-up">
      <div className="flex items-center gap-3">
        <div className="p-3 rounded-2xl bg-brand-500/10 text-brand-600 dark:text-brand-400">
          <GitBranch className="w-8 h-8" />
        </div>
        <div>
          <h1 className="text-3xl font-bold text-slate-900 dark:text-white">Lifestyle Simulators</h1>
          <p className="text-slate-500 dark:text-slate-400">Project carbon optimizations, cost savings, and test hypothetical scenarios.</p>
        </div>
      </div>

      {/* Simulator Switch Toggles */}
      <div className="flex bg-slate-200/50 dark:bg-slate-900/60 p-1.5 rounded-2xl w-full sm:w-fit border border-slate-200/50 dark:border-slate-800/40">
        <button
          onClick={() => setTab('twin')}
          className={`flex-1 sm:flex-initial px-6 py-2.5 rounded-xl text-sm font-semibold transition-all cursor-pointer ${
            tab === 'twin'
              ? 'bg-white dark:bg-slate-800 text-brand-700 dark:text-brand-400 shadow-sm border border-slate-200/20'
              : 'text-slate-500 hover:text-slate-900 dark:hover:text-slate-100'
          }`}
        >
          Carbon Twin Simulator
        </button>
        <button
          onClick={() => setTab('whatif')}
          className={`flex-1 sm:flex-initial px-6 py-2.5 rounded-xl text-sm font-semibold transition-all cursor-pointer ${
            tab === 'whatif'
              ? 'bg-white dark:bg-slate-800 text-brand-700 dark:text-brand-400 shadow-sm border border-slate-200/20'
              : 'text-slate-500 hover:text-slate-900 dark:hover:text-slate-100'
          }`}
        >
          What-If Scenario Console
        </button>
      </div>

      {/* TAB 1: Carbon Twin Simulator */}
      {tab === 'twin' && twinData && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Detailed metrics comparison */}
          <div className="lg:col-span-2 space-y-6">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
              {/* Current Card */}
              <div className="glass-panel p-6 rounded-3xl border border-red-500/10">
                <span className="text-slate-400 text-xs font-bold uppercase tracking-wider block">Current Lifestyle</span>
                <span className="text-3xl font-extrabold text-slate-850 dark:text-white mt-1 block">
                  {twinData.current.annual_emissions.toLocaleString()} kg
                </span>
                <span className="text-xs text-slate-500 mt-1 block">Annual CO₂ output</span>
                
                <div className="mt-4 pt-3 border-t border-slate-200/50 dark:border-slate-800/40 space-y-2 text-xs">
                  <div className="flex justify-between">
                    <span className="text-slate-500">Travel CO₂</span>
                    <span className="font-semibold">{twinData.current.breakdown.travel.toLocaleString()} kg</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-500">Energy CO₂</span>
                    <span className="font-semibold">{twinData.current.breakdown.energy.toLocaleString()} kg</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-500">Food CO₂</span>
                    <span className="font-semibold">{twinData.current.breakdown.food.toLocaleString()} kg</span>
                  </div>
                </div>
              </div>

              {/* Eco Lifestyle Card */}
              <div className="glass-panel p-6 rounded-3xl border border-brand-500/20 bg-brand-500/5">
                <span className="text-brand-600 dark:text-brand-400 text-xs font-bold uppercase tracking-wider block">Eco Carbon Twin</span>
                <span className="text-3xl font-extrabold text-brand-700 dark:text-brand-300 mt-1 block">
                  {twinData.eco.annual_emissions.toLocaleString()} kg
                </span>
                <span className="text-xs text-brand-600/70 mt-1 block">Projected CO₂ output</span>

                <div className="mt-4 pt-3 border-t border-brand-500/10 space-y-2 text-xs">
                  <div className="flex justify-between">
                    <span className="text-slate-500">Travel CO₂</span>
                    <span className="font-semibold text-brand-600 dark:text-brand-400">{twinData.eco.breakdown.travel.toLocaleString()} kg</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-500">Energy CO₂</span>
                    <span className="font-semibold text-brand-600 dark:text-brand-400">{twinData.eco.breakdown.energy.toLocaleString()} kg</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-500">Food CO₂</span>
                    <span className="font-semibold text-brand-600 dark:text-brand-400">{twinData.eco.breakdown.food.toLocaleString()} kg</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Savings Panel */}
            <div className="glass-panel p-6 rounded-3xl border border-slate-200/50 dark:border-slate-800/40">
              <h3 className="font-bold text-lg text-slate-800 dark:text-white border-b border-slate-200/50 dark:border-slate-800/40 pb-3 mb-4">
                Eco Optimization Savings Summary
              </h3>
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-5">
                <div className="p-4 rounded-2xl bg-brand-500/10 border border-brand-500/20 text-brand-900 dark:text-brand-300 flex items-start gap-3">
                  <TrendingDown className="w-5 h-5 text-brand-650 flex-shrink-0 mt-0.5" />
                  <div>
                    <span className="text-xs text-slate-500 block">Carbon Reduced</span>
                    <span className="text-lg font-bold">{twinData.savings.annual_co2_kg.toLocaleString()} kg/yr</span>
                  </div>
                </div>

                <div className="p-4 rounded-2xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-900 dark:text-emerald-300 flex items-start gap-3">
                  <DollarSign className="w-5 h-5 text-emerald-600 flex-shrink-0 mt-0.5" />
                  <div>
                    <span className="text-xs text-slate-500 block">Cost Saved</span>
                    <span className="text-lg font-bold">${twinData.savings.annual_cost_usd.toLocaleString()}/yr</span>
                  </div>
                </div>

                <div className="p-4 rounded-2xl bg-blue-500/10 border border-blue-500/20 text-blue-900 dark:text-blue-300 flex items-start gap-3">
                  <TreePine className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
                  <div>
                    <span className="text-xs text-slate-500 block">Offset Equivalent</span>
                    <span className="text-lg font-bold">{twinData.savings.trees_equivalent} trees</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Graph Comparison Sidebar */}
          <div className="glass-panel p-5 rounded-3xl border border-slate-200/50 dark:border-slate-800/40 flex flex-col justify-between">
            <div>
              <h3 className="text-lg font-bold text-slate-800 dark:text-white mb-4">Carbon Output Comparison</h3>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={twinChartData}>
                    <XAxis dataKey="name" stroke="#94a3b8" fontSize={11} tickLine={false} />
                    <YAxis stroke="#94a3b8" fontSize={11} tickLine={false} />
                    <Tooltip formatter={(value) => [`${value} kg CO₂ / yr`, 'Emissions']} contentStyle={{ borderRadius: '12px', border: 'none', background: 'rgba(15,23,42,0.85)', color: 'white' }} />
                    <Bar dataKey="emissions" radius={[10, 10, 0, 0]}>
                      <Cell fill="#f43f5e" />
                      <Cell fill="#10b981" />
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
            <div className="text-xs text-slate-500 text-center mt-3">
              *Calculated based on standard emissions indexes and average utility pricing metrics.
            </div>
          </div>
        </div>
      )}

      {/* TAB 2: What-If Simulator */}
      {tab === 'whatif' && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Sliders Control Panel */}
          <div className="lg:col-span-2 glass-panel p-6 rounded-3xl border border-slate-200/50 dark:border-slate-800/40 space-y-6">
            <h3 className="text-lg font-bold text-slate-800 dark:text-white border-b border-slate-200/50 dark:border-slate-800/40 pb-3">
              Modify Your Lifestyle Sliders
            </h3>

            {/* Travel Shift */}
            <div className="space-y-2">
              <div className="flex justify-between items-center text-sm font-semibold">
                <div className="flex items-center gap-2 text-slate-700 dark:text-slate-300">
                  <Car className="w-4 h-4 text-green-500" />
                  <span>Shift to Transit / Walking</span>
                </div>
                <span className="text-brand-600 dark:text-brand-400">{transitShift}%</span>
              </div>
              <input
                type="range"
                min="0"
                max="100"
                value={transitShift}
                onChange={(e) => setTransitShift(e.target.value)}
                className="w-full h-2 bg-slate-250 dark:bg-slate-800 rounded-lg appearance-none cursor-pointer accent-brand-600"
              />
              <p className="text-[10px] text-slate-400">Replaces driving distance with low-emissions public transit equivalent.</p>
            </div>

            {/* AC reduction */}
            <div className="space-y-2">
              <div className="flex justify-between items-center text-sm font-semibold">
                <div className="flex items-center gap-2 text-slate-700 dark:text-slate-300">
                  <Zap className="w-4 h-4 text-blue-500" />
                  <span>AC Run Time Reduction</span>
                </div>
                <span className="text-brand-600 dark:text-brand-400">{acReduction} hrs/day</span>
              </div>
              <input
                type="range"
                min="0"
                max="12"
                step="0.5"
                value={acReduction}
                onChange={(e) => setAcReduction(e.target.value)}
                className="w-full h-2 bg-slate-250 dark:bg-slate-800 rounded-lg appearance-none cursor-pointer accent-brand-600"
              />
              <p className="text-[10px] text-slate-400">Lowers air conditioner run times per day to save energy.</p>
            </div>

            {/* Meatless days */}
            <div className="space-y-2">
              <div className="flex justify-between items-center text-sm font-semibold">
                <div className="flex items-center gap-2 text-slate-700 dark:text-slate-300">
                  <Utensils className="w-4 h-4 text-amber-500" />
                  <span>Meatless Days / Week</span>
                </div>
                <span className="text-brand-600 dark:text-brand-400">{meatlessDays} days</span>
              </div>
              <input
                type="range"
                min="0"
                max="7"
                value={meatlessDays}
                onChange={(e) => setMeatlessDays(e.target.value)}
                className="w-full h-2 bg-slate-250 dark:bg-slate-800 rounded-lg appearance-none cursor-pointer accent-brand-600"
              />
              <p className="text-[10px] text-slate-400">Replaces non-vegetarian meals with vegetarian ones on these days.</p>
            </div>

            {/* Shopping reduction */}
            <div className="space-y-2">
              <div className="flex justify-between items-center text-sm font-semibold">
                <div className="flex items-center gap-2 text-slate-700 dark:text-slate-300">
                  <ShoppingBag className="w-4 h-4 text-pink-500" />
                  <span>Online Purchase Reduction</span>
                </div>
                <span className="text-brand-600 dark:text-brand-400">{shoppingReduction}%</span>
              </div>
              <input
                type="range"
                min="0"
                max="100"
                value={shoppingReduction}
                onChange={(e) => setShoppingReduction(e.target.value)}
                className="w-full h-2 bg-slate-250 dark:bg-slate-800 rounded-lg appearance-none cursor-pointer accent-brand-600"
              />
              <p className="text-[10px] text-slate-400">Cuts down on online deliveries, preventing freight emissions.</p>
            </div>
          </div>

          {/* Live Outcome Panel */}
          {whatIfData && (
            <div className="glass-panel p-6 rounded-3xl border border-slate-200/50 dark:border-slate-800/40 flex flex-col justify-between bg-brand-500/[0.02]">
              <div className="space-y-6">
                <h3 className="text-lg font-bold text-slate-800 dark:text-white border-b border-slate-200/50 dark:border-slate-800/40 pb-3">
                  Simulation Outcome
                </h3>
                
                <div className="space-y-5">
                  <div>
                    <span className="text-xs text-slate-500 block uppercase tracking-wider font-semibold">Annual CO₂ Prevented</span>
                    <span className="text-3xl font-extrabold text-brand-600 dark:text-brand-400">
                      {whatIfData.annual_co2_saved_kg.toLocaleString()} kg
                    </span>
                  </div>

                  <div>
                    <span className="text-xs text-slate-500 block uppercase tracking-wider font-semibold">Offset Equivalent</span>
                    <span className="text-3xl font-extrabold text-slate-800 dark:text-white flex items-center gap-1.5">
                      <TreePine className="w-7 h-7 text-emerald-500" />
                      <span>{whatIfData.trees_equivalent} trees/yr</span>
                    </span>
                  </div>

                  <div>
                    <span className="text-xs text-slate-500 block uppercase tracking-wider font-semibold">Sustainability Delta</span>
                    <span className="text-3xl font-extrabold text-indigo-600 dark:text-indigo-400">
                      +{whatIfData.sustainability_score} pts
                    </span>
                  </div>
                </div>
              </div>

              <div className="pt-4 border-t border-slate-200/50 dark:border-slate-800/40 text-xs text-slate-400">
                Adjust sliders to see immediate savings updates.
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
export default Simulators;
