'use client'

import { motion } from 'framer-motion'

interface WaveformProps {
  isAnimating: boolean
}

export default function Waveform({ isAnimating }: WaveformProps) {
  const bars = 12
  
  return (
    <div className="flex items-center justify-center gap-1 h-16">
      {Array.from({ length: bars }).map((_, i) => (
        <motion.div
          key={i}
          className="w-1 bg-gradient-to-t from-violet-500 to-pink-500 rounded-full"
          animate={
            isAnimating
              ? {
                  scaleY: [0.3, 1, 0.3],
                  opacity: [0.5, 1, 0.5],
                }
              : {
                  scaleY: 0.3,
                  opacity: 0.3,
                }
          }
          transition={{
            duration: 0.8,
            repeat: isAnimating ? Infinity : 0,
            delay: i * 0.05,
            ease: 'easeInOut',
          }}
          style={{
            height: '100%',
            originY: 0.5,
          }}
        />
      ))}
    </div>
  )
}
