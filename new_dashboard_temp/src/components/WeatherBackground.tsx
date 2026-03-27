import React, { useMemo } from 'react';
import { motion } from 'motion/react';

interface WeatherBackgroundProps {
  weatherCode: number;
  isDay: number;
}

export const WeatherBackground: React.FC<WeatherBackgroundProps> = ({ weatherCode, isDay }) => {
  // Map WMO weather codes to general conditions
  const isClear = weatherCode === 0 || weatherCode === 1;
  const isCloudy = weatherCode >= 2 && weatherCode <= 48;
  const isRainy = (weatherCode >= 51 && weatherCode <= 67) || (weatherCode >= 80 && weatherCode <= 82);
  const isSnowy = weatherCode >= 71 && weatherCode <= 77;
  const isStormy = weatherCode >= 95;

  // Determine color palette based on weather and time of day
  let colors = {
    bg: 'from-blue-400 to-blue-200',
    orb1: 'bg-yellow-300',
    orb2: 'bg-blue-300',
    orb3: 'bg-cyan-200',
  };

  if (isDay === 0) {
    // Night time
    if (isClear) {
      colors = { bg: 'from-indigo-950 via-slate-900 to-black', orb1: 'bg-indigo-500', orb2: 'bg-purple-900', orb3: 'bg-blue-900' };
    } else if (isCloudy) {
      colors = { bg: 'from-gray-800 via-slate-800 to-gray-900', orb1: 'bg-gray-600', orb2: 'bg-slate-700', orb3: 'bg-gray-800' };
    } else {
      colors = { bg: 'from-slate-900 via-gray-900 to-black', orb1: 'bg-slate-800', orb2: 'bg-gray-900', orb3: 'bg-blue-900' };
    }
  } else {
    // Day time
    if (isClear) {
      colors = { bg: 'from-sky-400 via-blue-300 to-blue-200', orb1: 'bg-yellow-200', orb2: 'bg-sky-300', orb3: 'bg-blue-100' };
    } else if (isCloudy) {
      colors = { bg: 'from-gray-300 via-slate-300 to-slate-200', orb1: 'bg-gray-100', orb2: 'bg-slate-300', orb3: 'bg-gray-200' };
    } else if (isRainy || isStormy) {
      colors = { bg: 'from-slate-500 via-gray-500 to-gray-400', orb1: 'bg-slate-400', orb2: 'bg-gray-500', orb3: 'bg-slate-600' };
    } else if (isSnowy) {
      colors = { bg: 'from-blue-100 via-slate-100 to-white', orb1: 'bg-white', orb2: 'bg-blue-50', orb3: 'bg-slate-100' };
    }
  }

  // Generate random stars for night
  const stars = useMemo(() => {
    if (isDay !== 0 || !isClear) return [];
    return Array.from({ length: 50 }).map((_, i) => ({
      id: i,
      x: Math.random() * 100,
      y: Math.random() * 100,
      size: Math.random() * 2 + 1,
      duration: Math.random() * 3 + 2,
      delay: Math.random() * 2,
    }));
  }, [isDay, isClear]);

  // Generate clouds
  const clouds = useMemo(() => {
    if (isClear && isDay === 0) return [];
    const count = isCloudy ? 6 : isClear ? 2 : 4;
    return Array.from({ length: count }).map((_, i) => ({
      id: i,
      x: Math.random() * 100,
      y: Math.random() * 40,
      scale: Math.random() * 1.5 + 0.5,
      duration: Math.random() * 40 + 40,
      delay: Math.random() * -40,
      opacity: isDay === 0 ? 0.1 : 0.4,
    }));
  }, [isClear, isCloudy, isDay]);

  return (
    <div className={`fixed inset-0 -z-20 w-full h-full bg-gradient-to-br ${colors.bg} transition-colors duration-1000 overflow-hidden`}>
      {/* Stars for clear night */}
      {isDay === 0 && isClear && stars.map(star => (
        <motion.div
          key={`star-${star.id}`}
          className="absolute rounded-full bg-white"
          style={{
            left: `${star.x}%`,
            top: `${star.y}%`,
            width: star.size,
            height: star.size,
          }}
          animate={{ opacity: [0.2, 1, 0.2] }}
          transition={{ duration: star.duration, repeat: Infinity, delay: star.delay, ease: "easeInOut" }}
        />
      ))}

      {/* Liquid Glass Ambient Orbs */}
      <motion.div
        animate={{
          x: ['-10%', '10%', '-5%', '-10%'],
          y: ['-10%', '5%', '15%', '-10%'],
          scale: [1, 1.2, 0.9, 1],
        }}
        transition={{ duration: 20, repeat: Infinity, ease: 'easeInOut' }}
        className={`absolute top-0 left-0 w-[60vw] h-[60vw] rounded-full blur-[100px] opacity-60 ${colors.orb1}`}
      />
      <motion.div
        animate={{
          x: ['10%', '-10%', '5%', '10%'],
          y: ['10%', '-5%', '-15%', '10%'],
          scale: [1, 0.8, 1.1, 1],
        }}
        transition={{ duration: 25, repeat: Infinity, ease: 'easeInOut' }}
        className={`absolute bottom-0 right-0 w-[70vw] h-[70vw] rounded-full blur-[120px] opacity-50 ${colors.orb2}`}
      />
      <motion.div
        animate={{
          x: ['0%', '20%', '-20%', '0%'],
          y: ['20%', '0%', '20%', '20%'],
          scale: [0.9, 1.1, 1, 0.9],
        }}
        transition={{ duration: 30, repeat: Infinity, ease: 'easeInOut' }}
        className={`absolute top-1/2 left-1/4 w-[50vw] h-[50vw] rounded-full blur-[90px] opacity-40 ${colors.orb3}`}
      />

      {/* Clouds */}
      {clouds.map(cloud => (
        <motion.div
          key={`cloud-${cloud.id}`}
          className="absolute w-64 h-24 bg-white rounded-full blur-3xl"
          style={{
            top: `${cloud.y}%`,
            opacity: cloud.opacity,
            transform: `scale(${cloud.scale})`,
          }}
          animate={{ x: ['-100vw', '100vw'] }}
          transition={{ duration: cloud.duration, repeat: Infinity, delay: cloud.delay, ease: "linear" }}
        />
      ))}

      {/* Weather specific overlays (Rain/Snow) */}
      {(isRainy || isStormy) && (
        <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSI0IiBoZWlnaHQ9IjIwIj48cmVjdCB3aWR0aD0iMSIgaGVpZ2h0PSIxMCIgZmlsbD0icmdiYSgyNTUsMjU1LDI1NSwwLjIpIi8+PC9zdmc+')] opacity-40 animate-[rain_0.4s_linear_infinite]" />
      )}
      {isSnowy && (
        <div className="absolute inset-0 opacity-60 animate-[snow_3s_linear_infinite]" 
             style={{ 
               backgroundImage: "url('data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSI4IiBoZWlnaHQ9IjgiPjxjaXJjbGUgY3g9IjQiIGN5PSI0IiByPSIyIiBmaWxsPSJyZ2JhKDI1NSwyNTUsMjU1LDAuOCkiLz48L3N2Zz4='), url('data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxNiIgaGVpZ2h0PSIxNiI+PGNpcmNsZSBjeD0iOCIgY3k9IjgiIHI9IjMiIGZpbGw9InJnYmEoMjU1LDI1NSwyNTUsMC40KSIvPjwvc3ZnPg==')",
               backgroundSize: "8px 8px, 16px 16px"
             }} 
        />
      )}
      {isStormy && (
        <motion.div 
          className="absolute inset-0 bg-white mix-blend-overlay"
          animate={{ opacity: [0, 0, 0.8, 0, 0, 0.4, 0, 0] }}
          transition={{ duration: 10, repeat: Infinity, times: [0, 0.9, 0.92, 0.94, 0.96, 0.97, 0.98, 1] }}
        />
      )}
      
      {/* Base noise texture for that Apple frosted glass feel */}
      <div className="absolute inset-0 opacity-[0.04] mix-blend-overlay pointer-events-none" 
           style={{ backgroundImage: 'url("data:image/svg+xml,%3Csvg viewBox=\'0 0 256 256\' xmlns=\'http://www.w3.org/2000/svg\'%3E%3Cfilter id=\'n\'%3E%3CfeTurbulence type=\'fractalNoise\' baseFrequency=\'0.9\' numOctaves=\'4\' stitchTiles=\'stitch\'/%3E%3C/filter%3E%3Crect width=\'100%25\' height=\'100%25\' filter=\'url(%23n)\'/%3E%3C/svg%3E")' }} />
    </div>
  );
};
