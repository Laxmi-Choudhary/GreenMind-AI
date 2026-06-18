import React, { useState } from 'react';
import { api } from '../services/api';
import { useAuth } from '../context/AuthContext';
import { 
  Car, 
  Tv, 
  Utensils, 
  ShoppingBag, 
  Trash2, 
  Calendar, 
  Award, 
  CheckCircle,
  Loader2
} from 'lucide-react';

export const Calculator = () => {
  const { refreshUser } = useAuth();
  const [date, setDate] = useState(new Date().toISOString().split('T')[0]);
  const [carKm, setCarKm] = useState(0);
  const [busKm, setBusKm] = useState(0);
  const [trainKm, setTrainKm] = useState(0);
  const [metroKm, setMetroKm] = useState(0);
  const [electricityKwh, setElectricityKwh] = useState(0);
  const [acHours, setAcHours] = useState(0);
  const [diet, setDiet] = useState('vegetarian');
  const [onlinePurchases, setOnlinePurchases] = useState(0);
  const [wasteLevel, setWasteLevel] = useState('medium');
  
  const [loading, setLoading] = useState(false);
  const [successResult, setSuccessResult] = useState(null);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setSuccessResult(null);

    const payload = {
      date,
      car_km: parseFloat(carKm) || 0,
      bus_km: parseFloat(busKm) || 0,
      train_km: parseFloat(trainKm) || 0,
      metro_km: parseFloat(metroKm) || 0,
      electricity_kwh: parseFloat(electricityKwh) || 0,
      ac_hours: parseFloat(acHours) || 0,
      diet,
      online_purchases: parseInt(onlinePurchases) || 0,
      waste_level: wasteLevel
    };

    try {
      const data = await api.post('/api/calculator/log', payload);
      setSuccessResult(data);
      await refreshUser(); // Update navbar points/levels
    } catch (err) {
      setError(err.message || 'Failed to submit calculation.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6 max-w-4xl mx-auto animate-slide-up">
      <div>
        <h1 className="text-3xl font-bold text-slate-900 dark:text-white">Carbon Calculator</h1>
        <p className="text-slate-500 dark:text-slate-400">Log your daily emissions details to compile carbon stats.</p>
      </div>

      {successResult && (
        <div className="p-6 rounded-3xl bg-brand-500/10 border border-brand-500/20 text-brand-900 dark:text-brand-300 space-y-4 shadow-sm animate-pulse-subtle">
          <div className="flex items-center gap-3">
            <CheckCircle className="w-8 h-8 text-brand-600 dark:text-brand-400 flex-shrink-0" />
            <div>
              <h3 className="font-bold text-lg">Footprint Logged Successfully!</h3>
              <p className="text-sm opacity-90">Your footprint logs are saved to your account profile.</p>
            </div>
          </div>
          
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 pt-2 border-t border-brand-500/10">
            <div>
              <span className="text-xs text-slate-500 dark:text-slate-400 uppercase tracking-wider block">Daily Footprint</span>
              <span className="text-2xl font-bold">{successResult.log.daily_emissions} kg CO₂</span>
            </div>
            <div>
              <span className="text-xs text-slate-500 dark:text-slate-400 uppercase tracking-wider block">Points Awarded</span>
              <span className="text-2xl font-bold">+{successResult.points_earned} XP</span>
            </div>
            <div>
              <span className="text-xs text-slate-500 dark:text-slate-400 uppercase tracking-wider block">Current Level</span>
              <span className="text-2xl font-bold">Lvl {successResult.new_level} {successResult.level_up && '🎉 (Level Up!)'}</span>
            </div>
          </div>

          {successResult.messages.length > 1 && (
            <div className="bg-white/40 dark:bg-slate-900/40 p-3 rounded-2xl border border-brand-500/10 space-y-1 text-xs">
              <span className="font-semibold block uppercase tracking-wider text-slate-500">Milestones Reached:</span>
              {successResult.messages.map((msg, i) => (
                <div key={i} className="flex items-center gap-1.5 font-medium">
                  <Award className="w-3.5 h-3.5 text-amber-500" />
                  <span>{msg}</span>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {error && (
        <div className="p-4 rounded-3xl bg-rose-500/10 border border-rose-500/20 text-rose-600 dark:text-rose-400 text-sm">
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Date Row */}
        <div className="glass-panel p-5 rounded-3xl flex flex-col sm:flex-row sm:items-center justify-between gap-4 border border-slate-200/50 dark:border-slate-800/40">
          <div className="flex items-center gap-3">
            <Calendar className="w-5 h-5 text-slate-400" />
            <div>
              <h3 className="font-bold text-slate-800 dark:text-white">Reporting Date</h3>
              <p className="text-xs text-slate-500">Record entries on a specific calendar date.</p>
            </div>
          </div>
          <input
            type="date"
            required
            value={date}
            onChange={(e) => setDate(e.target.value)}
            className="px-4 py-2.5 bg-white dark:bg-slate-900/60 border border-slate-300 dark:border-slate-800 rounded-xl text-slate-900 dark:text-white text-sm focus:outline-none focus:ring-2 focus:ring-brand-500"
          />
        </div>

        {/* Categories Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Transportation */}
          <div className="glass-panel p-6 rounded-3xl border border-slate-200/50 dark:border-slate-800/40 space-y-4">
            <div className="flex items-center gap-3 border-b border-slate-200/50 dark:border-slate-800/40 pb-3">
              <div className="p-2 rounded-xl bg-green-500/10 text-green-600">
                <Car className="w-5 h-5" />
              </div>
              <h3 className="font-bold text-slate-800 dark:text-white">Transportation</h3>
            </div>
            
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-semibold text-slate-500 dark:text-slate-400 mb-1">Car Travel (km)</label>
                <input
                  type="number"
                  min="0"
                  step="any"
                  value={carKm}
                  onChange={(e) => setCarKm(e.target.value)}
                  className="w-full px-3 py-2 bg-white/40 dark:bg-slate-900/40 border border-slate-300 dark:border-slate-800 rounded-xl text-slate-900 dark:text-white text-sm focus:outline-none focus:ring-2 focus:ring-brand-500"
                />
              </div>
              <div>
                <label className="block text-xs font-semibold text-slate-500 dark:text-slate-400 mb-1">Bus Commute (km)</label>
                <input
                  type="number"
                  min="0"
                  step="any"
                  value={busKm}
                  onChange={(e) => setBusKm(e.target.value)}
                  className="w-full px-3 py-2 bg-white/40 dark:bg-slate-900/40 border border-slate-300 dark:border-slate-800 rounded-xl text-slate-900 dark:text-white text-sm focus:outline-none focus:ring-2 focus:ring-brand-500"
                />
              </div>
              <div>
                <label className="block text-xs font-semibold text-slate-500 dark:text-slate-400 mb-1">Train Commute (km)</label>
                <input
                  type="number"
                  min="0"
                  step="any"
                  value={trainKm}
                  onChange={(e) => setTrainKm(e.target.value)}
                  className="w-full px-3 py-2 bg-white/40 dark:bg-slate-900/40 border border-slate-300 dark:border-slate-800 rounded-xl text-slate-900 dark:text-white text-sm focus:outline-none focus:ring-2 focus:ring-brand-500"
                />
              </div>
              <div>
                <label className="block text-xs font-semibold text-slate-500 dark:text-slate-400 mb-1">Metro Travel (km)</label>
                <input
                  type="number"
                  min="0"
                  step="any"
                  value={metroKm}
                  onChange={(e) => setMetroKm(e.target.value)}
                  className="w-full px-3 py-2 bg-white/40 dark:bg-slate-900/40 border border-slate-300 dark:border-slate-800 rounded-xl text-slate-900 dark:text-white text-sm focus:outline-none focus:ring-2 focus:ring-brand-500"
                />
              </div>
            </div>
          </div>

          {/* Energy & Utilities */}
          <div className="glass-panel p-6 rounded-3xl border border-slate-200/50 dark:border-slate-800/40 space-y-4">
            <div className="flex items-center gap-3 border-b border-slate-200/50 dark:border-slate-800/40 pb-3">
              <div className="p-2 rounded-xl bg-blue-500/10 text-blue-600">
                <Tv className="w-5 h-5" />
              </div>
              <h3 className="font-bold text-slate-800 dark:text-white">Energy & Utilities</h3>
            </div>
            
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-semibold text-slate-500 dark:text-slate-400 mb-1">Electricity (kWh)</label>
                <input
                  type="number"
                  min="0"
                  step="any"
                  value={electricityKwh}
                  onChange={(e) => setElectricityKwh(e.target.value)}
                  className="w-full px-3 py-2 bg-white/40 dark:bg-slate-900/40 border border-slate-300 dark:border-slate-800 rounded-xl text-slate-900 dark:text-white text-sm focus:outline-none focus:ring-2 focus:ring-brand-500"
                />
              </div>
              <div>
                <label className="block text-xs font-semibold text-slate-500 dark:text-slate-400 mb-1">AC Usage (hours)</label>
                <input
                  type="number"
                  min="0"
                  step="any"
                  value={acHours}
                  onChange={(e) => setAcHours(e.target.value)}
                  className="w-full px-3 py-2 bg-white/40 dark:bg-slate-900/40 border border-slate-300 dark:border-slate-800 rounded-xl text-slate-900 dark:text-white text-sm focus:outline-none focus:ring-2 focus:ring-brand-500"
                />
              </div>
            </div>
          </div>

          {/* Diet Preferences */}
          <div className="glass-panel p-6 rounded-3xl border border-slate-200/50 dark:border-slate-800/40 space-y-4">
            <div className="flex items-center gap-3 border-b border-slate-200/50 dark:border-slate-800/40 pb-3">
              <div className="p-2 rounded-xl bg-amber-500/10 text-amber-600">
                <Utensils className="w-5 h-5" />
              </div>
              <h3 className="font-bold text-slate-800 dark:text-white">Diet Preferences</h3>
            </div>
            
            <div className="space-y-3">
              <label className="block text-xs font-semibold text-slate-500 dark:text-slate-400">Primary Meal Habits</label>
              <div className="grid grid-cols-3 gap-3">
                {['vegan', 'vegetarian', 'non-vegetarian'].map((type) => (
                  <button
                    key={type}
                    type="button"
                    onClick={() => setDiet(type)}
                    className={`px-3 py-2.5 rounded-xl border text-xs font-semibold capitalize transition-all cursor-pointer ${
                      diet === type 
                        ? 'bg-brand-500 border-brand-500 text-white shadow-md shadow-brand-500/10' 
                        : 'border-slate-200 dark:border-slate-800 hover:bg-slate-100 dark:hover:bg-slate-900/40 text-slate-700 dark:text-slate-300'
                    }`}
                  >
                    {type.replace('-', ' ')}
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* Shopping & Waste */}
          <div className="glass-panel p-6 rounded-3xl border border-slate-200/50 dark:border-slate-800/40 space-y-4">
            <div className="flex items-center gap-3 border-b border-slate-200/50 dark:border-slate-800/40 pb-3">
              <div className="p-2 rounded-xl bg-pink-500/10 text-pink-600">
                <ShoppingBag className="w-5 h-5" />
              </div>
              <h3 className="font-bold text-slate-800 dark:text-white">Shopping & Waste</h3>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-semibold text-slate-500 dark:text-slate-400 mb-1">Online Purchases</label>
                <input
                  type="number"
                  min="0"
                  value={onlinePurchases}
                  onChange={(e) => setOnlinePurchases(e.target.value)}
                  className="w-full px-3 py-2 bg-white/40 dark:bg-slate-900/40 border border-slate-300 dark:border-slate-800 rounded-xl text-slate-900 dark:text-white text-sm focus:outline-none focus:ring-2 focus:ring-brand-500"
                />
              </div>
              <div>
                <label className="block text-xs font-semibold text-slate-500 dark:text-slate-400 mb-1">Waste Generated</label>
                <select
                  value={wasteLevel}
                  onChange={(e) => setWasteLevel(e.target.value)}
                  className="w-full px-3 py-2 bg-white/40 dark:bg-slate-900/40 border border-slate-300 dark:border-slate-800 rounded-xl text-slate-900 dark:text-white text-sm focus:outline-none focus:ring-2 focus:ring-brand-500"
                >
                  <option value="low">Low (Recycled)</option>
                  <option value="medium">Medium</option>
                  <option value="high">High (No Recycle)</option>
                </select>
              </div>
            </div>
          </div>
        </div>

        {/* Submit */}
        <div className="flex justify-end pt-2">
          <button
            type="submit"
            disabled={loading}
            className="flex items-center gap-2 px-8 py-3.5 bg-brand-600 hover:bg-brand-500 text-white font-semibold rounded-2xl shadow-lg shadow-brand-500/10 hover:shadow-brand-500/20 hover:scale-[1.01] active:scale-[0.99] transition-all cursor-pointer"
          >
            {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : <span>Record Daily Footprint</span>}
          </button>
        </div>
      </form>
    </div>
  );
};
export default Calculator;
