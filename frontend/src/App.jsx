// frontend/src/App.jsx

import React, { lazy, Suspense, useState } from "react";
import {
  BrowserRouter,
  Routes,
  Route,
  Navigate,
  Outlet,
} from "react-router-dom";

import { AuthProvider, useAuth } from "./context/AuthContext";
import { ThemeProvider } from "./context/ThemeContext";

import Navbar from "./components/Navbar";
import Sidebar from "./components/Sidebar";

// ==============================
// Lazy Loaded Pages
// ==============================

const Login = lazy(() => import("./pages/Login"));
const Register = lazy(() => import("./pages/Register"));
const Dashboard = lazy(() => import("./pages/Dashboard"));
const Calculator = lazy(() => import("./pages/Calculator"));
const Coach = lazy(() => import("./pages/Coach"));
const Chat = lazy(() => import("./pages/Chat"));
const Simulators = lazy(() => import("./pages/Simulators"));
const Challenges = lazy(() => import("./pages/Challenges"));
const Reports = lazy(() => import("./pages/Reports"));

// Optional future pages
// const Leaderboard = lazy(() => import("./pages/Leaderboard"));
// const SDGDashboard = lazy(() => import("./pages/SDGDashboard"));
// const ReceiptAnalyzer = lazy(() => import("./pages/ReceiptAnalyzer"));
// const BillAnalyzer = lazy(() => import("./pages/BillAnalyzer"));


// ==============================
// Full Screen Loader
// ==============================

const FullScreenLoader = () => {
  return (
    <div className="flex items-center justify-center min-h-screen bg-slate-50 dark:bg-slate-900">
      <div className="flex flex-col items-center gap-4">
        <div className="h-14 w-14 animate-spin rounded-full border-4 border-slate-300 border-t-green-500"></div>

        <div className="text-center">
          <h2 className="text-lg font-semibold text-slate-700 dark:text-slate-200">
            GreenMind AI
          </h2>

          <p className="text-sm text-slate-500 dark:text-slate-400">
            Loading...
          </p>
        </div>
      </div>
    </div>
  );
};


// ==============================
// Protected Layout
// ==============================

const ProtectedLayout = () => {
  const { user, loading } = useAuth();

  const [sidebarOpen, setSidebarOpen] = useState(false);

  if (loading) {
    return <FullScreenLoader />;
  }

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-900">
      {/* Navbar */}
      <Navbar
        toggleSidebar={() =>
          setSidebarOpen((prev) => !prev)
        }
      />

      {/* Sidebar */}
      <Sidebar
        isOpen={sidebarOpen}
        closeSidebar={() => setSidebarOpen(false)}
      />

      {/* Main Content */}
      <main className="md:ml-64 p-6 pt-4 min-h-[calc(100vh-64px)]">
        <Suspense fallback={<FullScreenLoader />}>
          <Outlet />
        </Suspense>
      </main>
    </div>
  );
};


// ==============================
// Public Routes
// ==============================

const PublicRoute = () => {
  const { user, loading } = useAuth();

  if (loading) {
    return <FullScreenLoader />;
  }

  if (user) {
    return <Navigate to="/" replace />;
  }

  return <Outlet />;
};


// ==============================
// Not Found Page
// ==============================

const NotFound = () => {
  return (
    <div className="flex flex-col items-center justify-center min-h-screen px-4">
      <h1 className="text-6xl font-bold text-green-600">
        404
      </h1>

      <h2 className="mt-4 text-2xl font-semibold">
        Page Not Found
      </h2>

      <p className="mt-2 text-slate-500 text-center">
        The page you are looking for does not exist.
      </p>

      <button
        onClick={() => (window.location.href = "/")}
        className="mt-6 rounded-lg bg-green-600 px-5 py-2 text-white hover:bg-green-700 transition"
      >
        Go Home
      </button>
    </div>
  );
};


// ==============================
// Root App Component
// ==============================

function App() {
  return (
    <BrowserRouter>
      <ThemeProvider>
        <AuthProvider>
          <Suspense fallback={<FullScreenLoader />}>
            <Routes>

              {/* =========================
                  Public Routes
              ========================= */}

              <Route element={<PublicRoute />}>
                <Route
                  path="/login"
                  element={<Login />}
                />

                <Route
                  path="/register"
                  element={<Register />}
                />
              </Route>


              {/* =========================
                  Protected Routes
              ========================= */}

              <Route element={<ProtectedLayout />}>
                <Route
                  path="/"
                  element={<Dashboard />}
                />

                <Route
                  path="/calculator"
                  element={<Calculator />}
                />

                <Route
                  path="/coach"
                  element={<Coach />}
                />

                <Route
                  path="/chat"
                  element={<Chat />}
                />

                <Route
                  path="/simulator"
                  element={<Simulators />}
                />

                <Route
                  path="/challenges"
                  element={<Challenges />}
                />

                <Route
                  path="/reports"
                  element={<Reports />}
                />

                {/* Future Features */}

                {/*
                <Route
                  path="/leaderboard"
                  element={<Leaderboard />}
                />

                <Route
                  path="/sdg-dashboard"
                  element={<SDGDashboard />}
                />

                <Route
                  path="/receipt-analyzer"
                  element={<ReceiptAnalyzer />}
                />

                <Route
                  path="/bill-analyzer"
                  element={<BillAnalyzer />}
                />
                */}
              </Route>


              {/* =========================
                  404 Page
              ========================= */}

              <Route
                path="*"
                element={<NotFound />}
              />

            </Routes>
          </Suspense>
        </AuthProvider>
      </ThemeProvider>
    </BrowserRouter>
  );
}

export default App;