import React, { useState } from 'react';
import { BrowserRouter, Routes, Route, Navigate, Outlet } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import { ThemeProvider } from './context/ThemeContext';
import Navbar from './components/Navbar';
import Sidebar from './components/Sidebar';
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import Calculator from './pages/Calculator';
import Coach from './pages/Coach';
import Chat from './pages/Chat';
import Simulators from './pages/Simulators';
import Challenges from './pages/Challenges';
import Reports from './pages/Reports';

/* ──────────────────────────────────────────────
   Protected Layout – shown only to logged-in users
   ────────────────────────────────────────────── */
const ProtectedLayout = () => {
  const { user, loading } = useAuth();
  const [sidebarOpen, setSidebarOpen] = useState(false);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="flex flex-col items-center gap-4">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-brand-500"></div>
          <p className="text-slate-500 dark:text-slate-400 text-sm font-medium">Loading GreenMind AI...</p>
        </div>
      </div>
    );
  }

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  return (
    <div className="min-h-screen">
      <Navbar toggleSidebar={() => setSidebarOpen((o) => !o)} />
      <Sidebar isOpen={sidebarOpen} closeSidebar={() => setSidebarOpen(false)} />

      <main className="md:ml-64 p-6 pt-4 min-h-[calc(100vh-61px)]">
        <Outlet />
      </main>
    </div>
  );
};

/* ──────────────────────────────────────────────
   Public layout – shown only to guests
   ────────────────────────────────────────────── */
const PublicRoute = () => {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-brand-500"></div>
      </div>
    );
  }

  if (user) {
    return <Navigate to="/" replace />;
  }

  return <Outlet />;
};

/* ──────────────────────────────────────────────
   Root App Component
   ────────────────────────────────────────────── */
function App() {
  return (
    <BrowserRouter>
      <ThemeProvider>
        <AuthProvider>
          <Routes>
            {/* Public auth pages */}
            <Route element={<PublicRoute />}>
              <Route path="/login" element={<Login />} />
              <Route path="/register" element={<Register />} />
            </Route>

            {/* Protected app pages */}
            <Route element={<ProtectedLayout />}>
              <Route path="/" element={<Dashboard />} />
              <Route path="/calculator" element={<Calculator />} />
              <Route path="/coach" element={<Coach />} />
              <Route path="/chat" element={<Chat />} />
              <Route path="/simulator" element={<Simulators />} />
              <Route path="/challenges" element={<Challenges />} />
              <Route path="/reports" element={<Reports />} />
            </Route>

            {/* Fallback */}
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </AuthProvider>
      </ThemeProvider>
    </BrowserRouter>
  );
}

export default App;
