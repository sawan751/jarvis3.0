import os
import win32gui
import win32con
import win32api
import time

def close_current_tab():
    """
    Closes the currently active tab by sending Ctrl+W.
    Works in browsers and tab-based applications.
    """
    try:
        # Send Ctrl+W to close the current tab
        win32api.keybd_event(win32con.VK_CONTROL, 0, 0, 0)  # Ctrl down
        win32api.keybd_event(ord('W'), 0, 0, 0)              # W down
        time.sleep(0.1)
        win32api.keybd_event(ord('W'), 0, win32con.KEYEVENTF_KEYUP, 0)  # W up
        win32api.keybd_event(win32con.VK_CONTROL, 0, win32con.KEYEVENTF_KEYUP, 0)  # Ctrl up
        return "Closed current tab"
    except Exception as e:
        return f"Error closing current tab: {str(e)}"

def close_current_window():
    """
    Closes the currently active (foreground) window by sending Alt+F4.
    """
    try:
        # Send Alt+F4 to close the current window
        win32api.keybd_event(win32con.VK_MENU, 0, 0, 0)  # Alt down
        win32api.keybd_event(win32con.VK_F4, 0, 0, 0)    # F4 down
        time.sleep(0.1)
        win32api.keybd_event(win32con.VK_F4, 0, win32con.KEYEVENTF_KEYUP, 0)  # F4 up
        win32api.keybd_event(win32con.VK_MENU, 0, win32con.KEYEVENTF_KEYUP, 0)  # Alt up
        return "Closed current window"
    except Exception as e:
        return f"Error closing current window: {str(e)}"

def close_window(window_title):
    """
    Closes a window by title (basic implementation).
    Note: Requires external tools like nircmd for better control.
    """
    try:
        # This is a placeholder; actual implementation might need win32api or similar
        os.system(f"taskkill /f /fi \"WINDOWTITLE eq {window_title}\"")
        return f"Attempted to close window: {window_title}"
    except Exception as e:
        return f"Error closing window {window_title}: {str(e)}"

def minimize_window(window_title):
    """
    Minimizes a window by title. If no title, minimizes current window.
    """
    try:
        if window_title:
            hwnd = win32gui.FindWindow(None, window_title)
            if hwnd:
                win32gui.ShowWindow(hwnd, win32con.SW_MINIMIZE)
                return f"Minimized window: {window_title}"
            else:
                return f"Window not found: {window_title}"
        else:
            hwnd = win32gui.GetForegroundWindow()
            win32gui.ShowWindow(hwnd, win32con.SW_MINIMIZE)
            return "Minimized the current window"
    except Exception as e:
        return f"Error minimizing window: {str(e)}"


def maximize_window(window_title):
    """
    Maximizes a window by title. If no title, maximizes current window.
    """
    try:
        if window_title:
            hwnd = win32gui.FindWindow(None, window_title)
            if hwnd:
                win32gui.ShowWindow(hwnd, win32con.SW_MAXIMIZE)
                return f"Maximized window: {window_title}"
            else:
                return f"Window not found: {window_title}"
        else:
            hwnd = win32gui.GetForegroundWindow()
            win32gui.ShowWindow(hwnd, win32con.SW_MAXIMIZE)
            return "Maximized the current window"
    except Exception as e:
        return f"Error maximizing window: {str(e)}"