import speech_recognition as sr
import pyttsx3
import winsound
from Backend import brain
import os
from pathlib import Path

# Voice GUI controls (safe fallbacks if GUI unavailable)
try:
    from gui.voice_gui import launch_gui, set_idle, set_listening, set_speaking, shutdown_gui, minimize_gui, restore_gui
except Exception:
    def launch_gui(*args, **kwargs):
        pass
    def set_idle():
        pass
    def set_listening():
        pass
    def set_speaking():
        pass
    def shutdown_gui():
        pass
    def minimize_gui():
        pass
    def restore_gui():
        pass
def play_listen_sound():
    winsound.Beep(1300,150)
def listen():
    r = sr.Recognizer()
    
    text = ''
    with sr.Microphone() as source:
        print("Adjusting for ambient noise... Please wait.")
        r.adjust_for_ambient_noise(source, duration=0.6)
        play_listen_sound()
        set_idle()
        print("Listening.........")
        audio = r.listen(source)

    try:
        text = r.recognize_google(audio)
        print("You said:", text)

    except sr.UnknownValueError:
        print("Google Speech Recognition could not understand your audio.")

    except sr.RequestError as e:
        print(f"Speech Recognition service unavailable: {e}")
    
    #return speak(text)
    print(text)
    return text


def speak(text):
    try:
        set_speaking()
        engine = pyttsx3.init()
        engine.setProperty('rate', 180)
        engine.setProperty('volume', 1.0)
        voices = engine.getProperty("voices")
        engine.setProperty("voice", voices[0].id)  # 0 for male, 1 for female
        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        print(f"Local TTS Error: {e}")
    finally:
        set_idle()


if __name__ == "__main__":
    launch_gui()
    speak("Your rex voice assistant activated")
    while True:
        quary = listen()
        #quary = listen().strip()   # isse kuch ni hore bee 
        if not quary:
            continue
        if quary: 
            if quary.lower().strip() in ["exit" ,"bye","goodbye"]:
                speak("Good bye, sir")
                shutdown_gui()
                break
            else:
                answer = brain.brainQ(quary)# ✅ pass correct variable
                speak(answer)
        else:
            print("\nplease Say something")
            speak("Sorry, I didn't get that. Please try again.")