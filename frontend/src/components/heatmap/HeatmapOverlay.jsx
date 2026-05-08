import React, { useRef, useEffect, useState } from 'react';

const HeatmapOverlay = ({ hotspots = [], width = 640, height = 480 }) => {
  const canvasRef = useRef(null);
  const [isVisible, setIsVisible] = useState(true);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');

    // Clear the previous frame
    ctx.clearRect(0, 0, width, height);

    if (!isVisible) return;

    // Use screen blend mode so overlapping hotspots brighten naturally
    ctx.globalCompositeOperation = 'screen';

    hotspots.forEach((spot) => {
      const { x, y, intensity } = spot;
      
      // Radius proportional to intensity
      // Assuming typical range, max radius of say 80px when intensity is 1
      const radius = Math.max(10, intensity * 80);

      // Create a radial gradient from center to edge
      const gradient = ctx.createRadialGradient(x, y, 0, x, y, radius);
      
      // Center color varies by intensity, fading out smoothly
      gradient.addColorStop(0, `rgba(255, 50, 50, ${Math.min(0.8, intensity * 0.6)})`);
      // Add a slight thermal warm ring
      gradient.addColorStop(0.4, `rgba(255, 120, 0, ${Math.min(0.4, intensity * 0.3)})`);
      gradient.addColorStop(1, 'rgba(0, 0, 0, 0)');

      ctx.fillStyle = gradient;
      ctx.beginPath();
      ctx.arc(x, y, radius, 0, 2 * Math.PI);
      ctx.fill();
    });
  }, [hotspots, width, height, isVisible]);

  return (
    <div 
      className="absolute top-0 left-0 w-full h-full overflow-hidden" 
      style={{ pointerEvents: 'none' }}
    >
      <canvas
        ref={canvasRef}
        width={width}
        height={height}
        className="w-full h-full"
        style={{
          opacity: isVisible ? 1 : 0,
          transition: 'opacity 0.5s ease-in-out',
        }}
      />
      
      {/* Toggle Button */}
      <button
        onClick={() => setIsVisible(!isVisible)}
        className="absolute top-4 right-4 bg-[#12121a]/80 text-white px-3 py-1.5 rounded-md text-sm backdrop-blur-md border border-gray-700/50 hover:bg-gray-800 transition-colors flex items-center gap-2"
        style={{ pointerEvents: 'auto' }}
      >
        <div 
          className={`w-2 h-2 rounded-full transition-colors duration-300 ${
            isVisible ? 'bg-red-500 shadow-[0_0_8px_rgba(239,68,68,0.8)]' : 'bg-gray-500'
          }`} 
        />
        Thermal Heatmap
      </button>
    </div>
  );
};

export default HeatmapOverlay;
