# volume_control.py
import ctypes
import comtypes
from ctypes import POINTER, cast
from comtypes import CLSCTX_ALL, GUID
from pycaw.pycaw import (
    IAudioEndpointVolume,
    IMMDeviceEnumerator,
    EDataFlow,
    ERole
)

# Required GUIDs for direct device enumeration
CLSID_MMDeviceEnumerator = GUID("{BCDE0395-E52F-467C-8E3D-C4579291692E}")

def _get_volume_interface():
    """
    Reliably gets the master volume interface using multiple fallback methods.
    Works on Windows 10/11 even with Spatial Sound or exclusive-mode apps.
    """
    comtypes.CoInitialize()

    # Method 1: Direct default endpoint via enumerator with eConsole
    try:
        enumerator = comtypes.CoCreateInstance(
            CLSID_MMDeviceEnumerator,
            IMMDeviceEnumerator,
            comtypes.CLSCTX_INPROC_SERVER
        )
        default_device = enumerator.GetDefaultAudioEndpoint(
            EDataFlow.eRender.value,  # Playback
            ERole.eConsole.value      # Default for console apps (games, media, etc.)
        )
        interface = default_device.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        return cast(interface, POINTER(IAudioEndpointVolume))
    except Exception as e:
        print(f"[Volume] Direct enumeration with eConsole failed: {e}")

    # Method 2: Fallback - try eMultimedia role
    try:
        enumerator = comtypes.CoCreateInstance(
            CLSID_MMDeviceEnumerator,
            IMMDeviceEnumerator,
            comtypes.CLSCTX_INPROC_SERVER
        )
        default_device = enumerator.GetDefaultAudioEndpoint(
            EDataFlow.eRender.value,
            ERole.eMultimedia.value
        )
        interface = default_device.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        return cast(interface, POINTER(IAudioEndpointVolume))
    except:
        pass

    raise Exception("Could not access any audio endpoint. Try running as Administrator or disabling Spatial Sound.")

def _get_current_volume_percent() -> int:
    try:
        volume = _get_volume_interface()
        return round(volume.GetMasterVolumeLevelScalar() * 100)
    except:
        return -1

def set_volume(level: int) -> str:
    """
    Sets system volume to a specific percentage (0–100).
    Called when query has 'volume' but no increase/decrease.
    """
    level = max(0, min(100, level))
    try:
        volume = _get_volume_interface()
        volume.SetMasterVolumeLevelScalar(level / 100.0, None)
        return f"Volume set to {level}%"
    except Exception as e:
        return f"Failed to set volume: {str(e)}"

def increase_volume(amount: int = 10) -> str:
    """
    Increases volume by given amount (default 10%).
    """
    try:
        current = _get_current_volume_percent()
        if current == -1:
            return "Could not read current volume level."
        
        new_level = min(100, current + amount)
        volume = _get_volume_interface()
        volume.SetMasterVolumeLevelScalar(new_level / 100.0, None)
        return f"Volume increased to {new_level}%"
    except Exception as e:
        return f"Failed to increase volume: {str(e)}"

def decrease_volume(amount: int = 10) -> str:
    """
    Decreases volume by given amount (default 10%).
    """
    try:
        current = _get_current_volume_percent()
        if current == -1:
            return "Could not read current volume level."
        
        new_level = max(0, current - amount)
        volume = _get_volume_interface()
        volume.SetMasterVolumeLevelScalar(new_level / 100.0, None)
        return f"Volume decreased to {new_level}%"
    except Exception as e:
        return f"Failed to decrease volume: {str(e)}"

# Optional: Add mute/unmute if you want to expand later
def mute() -> str:
    try:
        volume = _get_volume_interface()
        volume.SetMute(1, None)
        return "System muted"
    except Exception as e:
        return f"Failed to mute: {str(e)}"

def unmute() -> str:
    try:
        volume = _get_volume_interface()
        volume.SetMute(0, None)
        return "System unmuted"
    except Exception as e:
        return f"Failed to unmute: {str(e)}"