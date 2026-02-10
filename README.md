# Rex - Voice Assistant (Jarvis Inspired)

A personal voice assistant built in Python, inspired by Jarvis from Iron Man.  
Currently in active development — more features and polish coming soon.

https://github.com/its-sawan751/rex-voice-assistant  (replace with your actual repo URL)

## Current Features

- Voice input using Google Speech Recognition (with ambient noise adjustment)
- Text-to-Speech output:
  - Primary: ElevenLabs (multilingual Rachel voice)
  - Fallback: Windows SAPI (pyttsx3 — Zira voice)
- Animated circular GUI (PyQt6) showing states: Idle / Listening / Speaking
- Command categories:
  - **Realtime**: time, date, weather (wttr.in), stock prices (yfinance), news (NewsAPI)
  - **System**: open/close apps, play YouTube, volume control, shutdown/restart, settings, window minimize/maximize/close
  - **General**: any other question → answered by Groq (Llama-3.3-70B) with personality
- Shared conversation memory (saved to JSON)
- Basic personality: witty, sarcastic, British-style tone ("Sir", concise answers, dry humor)

## Demo / Current State (Feb 2026)

Works reasonably well for:
- "what's the time"
- "today's date"
- "open chrome"
- "play shape of you"
- "TCS stock price"

Still needs improvement in:
- Hindi/mixed language understanding
- Reliable weather & news fetching
- Robust system command parsing
- Wake-word / always-listening mode
- Graceful error handling & UX

## Tech Stack

- **Python**: 3.10+
- **Speech Recognition**: `speech_recognition` + Google API
- **TTS**: ElevenLabs (primary) + pyttsx3 (fallback)
- **LLM**: Groq API (Llama-3.3-70B-versatile)
- **GUI**: PyQt6 (circular animated widget)
- **Other libraries**: yfinance, newsapi-python, python-dotenv, sounddevice, soundfile, winsound

## Project Structure

## Installation

1. Clone the repo
   ```bash
   git clone https://github.com/sawan751/jarvis3.0.git
   cd rex-voice-assistant

Install dependencies
```Bash
  pip install -r requirements.txt
```

# Run
```
python main.py
```
