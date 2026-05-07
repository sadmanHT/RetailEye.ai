import React, { useState, useEffect } from 'react';
import { NavLink } from 'react-router-dom';
import { Camera, LayoutDashboard, Upload, BarChart3, Settings } from 'lucide-react';
import { getHealth } from '../../services/api.js';
import { cn } from '../../utils/formatters.js';

export const Sidebar = () => {
  const [isApiConnected, setIsApiConnected] = useState(false);

  useEffect(() => {
    let intervalId;
    const checkStatus = async () => {
      try {
        await getHealth();
        setIsApiConnected(true);
      } catch (err) {
        setIsApiConnected(false);
      }
    };

    checkStatus();
    // Re-check api health every 30 seconds
    intervalId = setInterval(checkStatus, 30000);

    return () => {
      clearInterval(intervalId);
    };
  }, []);

  const navItems = [
    { name: 'Dashboard', path: '/', icon: LayoutDashboard },
    { name: 'Upload', path: '/upload', icon: Upload },
    { name: 'Analytics', path: '/analytics', icon: BarChart3 },
    { name: 'Settings', path: '/settings', icon: Settings },
  ];

  return (
    <aside 
      className="fixed top-0 left-0 h-full flex flex-col z-50 text-gray-300 transition-all duration-300"
      style={{
        width: '240px',
        backgroundColor: '#0d0d14',
        borderRight: '1px solid rgba(255, 255, 255, 0.06)'
      }}
    >
      <div className="flex flex-shrink-0 items-center h-20 px-6 gap-3 mb-6">
        <div className="p-2 bg-gradient-to-br from-blue-500/20 to-purple-500/20 rounded-xl border border-white/5">
          <Camera className="text-blue-400" size={24} />
        </div>
        <span className="text-lg font-bold text-white tracking-tight">
          RetailEye <span className="bg-gradient-to-r from-blue-400 to-blue-600 bg-clip-text text-transparent">AI</span>
        </span>
      </div>

      <nav className="flex-1 px-4 space-y-1">
        {navItems.map((item) => (
          <NavLink
            key={item.name}
            to={item.path}
            className={({ isActive }) => cn(
              "flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium transition-all duration-200 relative overflow-hidden group",
              isActive 
                ? "text-white bg-white/[0.04]" 
                : "text-gray-400 hover:text-gray-200 hover:bg-white/[0.02]"
            )}
          >
            {({ isActive }) => (
              <>
                {isActive && (
                  <div className="absolute left-0 top-0 bottom-0 w-1 bg-blue-500 rounded-r-md"></div>
                )}
                <item.icon 
                  size={20} 
                  strokeWidth={isActive ? 2.5 : 2}
                  className={cn(
                    "transition-colors duration-200", 
                    isActive ? "text-blue-400" : "group-hover:text-gray-300"
                  )} 
                />
                <span className="z-10">{item.name}</span>
              </>
            )}
          </NavLink>
        ))}
      </nav>

      <div className="p-6 mt-auto border-t border-white/5">
        <div className="flex flex-col gap-2">
          <span className="text-xs font-semibold text-gray-500 uppercase tracking-wider">System Status</span>
          <div className="flex items-center gap-2.5">
            <div className="relative flex h-2.5 w-2.5">
              {isApiConnected && (
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
              )}
              <span className={cn(
                "relative inline-flex rounded-full h-2.5 w-2.5",
                isApiConnected ? "bg-green-500 shadow-[0_0_8px_rgba(34,197,94,0.5)]" : "bg-red-500 shadow-[0_0_8px_rgba(239,68,68,0.5)]"
              )}></span>
            </div>
            <span className="text-sm font-medium text-gray-300">
              {isApiConnected ? 'API Connected' : 'API Unreachable'}
            </span>
          </div>
        </div>
      </div>
    </aside>
  );
};