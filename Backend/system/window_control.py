import os
import win32gui
import win32con
import win32api
import time
try:
    import win32com.client
except Exception:
    win32com = None

# Import for window placement manipulation
try:
    from ctypes import wintypes, byref, Structure
    import ctypes
    
    class WINDOWPLACEMENT(Structure):
        _fields_ = [
            ('length', wintypes.UINT),
            ('flags', wintypes.UINT),
            ('showCmd', wintypes.UINT),
            ('ptMinPosition', wintypes.POINT),
            ('ptMaxPosition', wintypes.POINT),
            ('rcNormalPosition', wintypes.RECT),
        ]
except Exception:
    WINDOWPLACEMENT = None

def close_current_tab():
    """
    Closes the currently active tab by sending Ctrl+W.
    Works in browsers and tab-based applications.
    """
    try:
        # Prefer SendKeys via WScript.Shell for better compatibility
        if 'win32com' in globals() and win32com is not None:
            shell = win32com.client.Dispatch("WScript.Shell")
            shell.SendKeys('^w')
        else:
            # Fallback to keybd_event
            win32api.keybd_event(win32con.VK_CONTROL, 0, 0, 0)  # Ctrl down
            win32api.keybd_event(ord('W'), 0, 0, 0)              # W down
            time.sleep(0.05)
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
        if 'win32com' in globals() and win32com is not None:
            shell = win32com.client.Dispatch("WScript.Shell")
            shell.SendKeys('%{F4}')
        else:
            # Send Alt+F4 to close the current window
            win32api.keybd_event(win32con.VK_MENU, 0, 0, 0)  # Alt down
            win32api.keybd_event(win32con.VK_F4, 0, 0, 0)    # F4 down
            time.sleep(0.05)
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
        # Try to find window by partial title and send a close message
        if window_title:
            hwnd = _find_window_by_title(window_title)
            if hwnd:
                win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
                return f"Attempted to close window: {window_title}"
            else:
                # Fallback to taskkill filter
                os.system(f"taskkill /f /fi \"WINDOWTITLE eq {window_title}\"")
                return f"Attempted to close window (fallback): {window_title}"
        else:
            # Close foreground window
            hwnd = win32gui.GetForegroundWindow()
            win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
            return "Attempted to close current window"
    except Exception as e:
        return f"Error closing window {window_title}: {str(e)}"

def minimize_window(window_title=""):
    """
    Minimizes a window by title. If no title, minimizes current window.
    Uses WM_SYSCOMMAND for maximum reliability.
    """
    try:
        if window_title:
            hwnd = _find_window_by_title(window_title)
            if not hwnd:
                return f"Window not found: {window_title}"
        else:
            hwnd = win32gui.GetForegroundWindow()
        
        if not hwnd or hwnd == 0:
            return "No window to minimize"
        
        # Verify window exists and get title
        try:
            title = win32gui.GetWindowText(hwnd)
        except Exception:
            return "Error: Window handle is invalid"
        
        # Ensure window is in foreground with focus
        try:
            win32gui.SetForegroundWindow(hwnd)
            time.sleep(0.1)
        except Exception:
            pass
        
        # Method 1: Use PostMessage with WM_SYSCOMMAND (most reliable)
        try:
            win32gui.PostMessage(hwnd, win32con.WM_SYSCOMMAND, win32con.SC_MINIMIZE, 0)
            time.sleep(0.3)
            return f"Minimized: {title or 'current'}"
        except Exception as e1:
            # Method 2: Use ShowWindow directly
            try:
                win32gui.ShowWindow(hwnd, win32con.SW_MINIMIZE)
                time.sleep(0.3)
                return f"Minimized (method 2): {title}"
            except Exception as e2:
                # Method 3: Keyboard shortcut Alt+Space+N
                try:
                    win32gui.SetForegroundWindow(hwnd)
                    time.sleep(0.1)
                    if win32com is not None:
                        shell = win32com.client.Dispatch("WScript.Shell")
                        shell.SendKeys('%{ n}')
                        time.sleep(0.3)
                        return f"Minimized (keyboard): {title}"
                except Exception as e3:
                    return f"Failed to minimize: {str(e1[:50])}"
    except Exception as e:
        return f"Error minimizing window: {str(e)}"


def maximize_window(window_title=""):
    """
    Maximizes a window by title. If no title, maximizes current window.
    Supports both API-based and keyboard shortcut methods.
    """
    try:
        if window_title:
            hwnd = _find_window_by_title(window_title)
            if not hwnd:
                return f"Window not found: {window_title}"
        else:
            hwnd = win32gui.GetForegroundWindow()
        
        if not hwnd:
            return "No window to maximize"
        
        # Verify window exists and is valid
        try:
            title = win32gui.GetWindowText(hwnd)
        except Exception:
            return "Error: Window handle is invalid"
        
        # Bring to foreground to ensure it responds
        try:
            win32gui.SetForegroundWindow(hwnd)
            time.sleep(0.05)
        except Exception:
            pass
        
        # Try showing window in maximized state
        try:
            win32gui.ShowWindow(hwnd, win32con.SW_MAXIMIZE)
            time.sleep(0.1)
            return f"Maximized window: {title or 'current'}"
        except Exception:
            # Fallback: use keyboard shortcut (F11 for fullscreen in many apps)
            if win32com is not None:
                shell = win32com.client.Dispatch("WScript.Shell")
                shell.SendKeys('+{F10}')  # Shift+F10 may maximize in some contexts
            return "Attempted maximize using keyboard shortcut"
    except Exception as e:
        return f"Error maximizing window: {str(e)}"


def _find_window_by_title(partial_title: str):
    """Find top-level window whose title contains partial_title (case-insensitive)."""
    partial = partial_title.lower()
    result = []

    def _enum(hwnd, _ctx):
        if win32gui.IsWindowVisible(hwnd):
            try:
                title = win32gui.GetWindowText(hwnd) or ""
            except Exception:
                title = ""
            if partial in title.lower():
                result.append(hwnd)

    try:
        win32gui.EnumWindows(_enum, None)
        return result[0] if result else None
    except Exception:
        return None
    