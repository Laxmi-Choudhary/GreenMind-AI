// frontend/src/components/Navbar.jsx

import React, { memo, useState } from "react";
import { useAuth } from "../context/AuthContext";
import { useTheme } from "../context/ThemeContext";

import {
  Sun,
  Moon,
  LogOut,
  Award,
  Trophy,
  Leaf,
  Menu,
  User
} from "lucide-react";

const Navbar = ({ toggleSidebar }) => {
  const { user, logout } = useAuth();
  const { theme, toggleTheme } = useTheme();

  const [loggingOut, setLoggingOut] = useState(false);

  const handleLogout = async () => {
    try {
      setLoggingOut(true);
      await logout();
    } catch (error) {
      console.error("Logout failed:", error);
    } finally {
      setLoggingOut(false);
    }
  };

  return (
    <header className="sticky top-0 z-40 w-full bg-white/80 dark:bg-slate-900/80 backdrop-blur-md shadow-sm border-b border-slate-200 dark:border-slate-800 px-4 py-3">

      <div className="flex items-center justify-between">

        {/* Left Section */}
        <div className="flex items-center gap-3">

          <button
            onClick={toggleSidebar}
            className="md:hidden p-2 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800 transition"
            aria-label="Open sidebar"
          >
            <Menu className="w-6 h-6" />
          </button>

          <div className="flex items-center gap-2">
            <Leaf className="w-7 h-7 text-green-600 animate-pulse" />

            <h1 className="font-bold text-lg sm:text-xl text-green-700 dark:text-green-400">
              GreenMind AI
            </h1>
          </div>
        </div>

        {/* Right Section */}
        <div className="flex items-center gap-3">

          {/* User Stats */}
          {user && (
            <div className="hidden sm:flex items-center gap-3 rounded-full bg-green-100 dark:bg-green-900/30 px-4 py-2">

              <div className="flex items-center gap-1">
                <Trophy className="w-4 h-4 text-yellow-500" />
                <span className="text-sm font-semibold">
                  Lv {user.level}
                </span>
              </div>

              <div className="w-px h-4 bg-slate-300"></div>

              <div className="flex items-center gap-1">
                <Award className="w-4 h-4 text-emerald-500" />
                <span className="text-sm font-semibold">
                  {user.points} pts
                </span>
              </div>

            </div>
          )}

          {/* Theme Toggle */}
          <button
            onClick={toggleTheme}
            className="p-2 rounded-xl hover:bg-slate-100 dark:hover:bg-slate-800 transition"
            aria-label="Toggle theme"
          >
            {theme === "dark" ? (
              <Sun className="w-5 h-5 text-yellow-400" />
            ) : (
              <Moon className="w-5 h-5" />
            )}
          </button>

          {/* User Profile */}
          {user && (
            <div className="flex items-center gap-3">

              {/* Avatar */}
              <div className="w-10 h-10 rounded-full bg-green-600 text-white flex items-center justify-center font-bold">
                {user.username
                  ? user.username.charAt(0).toUpperCase()
                  : <User className="w-5 h-5" />}
              </div>

              {/* User Info */}
              <div className="hidden md:flex flex-col">
                <span className="text-sm font-semibold text-slate-700 dark:text-slate-200">
                  {user.username}
                </span>

                <span className="text-xs text-slate-500 dark:text-slate-400">
                  {user.email}
                </span>
              </div>

              {/* Logout */}
              <button
                onClick={handleLogout}
                disabled={loggingOut}
                className="p-2 rounded-xl text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20 transition disabled:opacity-50"
                aria-label="Logout"
                title="Logout"
              >
                <LogOut className="w-5 h-5" />
              </button>

            </div>
          )}

        </div>
      </div>
    </header>
  );
};

export default memo(Navbar);