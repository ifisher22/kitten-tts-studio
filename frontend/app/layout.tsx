import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'Kitten TTS - AI Text to Speech',
  description: 'Production-ready Text-to-Speech using KittenML/kitten-tts-mini-0.8',
  keywords: ['TTS', 'Text-to-Speech', 'AI', 'Kitten TTS', 'Voice Synthesis'],
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className="antialiased">
        {children}
      </body>
    </html>
  )
}
