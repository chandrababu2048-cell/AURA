import React, { useMemo } from 'react';
import { motion } from 'framer-motion';

const GalaxyBackground = () => {
  // Generate random stars
  const stars = useMemo(() => {
    return Array.from({ length: 200 }).map((_, i) => ({
      id: i,
      x: Math.random() * 100,
      y: Math.random() * 100,
      size: Math.random() * 2 + 1,
      opacity: Math.random() * 0.5 + 0.3,
      duration: Math.random() * 3 + 2,
    }));
  }, []);

  return (
    <div className="fixed inset-0 z-0 bg-[#050505] overflow-hidden">
      {/* Deep static background gradient */}
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,_var(--color-amber)_0%,_transparent_60%)] opacity-10"></div>
      
      {/* Rotating galaxy core */}
      <motion.div
        animate={{ rotate: 360 }}
        transition={{ duration: 150, repeat: Infinity, ease: "linear" }}
        className="absolute inset-[-50%] flex justify-center items-center"
      >
        <div className="w-[150%] h-[150%] rounded-full opacity-20 bg-[conic-gradient(from_0deg,transparent_0deg,rgba(255,176,0,0.4)_120deg,transparent_240deg)] blur-3xl"></div>
        <div className="absolute w-[80%] h-[80%] rounded-full opacity-30 bg-[conic-gradient(from_180deg,transparent_0deg,rgba(255,176,0,0.5)_120deg,transparent_240deg)] blur-3xl"></div>
      </motion.div>

      {/* Twinkling Stars */}
      <div className="absolute inset-0">
        {stars.map((star) => (
          <motion.div
            key={star.id}
            className="absolute rounded-full bg-amber"
            style={{
              left: `${star.x}%`,
              top: `${star.y}%`,
              width: `${star.size}px`,
              height: `${star.size}px`,
              backgroundColor: '#FFB000',
              boxShadow: '0 0 4px #FFB000',
            }}
            animate={{
              opacity: [star.opacity * 0.5, star.opacity, star.opacity * 0.5],
              scale: [1, 1.2, 1],
            }}
            transition={{
              duration: star.duration,
              repeat: Infinity,
              ease: "easeInOut",
            }}
          />
        ))}
      </div>
    </div>
  );
};

export default GalaxyBackground;
