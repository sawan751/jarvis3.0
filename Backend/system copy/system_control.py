import os
import platform

def shutdown_system():
    """
    Shuts down the system.
    """
    try:
        if platform.system() == "Windows":
            os.system("shutdown /s /t 1")
            return "Shutting down system"
        else:
            return f"Shutdown not implemented for {platform.system()}"
    except Exception as e:
        return f"Error shutting down: {str(e)}"

def restart_system():
    """
    Restarts the system.
    """
    try:
        if platform.system() == "Windows":
            os.system("shutdown /r /t 1")
            return "Restarting system"
        else:
            return f"Restart not implemented for {platform.system()}"
    except Exception as e:
        return f"Error restarting: {str(e)}"

def execute_command(command):
    """
    Executes a system command.
    """
    try:
        result = os.system(command)
        return f"Executed: {command} (exit code: {result})"
    except Exception as e:
        return f"Error executing {command}: {str(e)}"

def open_settings():
    """
    Opens system settings.
    """
    try:
        if platform.system() == "Windows":
            os.system("start ms-settings:")
            return "Opened settings"
        else:
            return f"Settings not implemented for {platform.system()}"
    except Exception as e:
        return f"Error opening settings: {str(e)}"