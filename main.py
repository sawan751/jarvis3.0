from gui.voice_gui import launch_gui, set_idle, set_listening, set_speaking
import assistant

print('Starting voice assistant...', flush=True)

# Register GUI callbacks
assistant.register_gui_callbacks(
    idle_cb=set_idle,
    listening_cb=set_listening,
    speaking_cb=set_speaking
)

print('Launching GUI...', flush=True)
launch_gui()
