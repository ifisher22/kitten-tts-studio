# 🎙️ Kitten TTS Web Application

A production-ready full-stack Text-to-Speech web application powered by [KittenML/kitten-tts-mini-0.8](https://huggingface.co/KittenML/kitten-tts-mini-0.8).

![Kitten TTS](https://img.shields.io/badge/Kitten-TTS-purple)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi)
![Next.js](https://img.shields.io/badge/Next.js-000000?logo=next.js)
![ONNX](https://img.shields.io/badge/ONNX-white?logo=onnx)

## ✨ Features

- 🎯 **8 Natural Voices** - 4 female and 4 male voices with distinct characteristics
- 🚀 **CPU Optimized** - Runs efficiently on CPU, no GPU required
- 🎨 **Modern UI** - Dark theme with glassmorphism design
- 🎵 **Audio Streaming** - Real-time WAV audio generation and playback
- 📥 **Download Support** - Save generated audio files
- ⚡ **Fast Inference** - ~79MB model with high-quality output
- 🐳 **Docker Ready** - Easy deployment with Docker Compose

## 📋 Available Voices

| Name | Gender | Alias |
|------|--------|-------|
| Bella | Female | expr-voice-2-f |
| Jasper | Male | expr-voice-2-m |
| Luna | Female | expr-voice-3-f |
| Bruno | Male | expr-voice-3-m |
| Rosie | Female | expr-voice-4-f |
| Hugo | Male | expr-voice-4-m |
| Kiki | Female | expr-voice-5-f |
| Leo | Male | expr-voice-5-m |

## 🏗️ Architecture

```
┌─────────────┐      HTTP/WebSocket       ┌─────────────┐
│   Next.js   │ ─────────────────────────> │   FastAPI   │
│  Frontend   │      (CORS enabled)        │   Backend   │
└─────────────┘                            └──────┬──────┘
     │ :3000                                         │
     │                                               │
     │                                        ┌──────┴──────┐
     │                                        │ KittenTTS   │
     │                                        │ ONNX Model  │
     │                                        └─────────────┘
     │
     ▼
┌─────────────┐
│ Audio Player│
│  (WAV/24kHz)│
└─────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 20+
- (Optional) Docker & Docker Compose

### Option 1: Local Development

#### 1. Setup Backend

```bash
# Create virtual environment using uv
uv venv backend/.venv

# Activate virtual environment
# Windows:
backend\.venv\Scripts\activate
# macOS/Linux:
source backend/.venv/bin/activate

# Install dependencies
cd backend
pip install -r requirements.txt

# Run backend server
python main.py
# or
uvicorn main:app --reload --host 0.0.0.0 --port 8008
```

The backend will:
- Auto-detect local model files (config.json, kitten_tts_mini_v0_8.onnx, voices.npz)
- Or download from HuggingFace if local files not found
- Start at http://localhost:8008
- OpenAPI docs at http://localhost:8008/docs

#### 2. Setup Frontend

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

The frontend will start at http://localhost:3000

### Option 2: Docker Compose (Recommended)

```bash
# Start both services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

Access:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8008
- API Docs: http://localhost:8008/docs

### Option 3: Backend Only (Docker)

```bash
# Build and run backend only
cd backend
docker build -t kitten-tts-backend -f Dockerfile ..
docker run -p 8008:8008 kitten-tts-backend
```

## 📚 API Documentation

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | API info |
| GET | `/health` | Health check |
| GET | `/tts/voices` | List available voices |
| POST | `/tts/generate` | Generate speech (download) |
| POST | `/tts/stream` | Generate speech (stream) |

### Request Examples

#### Generate Speech

```bash
curl -X POST http://localhost:8008/tts/stream \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Hello, this is a test of Kitten TTS!",
    "voice": "Jasper",
    "speed": 1.0
  }' \
  --output speech.wav
```

#### Python Client

```python
import requests

response = requests.post(
    "http://localhost:8008/tts/stream",
    json={
        "text": "Hello, world!",
        "voice": "Bella",
        "speed": 1.0
    }
)

# Save audio
with open("output.wav", "wb") as f:
    f.write(response.content)
```

## 🛠️ Development

### Project Structure

```
.
├── backend/               # FastAPI backend
│   ├── app/
│   │   ├── models/        # Pydantic schemas
│   │   ├── routers/       # API routes
│   │   └── services/      # Business logic
│   ├── main.py           # Application entry
│   └── requirements.txt
├── frontend/             # Next.js frontend
│   ├── app/              # App Router
│   ├── components/       # React components
│   ├── lib/              # Utilities
│   └── types/            # TypeScript types
├── config.json           # Model config
├── kitten_tts_mini_v0_8.onnx  # ONNX model
├── voices.npz            # Voice embeddings
├── Dockerfile            # Docker build
└── docker-compose.yml    # Compose config
```

### Backend Configuration

The backend automatically:
1. Detects local model files in the project root
2. Falls back to HuggingFace download if not found
3. Uses CPU-only inference (optimized for ~0.5-2s generation time)

### Frontend Configuration

Edit `frontend/next.config.js` to change the API URL:

```javascript
async rewrites() {
  return [
    {
      source: '/api/:path*',
      destination: 'http://your-backend:8008/:path*',
    },
  ]
}
```

## 🔮 Future Enhancements

The codebase is structured for easy extension:

- [ ] **Voice Style Selection** - Add prosody control
- [ ] **Batch TTS** - Process multiple texts
- [ ] **History List** - Save generation history
- [ ] **User Authentication** - Multi-user support
- [ ] **API Keys** - Rate limiting and access control
- [ ] **SSML Support** - Advanced speech markup

## 📦 Model Information

- **Model**: KittenML/kitten-tts-mini-0.8
- **Size**: ~79MB (ONNX)
- **Architecture**: StyleTTS 2
- **Sample Rate**: 24kHz
- **Parameters**: 80M
- **License**: Apache 2.0

## 🐛 Troubleshooting

### Model Loading Issues

```bash
# Check if model files exist
ls -la *.onnx *.npz config.json

# Verify backend can access files
curl http://localhost:8008/health
```

### CORS Errors

The backend has CORS enabled for all origins in development. For production, update:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],  # Restrict in production
    ...
)
```

### Audio Not Playing

- Check browser console for errors
- Ensure backend is running: `curl http://localhost:8008/health`
- Verify audio format: should be WAV/24kHz

## 📄 License

This project is licensed under the Apache 2.0 License - see the model page for details.

## 🙏 Acknowledgements

- [KittenML](https://huggingface.co/KittenML) for the TTS model
- [StyleTTS 2](https://github.com/yl4579/StyleTTS2) for the architecture

---

Built with ❤️ using FastAPI + Next.js + Kitten TTS
