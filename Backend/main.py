import speech_recognition as sr
import pyttsx3
import winsound
from brain import brainQ
def play_listen_sound():
    winsound.Beep(1300,150)
def listen():
    r = sr.Recognizer()
    
    text = ''
    with sr.Microphone() as source:
        print("Adjusting for ambient noise... Please wait.")
        r.adjust_for_ambient_noise(source, duration=0.1)
        play_listen_sound()
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
    engine = pyttsx3.init()
    engine.setProperty('rate', 180)
    engine.setProperty('volume',1.0)
    voices  = engine.getProperty("voices")
    engine.setProperty("voice",voices[0].id)
    engine.say(text)
    engine.runAndWait()
if __name__ == "__main__":
    speak("Your rex voice assistant activated")
    while True:
        quary = listen()
        #quary = listen().strip()   
        if quary: 
            if quary.lower().strip() in ["exit" ,"bye","goodbye"]:
                speak("Good bye, sir")
                break
            else:
                answer = brainQ(quary)# ✅ pass correct variable
                speak(answer)
        else:
            print("\nplease Say something")
            speak("Sorry, I didn't get that. Please try again.")