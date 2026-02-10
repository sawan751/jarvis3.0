# Backend/memory.py
import json
import os
from typing import List, Dict
from datetime import datetime

HISTORY_FILE = "Backend/chat_history.json"
SYSTEM_PROMPT = """You are Rex, a helpful, witty and slightly sarcastic British-style assistant. 
Address the user as Sir. Keep answers concise unless more detail is requested."""

class ConversationMemory:
    def __init__(self):
        self.history: List[Dict[str, str]] = []
        self._load()

    def _load(self):
        if os.path.exists(HISTORY_FILE):
            try:
                with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        self.history = data  # Load all history
                    else:
                        self.history = []
            except Exception:
                self.history = []
        else:
            self.history = []

        # Always make sure system prompt is first
        if not self.history or self.history[0]["role"] != "system":
            self.history.insert(0, {"role": "system", "content": SYSTEM_PROMPT})

    def save(self):
        try:
            os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)
            with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Warning: Could not save history → {e}")

    def add_exchange(self, user_text: str, assistant_text: str):
        self.history.append({"role": "user", "content": user_text.strip()})
        if assistant_text and assistant_text.strip():
            self.history.append({"role": "assistant", "content": assistant_text.strip()})
        
        # Save all history (no trimming)
        self.save()

    def get_context(self) -> List[Dict[str, str]]:
        return self.history.copy()

    def clear(self):
        self.history = [{"role": "system", "content": SYSTEM_PROMPT}]
        self.save()


# Singleton instance — import and use this
memory = ConversationMemory()


def get_recent_context(max_turns: int = 5) -> str:
    """Quick helper: returns formatted recent conversation for prompts"""
    recent = memory.get_context()[- (max_turns * 2 + 1):]  # +1 for system
    lines = []
    for msg in recent:
        role = "Rex" if msg["role"] == "assistant" else "You"
        lines.append(f"{role}: {msg['content']}")
    return "\n".join(lines)