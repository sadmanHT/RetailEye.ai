import React, { useState } from 'react';
import { Users, Clock, AlertTriangle, Eye, X } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

const iconMap = {
  queue: Users,
  dwell: Clock,
  crowd: AlertTriangle,
  anomaly: Eye,
};

const severityStyles = {
  high: 'border-l-red-500 bg-red-500/5 shadow-[0_0_15px_rgba(239,68,68,0.1)]',
  medium: 'border-l-amber-500 bg-amber-500/5 shadow-[0_0_15px_rgba(245,158,11,0.1)]',
  low: 'border-l-blue-500 bg-blue-500/5 shadow-[0_0_15px_rgba(59,130,246,0.1)]',
};

const iconColors = {
  high: 'text-red-400',
  medium: 'text-amber-400',
  low: 'text-blue-400',
};

const AlertCard = ({ id, type, message, timestamp, severity, zone, onDismiss }) => {
  const Icon = iconMap[type] || Eye;

  return (
    <motion.div
      initial={{ opacity: 0, x: 50 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: 50, scale: 0.95 }}
      transition={{ duration: 0.3, ease: "easeOut" }}
      className={`relative mb-3 flex items-start gap-4 p-4 border-l-4 rounded-r-lg border border-gray-800/50 backdrop-blur-sm ${severityStyles[severity]}`}
    >
      <div className={`mt-0.5 ${iconColors[severity]}`}>
        <Icon size={20} />
      </div>
      
      <div className="flex-1 min-w-0">
        <div className="flex justify-between items-start mb-1">
          <div className="flex items-center gap-2">
            <span className="text-sm font-medium text-gray-200 capitalize">{type} Alert</span>
            {zone && (
              <span className="text-[10px] px-2 py-0.5 bg-gray-800 text-gray-400 rounded-full border border-gray-700">
                {zone}
              </span>
            )}
          </div>
          <span className="text-xs text-gray-500">{timestamp}</span>
        </div>
        <p className="text-sm text-gray-400 leading-relaxed">{message}</p>
      </div>

      <button 
        onClick={() => onDismiss(id)}
        className="absolute top-2 right-2 p-1 rounded-md text-gray-500 hover:text-gray-300 hover:bg-gray-800/50 transition-colors"
      >
        <X size={14} />
      </button>
    </motion.div>
  );
};

export default AlertCard;
