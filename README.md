# 👩‍🏫 Shiksha Sahayak (शिक्षक सहायक)

[![Vercel Deployment](https://img.shields.io/badge/Frontend-Vercel-black?logo=vercel)](https://github.com/sp25126/CDF)
[![Render Deployment](https://img.shields.io/badge/Backend-Render-darkblue?logo=render)](https://github.com/sp25126/CDF)
[![Python Version](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)](https://www.python.org/)
[![Next.js Version](https://img.shields.io/badge/Next.js-14-black?logo=nextdotjs)](https://nextjs.org/)

**Shiksha Sahayak** (AI Classroom Assistant) is an interactive, voice-first educational co-pilot designed for classrooms in **Haryana Government Schools**. Built with touch-friendly, high-contrast controls for smartboards and projectors, it helps teachers explain complex topics, show context-aware diagrams/videos, and run interactive quizzes without losing the flow of their lessons.

---

## 🌟 Core Pillars & Features

### 📖 1. Live Concept Simplification
* **High-Context Explanations**: Converts complex science, math, or history subjects into simple explanations tailored for primary and secondary school levels.
* **Analogies & Real-World Examples**: Automatically generates culturally relevant analogies (e.g. comparing photosynthesis to a home kitchen) and local references.
* **Bilingual Support**: Instant toggle between Hindi (हिन्दी) and English explanations.

### ❓ 2. Voice-Triggered Quizzing
* **Interactive Classroom Quizzes**: Teachers can trigger multiple-choice quizzes vocally during lessons.
* **Interactive Navigation**: Navigate through questions, select answers, view real-time explanations, and check final scores on a dedicated Quiz Finish screen.
* **Accessibility-First**: Designed with large touch targets so teachers or students can easily tap answers on a smartboard.

### 🖼️ 3. Context-Aware Media & Video Rail
* **Wikimedia Commons Integration**: Automatically fetches copyright-free educational images based on context-aware search queries.
* **YouTube Video Fallback**: Dynamically searches for educational YouTube videos matching the lesson, using a static database match or live `yt-dlp` scraping fallback.
* **LLM-Based Topic Resolution**: Utilizes LLMs to determine clean, disambiguated search keywords (e.g. resolving a follow-up about "AI" in a chemistry lesson to "Aluminium", or in a computer science lesson to "Artificial Intelligence").

### 📋 4. Smart Whiteboard & Interactive History
* **Drawing Canvas**: An overlay canvas allowing teachers to sketch, highlight, and write notes during lessons.
* **Document Viewer**: Smart PDF viewer with scroll fixes for smartboard interactions.
* **Clickable Transcript History**: A linear, scrollable log of the current class conversation. Teachers can click any past prompt to instantly restore that context.

### 🗣️ 5. State-Aware Juli-E Avatar
* **Visual Cues**: A dynamic virtual avatar (Juli-E) transitions between states (**Idle, Listening, Thinking, Speaking**) so the entire classroom knows when the AI is active.
* **Voice Co-pilot**: High-fidelity text-to-speech (TTS) and speech-to-text (STT) support for hands-free teaching.

---

## 🛠️ Tech Stack

* **Frontend**: React (Next.js 14, App Router), Tailwind CSS, Zustand (State Management), Lucide Icons.
* **Backend**: FastAPI (Python 3.10+), Pydantic Settings.
* **AI Router**: Multi-tiered fallback logic supporting **Groq** (primary: Llama-3.3-70b-versatile, Llama-3.1-8b-instant) and **OpenRouter** (fallback: Google Gemma 4 31B IT).
* **Media Pipelines**: Wikimedia API (images) + `yt-dlp` (videos).

---

## 🚀 Local Development Setup

### Prerequisites
* **Node.js** v18.0 or higher
* **Python** v3.10 or higher
* **Git** installed on your system

---

### 1. Backend Setup

1. **Navigate to the backend directory**:
   ```bash
   cd backend
   ```

2. **Create and activate a Python virtual environment**:
   * **Windows (PowerShell)**:
     ```powershell
     python -m venv venv
     .\venv\Scripts\Activate.ps1
     ```
   * **macOS / Linux**:
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment Variables**:
   Create a `.env` file in the `backend/` directory (you can copy `.env.example` as a template):
   ```ini
   # App Settings
   APP_NAME="Shiksha Sahayak API"
   DEBUG=True

   # Groq (Primary LLM Provider)
   GROQ_API_KEY=your_groq_api_key_here
   GROQ_MODEL_STRONG=llama-3.3-70b-versatile
   GROQ_MODEL_FAST=llama-3.1-8b-instant

   # OpenRouter (Fallback LLM Provider)
   LLM_API_KEY=your_openrouter_api_key_here
   LLM_MODEL=google/gemma-4-31b-it:free

   # Ollama (Optional Local Fallback)
   OLLAMA_BASE_URL=http://localhost:11434
   ```

5. **Start the FastAPI Development Server**:
   ```bash
   python -m app.main
   ```
   The backend will start running on `http://localhost:8000`. You can access the interactive API docs at `http://localhost:8000/docs`.

6. **Run Backend Verification Tests**:
   Verify session memory logic, prompt assembly, and service routing using the built-in tests:
   ```bash
   python tests/test_memory.py
   python tests/test_prompt_assembly.py
   ```

---

### 2. Frontend Setup

1. **Navigate to the frontend directory**:
   ```bash
   cd ../frontend
   ```

2. **Install Node dependencies**:
   ```bash
   npm install
   ```

3. **Configure Environment Variables**:
   Create a `.env` file in the `frontend/` directory (or `.env.local` for local development):
   ```env
   # Local Backend API URL
   NEXT_PUBLIC_API_URL=http://localhost:8000
   ```

4. **Start the Next.js Development Server**:
   ```bash
   npm run dev
   ```
   Open `http://localhost:3000` in your web browser.
   * **Main App Console**: `http://localhost:3000`
   * **Interactive Component Preview / Demo**: `http://localhost:3000/demo`

---

## 🌐 Production Deployment

### 1. Backend (Deployed on Render)
The project includes a `render.yaml` configuration for quick deployment on Render Web Services:
* **Root Directory**: `backend`
* **Build Command**: `pip install -r requirements.txt`
* **Start Command**: `uvicorn app.main:app --host=0.0.0.0 --port=$PORT`
* **Required environment variables on Render**:
  * `GROQ_API_KEY` (Strong/Fast models default to Llama-3.3 and Llama-3.1)
  * `LLM_API_KEY` (OpenRouter API key)
  * `CORS_ORIGINS` (Set to your deployed Vercel frontend URL, e.g. `https://your-app.vercel.app`)
  * `DEBUG` (Should be set to `False`)

### 2. Frontend (Deployed on Vercel)
Connect the repository to Vercel and import the project:
* **Framework Preset**: Next.js
* **Root Directory**: `frontend`
* **Build Command**: `npm run build`
* **Environment Variables**:
  * `NEXT_PUBLIC_BACKEND_URL`: Set this to your deployed Render backend URL (e.g. `https://shiksha-sahayak-backend.onrender.com`).

---

## 🧪 Testing and Verification

To make sure everything is functioning correctly, you can perform these manual tests:
1. **Interactive Chat**: Type or speak a command like *"Explain gravity"* or *"Teach me about fractions"*. Ensure that Juli-E transitions states and generates the explanation page.
2. **Concept Switch**: Ask *"What about friction?"* as a follow-up and ensure that the media rail updates with friction-related images and videos, showing correct context resolution.
3. **Quizzing Flow**: Trigger a quiz by asking *"Quiz me on photosynthesis"*. Complete the questions and check the final scoring screen.
4. **Context Retrieval**: Ask 3-4 separate questions, then click on the earliest question in the sidebar/transcript strip. Juli-E should restore the canvas to that exact explanation state.

---

## 🤝 Contributing & Guidelines

* **Code Aesthetics**: Ensure all UI elements adhere to the color palette (`Indigo` primary, high contrast backgrounds) and avoid unnecessary "AI slop" or over-stimulating gradients.
* **Component Design**: Place reusable smartboard UI cards in `frontend/src/components/cards` and ensure they are responsive and AA contrast compliant.
* **State Stores**: Keep state logic in Zustand stores under `frontend/src/state` to maintain clean reactive flows.
