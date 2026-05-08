import React, { useState } from 'react';
import { useLocation } from 'react-router-dom';
import { Search, Bell, Moon, Sun, Home, ChevronRight } from 'lucide-react';

export const TopBar = () => {
  const location = useLocation();
  const [isDark, setIsDark] = useState(true);

  // Derive page name from URL path
  const pathParts = location.pathname.split('/').filter(Boolean);
  const pageName = pathParts.length > 0 
    ? pathParts[0].charAt(0).toUpperCase() + pathParts[0].slice(1) 
    : 'Overview';

  return (
    <header className="sticky top-0 z-50 h-[56px] w-full bg-[#080810]/80 backdrop-blur-md border-b border-white/5 flex items-center justify-between px-6 shadow-sm">
      
      {/* Left: Breadcrumbs */}
      <div className="flex items-center flex-1">
        <div className="flex items-center text-sm font-medium text-gray-400">
          <Home size={16} className="text-gray-500 mr-2" />
          <span className="hover:text-gray-300 cursor-pointer transition-colors">Home</span>
          <ChevronRight size={14} className="mx-2 text-gray-600" />
          <span className="text-gray-100 shadow-sm">{pageName}</span>
        </div>
      </div>

      {/* Center: Search Bar */}
      <div className="flex-1 max-w-xl mx-4">
        <div className="relative group">
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <Search size={16} className="text-gray-500 group-focus-within:text-purple-400 transition-colors" />
          </div>
          <input
            type="text"
            placeholder="Search analytics..."
            className="w-full bg-[#161622] text-sm text-gray-200 placeholder-gray-500 rounded-full py-1.5 pl-10 pr-4 border border-white/5 focus:outline-none focus:border-purple-500/30 focus:bg-[#1a1a27] focus:ring-1 focus:ring-purple-500/20 transition-all shadow-inner"
          />
        </div>
      </div>

      {/* Right: Actions */}
      <div className="flex items-center justify-end flex-1 gap-3">
        {/* Dark/Light Mode Toggle */}
        <button 
          onClick={() => setIsDark(!isDark)}
          className="p-2 rounded-full text-gray-400 hover:text-white hover:bg-white/5 transition-colors"
          aria-label="Toggle theme"
        >
          {isDark ? <Sun size={18} /> : <Moon size={18} />}
        </button>

        {/* Notifications */}
        <button 
          className="relative p-2 rounded-full text-gray-400 hover:text-white hover:bg-white/5 transition-colors group"
          aria-label="Notifications"
        >
          <Bell size={18} className="group-hover:text-gray-200 transition-colors" />
          
          {/* Animated Notification Pulse Dot */}
          <span className="absolute top-2 right-2 flex h-2 w-2">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-red-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2 w-2 bg-red-500 border border-[#080810]"></span>
          </span>
        </button>

        {/* Profile Avatar */}
        <div className="ml-2 pl-4 border-l border-white/10">
          <button className="flex items-center justify-center w-8 h-8 rounded-full bg-gradient-to-br from-blue-500 to-blue-700 text-white text-xs font-bold shadow-[0_0_10px_rgba(59,130,246,0.3)] hover:scale-105 hover:shadow-[0_0_15px_rgba(59,130,246,0.5)] transition-all border border-blue-400/20">
            RE
          </button>
        </div>
      </div>

    </header>
  );
};