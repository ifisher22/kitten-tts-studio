'use client'

import { useState, useRef, useEffect } from 'react'
import { Play, Pause, Download, Volume2 } from 'lucide-react'
import { motion } from 'framer-motion'

interface AudioPlayerProps {
  audioUrl: string
  onDownload: () => void
}

export default function AudioPlayer({ audioUrl, onDownload }: AudioPlayerProps) {
  const [isPlaying, setIsPlaying] = useState(false)
  const [currentTime, setCurrentTime] = useState(0)
  const [duration, setDuration] = useState(0)
  const [volume, setVolume] = useState(1)
  const audioRef = useRef<HTMLAudioElement | null>(null)

  useEffect(() => {
    if (audioRef.current) {
      audioRef.current.src = audioUrl
      audioRef.current.load()
      // Auto-play when new audio is loaded
      audioRef.current.play().then(() => {
        setIsPlaying(true)
      }).catch(() => {
        // Auto-play was blocked, user needs to click play
      })
    }
  }, [audioUrl])

  const togglePlay = () => {
    if (audioRef.current) {
      if (isPlaying) {
        audioRef.current.pause()
      } else {
        audioRef.current.play()
      }
      setIsPlaying(!isPlaying)
    }
  }

  const handleTimeUpdate = () => {
    if (audioRef.current) {
      setCurrentTime(audioRef.current.currentTime)
    }
  }

  const handleLoadedMetadata = () => {
    if (audioRef.current) {
      setDuration(audioRef.current.duration)
    }
  }

  const handleSeek = (e: React.ChangeEvent<HTMLInputElement>) => {
    const time = parseFloat(e.target.value)
    if (audioRef.current) {
      audioRef.current.currentTime = time
      setCurrentTime(time)
    }
  }

  const handleVolumeChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const vol = parseFloat(e.target.value)
    if (audioRef.current) {
      audioRef.current.volume = vol
      setVolume(vol)
    }
  }

  const formatTime = (time: number) => {
    const minutes = Math.floor(time / 60)
    const seconds = Math.floor(time % 60)
    return `${minutes}:${seconds.toString().padStart(2, '0')}`
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="glass rounded-2xl p-6 space-y-4"
    >
      <audio
        ref={audioRef}
        onTimeUpdate={handleTimeUpdate}
        onLoadedMetadata={handleLoadedMetadata}
        onEnded={() => setIsPlaying(false)}
        className="hidden"
      />

      <div className="flex items-center gap-4">
        <button
          onClick={togglePlay}
          className="w-14 h-14 rounded-full bg-gradient-to-r from-violet-500 to-pink-500 flex items-center justify-center hover:opacity-90 transition-opacity"
        >
          {isPlaying ? (
            <Pause className="w-6 h-6 text-white" />
          ) : (
            <Play className="w-6 h-6 text-white ml-1" />
          )}
        </button>

        <div className="flex-1 space-y-2">
          <input
            type="range"
            min={0}
            max={duration || 100}
            value={currentTime}
            onChange={handleSeek}
            className="w-full h-1.5 bg-white/10 rounded-full appearance-none cursor-pointer [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:w-3 [&::-webkit-slider-thumb]:h-3 [&::-webkit-slider-thumb]:rounded-full [&::-webkit-slider-thumb]:bg-gradient-to-r [&::-webkit-slider-thumb]:from-violet-500 [&::-webkit-slider-thumb]:to-pink-500"
          />
          <div className="flex justify-between text-xs text-zinc-400">
            <span>{formatTime(currentTime)}</span>
            <span>{formatTime(duration)}</span>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <Volume2 className="w-4 h-4 text-zinc-400" />
          <input
            type="range"
            min={0}
            max={1}
            step={0.1}
            value={volume}
            onChange={handleVolumeChange}
            className="w-20 h-1 bg-white/10 rounded-full appearance-none cursor-pointer [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:w-2.5 [&::-webkit-slider-thumb]:h-2.5 [&::-webkit-slider-thumb]:rounded-full [&::-webkit-slider-thumb]:bg-white/50"
          />
        </div>

        <button
          onClick={onDownload}
          className="p-2 rounded-lg bg-white/5 hover:bg-white/10 transition-colors"
          title="Download audio"
        >
          <Download className="w-5 h-5 text-zinc-300" />
        </button>
      </div>
    </motion.div>
  )
}
