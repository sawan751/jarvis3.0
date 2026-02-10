# Backend/general_q.py
import os
import sys
from groq import Groq
from dotenv import load_dotenv

from Backend.memory import memory   # shared memory we added earlier

# ─────────────────────────────────────────────────────────────
#  Load API key (same as before)
# ─────────────────────────────────────────────────────────────

load_dotenv('api.env')
GROQ_API_KEY = os.getenv('GROK_API_KEY')

if not GROQ_API_KEY:
    print("Error: GROQ_API_KEY not found in api.env", file=sys.stderr)
    sys.exit(1)

client = Groq(api_key=GROQ_API_KEY)

MODEL = "llama-3.3-70b-versatile"          # or mixtral, gemma2-27b, etc.

# ─────────────────────────────────────────────────────────────
#  System prompt — Rex personality
# ─────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """You are Rex, an intelligent, witty and slightly sarcastic personal assistant 
inspired by Jarvis from Iron Man. You speak with a refined British tone.

Rules:
- Always address the user as "Sir" (or "Madam" if appropriate).
- Be concise unless more detail is explicitly requested.
- Use subtle humor, dry wit, clever remarks when it fits naturally.
- Never use emojis, markdown lists, code blocks or excessive formatting in spoken answers.
- For factual answers, be precise and do not invent numbers or details.
- If given fresh realtime data in the system message, use ONLY that information — never make up values.
- Decline unsafe, illegal or harmful requests with a polite but sharp quip.

Example responses:
- Time query → "It's 7:42 in the evening, Sir. Still conquering the world at this hour?"
- Weather   → "Scorching 38°C in Indore right now, Sir. Hydration is advised."
- General   → "Certainly, Sir. Though I must say that's a rather bold question."
"""

def general(user_query: str, extra_context: str = "") -> str:
    """
    Main general answer generator.
    - Uses shared memory
    - Can receive injected realtime facts via extra_context
    - Streams output to console (for debugging)
    - Saves to memory automatically
    """
    messages = memory.get_context()

    # Inject realtime data as a strict system message
    if extra_context:
        messages.append({
            "role": "system",
            "content": f"Current realtime fact — use EXACTLY this and nothing else:\n{extra_context}\nDo NOT make up or modify any values."
        })

    messages.append({"role": "user", "content": user_query.strip()})

    try:
        stream = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            temperature=0.85,           # slightly creative but not too wild
            max_tokens=1024,
            top_p=0.95,
            stream=True,
            stop=None
        )

        response_text = ""
        print("Rex: ", end="", flush=True)

        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                delta = chunk.choices[0].delta.content
                response_text += delta
                print(delta, end="", flush=True)

        print()  # final newline

        clean_answer = response_text.strip()

        # Save the full exchange to shared memory
        memory.add_exchange(user_query, clean_answer)

        return clean_answer

    except Exception as e:
        print(f"\n[General LLM error]: {e}", file=sys.stderr)
        fallback = "Apologies, Sir. A momentary lapse in the matrix. Could you repeat that?"
        memory.add_exchange(user_query, fallback)
        return fallback