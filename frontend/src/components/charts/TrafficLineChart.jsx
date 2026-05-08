import React, { useState, useEffect, useRef } from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';

export const TrafficLineChart = ({ websocketUrl }) => {
  const [data, setData] = useState(Array.from({ length: 60 }, (_, i) => ({ time: '', count: 0 })));
  const [isConnected, setIsConnected] = useState(false);
  const wsRef = useRef(null);

  useEffect(() => {
    if (!websocketUrl) return;

    const connectWebSocket = () => {
      const ws = new WebSocket(websocketUrl);
      wsRef.current = ws;

      ws.onopen = () => {
        setIsConnected(true);
      };

      ws.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data);
          const count = message.analytics?.total_people || 0;
          const timestamp = new Date().toLocaleTimeString(); // Update to actual local time or use message.timestamp

          setData((prevData) => {
            const newData = [...prevData.slice(1), { time: timestamp, count }];
            return newData;
          });
        } catch (error) {
          console.error("Error parsing websocket message:", error);
        }
      };

      ws.onclose = () => {
        setIsConnected(false);
      };

      ws.onerror = () => {
        setIsConnected(false);
      };
    };

    connectWebSocket();

    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [websocketUrl]);

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
          <p className="text-gray-400 text-xs mb-1">{label}</p>
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 rounded-full bg-blue-400" />
            <span className="text-gray-300 text-sm">People Count:</span>
            <span className="text-white font-bold">{payload[0].value}</span>
          </div>
        </div>
      );
    }
    return null;
  };

  const CustomDot = (props) => {
    const { cx, cy, index, dataLength } = props;
    if (index === dataLength - 1 && isConnected) {
      return (
        <g>
          <circle cx={cx} cy={cy} r={6} fill="#a855f7" className="animate-pulse" opacity={0.5} />
          <circle cx={cx} cy={cy} r={3} fill="#fff" />
        </g>
      );
    }
    return null;
  };

  return (
    <div 
      className="w-full p-4 relative"
      style={{ 
        backgroundColor: '#12121a', 
        borderRadius: '16px', 
        border: '1px solid rgba(255, 255, 255, 0.06)' 
      }}
    >
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-sm font-semibold text-gray-300">Live Traffic</h3>
        <div className="flex items-center gap-2">
          {isConnected ? (
            <span className="flex items-center gap-2 px-2 py-1 rounded-md bg-green-500/10 border border-green-500/20 text-green-400 text-xs font-medium">
              <span className="relative flex h-2 w-2">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2 w-2 bg-green-500"></span>
              </span>
              LIVE
            </span>
          ) : (
            <span className="flex items-center gap-2 px-2 py-1 rounded-md bg-gray-500/10 border border-gray-500/20 text-gray-400 text-xs font-medium">
              <span className="relative inline-flex rounded-full h-2 w-2 bg-gray-500"></span>
              DISCONNECTED
            </span>
          )}
        </div>
      </div>

      <div style={{ opacity: isConnected ? 1 : 0.5, transition: 'opacity 0.3s' }}>
        <ResponsiveContainer width="100%" height={250}>
          <LineChart
            data={data}
            margin={{ top: 5, right: 20, left: -20, bottom: 0 }}
          >
            <defs>
              <linearGradient id="colorCount" x1="0" y1="0" x2="1" y2="0">
                <stop offset="0%" stopColor="#3b82f6" />
                <stop offset="100%" stopColor="#a855f7" />
              </linearGradient>
            </defs>
            <CartesianGrid 
              strokeDasharray="3 3" 
              stroke="rgba(255, 255, 255, 0.05)" 
              vertical={false} 
            />
            <XAxis 
              dataKey="time" 
              stroke="#9ca3af" 
              tick={{ fill: '#9ca3af', fontSize: 10 }} 
              axisLine={false} 
              tickLine={false} 
              minTickGap={30}
            />
            <YAxis 
              stroke="#9ca3af" 
              tick={{ fill: '#9ca3af', fontSize: 10 }} 
              axisLine={false} 
              tickLine={false} 
              allowDecimals={false}
            />
            <Tooltip 
              content={<CustomTooltip />}
              cursor={{ stroke: 'rgba(255,255,255,0.1)', strokeWidth: 1 }}
            />
            <Line 
              type="monotone" 
              dataKey="count" 
              stroke="url(#colorCount)" 
              strokeWidth={3}
              dot={<CustomDot dataLength={data.length} />}
              activeDot={{ r: 4, fill: '#fff', stroke: '#a855f7', strokeWidth: 2 }}
              isAnimationActive={false} // Disable Recharts default animation to allow smooth sliding
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};
