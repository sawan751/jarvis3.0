# brain.py
import os
from groq import Groq
from general_q import general
from dotenv import load_dotenv

def brainQ(text):
    try:
        # Load environment variables from api.env
        env_file = "api.env"
        load_dotenv(env_file)  # Explicitly load api.env

        # Retrieve the API key
        API_KEY = os.getenv("GROK_API_KEY")

        # Initialize Groq client
        client = Groq(api_key=API_KEY)

        # System prompt
        system_prompt = """You are a prompt classifier that predicts if the input is related to
        system (e.g., queries about open, modify, close, volume), 
        realtime (requires live data, e.g., time, date, stocks), 
        or general (normal questions). 
        Answer only: system, realtime, or general. I can also ask in Hindi."""

        # Request classification
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text}
            ],
            temperature=1,
            max_completion_tokens=1024,
            top_p=1,
            stream=True,
            stop=None
        )

        # Collect streamed response
        response = ""
        for chunk in completion:
            chunk_content = chunk.choices[0].delta.content or ""
            response += chunk_content
            print(chunk_content, end="")

        # Normalize response
        response = response.lower().strip()

        # Handle classification
        if response == "system":
            print("\n🔹 System task detected")
            # TODO: Call system handler here
        elif response == "general":
            print("\n🔹 General query detected")
            return general(text)
        elif response == "realtime":
            print("\n🔹 Realtime query detected")
            return general(text)

        return response  # Useful if you want to capture output programmatically

    except Exception as e:
        print(f"An error occurred: {e}")
        return None


# Example usage
