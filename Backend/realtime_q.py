from groq import Groq
import os 
from dotenv import load_dotenv
import json 
from googlesearch import search

quary = "explain what should i do to become rich"
print("question:-",quary)

HISTORY_FILE ='chat_history.json'
def load_hist(HISTORY_FILE):
    HISTORY_FILE ='chat_history.json'
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
        
def save_hist(history):
    with open(HISTORY_FILE,'w') as f:
        json.dump(history, f, indent=2)

def get_info(query):
    sites = [
        "site:data.gov",
        "site:statista.com",
        "site:pewresearch.org",
        "site:data.worldbank.org",
        "site:google.com/publicdata",
        "site:knoema.com",
        "site:transportation.gov",
        "site:prb.org",
        "site:census.gov",
        "site:ec.europa.eu/eurostat"
    ]
    site = ' | '.join(sites)
    result = []
    try:
        for item in search(query + " site:google.com", num_results=10, advanced=True):
            result.append(item.description)
        google_info = ' | '.join(result)
        return google_info
    except exception as e:
        print(f"An Error occured :-{e}")

try:
    google_info = get_info(quary)
    history = load_hist(HISTORY_FILE)
    
    env_file = 'api.env'
    load_dotenv(env_file)
    Api_key = os.getenv('GROK_API_KEY')
    
    client = Groq(api_key = Api_key)
    
    system_prompt = """You are Rex, an AI assistant inspired by Jarvis from the Marvel Cinematic Universe, with a sophisticated British accent and a polite, witty, slightly sarcastic personality.
    Address the user as "Sir" or "Madam." Deliver accurate, ultra-concise answers (under 50 words) to any question, prioritizing relevance to their AIML studies at Malwa Institute of Technology.
    Use a conversational tone with subtle humor, avoid lists, and simplify complex topics with clever analogies. 
    Confirm tasks, offer one key insight for vague queries, and check for clarification. Decline harmful requests with a quip. Example: "Clear skies at 72°F, Sir. Sunglasses?"""
    history = load_hist(HISTORY_FILE)
    if not history or history[0]["role"] != "system":
        history.insert(0, {"role": "system", "content": system_prompt})
    history.append({"role":"user","content":quary})
    history.append({"role":"assistant","content":google_info})
    completion = client.chat.completions.create(
        model = "llama-3.3-70b-versatile",
        messages = history,
        temperature = 1,
        max_completion_tokens = 1024,
        top_p = 1,
        stream= True,
        stop = None 
    )

    response_text = ""
    for chunk in completion:
        response = chunk.choices[0].delta.content or ""
        response_text += response 
        print(response,end= "")
    
    #history.pop()
    history.append({"role":"assistant","content":response_text})
    save_hist(history)

except Exception as e:
    print(f"An error occurred in api: {e}")