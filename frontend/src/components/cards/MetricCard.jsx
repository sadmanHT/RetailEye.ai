import React from 'react';
import { motion } from 'framer-motion';
import { ArrowUpRight, ArrowDownRight, Minus } from 'lucide-react';

const COLOR_MAP = {
  blue: { bg: 'rgba(59, 130, 246, 0.15)', text: '#3b82f6' },
  purple: { bg: 'rgba(168, 85, 247, 0.15)', text: '#a855f7' },
  green: { bg: 'rgba(34, 197, 94, 0.15)', text: '#22c55e' },
  red: { bg: 'rgba(239, 68, 68, 0.15)', text: '#ef4444' },
};

export const MetricCard = ({ 
  title, 
  value, 
  subtitle, 
  icon: Icon, 
  trend, 
  color = 'blue' 
}) => {
  const styles = COLOR_MAP[color] || COLOR_MAP.blue;
  const isPositive = trend > 0;
  const isNegative = trend < 0;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, ease: 'easeOut' }}
      style={{
        backgroundColor: '#12121a',
        border: '1px solid rgba(255, 255, 255, 0.06)',
        borderRadius: '16px',
        padding: '24px',
      }}
      className="relative flex flex-col justify-between w-full"
    >
      <div className="flex justify-between items-start mb-4">
        <span className="text-sm font-medium text-gray-400">{title}</span>
        {Icon && (
          <div 
            className="p-2 rounded-lg flex items-center justify-center"
            style={{ backgroundColor: styles.bg, color: styles.text }}
          >
            <Icon size={20} />
          </div>
        )}
      </div>

      <div>
        <div className="flex items-baseline gap-3">
          <span 
            className="font-bold text-white tracking-tight"
            style={{ fontSize: '2rem', lineHeight: '1.2' }}
          >
            {value}
          </span>
          
          {trend !== undefined && trend !== null && (
            <div 
              className={`flex items-center text-xs font-semibold px-2 py-0.5 rounded-full ${
                isPositive ? 'text-green-400 bg-green-400/10' : 
                isNegative ? 'text-red-400 bg-red-400/10' : 
                'text-gray-400 bg-gray-400/10'
              }`}
            >
              {isPositive && <ArrowUpRight size={14} className="mr-0.5" />}
              {isNegative && <ArrowDownRight size={14} className="mr-0.5" />}
              {trend === 0 && <Minus size={14} className="mr-0.5" />}
              <span>{Math.abs(trend)}%</span>
            </div>
          )}
        </div>
        
        {subtitle && (
          <p className="text-sm text-gray-500 mt-1">{subtitle}</p>
        )}
      </div>
    </motion.div>
  );
};
