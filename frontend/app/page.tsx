'use client'

import { useState, useEffect, useCallback } from 'react'
import { motion } from 'framer-motion'
import { Mic, Sparkles, AlertCircle, CheckCircle2 } from 'lucide-react'
import Waveform from '@/components/Waveform'
import AudioPlayer from '@/components/AudioPlayer'
import type { VoiceInfo, HealthResponse, ModelInfo } from '@/types'

const MAX_CHARS = 5000

export default function Home() {
  const [text, setText] = useState('')
  const [voice, setVoice] = useState('Jasper')
  const [model, setModel] = useState<'kitten-tts-mini-0.8' | 'kitten-tts-nano-0.2'>('kitten-tts-mini-0.8')
  const [speed, setSpeed] = useState(1.0)
  const [isGenerating, setIsGenerating] = useState(false)
  const [audioUrl, setAudioUrl] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [voices, setVoices] = useState<VoiceInfo[]>([])
  const [models, setModels] = useState<ModelInfo[]>([])
  const [health, setHealth] = useState<HealthResponse | null>(null)

  // Fetch available voices/models and health status on mount
  useEffect(() => {
    fetchHealth()
    fetchModels()
  }, [])

  useEffect(() => {
    fetchVoices(model)
  }, [model])

  const fetchHealth = async () => {
    try {
      const response = await fetch('/api/health')
      if (response.ok) {
        const data = await response.json()
        setHealth(data)
      }
    } catch (err) {
      console.error('Health check failed:', err)
    }
  }

  const fetchVoices = async (selectedModel?: 'kitten-tts-mini-0.8' | 'kitten-tts-nano-0.2') => {
    try {
      const query = selectedModel ? `?model=${encodeURIComponent(selectedModel)}` : ''
      const response = await fetch(`/api/tts/voices${query}`)
      if (response.ok) {
        const data = await response.json()
        setVoices(data.voices)
        if (data.voices?.length > 0 && !data.voices.some((v: VoiceInfo) => v.name === voice)) {
          setVoice(data.voices[0].name)
        }
      }
    } catch (err) {
      console.error('Failed to fetch voices:', err)
      // Fallback voices
      setVoices([
        { name: 'Bella', alias: 'expr-voice-2-f', gender: 'female' },
        { name: 'Jasper', alias: 'expr-voice-2-m', gender: 'male' },
        { name: 'Luna', alias: 'expr-voice-3-f', gender: 'female' },
        { name: 'Bruno', alias: 'expr-voice-3-m', gender: 'male' },
        { name: 'Rosie', alias: 'expr-voice-4-f', gender: 'female' },
        { name: 'Hugo', alias: 'expr-voice-4-m', gender: 'male' },
        { name: 'Kiki', alias: 'expr-voice-5-f', gender: 'female' },
        { name: 'Leo', alias: 'expr-voice-5-m', gender: 'male' },
      ])
    }
  }

  const fetchModels = async () => {
    try {
      const response = await fetch('/api/tts/models')
      if (response.ok) {
        const data = await response.json()
        setModels(data.models)
        if (data.active_model) {
          setModel(data.active_model)
        }
      }
    } catch (err) {
      console.error('Failed to fetch models:', err)
      setModels([
        { key: 'kitten-tts-mini-0.8', label: 'Kitten TTS Mini 0.8', loaded: true },
        { key: 'kitten-tts-nano-0.2', label: 'Kitten TTS Nano 0.2', loaded: false },
      ])
    }
  }

  const handleGenerate = useCallback(async () => {
    if (!text.trim()) {
      setError('Please enter some text')
      return
    }

    if (text.length > MAX_CHARS) {
      setError(`Text exceeds maximum length of ${MAX_CHARS} characters`)
      return
    }

    setIsGenerating(true)
    setError(null)
    setAudioUrl(null)

    try {
      const response = await fetch('/api/tts/stream', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          text: text.trim(),
          voice,
          speed,
          model,
        }),
      })

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        throw new Error(errorData.detail || 'Failed to generate speech')
      }

      // Get audio blob from response
      const blob = await response.blob()
      const url = URL.createObjectURL(blob)
      setAudioUrl(url)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to generate speech')
    } finally {
      setIsGenerating(false)
    }
  }, [text, voice, speed, model])

  const handleDownload = useCallback(() => {
    if (audioUrl) {
      const a = document.createElement('a')
      a.href = audioUrl
      a.download = `kitten-tts-${Date.now()}.wav`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
    }
  }, [audioUrl])

  const femaleVoices = voices.filter(v => v.gender === 'female')
  const maleVoices = voices.filter(v => v.gender === 'male')

  return (
    <main className="min-h-screen relative overflow-hidden">
      {/* Background gradient */}
      <div className="absolute inset-0 bg-gradient-glow pointer-events-none" />

      {/* Floating orbs */}
      <div className="absolute top-20 left-10 w-72 h-72 bg-violet-500/20 rounded-full blur-[100px] animate-float" />
      <div className="absolute bottom-20 right-10 w-96 h-96 bg-pink-500/10 rounded-full blur-[120px] animate-float" style={{ animationDelay: '-3s' }} />

      <div className="relative z-10 max-w-4xl mx-auto px-4 py-12 sm:px-6 lg:px-8">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-12"
        >
          <div className="flex items-center justify-center gap-3 mb-4">
            <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-violet-500 to-pink-500 flex items-center justify-center">
              <Mic className="w-6 h-6 text-white" />
            </div>
            <h1 className="text-4xl sm:text-5xl font-bold gradient-text">
              Kitten TTS
            </h1>
          </div>
          <p className="text-zinc-400 text-lg max-w-2xl mx-auto">
            AI-powered text-to-speech with natural, human-like voices.
            <br />
            <span className="text-sm">Powered by local Kitten TTS models (Mini + Nano)</span>
          </p>

          {/* Health status */}
          {health && (
            <div className="mt-4 flex items-center justify-center gap-2">
              {health.model_loaded ? (
                <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-green-500/10 text-green-400 text-sm">
                  <CheckCircle2 className="w-4 h-4" />
                  Model Ready
                </span>
              ) : (
                <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-yellow-500/10 text-yellow-400 text-sm">
                  <AlertCircle className="w-4 h-4" />
                  Loading Model...
                </span>
              )}
            </div>
          )}
        </motion.div>

        {/* Main Card */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="glass rounded-3xl p-6 sm:p-8 space-y-6"
        >
          {/* Text Input */}
          <div className="space-y-2">
            <label className="text-sm font-medium text-zinc-300 flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-violet-400" />
              Enter your text
            </label>
            <textarea
              value={text}
              onChange={(e) => setText(e.target.value)}
              placeholder="Type or paste the text you want to convert to speech..."
              className="w-full h-40 p-4 rounded-xl bg-white/5 border border-white/10 text-zinc-100 placeholder:text-zinc-500 resize-none focus:ring-2 focus:ring-violet-500/50 focus:border-transparent transition-all"
              disabled={isGenerating}
            />
            <div className="flex justify-between text-xs text-zinc-500">
              <span>{text.length} / {MAX_CHARS} characters</span>
              <span className={text.length > MAX_CHARS ? 'text-red-400' : ''}>
                {text.length > MAX_CHARS ? 'Too long!' : `${MAX_CHARS - text.length} remaining`}
              </span>
            </div>
          </div>

          {/* Model + Voice + Speed Selection */}
          <div className="grid lg:grid-cols-3 gap-4">
            <div className="space-y-2">
              <label className="text-sm font-medium text-zinc-300">Model</label>
              <select
                value={model}
                onChange={(e) => setModel(e.target.value as 'kitten-tts-mini-0.8' | 'kitten-tts-nano-0.2')}
                className="w-full p-3 rounded-xl bg-white/5 border border-white/10 text-zinc-100 focus:ring-2 focus:ring-violet-500/50 transition-all"
                disabled={isGenerating}
              >
                {models.map(m => (
                  <option key={m.key} value={m.key}>{m.label}</option>
                ))}
              </select>
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium text-zinc-300">Voice</label>
              <select
                value={voice}
                onChange={(e) => setVoice(e.target.value)}
                className="w-full p-3 rounded-xl bg-white/5 border border-white/10 text-zinc-100 focus:ring-2 focus:ring-violet-500/50 transition-all"
                disabled={isGenerating}
              >
                {femaleVoices.length > 0 && (
                  <optgroup label="Female Voices">
                    {femaleVoices.map(v => (
                      <option key={v.name} value={v.name}>{v.name}</option>
                    ))}
                  </optgroup>
                )}
                {maleVoices.length > 0 && (
                  <optgroup label="Male Voices">
                    {maleVoices.map(v => (
                      <option key={v.name} value={v.name}>{v.name}</option>
                    ))}
                  </optgroup>
                )}
              </select>
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium text-zinc-300">
                Speed: {speed.toFixed(1)}x
              </label>
              <input
                type="range"
                min={0.5}
                max={2.0}
                step={0.1}
                value={speed}
                onChange={(e) => setSpeed(parseFloat(e.target.value))}
                className="w-full h-2 bg-white/10 rounded-full appearance-none cursor-pointer [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:w-4 [&::-webkit-slider-thumb]:h-4 [&::-webkit-slider-thumb]:rounded-full [&::-webkit-slider-thumb]:bg-gradient-to-r [&::-webkit-slider-thumb]:from-violet-500 [&::-webkit-slider-thumb]:to-pink-500"
                disabled={isGenerating}
              />
              <div className="flex justify-between text-xs text-zinc-500">
                <span>Slow (0.5x)</span>
                <span>Normal (1.0x)</span>
                <span>Fast (2.0x)</span>
              </div>
            </div>
          </div>

          {/* Generate Button */}
          <button
            onClick={handleGenerate}
            disabled={isGenerating || !text.trim()}
            className="w-full py-4 rounded-xl bg-gradient-to-r from-violet-500 to-pink-500 text-white font-semibold text-lg hover:opacity-90 disabled:opacity-50 disabled:cursor-not-allowed transition-all transform hover:scale-[1.02] active:scale-[0.98] flex items-center justify-center gap-2"
          >
            {isGenerating ? (
              <>
                <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                Generating...
              </>
            ) : (
              <>
                <Sparkles className="w-5 h-5" />
                Generate Speech
              </>
            )}
          </button>

          {/* Error Message */}
          {error && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              className="p-4 rounded-xl bg-red-500/10 border border-red-500/20 text-red-400 flex items-center gap-2"
            >
              <AlertCircle className="w-5 h-5 flex-shrink-0" />
              <span>{error}</span>
            </motion.div>
          )}
        </motion.div>

        {/* Waveform Animation */}
        {(isGenerating || audioUrl) && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="mt-8"
          >
            <Waveform isAnimating={isGenerating} />
          </motion.div>
        )}

        {/* Audio Player */}
        {audioUrl && !isGenerating && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="mt-8"
          >
            <AudioPlayer audioUrl={audioUrl} onDownload={handleDownload} />
          </motion.div>
        )}

        {/* Features */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.3 }}
          className="mt-12 grid sm:grid-cols-3 gap-4"
        >
          {[
            { label: '8 Natural Voices', desc: 'Male & Female' },
            { label: 'High Quality', desc: '24kHz Audio' },
            { label: '2 Model Sizes', desc: 'Mini & Nano' },
          ].map((feature, i) => (
            <div key={i} className="text-center p-4 rounded-2xl bg-white/5">
              <div className="text-violet-400 font-semibold">{feature.label}</div>
              <div className="text-zinc-500 text-sm">{feature.desc}</div>
            </div>
          ))}
        </motion.div>

        {/* Footer */}
        <motion.footer
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.4 }}
          className="mt-12 text-center text-zinc-500 text-sm"
        >
          <p>
            Open source project
            {' | '}
            <a href="https://huggingface.co/KittenML/kitten-tts-mini-0.8" target="_blank" rel="noopener noreferrer" className="text-violet-400 hover:underline">
              Mini model
            </a>
            {' | '}
            <a href="https://huggingface.co/KittenML/kitten-tts-nano-0.2" target="_blank" rel="noopener noreferrer" className="text-violet-400 hover:underline">
              Nano model
            </a>
          </p>
        </motion.footer>
      </div>
    </main>
  )
}
