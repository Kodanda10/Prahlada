import React from 'react';
import { motion } from 'framer-motion';

interface PlasmaStreamProps {
  fromStatus: 'idle' | 'active' | 'completed';
  toStatus: 'idle' | 'active' | 'completed';
  isActive: boolean;
  isVertical?: boolean; // New prop for vertical layout
}

/**
 * Liquid Light Connection - Electric Stream between nodes
 * तरल प्रकाश धारा - नोड्स के बीच जीवित ऊर्जा
 */
export const PlasmaStream: React.FC<PlasmaStreamProps> = ({ fromStatus, toStatus, isActive, isVertical = false }) => {
  // Generate organic, turbulent path
  const generateTurbulentPath = () => {
    const points = [];
    const numPoints = 20;

    for (let i = 0; i <= numPoints; i++) {
      const t = i / numPoints;

      if (isVertical) {
        // Vertical path (top to bottom)
        const y = t * 100;
        const turbulence = Math.sin(t * Math.PI * 3) * 5 + Math.cos(t * Math.PI * 5) * 3;
        const x = 50 + turbulence;
        points.push(`${x},${y}`);
      } else {
        // Horizontal path (left to right)
        const x = t * 100;
        const turbulence = Math.sin(t * Math.PI * 3) * 3 + Math.cos(t * Math.PI * 5) * 2;
        const y = 50 + turbulence;
        points.push(`${x},${y}`);
      }
    }

    return `M ${points.join(' L ')}`;
  };

  const streamColors = {
    idle: {
      primary: 'rgba(139, 245, 230, 0.2)',
      glow: 'rgba(139, 245, 230, 0.4)',
      trail: 'rgba(139, 245, 230, 0.6)',
    },
    active: {
      primary: 'rgba(255, 191, 0, 0.6)',
      glow: 'rgba(255, 191, 0, 0.9)',
      trail: 'rgba(255, 140, 0, 1)',
    },
  };

  const colors = isActive ? streamColors.active : streamColors.idle;

  return (
    <div className={`relative ${isVertical ? 'w-32 h-full' : 'flex-1 h-32 mx-4'}`}>
      <svg
        className="absolute inset-0 w-full h-full"
        viewBox="0 0 100 100"
        preserveAspectRatio="none"
        style={{ overflow: 'visible' }}
      >
        <defs>
          {/* Turbulence filter for organic look */}
          <filter id="turbulence">
            <feTurbulence
              type="fractalNoise"
              baseFrequency="0.02 0.05"
              numOctaves="3"
              seed="2"
              stitchTiles="stitch"
            >
              <animate
                attributeName="baseFrequency"
                values="0.02 0.05; 0.03 0.06; 0.02 0.05"
                dur="8s"
                repeatCount="indefinite"
              />
            </feTurbulence>
            <feDisplacementMap in="SourceGraphic" scale="3" />
          </filter>

          {/* Glow effect */}
          <filter id="glow">
            <feGaussianBlur stdDeviation="3" result="coloredBlur" />
            <feMerge>
              <feMergeNode in="coloredBlur" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>

          {/* Gradient for the stream */}
          <linearGradient id="streamGradient" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor={colors.primary} stopOpacity="0.3" />
            <stop offset="50%" stopColor={colors.glow} stopOpacity="0.8" />
            <stop offset="100%" stopColor={colors.primary} stopOpacity="0.3" />
          </linearGradient>
        </defs>

        {/* Base stream path with turbulence */}
        <motion.path
          d={generateTurbulentPath()}
          fill="none"
          stroke="url(#streamGradient)"
          strokeWidth="2"
          filter="url(#turbulence)"
          initial={{ pathLength: 0, opacity: 0 }}
          animate={{
            pathLength: isActive ? 1 : 0.3,
            opacity: isActive ? 1 : 0.4,
          }}
          transition={{
            pathLength: { duration: 2, ease: 'easeInOut' },
            opacity: { duration: 1 },
          }}
        />

        {/* Glowing core */}
        {isActive && (
          <motion.path
            d={generateTurbulentPath()}
            fill="none"
            stroke={colors.trail}
            strokeWidth="1"
            filter="url(#glow)"
            initial={{ pathLength: 0 }}
            animate={{ pathLength: 1 }}
            transition={{ duration: 2, ease: 'easeInOut' }}
          />
        )}

        {/* Energy particles (comets) flowing through */}
        {isActive &&
          [...Array(3)].map((_, i) => (
            <motion.circle
              key={i}
              r="2"
              fill={colors.trail}
              filter="url(#glow)"
              initial={{ offsetDistance: '0%' }}
              animate={{ offsetDistance: '100%' }}
              transition={{
                duration: 2,
                repeat: Infinity,
                delay: i * 0.6,
                ease: 'linear',
              }}
              style={{
                offsetPath: `path('${generateTurbulentPath()}')`,
              }}
            >
              {/* Comet tail */}
              <animate
                attributeName="opacity"
                values="0;1;1;0"
                dur="2s"
                repeatCount="indefinite"
                begin={`${i * 0.6}s`}
              />
            </motion.circle>
          ))}
      </svg>

      {/* Comet trails (separate elements for better control) */}
      {isActive &&
        [...Array(3)].map((_, i) => (
          <motion.div
            key={`trail-${i}`}
            className="absolute top-1/2 left-0 w-12 h-1"
            style={{
              background: `linear-gradient(to right, transparent, ${colors.trail})`,
              filter: 'blur(4px)',
              transformOrigin: 'left center',
            }}
            initial={{ x: '0%', scaleX: 0, opacity: 0 }}
            animate={{
              x: '100%',
              scaleX: [0, 1, 0.5, 0],
              opacity: [0, 1, 0.8, 0],
            }}
            transition={{
              duration: 2,
              repeat: Infinity,
              delay: i * 0.6,
              ease: 'linear',
            }}
          />
        ))}

      {/* Pulsing energy nodes along the stream */}
      {isActive && (
        <>
          {[25, 50, 75].map((position, i) => (
            <motion.div
              key={`node-${i}`}
              className="absolute top-1/2 rounded-full"
              style={{
                left: `${position}%`,
                width: '4px',
                height: '4px',
                background: colors.trail,
                boxShadow: `0 0 10px ${colors.glow}, 0 0 20px ${colors.glow}`,
                transform: 'translate(-50%, -50%)',
              }}
              animate={{
                scale: [1, 1.5, 1],
                opacity: [0.6, 1, 0.6],
              }}
              transition={{
                duration: 2,
                repeat: Infinity,
                delay: i * 0.3,
                ease: 'easeInOut',
              }}
            />
          ))}
        </>
      )}
    </div>
  );
};
