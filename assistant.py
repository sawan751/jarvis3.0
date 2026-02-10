import os
import time
from dotenv import load_dotenv

# Audio / TTS / STT
import speech_recognition as sr
import winsound
import pyttsx3
import soundfile as sf
import sounddevice as sd
from elevenlabs import ElevenLabs

# Backend brain
from Backend import brain

# Load env
env_file = 'api.env'
load_dotenv(env_file)

# GUI callbacks
_set_idle_cb = lambda: None
_set_listening_cb = lambda: None
_set_speaking_cb = lambda: None


def register_gui_callbacks(idle_cb=None, listening_cb=None, speaking_cb=None):
    """Register GUI callbacks for state updates."""
    global _set_idle_cb, _set_listening_cb, _set_speaking_cb
    if idle_cb is not None:
        _set_idle_cb = idle_cb
    if listening_cb is not None:
        _set_listening_cb = listening_cb
    if speaking_cb is not None:
        _set_speaking_cb = speaking_cb


def set_idle():
    """Notify GUI to set idle state."""
    try:
        _set_idle_cb()
    except Exception:
        pass


def set_listening():
    """Notify GUI to set listening state."""
    try:
        _set_listening_cb()
    except Exception:
        pass


def set_speaking():
    """Notify GUI to set speaking state."""
    try:
        _set_speaking_cb()
    except Exception:
        pass


def play_listen_sound():
    """Play a beep sound."""
    try:
        winsound.Beep(1300, 150)
    except Exception:
        pass


def listen():
    """Listen for speech and return recognized text."""
    print("[LISTEN] Starting listen cycle", flush=True)
    r = sr.Recognizer()

    r.energy_threshold = 300
    r.dynamic_energy_threshold = True
    r.dynamic_energy_adjustment_damping = 0.15
    r.dynamic_energy_ratio = 1.5

    text = ''

    try:
        with sr.Microphone() as source:
            print("[LISTEN] Microphone opened, adjusting for ambient noise...", flush=True)
            r.adjust_for_ambient_noise(source, duration=1.5)
            print(f"[LISTEN] Energy threshold: {r.energy_threshold:.1f}", flush=True)

            set_listening()
            print("[LISTEN] Listening now... Speak clearly", flush=True)

            try:
                audio = r.listen(source, timeout=5, phrase_time_limit=8)
                print("[LISTEN] Audio captured, processing...", flush=True)
                text = r.recognize_google(audio, language="en-IN")
                print(f"[LISTEN] You said: {text}", flush=True)

            except sr.WaitTimeoutError:
                print("[LISTEN] No speech detected within timeout.", flush=True)
                text = ""

            except sr.UnknownValueError:
                play_listen_sound()
                print("[LISTEN] Google could not understand the audio", flush=True)
                text = ""

            except sr.RequestError as e:
                print(f"[LISTEN] Google service error: {e}", flush=True)
                text = ""
    except Exception as e:
        print(f"[LISTEN] Microphone error: {e}", flush=True)
        text = ""
    finally:
        print("[LISTEN] Setting idle state", flush=True)
        set_idle()
        print("[LISTEN] Listen cycle complete\n", flush=True)
    
    return text.strip()


# ElevenLabs client
api_key = os.getenv("ELEVENLABS_API_KEY")
client = None
if api_key:
    try:
        client = ElevenLabs(api_key=api_key)
    except Exception:
        client = None


def speak(text: str):
    """Speak text using ElevenLabs or pyttsx3."""
    global client
    print(f"[SPEAK] Starting to speak: {text[:50]}...", flush=True)
    
    try:
        if client is not None:
            print("[SPEAK] Using ElevenLabs", flush=True)
            try:
                audio_stream = client.text_to_speech.convert(
                    text=text,
                    voice_id="TX3LPaxmHKxFdv7VOQHJ",
                    model_id="eleven_multilingual_v2",
                )
                audio_bytes = b"".join(chunk for chunk in audio_stream)
                print(f"[SPEAK] Got {len(audio_bytes)} bytes from ElevenLabs", flush=True)

                set_speaking()
                with open("output.wav", "wb") as f:
                    f.write(audio_bytes)
                print("[SPEAK] Wrote WAV file", flush=True)

                data, samplerate = sf.read("output.wav")
                print(f"[SPEAK] Read WAV: {len(data)} samples at {samplerate} Hz", flush=True)
                
                sd.play(data, samplerate)
                print("[SPEAK] Audio playing... waiting for completion", flush=True)
                
                sd.wait()
                print("[SPEAK] Audio complete", flush=True)
                time.sleep(1.0)  # Extra buffer
                sd.stop()
                print("[SPEAK] Playback stopped", flush=True)
                
            except Exception as e:
                print(f"[SPEAK] ElevenLabs error: {e}", flush=True)
                raise

        else:
            raise RuntimeError("No ElevenLabs client configured")

    except Exception as e:
        print(f"[SPEAK] Trying pyttsx3 fallback: {e}", flush=True)
        try:
            set_speaking()
            engine = pyttsx3.init("sapi5")
            engine.setProperty("rate", 165)
            engine.setProperty("volume", 1.0)
            for v in engine.getProperty("voices"):
                if "zira" in v.name.lower():
                    engine.setProperty("voice", v.id)
                    break
            
            print("[SPEAK] pyttsx3 speaking...", flush=True)
            engine.say(text)
            engine.runAndWait()
            print("[SPEAK] pyttsx3 complete, sleeping 1 second", flush=True)
            time.sleep(1.0)

        except Exception as e2:
            print(f"[SPEAK] pyttsx3 failed: {e2}", flush=True)

    finally:
        print("[SPEAK] Setting idle state\n", flush=True)
        set_idle()


def process_query(query: str) -> str:
    """Process query and return answer from brain."""
    try:
        return brain.brainQ(query)
    except Exception as e:
        print("Error in brain processing:", e)
        return "Sorry, I couldn't process that."
