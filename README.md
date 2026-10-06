# 🐱 KittenTTS Studio

基于 [KittenTTS](https://github.com/KittenML/KittenTTS) 的本地文本转语音（TTS）合成工作台。FastAPI 后端 + Next.js 前端，CPU 即可运行，支持 Docker 一键部署。

![Python](https://img.shields.io/badge/Python-3.10+-blue) ![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green) ![Next.js](https://img.shields.io/badge/Next.js-14-black) ![License](https://img.shields.io/badge/License-MIT-yellow)

## ✨ 功能特性

- **双模型切换** — `kitten-tts-mini-0.8`（75MB）与 `kitten-tts-nano-0.2`（23MB）在线切换
- **多音色支持** — 内置多说话人音色（Jasper 等），由各模型的 `voices.npz` 提供
- **语速调节** — 0.5x ~ 2.0x 自由设定
- **流式合成** — `/tts/stream` 端点支持音频流式返回，边生成边播放
- **波形可视化** — 前端实时 Waveform 组件
- **长文本支持** — 单次最多 5000 字符
- **Docker 部署** — 多阶段构建，`docker compose up` 一键启动前后端
- **纯 CPU 推理** — 使用 onnxruntime CPU 版，无需 GPU

## 🏗️ 技术栈

| 层 | 技术 |
|---|---|
| 后端 | FastAPI + Uvicorn + ONNX Runtime (CPU) |
| 前端 | Next.js 14 (App Router) + TypeScript + Tailwind CSS + Framer Motion |
| 语音引擎 | KittenTTS 0.8（misaki 音素化 + espeak-ng） |
| 部署 | Docker Compose（backend / frontend 双服务） |

## 📁 项目结构

```
├── backend/            # FastAPI 后端
│   ├── app/
│   │   ├── routers/    # /tts 与 /health 路由
│   │   ├── models/     # Pydantic schemas
│   │   └── services/   # TTS 引擎封装
│   ├── main.py
│   └── requirements.txt
├── frontend/           # Next.js 前端
│   ├── app/            # 页面
│   ├── components/     # AudioPlayer / Waveform
│   └── types/
├── model/              # 模型权重（需自行下载，见下文）
│   ├── KittenML_kitten-tts-mini-0.8/
│   └── KittenML_kitten-tts-nano-0.2/
├── Dockerfile          # 多阶段构建（backend / frontend）
└── docker-compose.yml
```

## 🚀 快速开始

### 方式一：Docker（推荐）

```bash
docker compose up --build
# 前端: http://localhost:3000
# 后端: http://localhost:8008
```

### 方式二：本地运行

**1. 下载模型权重**

模型文件不随仓库分发，请从 Hugging Face 下载后放入 `model/` 目录：

```bash
# kitten-tts-mini-0.8 (~75MB)
# kitten-tts-nano-0.2 (~23MB)
# 来源: https://huggingface.co/KittenML
# 目录结构参考: model/KittenML_kitten-tts-mini-0.8/{config.json, voices.npz, *.onnx}
```

**2. 启动后端**

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -r requirements.txt
# 安装 KittenTTS 主包（不自动装依赖）
python -m pip install https://github.com/KittenML/KittenTTS/releases/download/0.8/kittentts-0.8.0-py3-none-any.whl --no-deps
uvicorn main:app --host 0.0.0.0 --port 8008 --reload
```

**3. 启动前端**

```bash
cd frontend
npm install
npm run dev
# 打开 http://localhost:3000
```

## 🔌 API 一览

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | `/health` | 健康检查（含模型加载状态） |
| GET | `/tts/models` | 可用模型列表 |
| GET | `/tts/voices` | 当前模型可用音色 |
| POST | `/tts/generate` | 同步合成，返回完整音频 |
| POST | `/tts/stream` | 流式合成，音频分块返回 |

交互式文档：启动后端后访问 `http://localhost:8008/docs`

## ⚠️ 注意事项

- 模型权重体积较大，通过 `.gitignore` 排除在仓库之外，请按上文说明自行下载
- 首次启动需加载 ONNX 模型，冷启动约需数秒
- 音素化依赖 espeak-ng 数据（`espeakng-loader` 自动处理），Windows 无需额外安装系统包

## 🙏 致谢

- [KittenML/KittenTTS](https://github.com/KittenML/KittenTTS) — 轻量级开源 TTS 引擎
- [misaki](https://github.com/hexgrad/misaki) — 文本音素化

## License

MIT
