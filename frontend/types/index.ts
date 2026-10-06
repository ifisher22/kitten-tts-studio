export interface TTSRequest {
  text: string
  voice?: string
  speed?: number
  model?: 'kitten-tts-mini-0.8' | 'kitten-tts-nano-0.2'
}

export interface TTSResponse {
  success: boolean
  message: string
  voice_used: string
  text_length: number
  audio_duration_estimate: number
}

export interface VoiceInfo {
  name: string
  alias: string
  gender: string
}

export interface VoicesResponse {
  voices: VoiceInfo[]
}

export interface HealthResponse {
  status: string
  model_loaded: boolean
  available_voices: string[]
  available_models: string[]
  active_model: string
  version: string
}

export interface ModelInfo {
  key: string
  label: string
  loaded: boolean
}

export interface ModelsResponse {
  models: ModelInfo[]
  active_model: string
}
