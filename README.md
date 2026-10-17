# 🌐 Aniruddh Python Web Agent

An autonomous, web-connected AI assistant built with **Python**, **FastAPI**, and **Google Gemini** featuring real-time web search, full webpage content extraction, workspace notes management, and a Python math sandbox.

![Web Agent](https://img.shields.io/badge/Agent-Autonomous-cyan) ![Python](https://img.shields.io/badge/Python-3.13+-blue) ![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688) ![Gemini](https://img.shields.io/badge/Google%20Gemini-2.5%20Flash-purple)

---

## ✨ Features

- **🌐 Live DuckDuckGo Web Search**: Instant real-time web searching without requiring third-party search API keys.
- **📄 Webpage Content Extractor**: Reads and extracts clean article text from any URL with HTML boilerplate cleanup.
- **📝 Workspace Notes System**: Save, search, update, and manage Markdown notes directly from chat conversations or the slide-over Notes drawer.
- **🧮 Python Math & Code Sandbox**: Evaluates mathematical computations, statistical calculations, and date arithmetic safely.
- **⚡ Real-time SSE Streaming**: Token-by-token streaming response with live interactive tool execution cards (status, arguments, collapsible outputs).
- **🎨 Modern Glassmorphic Dark UI**: Sleek aesthetic with Inter typography, JetBrains Mono code blocks, syntax highlighting, and responsive layout.
- **⚙️ In-App Settings & Key Manager**: Set your free Gemini API key right in the UI Settings modal or in `.env` without restarting.

---

## 🚀 Quick Start

### 1. Activate the Virtual Environment
```bash
source .venv/bin/activate
```

### 2. Configure Your Gemini API Key
You can obtain a free Gemini API key from [Google AI Studio](https://aistudio.google.com/).
Either:
- Add it to `.env`:
  ```bash
  GEMINI_API_KEY=your_gemini_api_key_here
  ```
- Or simply open the web application and enter it in the **Settings (⚙️)** modal.

### 3. Launch the Web Agent
```bash
python run.py
```
Open your browser and navigate to:
```
http://127.0.0.1:8000
```

---

## 🛠️ Project Structure

```
Agent_build/
├── run.py                 # Application launcher
├── requirements.txt       # Dependencies
├── .env.example           # Environment configuration template
├── app/
│   ├── main.py            # FastAPI application & SSE endpoints
│   ├── config.py          # Settings and environment loader
│   ├── agent/
│   │   ├── core.py        # Multi-step ReAct agent loop & tool orchestrator
│   │   └── prompts.py     # System instructions and persona
│   └── tools/
│       ├── __init__.py    # Tools registry & metadata
│       ├── web_search.py  # DuckDuckGo search engine
│       ├── web_reader.py  # Webpage fetcher & HTML cleaner
│       ├── notes.py       # Workspace notes CRUD system
│       ├── calculator.py  # Python safe calculator sandbox
│       └── datetime_tool.py # Live date, time & timezone tool
├── static/
│   ├── index.html         # Rich web UI
│   ├── css/style.css      # Dark glassmorphic styling
│   └── js/app.js          # Chat streaming, notes drawer & UI logic
└── user_data/
    └── notes/             # Markdown notes stored in workspace
```

---

## 💡 Example Tasks You Can Try

1. **Web Research**:
   > *"Search the web for the latest updates on Python 3.13 and summarize the top new features with source links."*

2. **Research & Save Note**:
   > *"Find the top 5 prompt engineering techniques and save them into a new note titled 'Prompt_Engineering_Tips'."*

3. **Complex Math**:
   > *"If an investment of $25,000 grows at 8.2% annual interest compounded quarterly, what will it be worth in 15 years? Use the calculator."*

4. **Webpage Deep Dive**:
   > *"Search for recent news about James Webb Space Telescope discoveries, pick the top result, read its webpage, and explain the key findings."*

5. **Notes Exploration**:
   > *"List all my saved workspace notes and summarize the Welcome_Guide note."*
