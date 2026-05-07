import React from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';

const CustomTooltip = ({ active, payload, label }) => {
  if (active && payload && payload.length) {
    return (
      <div 
        className="p-3 rounded-lg shadow-lg border"
        style={{ 
          backgroundColor: '#1a1a24', 
          borderColor: 'rgba(255, 255, 255, 0.1)',
        }}
      >
        <p className="text-gray-300 text-sm font-semibold mb-2">{label}</p>
        {payload.map((entry, index) => (
          <div key={index} className="flex items-center gap-2 text-sm mt-1">
            <div 
              className="w-3 h-3 rounded-sm" 
              style={{ backgroundColor: entry.color }} 
            />
            <span className="text-gray-400 capitalize">{entry.name}:</span>
            <span className="text-white font-medium">{entry.value}</span>
          </div>
        ))}
      </div>
    );
  }
  return null;
};

export const ZoneBarChart = ({ data }) => {
  if (!data || data.length === 0) {
    return (
      <div 
        className="w-full flex items-center justify-center text-gray-500 text-sm"
        style={{ height: 300, backgroundColor: '#12121a', borderRadius: '16px', border: '1px solid rgba(255, 255, 255, 0.06)' }}
      >
        No zone data available
      </div>
    );
  }

  return (
    <div 
      className="w-full p-4"
      style={{ 
        backgroundColor: '#12121a', 
        borderRadius: '16px', 
        border: '1px solid rgba(255, 255, 255, 0.06)' 
      }}
    >
      <ResponsiveContainer width="100%" height={300}>
        <BarChart
          data={data}
          margin={{ top: 10, right: 10, left: -20, bottom: 0 }}
        >
          <CartesianGrid 
            strokeDasharray="3 3" 
            stroke="rgba(255, 255, 255, 0.05)" 
            vertical={false} 
          />
          <XAxis 
            dataKey="zone_name" 
            stroke="#9ca3af" 
            tick={{ fill: '#9ca3af', fontSize: 12 }} 
            axisLine={false} 
            tickLine={false} 
            dy={10}
          />
          <YAxis 
            stroke="#9ca3af" 
            tick={{ fill: '#9ca3af', fontSize: 12 }} 
            axisLine={false} 
            tickLine={false} 
          />
          <Tooltip 
            content={<CustomTooltip />} 
            cursor={{ fill: 'rgba(255, 255, 255, 0.03)' }} 
          />
          <Legend 
            wrapperStyle={{ 
              paddingTop: '20px', 
              fontSize: '12px', 
              color: '#9ca3af' 
            }} 
            iconType="circle"
          />
          <Bar 
            dataKey="current_count" 
            name="Current Count" 
            fill="#3b82f6" 
            radius={[4, 4, 0, 0]} 
            animationDuration={1500}
            animationEasing="ease-out"
          />
          <Bar 
            dataKey="average_dwell_seconds" 
            name="Avg Dwell (s)" 
            fill="#a855f7" 
            radius={[4, 4, 0, 0]} 
            animationDuration={1500}
            animationEasing="ease-out"
          />
          <Bar 
            dataKey="total_visits" 
            name="Total Visits" 
            fill="#22c55e" 
            radius={[4, 4, 0, 0]} 
            animationDuration={1500}
            animationEasing="ease-out"
          />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
};
