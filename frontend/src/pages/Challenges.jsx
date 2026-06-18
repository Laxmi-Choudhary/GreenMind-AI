import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import { useAuth } from '../context/AuthContext';
import { 
  Trophy, 
  Award, 
  Plus, 
  TrendingUp, 
  CheckCircle,
  HelpCircle,
  Loader2,
  Lock
} from 'lucide-react';

export const Challenges = () => {
  const { user, refreshUser } = useAuth();
  const [challenges, setChallenges] = useState([]);
  const [loading, setLoading] = useState(true);
  const [updatingId, setUpdatingId] = useState(null);

  useEffect(() => {
    const fetchChallenges = async () => {
      try {
        const data = await api.get('/api/challenges');
        setChallenges(data);
      } catch (err) {
        console.error("Failed to load challenges:", err);
      } finally {
        setLoading(false);
      }
    };
    fetchChallenges();
  }, []);

  const handleProgressIncrement = async (challengeId) => {
    setUpdatingId(challengeId);
    try {
      const result = await api.post(`/api/challenges/${challengeId}/progress`, { increment: 1 });
      
      // Update local state for challenges
      setChallenges(prev => prev.map(ch => ch.id === challengeId ? result.challenge : ch));
      
      // Update context user profile stats
      await refreshUser();
    } catch (err) {
      console.error("Failed to update challenge progress:", err);
    } finally {
      setUpdatingId(null);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-brand-500"></div>
      </div>
    );
  }

  // Pre-configured Badge icons dictionary
  const badgeIcons = {
    "First Step": { color: "bg-emerald-500/10 text-emerald-600 border-emerald-500/25", desc: "Logged first carbon footprint" },
    "Eco Warrior": { color: "bg-amber-500/10 text-amber-600 border-amber-500/25", desc: "Submitted entry under 10 kg CO₂" },
    "Consistent Saver": { color: "bg-blue-500/10 text-blue-600 border-blue-500/25", desc: "Submitted 5 daily entries" },
    "Energy Saver": { color: "bg-cyan-500/10 text-cyan-600 border-cyan-500/25", desc: "Logged 0 AC hours + low utilities" },
    "Cruisin' Green": { color: "bg-indigo-500/10 text-indigo-600 border-indigo-500/25", desc: "Opted for metro/bus transit over car" },
    "Eco Commuter": { color: "bg-green-500/10 text-green-600 border-green-500/25", desc: "Completed Walk To Work challenge" },
    "Watts Miner": { color: "bg-yellow-500/10 text-yellow-600 border-yellow-500/25", desc: "Completed Save Electricity challenge" },
    "Green Gourmet": { color: "bg-lime-500/10 text-lime-600 border-lime-500/25", desc: "Completed Vegan/Vegetarian challenge" },
    "Minimalist Pack": { color: "bg-pink-500/10 text-pink-600 border-pink-500/25", desc: "Completed Sustainable Shopping challenge" },
    "Zero Waster": { color: "bg-purple-500/10 text-purple-600 border-purple-500/25", desc: "Completed No Plastic Week challenge" }
  };

  const unlockedBadges = user?.badges || [];

  return (
    <div className="space-y-6 max-w-5xl mx-auto animate-slide-up">
      {/* Title */}
      <div className="flex items-center gap-3">
        <div className="p-3 rounded-2xl bg-brand-500/10 text-brand-600 dark:text-brand-400">
          <Trophy className="w-8 h-8 animate-pulse-subtle" />
        </div>
        <div>
          <h1 className="text-3xl font-bold text-slate-900 dark:text-white">Eco Challenges & Badges</h1>
          <p className="text-slate-500 dark:text-slate-400">Adopt micro-habits, complete challenges, and earn badges to level up.</p>
        </div>
      </div>

      {/* Stats row */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
        <div className="glass-panel p-5 rounded-3xl border border-slate-200/50 dark:border-slate-800/40 text-center">
          <span className="text-xs text-slate-400 font-bold uppercase tracking-wider block">Level Status</span>
          <span className="text-3xl font-extrabold text-brand-600 dark:text-brand-400 mt-2 block">Level {user?.level}</span>
          <p className="text-xs text-slate-500 mt-1">Crosses level boundaries every 100 XP</p>
        </div>

        <div className="glass-panel p-5 rounded-3xl border border-slate-200/50 dark:border-slate-800/40 text-center">
          <span className="text-xs text-slate-400 font-bold uppercase tracking-wider block">Total Points</span>
          <span className="text-3xl font-extrabold text-slate-900 dark:text-white mt-2 block">{user?.points} XP</span>
          <p className="text-xs text-slate-500 mt-1">Complete tasks to accumulate points</p>
        </div>

        <div className="glass-panel p-5 rounded-3xl border border-slate-200/50 dark:border-slate-800/40 text-center">
          <span className="text-xs text-slate-400 font-bold uppercase tracking-wider block">Badges Claimed</span>
          <span className="text-3xl font-extrabold text-slate-900 dark:text-white mt-2 block">{unlockedBadges.length} unlocked</span>
          <p className="text-xs text-slate-500 mt-1">10 unique achievements available</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Active Challenges list */}
        <div className="lg:col-span-2 space-y-4">
          <h3 className="text-lg font-bold text-slate-800 dark:text-white mb-2">Available Challenges</h3>
          
          <div className="space-y-4">
            {challenges.map((ch) => {
              const isCompleted = ch.status === 'completed';
              return (
                <div 
                  key={ch.id} 
                  className={`glass-panel p-5 rounded-3xl border flex flex-col sm:flex-row sm:items-center justify-between gap-4 transition-all ${
                    isCompleted 
                      ? 'border-brand-500/20 bg-brand-500/[0.02] opacity-75' 
                      : 'border-slate-200/50 dark:border-slate-800/40'
                  }`}
                >
                  <div className="space-y-2 flex-1">
                    <div className="flex items-center gap-2">
                      <span className={`px-2 py-0.5 rounded-md text-[10px] font-bold uppercase ${
                        ch.category === 'travel' ? 'bg-green-500/10 text-green-600' :
                        ch.category === 'energy' ? 'bg-blue-500/10 text-blue-600' :
                        ch.category === 'food' ? 'bg-amber-500/10 text-amber-600' :
                        ch.category === 'shopping' ? 'bg-pink-500/10 text-pink-650' : 'bg-purple-500/10 text-purple-650'
                      }`}>
                        {ch.category}
                      </span>
                      <h4 className="font-bold text-slate-855 dark:text-white text-base">{ch.title}</h4>
                    </div>
                    <p className="text-xs text-slate-500 dark:text-slate-400">{ch.description}</p>
                    
                    {/* Progress slider bar */}
                    <div className="flex items-center gap-3 w-full max-w-xs pt-1">
                      <div className="flex-1 h-2 bg-slate-200 dark:bg-slate-800 rounded-full overflow-hidden">
                        <div 
                          className="h-full bg-brand-500 rounded-full transition-all duration-300"
                          style={{ width: `${(ch.progress / ch.target) * 100}%` }}
                        />
                      </div>
                      <span className="text-xs font-semibold text-slate-500">{ch.progress}/{ch.target}</span>
                    </div>
                  </div>

                  <div className="flex sm:flex-col items-end justify-between sm:justify-center gap-2 border-t sm:border-t-0 pt-3 sm:pt-0 border-slate-100 dark:border-slate-800/40">
                    <span className="text-xs font-bold text-slate-650 dark:text-slate-300 bg-slate-100 dark:bg-slate-800 px-2 py-1 rounded-lg">
                      +{ch.points} XP
                    </span>
                    {isCompleted ? (
                      <div className="flex items-center gap-1 text-xs font-semibold text-brand-600 dark:text-brand-400 px-3 py-2 rounded-xl bg-brand-500/10">
                        <CheckCircle className="w-4 h-4" />
                        <span>Completed</span>
                      </div>
                    ) : (
                      <button
                        onClick={() => handleProgressIncrement(ch.id)}
                        disabled={updatingId !== null}
                        className="flex items-center gap-1 px-4 py-2 bg-brand-600 hover:bg-brand-500 text-white rounded-xl text-xs font-bold transition-all disabled:opacity-50 cursor-pointer shadow-md shadow-brand-500/5"
                      >
                        {updatingId === ch.id ? (
                          <Loader2 className="w-3.5 h-3.5 animate-spin" />
                        ) : (
                          <>
                            <Plus className="w-3.5 h-3.5" />
                            <span>Log Action</span>
                          </>
                        )}
                      </button>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Badges Panel */}
        <div className="glass-panel p-5 rounded-3xl border border-slate-200/50 dark:border-slate-800/40 flex flex-col">
          <h3 className="text-lg font-bold text-slate-800 dark:text-white mb-4">Your Badges</h3>
          
          <div className="grid grid-cols-2 gap-3 flex-1">
            {Object.keys(badgeIcons).map((badgeName) => {
              const isUnlocked = unlockedBadges.includes(badgeName);
              const { color, desc } = badgeIcons[badgeName];
              return (
                <div 
                  key={badgeName}
                  className={`p-3 rounded-2xl border text-center flex flex-col items-center justify-center gap-2 transition-all ${
                    isUnlocked 
                      ? `${color} transform hover:scale-[1.03]` 
                      : 'bg-slate-100 dark:bg-slate-900/40 border-slate-200/30 dark:border-slate-800/30 opacity-40'
                  }`}
                >
                  <div className="p-2.5 rounded-full bg-white dark:bg-slate-950 shadow-sm border border-slate-200/30 dark:border-slate-800/30">
                    {isUnlocked ? (
                      <Award className="w-6 h-6 text-brand-500" />
                    ) : (
                      <Lock className="w-6 h-6 text-slate-400" />
                    )}
                  </div>
                  <div className="space-y-0.5">
                    <h5 className="text-[10px] font-bold tracking-tight text-slate-900 dark:text-white leading-tight">
                      {badgeName}
                    </h5>
                    <p className="text-[9px] text-slate-550 leading-tight block truncate w-24" title={desc}>
                      {desc}
                    </p>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
};
export default Challenges;
