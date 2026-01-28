import math
import socket
import sys
import time
from multiprocessing import Process
from dataclasses import dataclass

from PyQt6.QtCore import Qt, QTimer, QPointF, QRectF
from PyQt6.QtGui import QColor, QPainter, QPainterPath, QPen, QLinearGradient, QBrush
from PyQt6.QtWidgets import QApplication, QWidget
from PyQt6.QtCore import QSocketNotifier


# Public API (call from your backend)
_gui_process: Process | None = None
_gui_addr: tuple[str, int] | None = None

DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 51235


# ============ Public control functions ============

def launch_gui(host: str = DEFAULT_HOST, port: int = DEFAULT_PORT, x: int = -1, y: int = -1, size: int = 320) -> None:
    """
    Launch the GUI in a separate process. Subsequent calls to set_listening/set_speaking/set_idle
    will control the GUI state via UDP messages.
    """
    global _gui_process, _gui_addr
    if _gui_process is not None and _gui_process.is_alive():
        return

    _gui_addr = (host, port)

    p = Process(target=_run_gui_server, args=(host, port, x, y, size), daemon=True)
    p.start()
    _gui_process = p


def set_idle() -> None:
    _send_cmd("STATE:IDLE")


def set_listening() -> None:
    _send_cmd("STATE:LISTENING")


def set_speaking() -> None:
    _send_cmd("STATE:SPEAKING")


def minimize_gui() -> None:
    _send_cmd("MINIMIZE")


def restore_gui() -> None:
    _send_cmd("RESTORE")


def shutdown_gui() -> None:
    global _gui_process
    _send_cmd("QUIT")
    # Allow the GUI to shutdown gracefully
    if _gui_process is not None:
        for _ in range(20):  # ~2s grace
            if not _gui_process.is_alive():
                break
            time.sleep(0.1)
        _gui_process = None


# ============ Internal helpers ============

def _send_cmd(msg: str) -> None:
    global _gui_addr
    if _gui_addr is None:
        # Default to localhost:DEFAULT_PORT if launch_gui() not called yet
        _gui_addr = (DEFAULT_HOST, DEFAULT_PORT)
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.sendto(msg.encode("utf-8"), _gui_addr)
    except OSError:
        pass


# ============ GUI Process ============

@dataclass
class GuiState:
    mode: str = "IDLE"  # IDLE | LISTENING | SPEAKING
    phase: float = 0.0
    last_time: float = 0.0


class VoiceWidget(QWidget):
    def __init__(self, size: int = 320):
        super().__init__()
        # Pill bar sizing
        self.bar_w = size
        self.bar_h = max(54, int(size * 0.16))
        self.setFixedSize(self.bar_w, self.bar_h)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )

        self.state = GuiState()

        # Animation timer (60 FPS)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._tick)
        self.timer.start(int(1000 / 60))

        # Dragging support
        self._drag_pos = None

        # Styling
        self.bg_color = QColor(20, 20, 26, 200)
        self.glass_stroke = QColor(255, 255, 255, 40)
        self.wave_colors = [QColor(94, 222, 255), QColor(170, 120, 255), QColor(255, 86, 148), QColor(255, 200, 90)]
        self.border_radius = self.bar_h / 2 - 4

    # -------------- Public API --------------
    def set_mode(self, mode: str):
        self.state.mode = mode
        self.update()

    # -------------- Events --------------
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if self._drag_pos is not None and event.buttons() & Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        self._drag_pos = None
        event.accept()

    def _tick(self):
        # Advance phase depending on mode
        now = time.time()
        if self.state.last_time == 0:
            self.state.last_time = now
        dt = now - self.state.last_time
        self.state.last_time = now

        if self.state.mode == "SPEAKING":
            self.state.phase += 4.0 * dt
        elif self.state.mode == "LISTENING":
            self.state.phase += 0.5 * dt  # very slow, subtle pulse
        else:  # IDLE
            self.state.phase += 0.0
        self.update()

    # -------------- Painting --------------
    def paintEvent(self, event):
        w, h = self.width(), self.height()
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        # Glassmorphism pill background
        rect = QRectF(2, 2, w - 4, h - 4)
        painter.setPen(QPen(self.glass_stroke, 1.5))
        painter.setBrush(QColor(self.bg_color))
        path = QPainterPath()
        path.addRoundedRect(rect, self.border_radius, self.border_radius)
        painter.drawPath(path)

        # Wave line across the pill
        mid_y = h / 2
        left = 20
        right = w - 20
        width = right - left

        if self.state.mode == "SPEAKING":
            amp = max(10, int(h * 0.26))
            freq = 3.0
            speed = self.state.phase * 4.0
        elif self.state.mode == "LISTENING":
            amp = max(4, int(h * 0.10))
            freq = 1.2
            speed = self.state.phase * 1.5
        else:  # IDLE
            amp = 2
            freq = 1.0
            speed = 0.0

        # Multi-color gradient
        grad = QLinearGradient(left, 0, right, 0)
        stops = [0.0, 0.33, 0.66, 1.0]
        for s, c in zip(stops, self.wave_colors):
            grad.setColorAt(s, c)

        pen = QPen(QBrush(grad), 3.0 if self.state.mode != "IDLE" else 2.0)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)

        path = QPainterPath()
        steps = max(200, int(width))
        for i in range(steps + 1):
            t = i / steps
            x = left + t * width
            # Center-weighted envelope: 0 at edges, 1 at center
            envelope = math.sin(math.pi * t)
            y = mid_y + math.sin(t * math.pi * 2 * freq + speed) * (amp * envelope)
            if i == 0:
                path.moveTo(x, y)
            else:
                path.lineTo(x, y)

        painter.drawPath(path)

        # Soft glow below wave
        glow = QLinearGradient(left, mid_y, right, mid_y)
        for s, c in zip(stops, self.wave_colors):
            cc = QColor(c)
            cc.setAlpha(80 if self.state.mode != "IDLE" else 40)
            glow.setColorAt(s, cc)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(glow))
        painter.drawRoundedRect(QRectF(left, mid_y + 4, width, 8), 4, 4)


class UdpControl:
    def __init__(self, host: str, port: int, widget: VoiceWidget):
        self.widget = widget
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setblocking(False)
        self.sock.bind((host, port))
        self.notifier = QSocketNotifier(self.sock.fileno(), QSocketNotifier.Type.Read)
        self.notifier.activated.connect(self._on_ready_read)

    def _on_ready_read(self):
        try:
            while True:
                data, _addr = self.sock.recvfrom(4096)
                msg = data.decode("utf-8", errors="ignore").strip()
                if msg.startswith("STATE:"):
                    state = msg.split(":", 1)[1].strip().upper()
                    if state in ("IDLE", "LISTENING", "SPEAKING"):
                        self.widget.set_mode(state)
                elif msg == "MINIMIZE":
                    self.widget.showMinimized()
                elif msg == "RESTORE":
                    self.widget.showNormal()
                    self.widget.setWindowFlags(
                        Qt.WindowType.FramelessWindowHint
                        | Qt.WindowType.WindowStaysOnTopHint
                        | Qt.WindowType.Tool
                    )
                    self.widget.show()
                elif msg == "QUIT":
                    QApplication.instance().quit()
                    return
        except BlockingIOError:
            pass
        except OSError:
            pass


def _run_gui_server(host: str, port: int, x: int, y: int, size: int):
    # Separate process: runs Qt event loop
    app = QApplication(["VoiceGUI"])  # stand-alone app name
    widget = VoiceWidget(size=size)
    # Bottom-center placement if x/y negative
    screen = app.primaryScreen().availableGeometry()
    if x < 0 or y < 0:
        x = int(screen.x() + (screen.width() - widget.width()) / 2)
        y = int(screen.y() + screen.height() - widget.height() - 30)
    widget.move(x, y)
    widget.show()

    _ = UdpControl(host, port, widget)

    sys.exit(app.exec())
