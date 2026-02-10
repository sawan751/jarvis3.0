# Possible System Queries:
# These are examples of queries that would be classified as system tasks based on keywords.
# The system can handle operations related to applications, files, folders, volume, shutdown, etc.
#
# Application Control:
# - Open browser
# - Close application done 
# - Launch program aada hua
# - Start/stop application not complete yet
# - Run executable pta nhi 
#
# File and Folder Operations: ye sb complete
# - Open file
# - Modify file
# - Create folder
# - Delete directory
#
# System Control: ye bhi sb complete
# - Shutdown computer
# - Restart system
# - Increase volume
# - Decrease volume
# - Adjust settings
#
# Window Management: ye sb complete
# - Close window
# - Minimize window
# - Maximize window
#
# Other System Tasks: 
# - Execute command
# - Control panel done 
# - System settings 
# - Browser settings
# - Search in browser
# - Search in files with regex
#
# Note: These queries are detected using keywords like: open, close, modify, volume, shutdown,
# restart, start, stop, launch, run, execute, file, folder, directory, window, application,
# program, browser, settings, control, search

from Backend.system import app_control, volume_control, file_control, system_control, window_control, search_control
def handle_system_query(query):
    """
    Dispatches system queries to appropriate handlers.
    """
    query_lower = query.lower()
    result = ""

    # Application control
    if "open" in query_lower:
        if "browser" in query_lower or "chrome" in query_lower or "firefox" in query_lower:
            app = "browser" if "browser" in query_lower else query_lower.split()[-1]
        else:
            app = query_lower.replace("open", "").strip()
        result = app_control.open_application(app)
    elif "play" in query_lower:
        query_part = query_lower.replace("play", "").strip()
        result = app_control.open_application(f"play {query_part}")
    elif "close" in query_lower and "application" in query_lower:
        app = query_lower.replace("close application", "").strip()
        result = app_control.close_application(app)
    elif "launch" in query_lower or "run" in query_lower:
        program = query_lower.replace("launch", "").replace("run", "").strip()
        result = app_control.launch_program(program)

    # Volume control
    elif "volume" in query_lower:
        import re
        # Check for specific percentage in the query
        percent_match = re.search(r'(\d+)%?', query_lower)
        if percent_match:
            level = int(percent_match.group(1))
            result = volume_control.set_volume(level)
        elif "increase" in query_lower:
            result = volume_control.increase_volume()
        elif "decrease" in query_lower:
            result = volume_control.decrease_volume()
        elif "what" in query_lower or "show" in query_lower:
            current_vol = volume_control._get_current_volume_percent()
            result = f"Current volume is {current_vol}%"
        else:
            level = 50  # default
            result = volume_control.set_volume(level)

    # File control
    elif "open file" in query_lower:
        file_path = query.replace("open file", "").strip()
        result = file_control.open_file(file_path)
    elif "create folder" in query_lower:
        folder_path = query.replace("create folder", "").strip()
        result = file_control.create_folder(folder_path)
    elif "delete" in query_lower:
        if "file" in query_lower:
            file_path = query.replace("delete file", "").strip()
            result = file_control.delete_file(file_path)
        elif "folder" in query_lower:
            folder_path = query.replace("delete folder", "").strip()
            result = file_control.delete_folder(folder_path)

    # System control
    elif "shutdown" in query_lower:
        result = system_control.shutdown_system()
    elif "restart" in query_lower:
        result = system_control.restart_system()
    elif "execute" in query_lower:
        command = query_lower.replace("execute", "").strip()
        result = system_control.execute_command(command)
    elif "settings" in query_lower:
        result = system_control.open_settings()

    # Window control
    elif "close window" in query_lower or "close current window" in query_lower:
        window_title = query_lower.replace("close window", "").strip()
        if window_title:
            result = window_control.close_window(window_title)
        else:
            result = window_control.close_current_window()
    elif "close current tab" in query_lower or ("close" in query_lower and "tab" in query_lower):
        result = window_control.close_current_tab()
    elif "minimize" in query_lower:
        # Check if specific window title is mentioned (after "minimize" keyword)
        window_title = query_lower.replace("minimize", "").replace("window", "").strip()
        result = window_control.minimize_window(window_title)
    elif "maximize" in query_lower:
        # Check if specific window title is mentioned (after "maximize" keyword)
        window_title = query_lower.replace("maximize", "").replace("window", "").strip()
        result = window_control.maximize_window(window_title)

    # Search control
    elif "search" in query_lower:
        if "about" in query_lower:
            search_term = query_lower.replace("search about", "").strip()
            result = app_control.open_browser_with_search(search_term)
        elif "in" in query_lower and "files" in query_lower:
            # Regex search in files
            parts = query_lower.replace("search", "").replace("in files", "").strip()
            pattern = parts.strip()
            result = search_control.search_with_regex(pattern)
        else:
            # Default to web search
            search_term = query_lower.replace("search", "").strip()
            result = app_control.open_browser_with_search(search_term)

    else:
        result = f"System query not recognized: {query}"

    return result