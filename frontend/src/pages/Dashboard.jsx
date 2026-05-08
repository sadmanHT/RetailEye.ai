import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Users, Clock, MapPin, Timer, Bell } from 'lucide-react';
import { MetricCard } from '../components/cards/MetricCard.jsx';
import { ZoneBarChart } from '../components/charts/ZoneBarChart.jsx';
import AlertCard from '../components/cards/AlertCard.jsx';
import { useAnalytics } from '../hooks/useAnalytics.js';
import { formatDuration } from '../utils/formatters.js';

export const Dashboard = ({ jobId }) => {
  const { data, isLoading, error } = useAnalytics(jobId);
  const [alerts, setAlerts] = useState([]);

  // Generate mock alerts from analytics data
  useEffect(() => {
    if (!data) return;
    
    const generatedAlerts = [];
    const now = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    let idCounter = Date.now();

    const zoneData = data.zone_analytics || [];
    const summary = data.summary_metrics || {};

    zoneData.forEach(zone => {
      // Crowd alert
      if (zone.total_people_entered > 5) {
        generatedAlerts.push({
          id: `alert-crowd-${idCounter++}`,
          type: 'crowd',
          message: `High traffic volume detected in zone.`,
          timestamp: now,
          severity: 'high',
          zone: zone.zone_name
        });
      }
      
      // Dwell alert
      if (zone.average_dwell_time > 120) {
        generatedAlerts.push({
          id: `alert-dwell-${idCounter++}`,
          type: 'dwell',
          message: `Average dwell time exceeded 2 minutes.`,
          timestamp: now,
          severity: 'medium',
          zone: zone.zone_name
        });
      }
    });

    // Queue alert mockup
    if (summary.busiest_zone && summary.busiest_zone.toLowerCase().includes('checkout')) {
         generatedAlerts.push({
          id: `alert-queue-${idCounter++}`,
          type: 'queue',
          message: `Queue formation detected at checkout line.`,
          timestamp: now,
          severity: 'high',
          zone: summary.busiest_zone
        });
    }

    setAlerts(generatedAlerts);
  }, [data]);

  const handleDismissAlert = (id) => {
    setAlerts(prev => prev.filter(a => a.id !== id));
  };

  const clearAllAlerts = () => {
    setAlerts([]);
  };

  if (error) {
    return (
      <div className="p-8 text-center text-red-500">
        <h2 className="text-xl font-bold mb-2">Error Loading Analytics</h2>
        <p>{error}</p>
      </div>
    );
  }

  // Skeleton loading component
  if (isLoading || !data) {
    return (
      <div className="w-full max-w-6xl mx-auto p-6 space-y-8 animate-pulse">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="h-32 bg-[#12121a] rounded-2xl border border-white/5"></div>
          ))}
        </div>
        <div className="h-96 bg-[#12121a] rounded-2xl border border-white/5"></div>
        <div className="h-64 bg-[#12121a] rounded-2xl border border-white/5"></div>
      </div>
    );
  }

  // Derive metrics
  const summary = data.summary_metrics || {};
  const totalPeople = summary.total_unique_people || 0;
  const videoDuration = summary.processed_duration_seconds || 0;
  const busiestZone = summary.busiest_zone || 'None';
  const avgDwellAll = summary.average_dwell_time_all_zones || 0;

  const zoneData = data.zone_analytics || [];
  const tracks = data.tracked_individuals || [];
  
  // Sort tracks by dwell time for Top tracked
  const topTracks = [...tracks]
    .sort((a, b) => Math.max(...Object.values(b.dwell_times || {0:0})) - Math.max(...Object.values(a.dwell_times || {0:0})))
    .slice(0, 10);

  const containerVariants = {
    hidden: { opacity: 0 },
    show: {
      opacity: 1,
      transition: { staggerChildren: 0.1 }
    }
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    show: { opacity: 1, y: 0, transition: { duration: 0.5 } }
  };

  return (
    <div className="flex flex-col lg:flex-row gap-6 w-full max-w-7xl mx-auto p-6 text-white h-full">
      {/* Left Column - 65% Main Content */}
      <div className="flex-[0.65] flex flex-col space-y-8 h-full overflow-y-auto pr-2 custom-scrollbar">
        <motion.div 
          variants={containerVariants}
          initial="hidden"
          animate="show"
          className="grid grid-cols-1 md:grid-cols-2 gap-6"
        >
          <MetricCard
            title="Total People Tracked"
            value={totalPeople}
            icon={Users}
            color="blue"
            trend={5.2} // placeholder trend
          />
          <MetricCard
            title="Video Duration"
            value={formatDuration(videoDuration)}
            icon={Clock}
            color="purple"
          />
          <MetricCard
            title="Busiest Zone"
            value={busiestZone}
            icon={MapPin}
            color="red"
          />
          <MetricCard
            title="Avg Dwell Time"
            value={formatDuration(avgDwellAll)}
            icon={Timer}
            color="green"
          />
        </motion.div>

        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4, duration: 0.5 }}
        >
          <h2 className="text-2xl font-bold mb-4 text-white">Zone Analytics</h2>
          <ZoneBarChart data={zoneData} />
        </motion.div>

        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6, duration: 0.5 }}
          className="pt-4 pb-12"
        >
          <h2 className="text-2xl font-bold mb-4 text-white">Top Tracked Individuals</h2>
          <div className="overflow-x-auto rounded-xl border border-white/5 bg-[#12121a]">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-white/5 text-gray-400 text-sm bg-[#161622]">
                  <th className="p-4 font-medium">Track ID</th>
                  <th className="p-4 font-medium">Time in Frame</th>
                  <th className="p-4 font-medium">Zones Visited</th>
                  <th className="p-4 font-medium">Max Dwell Time</th>
                </tr>
              </thead>
              <tbody className="text-sm">
                {topTracks.map((track, idx) => {
                  const zones = track.zones_visited || [];
                  const maxDwell = Math.max(...Object.values(track.dwell_times || {0:0}));
                  return (
                    <tr 
                      key={track.track_id || idx} 
                      className="border-b border-white/5 hover:bg-white/[0.02] transition-colors"
                    >
                      <td className="p-4 font-medium text-gray-200">#{track.track_id}</td>
                      <td className="p-4 text-gray-400">{formatDuration(track.total_time_in_frame)}</td>
                      <td className="p-4">
                        <div className="flex flex-wrap gap-1">
                          {zones.length > 0 ? zones.map((z, i) => (
                            <span key={i} className="px-2 py-0.5 rounded bg-gray-800 text-xs text-gray-300">
                              {z}
                            </span>
                          )) : <span className="text-gray-500">None</span>}
                        </div>
                      </td>
                      <td className="p-4 text-gray-400">{formatDuration(maxDwell)}</td>
                    </tr>
                  );
                })}
                {topTracks.length === 0 && (
                  <tr>
                    <td colSpan={4} className="p-8 text-center text-gray-500">
                      No individuals tracked
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </motion.div>
      </div>

      {/* Right Column - 35% Live Alerts */}
      <div className="flex-[0.35] flex flex-col h-full max-h-[85vh] border-l border-white/10 pl-6">
        <div className="flex items-center justify-between mb-6 shrink-0">
          <div className="flex items-center gap-3">
            <Bell size={24} className="text-white" />
            <h2 className="text-2xl font-bold text-white">Live Alerts</h2>
            {alerts.length > 0 && (
              <span className="px-2.5 py-0.5 bg-blue-500/20 text-blue-400 rounded-full text-sm font-semibold border border-blue-500/30">
                {alerts.length}
              </span>
            )}
          </div>
          {alerts.length > 0 && (
            <button 
              onClick={clearAllAlerts}
              className="text-sm text-gray-400 hover:text-white transition-colors"
            >
              Clear All
            </button>
          )}
        </div>

        <div className="flex-1 overflow-y-auto pr-2 space-y-1 custom-scrollbar">
          <AnimatePresence>
            {alerts.length > 0 ? (
              alerts.map(alert => (
                <AlertCard
                  key={alert.id}
                  id={alert.id}
                  type={alert.type}
                  message={alert.message}
                  timestamp={alert.timestamp}
                  severity={alert.severity}
                  zone={alert.zone}
                  onDismiss={handleDismissAlert}
                />
              ))
            ) : (
              <motion.div 
                initial={{ opacity: 0 }} 
                animate={{ opacity: 1 }} 
                className="flex flex-col items-center justify-center p-8 text-center text-gray-500 bg-[#12121a] rounded-xl border border-white/5"
              >
                <Bell size={32} className="mb-3 opacity-20" />
                <p>No active alerts right now.</p>
                <span className="text-xs mt-1">Monitoring zones...</span>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>
    </div>
  );
};
