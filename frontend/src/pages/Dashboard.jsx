import React from 'react';
import { motion } from 'framer-motion';
import { Users, Clock, MapPin, Timer } from 'lucide-react';
import { MetricCard } from '../components/cards/MetricCard.jsx';
import { ZoneBarChart } from '../components/charts/ZoneBarChart.jsx';
import { useAnalytics } from '../hooks/useAnalytics.js';
import { formatDuration } from '../utils/formatters.js';

export const Dashboard = ({ jobId }) => {
  const { data, isLoading, error } = useAnalytics(jobId);

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
    <div className="w-full max-w-6xl mx-auto p-6 text-white space-y-8">
      <motion.div 
        variants={containerVariants}
        initial="hidden"
        animate="show"
        className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6"
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
        className="pt-4"
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
  );
};
