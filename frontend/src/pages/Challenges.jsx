import React, { useState, useEffect, useMemo } from 'react';
import { api } from '../services/api';
import { useAuth } from '../context/AuthContext';
import {
  Trophy,
  Award,
  Plus,
  CheckCircle,
  Loader2,
  Lock,
  RotateCcw,
  Target,
  TrendingUp,
  Star,
  AlertCircle
} from 'lucide-react';

export const Challenges = () => {
  const { user, refreshUser } = useAuth();

  const [challenges, setChallenges] = useState([]);
  const [loading, setLoading] = useState(true);
  const [updatingId, setUpdatingId] = useState(null);
  const [resetting, setResetting] = useState(false);
  const [error, setError] = useState('');
  const [message, setMessage] = useState('');

  // =====================================================
  // FETCH CHALLENGES
  // =====================================================

  useEffect(() => {
    fetchChallenges();
  }, []);

  const fetchChallenges = async () => {
    try {
      setLoading(true);
      setError('');

      const res = await api.get('/api/challenges');

      const challengeList =
        res?.data?.challenges ||
        res?.challenges ||
        [];

      setChallenges(
        Array.isArray(challengeList)
          ? challengeList
          : []
      );
    } catch (err) {
      console.error('Failed to load challenges:', err);
      setError('Failed to load challenges');
      setChallenges([]);
    } finally {
      setLoading(false);
    }
  };

  // =====================================================
  // UPDATE PROGRESS
  // =====================================================

  const handleProgressIncrement = async (challengeId) => {
    try {
      setUpdatingId(challengeId);
      setMessage('');
      setError('');

      const res = await api.post(
        `/api/challenges/${challengeId}/progress`,
        {
          increment: 1
        }
      );

      const updatedChallenge =
        res?.data?.challenge ||
        res?.challenge;

      const messages =
        res?.data?.messages ||
        res?.messages ||
        [];

      if (updatedChallenge) {
        setChallenges(prev =>
          prev.map(ch =>
            ch.id === challengeId
              ? updatedChallenge
              : ch
          )
        );
      }

      if (messages.length > 0) {
        setMessage(messages.join(' • '));
      }

      await refreshUser();
    } catch (err) {
      console.error(
        'Failed to update challenge:',
        err
      );

      setError(
        err?.response?.data?.detail ||
        'Failed to update challenge'
      );
    } finally {
      setUpdatingId(null);
    }
  };

  // =====================================================
  // RESET CHALLENGES
  // =====================================================

  const handleReset = async () => {
    if (
      !window.confirm(
        'Reset all challenges?'
      )
    ) {
      return;
    }

    try {
      setResetting(true);

      const res = await api.post(
        '/api/challenges/reset'
      );

      const newChallenges =
        res?.data?.challenges ||
        res?.challenges ||
        [];

      setChallenges(newChallenges);
      setMessage(
        'Challenges reset successfully.'
      );

      await refreshUser();
    } catch (err) {
      console.error(err);

      setError(
        err?.response?.data?.detail ||
        'Failed to reset challenges'
      );
    } finally {
      setResetting(false);
    }
  };

  // =====================================================
  // STATS
  // =====================================================

  const stats = useMemo(() => {
    const completed = challenges.filter(
      c => c.status === 'completed'
    ).length;

    return {
      total: challenges.length,
      completed,
      active: challenges.length - completed
    };
  }, [challenges]);

  // =====================================================
  // BADGES
  // =====================================================

  const badgeData = {
    'First Step': {
      desc: 'Logged first footprint',
      color:
        'bg-emerald-100 text-emerald-700'
    },

    'Eco Warrior': {
      desc: 'Low carbon footprint',
      color:
        'bg-amber-100 text-amber-700'
    },

    'Consistent Saver': {
      desc: '5 daily entries',
      color:
        'bg-blue-100 text-blue-700'
    },

    'Energy Saver': {
      desc: 'Low energy usage',
      color:
        'bg-cyan-100 text-cyan-700'
    },

    'Cruisin\' Green': {
      desc: 'Green transportation',
      color:
        'bg-indigo-100 text-indigo-700'
    },

    'Eco Commuter': {
      desc: 'Completed travel challenge',
      color:
        'bg-green-100 text-green-700'
    },

    'Watts Saver': {
      desc: 'Completed energy challenge',
      color:
        'bg-yellow-100 text-yellow-700'
    },

    'Green Gourmet': {
      desc: 'Completed food challenge',
      color:
        'bg-lime-100 text-lime-700'
    },

    'Minimalist Pack': {
      desc: 'Completed shopping challenge',
      color:
        'bg-pink-100 text-pink-700'
    },

    'Zero Waster': {
      desc: 'Completed waste challenge',
      color:
        'bg-purple-100 text-purple-700'
    }
  };

  const unlockedBadges =
    user?.badges || [];

  // =====================================================
  // LOADING
  // =====================================================

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-[60vh]">
        <Loader2 className="w-10 h-10 animate-spin text-green-600" />
      </div>
    );
  }

  // =====================================================
  // UI
  // =====================================================

  return (
    <div className="max-w-7xl mx-auto space-y-8">

      {/* HEADER */}

      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">

        <div className="flex items-center gap-4">
          <div className="p-4 rounded-2xl bg-green-100">
            <Trophy className="w-8 h-8 text-green-600" />
          </div>

          <div>
            <h1 className="text-3xl font-bold">
              Eco Challenges
            </h1>

            <p className="text-gray-500">
              Complete challenges and earn rewards
            </p>
          </div>
        </div>

        <button
          onClick={handleReset}
          disabled={resetting}
          className="flex items-center gap-2 px-4 py-2 rounded-xl bg-gray-900 text-white hover:bg-gray-800"
        >
          {resetting ? (
            <Loader2 className="w-4 h-4 animate-spin" />
          ) : (
            <RotateCcw className="w-4 h-4" />
          )}

          Reset Challenges
        </button>
      </div>

      {/* ALERTS */}

      {message && (
        <div className="p-4 rounded-xl bg-green-100 text-green-700">
          {message}
        </div>
      )}

      {error && (
        <div className="p-4 rounded-xl bg-red-100 text-red-700 flex items-center gap-2">
          <AlertCircle className="w-5 h-5" />
          {error}
        </div>
      )}

      {/* STATS */}

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">

        <div className="p-6 rounded-3xl border bg-white">
          <Target className="w-6 h-6 text-blue-600 mb-3" />

          <p className="text-gray-500 text-sm">
            Total Challenges
          </p>

          <h2 className="text-3xl font-bold">
            {stats.total}
          </h2>
        </div>

        <div className="p-6 rounded-3xl border bg-white">
          <CheckCircle className="w-6 h-6 text-green-600 mb-3" />

          <p className="text-gray-500 text-sm">
            Completed
          </p>

          <h2 className="text-3xl font-bold">
            {stats.completed}
          </h2>
        </div>

        <div className="p-6 rounded-3xl border bg-white">
          <TrendingUp className="w-6 h-6 text-purple-600 mb-3" />

          <p className="text-gray-500 text-sm">
            Level
          </p>

          <h2 className="text-3xl font-bold">
            {user?.level || 1}
          </h2>
        </div>

        <div className="p-6 rounded-3xl border bg-white">
          <Star className="w-6 h-6 text-yellow-600 mb-3" />

          <p className="text-gray-500 text-sm">
            XP Points
          </p>

          <h2 className="text-3xl font-bold">
            {user?.points || 0}
          </h2>
        </div>

      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">

        {/* CHALLENGES */}

        <div className="lg:col-span-2 space-y-4">

          <h2 className="text-xl font-bold">
            Available Challenges
          </h2>

          {challenges.length === 0 ? (
            <div className="p-10 border rounded-3xl text-center">
              No challenges available.
            </div>
          ) : (
            challenges.map(challenge => {

              const completed =
                challenge.status === 'completed';

              const percentage =
                challenge.target > 0
                  ? Math.round(
                    (challenge.progress /
                      challenge.target) *
                    100
                  )
                  : 0;

              return (
                <div
                  key={challenge.id}
                  className="border rounded-3xl p-6 bg-white shadow-sm"
                >

                  <div className="flex flex-col md:flex-row justify-between gap-5">

                    <div className="flex-1">

                      <div className="flex items-center gap-2 mb-2">

                        <span className="text-xs bg-green-100 text-green-700 px-2 py-1 rounded">
                          {challenge.category}
                        </span>

                        <h3 className="font-bold text-lg">
                          {challenge.title}
                        </h3>

                      </div>

                      <p className="text-gray-500 mb-4">
                        {challenge.description}
                      </p>

                      <div className="w-full h-3 rounded-full bg-gray-200 overflow-hidden">

                        <div
                          className="h-full bg-green-600 transition-all"
                          style={{
                            width: `${percentage}%`
                          }}
                        />

                      </div>

                      <div className="flex justify-between mt-2 text-sm text-gray-500">

                        <span>
                          {challenge.progress}/
                          {challenge.target}
                        </span>

                        <span>
                          {percentage}%
                        </span>

                      </div>
                    </div>

                    <div className="flex flex-col gap-3 items-end">

                      <span className="font-bold text-yellow-600">
                        +{challenge.points} XP
                      </span>

                      {completed ? (
                        <div className="flex items-center gap-2 px-4 py-2 rounded-xl bg-green-100 text-green-700">
                          <CheckCircle className="w-4 h-4" />
                          Completed
                        </div>
                      ) : (
                        <button
                          onClick={() =>
                            handleProgressIncrement(
                              challenge.id
                            )
                          }
                          disabled={
                            updatingId ===
                            challenge.id
                          }
                          className="flex items-center gap-2 px-4 py-2 rounded-xl bg-green-600 text-white hover:bg-green-700"
                        >
                          {updatingId ===
                            challenge.id ? (
                            <Loader2 className="w-4 h-4 animate-spin" />
                          ) : (
                            <>
                              <Plus className="w-4 h-4" />
                              Log Action
                            </>
                          )}
                        </button>
                      )}

                    </div>

                  </div>
                </div>
              );
            })
          )}

        </div>

        {/* BADGES */}

        <div className="border rounded-3xl p-6 bg-white">

          <h2 className="text-xl font-bold mb-5">
            Your Badges
          </h2>

          <div className="grid grid-cols-2 gap-4">

            {Object.entries(badgeData).map(
              ([name, badge]) => {

                const unlocked =
                  unlockedBadges.includes(name);

                return (
                  <div
                    key={name}
                    className={`rounded-2xl p-4 border text-center ${unlocked
                        ? badge.color
                        : 'bg-gray-100 text-gray-400'
                      }`}
                  >

                    <div className="flex justify-center mb-2">

                      {unlocked ? (
                        <Award className="w-7 h-7" />
                      ) : (
                        <Lock className="w-7 h-7" />
                      )}

                    </div>

                    <h4 className="font-semibold text-sm">
                      {name}
                    </h4>

                    <p className="text-xs mt-1">
                      {badge.desc}
                    </p>

                  </div>
                );
              }
            )}

          </div>

        </div>

      </div>
    </div>
  );
};

export default Challenges;