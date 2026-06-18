import React from 'react';
import { useAuth } from '../context/AuthContext';
import { useTheme } from '../context/ThemeContext';
import { Sun, Moon, LogOut, Award, Trophy, User, Leaf, Menu } from 'lucide-react';

export const Navbar = ({ toggleSidebar }) => {
  const { user, logout } = useAuth();
  const { theme, toggleTheme } = useTheme();

  return (
    <header className="sticky top-0 z-40 w-full glass-panel shadow-sm px-4 py-3 flex items-center justify-between border-b border-slate-200/50 dark:border-slate-800/40">
      <div className="flex items-center gap-3">
        <button 
          onClick={toggleSidebar}
          className="p-1.5 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800 md:hidden transition-colors"
          aria-label="Toggle sidebar"
        >
          <Menu className="w-6 h-6" />
        </button>
        <div className="flex items-center gap-2 text-brand-600 dark:text-brand-400 font-bold text-xl tracking-tight">
          <Leaf className="w-6 h-6 animate-pulse-subtle" />
          <span>GreenMind AI</span>
        </div>
      </div>

      <div className="flex items-center gap-4">
        {user && (
          <div className="hidden sm:flex items-center gap-3 bg-brand-500/10 text-brand-700 dark:text-brand-300 px-3 py-1.5 rounded-full text-sm font-semibold border border-brand-500/20">
            <Trophy className="w-4 h-4 text-amber-500" />
            <span>Lvl {user.level}</span>
            <span className="w-1.5 h-1.5 bg-brand-500 rounded-full"></span>
            <Award className="w-4 h-4 text-emerald-500" />
            <span>{user.points} pts</span>
          </div>
        )}

        <button
          onClick={toggleTheme}
          className="p-2 rounded-xl border border-slate-200/50 dark:border-slate-800/40 hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-600 dark:text-slate-300 transition-all"
          aria-label="Toggle dark mode"
        >
          {theme === 'dark' ? <Sun className="w-5 h-5 text-amber-400" /> : <Moon className="w-5 h-5" />}
        </button>

        {user && (
          <div className="flex items-center gap-2">
            <div className="hidden md:flex flex-col text-right">
              <span className="text-sm font-medium text-slate-700 dark:text-slate-200">{user.username}</span>
              <span className="text-xs text-slate-500 dark:text-slate-400">{user.email}</span>
            </div>
            
            <button
              onClick={logout}
              className="p-2 ml-1 rounded-xl text-rose-500 hover:bg-rose-500/10 transition-colors border border-transparent hover:border-rose-500/20"
              title="Logout"
              aria-label="Logout"
            >
              <LogOut className="w-5 h-5" />
            </button>
          </div>
        )}
      </div>
    </header>
  );
};
export default Navbar;
