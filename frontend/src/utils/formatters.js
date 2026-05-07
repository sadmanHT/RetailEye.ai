import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

/**
 * Formats a duration in seconds to a string like '2m 34s'.
 * @param {number} seconds - The duration in seconds.
 * @returns {string} The formatted duration.
 */
export const formatDuration = (seconds) => {
  if (seconds === null || seconds === undefined || isNaN(seconds)) return '0m 0s';
  const m = Math.floor(seconds / 60);
  const s = Math.floor(seconds % 60);
  if (m === 0) return `${s}s`;
  return `${m}m ${s}s`;
};

/**
 * Formats a number with comma separators.
 * @param {number} num - The number to format.
 * @returns {string} The formatted string.
 */
export const formatCount = (num) => {
  if (num === null || num === undefined || isNaN(num)) return '0';
  return Number(num).toLocaleString('en-US');
};

/**
 * Converts a confidence float (0 to 1) to a percentage string.
 * @param {number} val - The confidence value.
 * @returns {string} The percentage string.
 */
export const formatConfidence = (val) => {
  if (val === null || val === undefined || isNaN(val)) return '0%';
  return `${(val * 100).toFixed(0)}%`;
};

/**
 * Maps a zone name to a specific hex color string.
 * @param {string} zoneName - The name of the zone.
 * @returns {string} The hex color string.
 */
export const getZoneColor = (zoneName) => {
  if (!zoneName) return '#9ca3af'; // Tailwind gray-400
  
  const normalized = zoneName.toLowerCase();
  if (normalized.includes('entrance')) return '#3b82f6'; // Tailwind blue-500
  if (normalized.includes('middle')) return '#a855f7';   // Tailwind purple-500
  if (normalized.includes('checkout')) return '#22c55e'; // Tailwind green-500
  
  return '#9ca3af'; // Default unknown mapped to gray
};

/**
 * Merges multiple class names using clsx and tailwind-merge.
 * @param  {...any} inputs - Class names or conditional class objects.
 * @returns {string} The merged class string.
 */
export function cn(...inputs) {
  return twMerge(clsx(inputs));
}
