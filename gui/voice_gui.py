"""
Simple PyQt6 Voice GUI with Start/Stop button and animated wave.
"""

from __future__ import annotations

import math
import sys
import time
from dataclasses import dataclass

from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal, QObject, QRectF, QPointF
from PyQt6.QtGui import QColor, QPainter, QPainterPath, QPen, QLinearGradient, QBrush, QFont
from PyQt6.QtWidgets import QApplication, QWidget


# ============ Global State ============

_gui_widget: VoiceWidget | None = None
_listener_worker: ListenerWorker | None = None
_listener_thread: QThread | None = None


# ============ Public API ============

def launch_gui(x: int = -1, y: int = -1, size: int = 320) -> None:
    """Launch the GUI window in-process."""
    global _gui_widget
    
    app = QApplication.instance()
    if app is None:
        app = QApplication([])

    _gui_widget = VoiceWidget(size=size)
    
    # Position: center-bottom if not specified
    screen = app.primaryScreen().availableGeometry()
    if x < 0 or y < 0:
        x = int(screen.x() + (screen.width() - _gui_widget.width()) / 2)
        y = int(screen.y() + screen.height() - _gui_widget.height() - 30)
    
    _gui_widget.move(x, y)
    _gui_widget.show()

    sys.exit(app.exec())


def set_idle() -> None:
    """Set GUI to idle state."""
    if _gui_widget is not None:
        _gui_widget.set_mode("IDLE")


def set_listening() -> None:
    """Set GUI to listening state."""
    if _gui_widget is not None:
        _gui_widget.set_mode("LISTENING")


def set_speaking() -> None:
    """Set GUI to speaking state."""
    if _gui_widget is not None:
        _gui_widget.set_mode("SPEAKING")


def shutdown_gui() -> None:
    """Shutdown GUI cleanly."""
    global _listener_worker, _listener_thread, _gui_widget
    
    try:
        if _listener_worker is not None:
            _listener_worker.stop()
        
        if _listener_thread is not None:
            _listener_thread.quit()
            _listener_thread.wait(2000)
        
        if _gui_widget is not None:
            _gui_widget.close()
        
        app = QApplication.instance()
        if app is not None:
            app.quit()
    except Exception as e:
        print(f"[GUI] Error during shutdown: {e}", flush=True)


# ============ Worker Thread ============

class ListenerWorker(QObject):
    """Worker that runs the listen->process->speak loop in background thread."""
    
    finished = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self._is_running = False
    
    def run(self):
        """Main loop: listen -> process -> speak."""
        import assistant
        
        self._is_running = True
        print("[WORKER] Started", flush=True)
        
        try:
            while self._is_running:
                try:
                    if not self._is_running:
                        break
                    
                    # LISTEN
                    print("[WORKER] Calling listen()...", flush=True)
                    query = assistant.listen()
                    
                    if not self._is_running:
                        break
                    
                    if not query:
                        print("[WORKER] No query, continuing...", flush=True)
                        continue
                    
                    print(f"[WORKER] Got query: {query}", flush=True)
                    
                    # Check exit commands
                    if query.lower().strip() in ["exit", "bye", "goodbye"]:
                        print("[WORKER] Exit command detected", flush=True)
                        try:
                            assistant.speak("Good bye, sir")
                        except Exception as e:
                            print(f"[WORKER] Error in goodbye: {e}", flush=True)
                        break
                    
                    # PROCESS
                    print("[WORKER] Processing query...", flush=True)
                    try:
                        answer = assistant.process_query(query)
                        print(f"[WORKER] Got answer: {answer[:50]}...", flush=True)
                    except Exception as e:
                        print(f"[WORKER] Process error: {e}", flush=True)
                        answer = "Sorry, I couldn't process that."
                    
                    # SPEAK
                    if self._is_running:
                        print("[WORKER] Calling speak()...", flush=True)
                        try:
                            assistant.speak(answer)
                            print("[WORKER] Speak done, waiting 1.5s before next listen...", flush=True)
                            time.sleep(1.5)
                        except Exception as e:
                            print(f"[WORKER] Speak error: {e}", flush=True)
                
                except Exception as e:
                    print(f"[WORKER] Loop error: {e}", flush=True)
                    if self._is_running:
                        time.sleep(0.5)
        
        finally:
            self._is_running = False
            print("[WORKER] Finished", flush=True)
            self.finished.emit()
    
    def stop(self):
        """Signal worker to stop."""
        print("[WORKER] Stop called", flush=True)
        self._is_running = False


# ============ GUI Animation State ============

@dataclass
class GuiState:
    mode: str = "IDLE"  # IDLE | LISTENING | SPEAKING
    phase: float = 0.0
    last_time: float = 0.0


# ============ Main GUI Widget ============

class VoiceWidget(QWidget):
    """Frameless voice widget with animated wave and circular start/stop button."""
    
    def __init__(self, size: int = 320):
        super().__init__()
        global _listener_worker, _listener_thread
        
        # Dimensions
        self.bar_w = size
        self.bar_h = max(54, int(size * 0.16))
        self.setFixedSize(self.bar_w + 100, self.bar_h)  # Extra space for button
        
        # Window setup
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        
        # State
        self.state = GuiState()
        self.is_listening = False
        self.button_hover = False
        
        # Colors
        self.bg_color = QColor(20, 20, 26, 200)
        self.glass_stroke = QColor(255, 255, 255, 40)
        self.wave_colors = [
            QColor(94, 222, 255),
            QColor(170, 120, 255),
            QColor(255, 86, 148),
            QColor(255, 200, 90),
        ]
        self.border_radius = self.bar_h / 2 - 4
        
        # Button
        self.button_size = 70
        self.button_x = 10
        self.button_y = (self.bar_h - self.button_size) // 2
        
        # Animation timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._tick)
        self.timer.start(int(1000 / 60))
        
        # Drag support
        self._drag_pos = None
        
        # Create worker thread (don't start yet)
        _listener_thread = QThread()
        _listener_worker = ListenerWorker()
        _listener_worker.moveToThread(_listener_thread)
        _listener_thread.started.connect(_listener_worker.run)
        _listener_worker.finished.connect(_listener_thread.quit)
    
    def set_mode(self, mode: str):
        """Update animation mode (IDLE, LISTENING, SPEAKING)."""
        self.state.mode = mode
        self.update()
    
    def _on_button_click(self):
        """Handle button click: start or stop listening."""
        global _listener_worker, _listener_thread
        
        if self.is_listening:
            # STOP
            print("[GUI] Stop button clicked", flush=True)
            self.is_listening = False
            if _listener_worker is not None:
                _listener_worker.stop()
            if _listener_thread is not None and _listener_thread.isRunning():
                _listener_thread.quit()
                _listener_thread.wait(2000)
            print("[GUI] Listening stopped", flush=True)
        else:
            # START
            print("[GUI] Start button clicked", flush=True)
            self.is_listening = True
            if _listener_thread is not None and not _listener_thread.isRunning():
                _listener_thread.start()
            print("[GUI] Listening started", flush=True)
        
        self.update()
    
    # ============ Events ============
    
    def mousePressEvent(self, event):
        """Handle mouse press: button click or drag prep."""
        pos = event.position()
        
        # Check if button clicked
        button_center_x = self.button_x + self.button_size / 2
        button_center_y = self.button_y + self.button_size / 2
        dist = math.sqrt(
            (pos.x() - button_center_x) ** 2 + (pos.y() - button_center_y) ** 2
        )
        
        if dist <= self.button_size / 2:
            self._on_button_click()
            event.accept()
            return
        
        # Prepare for drag
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()
    
    def mouseMoveEvent(self, event):
        """Handle drag and button hover."""
        pos = event.position()
        
        # Check button hover
        button_center_x = self.button_x + self.button_size / 2
        button_center_y = self.button_y + self.button_size / 2
        dist = math.sqrt(
            (pos.x() - button_center_x) ** 2 + (pos.y() - button_center_y) ** 2
        )
        
        old_hover = self.button_hover
        self.button_hover = dist <= self.button_size / 2
        if old_hover != self.button_hover:
            self.update()
        
        # Drag
        if self._drag_pos is not None and event.buttons() & Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_pos)
            event.accept()
    
    def mouseReleaseEvent(self, event):
        """Handle mouse release."""
        self._drag_pos = None
        event.accept()
    
    def closeEvent(self, event):
        """Handle window close event."""
        print("[GUI] Window close requested", flush=True)
        shutdown_gui()
        event.accept()
    def _tick(self):
        """Advance animation phase."""
        now = time.time()
        if self.state.last_time == 0:
            self.state.last_time = now
        dt = now - self.state.last_time
        self.state.last_time = now
        
        if self.state.mode == "SPEAKING":
            self.state.phase += 4.0 * dt
        elif self.state.mode == "LISTENING":
            self.state.phase += 0.5 * dt
        else:  # IDLE
            self.state.phase += 0.0
        
        self.update()
    
    def paintEvent(self, event):
        """Draw the widget: pill + wave + button."""
        w, h = self.width(), self.height()
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        
        # ============ Draw Wave Pill ============
        pill_x = 90
        pill_w = self.bar_w
        pill_h = self.bar_h
        
        # Pill background
        rect = QRectF(pill_x + 2, 2, pill_w - 4, pill_h - 4)
        painter.setPen(QPen(self.glass_stroke, 1.5))
        painter.setBrush(QColor(self.bg_color))
        path = QPainterPath()
        path.addRoundedRect(rect, self.border_radius, self.border_radius)
        painter.drawPath(path)
        
        # Wave animation
        mid_y = h / 2
        left = pill_x + 20
        right = pill_x + pill_w - 20
        width = right - left
        
        if self.state.mode == "SPEAKING":
            amp = max(10, int(pill_h * 0.26))
            freq = 3.0
            speed = self.state.phase * 4.0
        elif self.state.mode == "LISTENING":
            amp = max(4, int(pill_h * 0.10))
            freq = 1.2
            speed = self.state.phase * 1.5
        else:  # IDLE
            amp = 2
            freq = 1.0
            speed = 0.0
        
        # Gradient
        grad = QLinearGradient(left, 0, right, 0)
        stops = [0.0, 0.33, 0.66, 1.0]
        for s, c in zip(stops, self.wave_colors):
            grad.setColorAt(s, c)
        
        pen = QPen(QBrush(grad), 3.0 if self.state.mode != "IDLE" else 2.0)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        
        # Draw wave
        path = QPainterPath()
        steps = max(200, int(width))
        for i in range(steps + 1):
            t = i / steps
            x = left + t * width
            envelope = math.sin(math.pi * t)
            y = mid_y + math.sin(t * math.pi * 2 * freq + speed) * (amp * envelope)
            if i == 0:
                path.moveTo(x, y)
            else:
                path.lineTo(x, y)
        
        painter.drawPath(path)
        
        # Glow below wave
        glow = QLinearGradient(left, mid_y, right, mid_y)
        for s, c in zip(stops, self.wave_colors):
            cc = QColor(c)
            cc.setAlpha(80 if self.state.mode != "IDLE" else 40)
            glow.setColorAt(s, cc)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(glow))
        painter.drawRoundedRect(QRectF(left, mid_y + 4, width, 8), 4, 4)
        
        # ============ Draw Circular Button ============
        button_center_x = self.button_x + self.button_size / 2
        button_center_y = self.button_y + self.button_size / 2
        
        # Button colors
        if self.is_listening:
            button_color = QColor(200, 50, 50, 100) if not self.button_hover else QColor(220, 70, 70, 140)
            button_text = "Stop"
        else:
            button_color = QColor(50, 150, 50, 100) if not self.button_hover else QColor(70, 170, 70, 140)
            button_text = "Start"
        
        # Draw button circle
        painter.setPen(QPen(Qt.PenStyle.NoPen))
        painter.setBrush(button_color)
        painter.drawEllipse(QPointF(button_center_x, button_center_y), self.button_size / 2, self.button_size / 2)
        
        # Button border
        painter.setPen(QPen(QColor(255, 255, 255, 70), 2))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(QPointF(button_center_x, button_center_y), self.button_size / 2, self.button_size / 2)
        
        # Button text
        painter.setPen(QColor(255, 255, 255))
        font = QFont()
        font.setBold(True)
        font.setPointSize(11)
        painter.setFont(font)
        painter.drawText(
            QRectF(self.button_x, self.button_y, self.button_size, self.button_size),
            Qt.AlignmentFlag.AlignCenter,
            button_text,
        )
