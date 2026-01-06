from groq import Groq
import json
from dotenv import load_dotenv
import os

def general(user_input):
    
    # Load API key
    env_file = 'api.env'
    load_dotenv(env_file)
    Api_key = os.getenv('GROK_API_KEY')

    # Initialize client
    client = Groq(api_key=Api_key)
    

    # System prompt
    system_prompt = """You are Rex, an AI assistant inspired by Jarvis from the Marvel Cinematic Universe, with a sophisticated British accent and a polite, witty, slightly sarcastic personality.
Address the user as "Sir" or "Madam." Deliver accurate, ultra-concise answers (under 50 words) to any question, prioritizing relevance to their AIML studies at Malwa Institute of Technology.
Use a conversational tone with subtle humor, avoid lists, and simplify complex topics with clever analogies. 
Confirm tasks, offer one key insight for vague queries, and check for clarification. Decline harmful requests with a quip. Example: "Clear skies at 72°F, Sir. Sunglasses?"""
    
    # Load chat history (optional)
    HISTORY_FILE ='chat_history.json'
    def load_hist(HISTORY_FILE):
        try:
            if os.path.exists(HISTORY_FILE):
                with open(HISTORY_FILE,'r') as f:
                    history = json.load(f)
                    if not isinstance(history, list):
                        print("History is blank, Start fresh please")
                        return [{"role": "system", "content": system_prompt}]
                    return history
            else:
                print("Json File not exist, Save the Json file first")
                return [{"role": "system", "content": system_prompt}]
        except:
            print("Problem in Executing code of HIstory file ")
            return [{"role": "system", "content": system_prompt}]
    #history ko save kra yha pr        
    def save_hist(history):
        with open(HISTORY_FILE,'w') as f:
            json.dump(history, f, indent=2)
    
            
                
    try:
        history = load_hist(HISTORY_FILE)
        
        history.append({"role": "user", "content": user_input})
        # Request to Groq
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=history,
            temperature=1,
            max_completion_tokens=1024,
            top_p=1,
            stream=True,
            stop=None
        )

        # Collect response
        response_text = ""
        for chunk in completion:
            response = chunk.choices[0].delta.content or ""
            response_text += response
            print(response, end="")
            
        history.append({"role": "assistant", "content":response_text})
        save_hist(history)
        

        return response_text.strip()  # ✅ return answer string

    except Exception as e:
        print(f"An error occurred: {e}")
        return None
    