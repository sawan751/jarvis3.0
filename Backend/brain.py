# brain.py
import os
import json
import logging
from typing import Optional, Dict, Tuple
from groq import Groq
from dotenv import load_dotenv

# Import your existing handlers
from Backend.general_q import general
from Backend.realtime_q import *
from Backend.systemq import handle_system_query
from Backend.memory import memory

# ────────────────────────────────────────────────
#  Config & Setup
# ────────────────────────────────────────────────

load_dotenv('api.env')
GROQ_API_KEY = os.getenv('GROK_API_KEY')

if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY not found in api.env")

client = Groq(api_key=GROQ_API_KEY)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

MODEL = "llama-3.3-70b-versatile"   # same as in general_q.py

# ────────────────────────────────────────────────
#  Classification Prompt (strict JSON output)
# ────────────────────────────────────────────────

CLASSIFY_PROMPT = """You are a precise query classifier for a voice assistant named Rex.

Given the user's spoken query, respond **ONLY** with valid JSON (nothing else).

Required fields:
{{
  "category":    one of "system", "realtime", "general",
  "normalized":  short, clear English command optimized for the handler (max 12 words),
  "confidence":  number 0.0–1.0 how sure you are,
  "language":    detected language code ("en", "hi", etc.)
}}

Rules:
- "system"    → anything that controls computer/apps/files/volume/windows/settings/execute/open/close/play/launch/delete/shutdown/...
- "realtime"  → time, date, weather, stock price, news, current/now/live/today/...
- "general"   → everything else: questions, explanations, jokes, stories, math, opinions, chit-chat

Examples:
User: "open chrome"
→ {{"category":"system", "normalized":"open chrome", "confidence":0.98, "language":"en"}}

User: "what is the time now"
→ {{"category":"realtime", "normalized":"what is the current time", "confidence":0.99, "language":"en"}}

User: "band karo spotify"
→ {{"category":"system", "normalized":"close spotify", "confidence":0.92, "language":"hi"}}

User: "who is iron man"
→ {{"category":"general", "normalized":"who is iron man", "confidence":0.97, "language":"en"}}

User query: {{query}}
"""

# ────────────────────────────────────────────────
#  Core Classification Function
# ────────────────────────────────────────────────

def classify_with_groq(query: str) -> Optional[Dict]:
    """Call Groq → strict JSON classification"""
    try:
        prompt = CLASSIFY_PROMPT.replace("{{query}}", query.strip())

        completion = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,                # low randomness for classification
            max_tokens=256,
            top_p=0.95,
            stream=False
        )

        content = completion.choices[0].message.content.strip()

        # Try to parse JSON
        print(content)
        try:
            result = json.loads(content)
        except json.JSONDecodeError:
            # Sometimes model adds markdown or extra text → try to extract { ... }
            start = content.find('{')
            end = content.rfind('}') + 1
            if start >= 0 and end > start:
                cleaned = content[start:end]
                result = json.loads(cleaned)
            else:
                logger.warning(f"Could not parse JSON from: {content}")
                return None
        print(result)
        # Basic validation
        required = {"category", "normalized", "confidence"}
        if not all(k in result for k in required):
            return None

        category = result["category"].lower()
        if category not in {"system", "realtime", "general"}:
            return None

        return result

    except Exception as e:
        logger.exception("Groq classification failed")
        return None


# ────────────────────────────────────────────────
#  Public brain entry point (what main.py calls)
# ────────────────────────────────────────────────

def brainQ(user_input: str) -> str:
    if not user_input or not user_input.strip():
        return "Sorry Sir, I didn't catch that. Could you repeat?"

    # Step 1: Try to get realtime data first (fast path)
    realtime_result = get_realtime_data(user_input)   # ← use the new function name

    if realtime_result:
        # We have fresh data → pass it to general LLM for personality
        data_str = realtime_result.get("display_str") or str(realtime_result.get("key_data", ""))
        enhanced_query = (
            f"{user_input}\n\n"
            f"Use this exact realtime information — do NOT invent or change any numbers:\n"
            f"{data_str}"
        )
        answer = general(enhanced_query, extra_context=data_str)
        return answer

    # Step 2: Check for system commands (fast, no LLM needed)
    # Prefer classifier for system detection so we can get a normalized English command
    classification = classify_with_groq(user_input)

    if classification and classification.get("category") == "system":
        # Use the classifier's English-normalized prompt only for system handler
        normalized_cmd = classification.get("normalized", user_input)
        answer = handle_system_query(normalized_cmd)
        if answer and "not recognized" not in answer.lower():
            memory.add_exchange(user_input, answer)
            return answer

    # Fallback keyword heuristic if classifier failed or wasn't sure
    query_lower = user_input.lower()
    if any(kw in query_lower for kw in [
        'open', 'close', 'play', 'launch', 'run', 'volume', 'shutdown', 'restart',
        'file', 'folder', 'delete', 'window', 'minimize', 'maximize', 'settings'
    ]):
        answer = handle_system_query(user_input)
        if answer and "not recognized" not in answer.lower():
            memory.add_exchange(user_input, answer)
            return answer

    # Step 3: Everything else → normal general LLM
    answer = general(user_input)
    print(realtime_result)
    return answer or "I'm afraid I don't have an answer for that right now, Sir."
