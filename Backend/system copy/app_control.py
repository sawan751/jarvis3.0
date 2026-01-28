import os
import subprocess
import platform
import webbrowser
from youtube_search import YoutubeSearch
import urllib.parse

def open_application(app_name):
    """
    Opens an application based on the app_name.
    Supports common apps like browser, notepad, etc.
    Also supports playing songs/videos on YouTube by saying 'play {query}'
    """
    try:
        if platform.system() == "Windows":
            # Check for play command
            if app_name.lower().startswith("play "):
                query = app_name[5:].strip()
                try:
                    results = YoutubeSearch(query, max_results=1).to_dict()
                    if results:
                        video_id = results[0]['id']
                        url = f"https://www.youtube.com/watch?v={video_id}"
                        webbrowser.open(url)
                        return f"Playing '{query}' on YouTube"
                    else:
                        search_url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
                        webbrowser.open(search_url)
                        return f"No results found, searching for '{query}' on YouTube"
                except Exception as e:
                    search_url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
                    webbrowser.open(search_url)
                    return f"Error searching, opened search for '{query}' on YouTube: {str(e)}"
            
            # Map common app names to executables
            app_map = {
                "browser": "msedge",
                "chrome": "chrome",
                "firefox": "firefox",
                "edge": "msedge",
                "notepad": "notepad",
                "calculator": "calc",
                "calc": "calc",
                "explorer": "explorer",
                "cmd": "cmd",
                "powershell": "powershell",
                "wordpad": "wordpad",
                "control panel": "control",
                "control": "control",
                "settings": "control",
                "vscode": "code",
                "visual studio code": "code",
                "whatsapp": "whatsapp",
                "anti gravity": "antigravity",
            }
            if app_name.lower() in app_map:
                exe = app_map[app_name.lower()]
                os.system(f"start {exe}")
                return f"Opened {app_name}"
            else:
                # Try to open as executable
                subprocess.run([app_name], shell=True)
                return f"Attempted to open {app_name}"
        else:
            return f"Platform {platform.system()} not fully supported yet"
    except Exception as e:
        return f"Error opening {app_name}: {str(e)}"

def close_application(app_name):
    """
    Closes an application by name.
    Note: This is basic; for better control, might need psutil.
    """
    try:
        if platform.system() == "Windows":
            # Map common app names to executables
            app_map = {
                "browser": "msedge",
                "chrome": "chrome",
                "firefox": "firefox",
                "edge": "msedge",
                "notepad": "notepad",
                "calculator": "calc",
                "calc": "calc",
                "explorer": "explorer",
                "cmd": "cmd",
                "powershell": "powershell",
                "wordpad": "wordpad",
                "control panel": "control",
                "control": "control",
                "settings": "control",
                "vscode": "code",
                "visual studio code": "code",
                "whatsapp": "whatsapp",
                "anti gravity": "antigravity",
            }
            if app_name.lower() in app_map:
                exe = app_map[app_name.lower()]
                os.system(f"taskkill /f /im {exe}.exe")
                return f"Closed {app_name}"
            else:
                os.system(f"taskkill /f /im {app_name}.exe")
                return f"Closed {app_name}"
        else:
            return f"Platform {platform.system()} not supported"
    except Exception as e:
        return f"Error closing {app_name}: {str(e)}"

def launch_program(program_path):
    """
    Launches a program from a given path or name.
    """
    try:
        # Map common app names to executables
        app_map = {
            "browser": "msedge",
            "chrome": "chrome",
            "firefox": "firefox",
            "edge": "msedge",
            "notepad": "notepad",
            "calculator": "calc",
            "calc": "calc",
            "explorer": "explorer",
            "cmd": "cmd",
            "powershell": "powershell",
            "wordpad": "wordpad",
            "control panel": "control",
            "control": "control",
            "settings": "control",
            "vscode": "code",
            "visual studio code": "code",
            "whatsapp": "whatsapp",
            "anti gravity": "antigravity",
        }
        if program_path.lower() in app_map:
            exe = app_map[program_path.lower()]
            os.system(f"start {exe}")
            return f"Launched {program_path}"
        else:
            os.startfile(program_path)
            return f"Launched {program_path}"
    except Exception as e:
        return f"Error launching {program_path}: {str(e)}"

def start_stop_application(app_name, action):
    """
    Starts or stops an application.
    action: 'start' or 'stop'
    """
    if action == "start":
        return open_application(app_name)
    elif action == "stop":
        return close_application(app_name)
    else:
        return f"Invalid action: {action}"

def open_browser_with_search(query):
    """
    Opens the default browser (Edge on Windows) with a Bing search for the query.
    """
    try:
        search_url = f"https://www.bing.com/search?q={urllib.parse.quote(query)}"
        webbrowser.open(search_url)
        return f"Searching for '{query}' in browser"
    except Exception as e:
        return f"Error opening browser for search: {str(e)}"