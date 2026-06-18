import React from 'react';
import { NavLink } from 'react-router-dom';
import { 
  LayoutDashboard, 
  Calculator, 
  Sparkles, 
  MessageSquare, 
  GitBranch, 
  Trophy, 
  FileText,
  User,
  X
} from 'lucide-react';

export const Sidebar = ({ isOpen, closeSidebar }) => {
  const menuItems = [
    { name: 'Dashboard', path: '/', icon: LayoutDashboard },
    { name: 'Carbon Calculator', path: '/calculator', icon: Calculator },
    { name: 'AI Coach Insights', path: '/coach', icon: Sparkles },
    { name: 'AI Chat Assistant', path: '/chat', icon: MessageSquare },
    { name: 'Lifestyle Simulators', path: '/simulator', icon: GitBranch },
    { name: 'Eco Challenges', path: '/challenges', icon: Trophy },
    { name: 'Weekly AI Reports', path: '/reports', icon: FileText },
  ];

  return (
    <>
      {/* Backdrop for mobile */}
      {isOpen && (
        <div 
          onClick={closeSidebar}
          className="fixed inset-0 z-40 bg-slate-950/20 backdrop-blur-sm md:hidden"
        />
      )}

      <aside className={`
        fixed top-[61px] bottom-0 left-0 z-40 w-64 glass-panel border-r border-slate-200/50 dark:border-slate-800/40 
        transform transition-transform duration-300 ease-in-out md:translate-x-0
        ${isOpen ? 'translate-x-0' : '-translate-x-full'}
      `}>
        <div className="flex justify-between items-center px-6 py-4 md:hidden border-b border-slate-200/50 dark:border-slate-800/40">
          <span className="font-semibold text-slate-700 dark:text-slate-200 text-sm uppercase tracking-wider">Navigation</span>
          <button 
            onClick={closeSidebar}
            className="p-1 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800"
            aria-label="Close menu"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <nav className="p-4 space-y-1.5 overflow-y-auto h-[calc(100vh-120px)] md:h-[calc(100vh-61px)]">
          {menuItems.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              onClick={closeSidebar}
              className={({ isActive }) => `
                flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium transition-all duration-200
                ${isActive 
                  ? 'bg-brand-500 text-white shadow-md shadow-brand-500/20 dark:shadow-brand-500/10' 
                  : 'text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 hover:text-slate-900 dark:hover:text-slate-100'}
              `}
            >
              <item.icon className="w-5 h-5 flex-shrink-0" />
              <span>{item.name}</span>
            </NavLink>
          ))}
        </nav>
      </aside>
    </>
  );
};
export default Sidebar;
