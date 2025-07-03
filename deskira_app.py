import sys
import threading
from typing import Dict, Callable

from pynput import keyboard
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout


class DeskiraApp(QWidget):
    """
    The main application window for Deskira.
    This class creates a semi-transparent, borderless window that stays on top,
    can be toggled with a global hotkey, and can be moved with hotkeys.
    """
    toggle_visibility_signal = pyqtSignal()
    move_window_signal = pyqtSignal(str)
    quit_app_signal = pyqtSignal()

    MOVE_INCREMENT: int = 30

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Deskira")

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint
        )

        self.setWindowOpacity(0.85)
        self.setStyleSheet("""
            background-color: #2E2E2E;
            color: #FFFFFF;
            font-size: 16px;
        """)
        self.resize(800, 600)
        self.center_window()

        self.setup_ui()

        self.toggle_visibility_signal.connect(self.toggle_visibility)  # type: ignore
        self.move_window_signal.connect(self.move_window)  # type: ignore
        self.quit_app_signal.connect(self.quit_app)  # type: ignore

        self.hotkey_listener_thread = threading.Thread(target=self.setup_hotkey_listener, daemon=True)
        self.hotkey_listener_thread.start()

        self.show()

    def setup_ui(self) -> None:
        """Creates and arranges UI widgets."""
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        instructions_text = (
            "Welcome to Deskira!\n\n"
            "Hotkeys:\n"
            "  - Cmd + B: Show / Hide Window\n"
            "  - Cmd + Arrow Keys: Move Window\n"
            "  - Cmd + Q: Quit Application"
        )
        instructions_label = QLabel(instructions_text)
        instructions_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        instructions_label.setWordWrap(True)

        layout.addWidget(instructions_label)
        self.setLayout(layout)

    def center_window(self) -> None:
        """Helper function to center the window on the primary screen."""
        primary_screen = QApplication.primaryScreen()
        if primary_screen:
            screen_geometry = primary_screen.geometry()
            x = (screen_geometry.width() - self.width()) // 2
            y = (screen_geometry.height() - self.height()) // 2
            self.move(x, y)

    def toggle_visibility(self) -> None:
        """Shows the window if it's hidden, and hides it if it's visible."""
        if self.isVisible():
            self.hide()
        else:
            self.center_window()
            self.show()
            self.activateWindow()

    def move_window(self, direction: str) -> None:
        """Moves the window in the specified direction."""
        if not self.isVisible():
            return

        current_pos = self.pos()
        new_x, new_y = current_pos.x(), current_pos.y()

        if direction == "up":
            new_y -= self.MOVE_INCREMENT
        elif direction == "down":
            new_y += self.MOVE_INCREMENT
        elif direction == "left":
            new_x -= self.MOVE_INCREMENT
        elif direction == "right":
            new_x += self.MOVE_INCREMENT

        self.move(new_x, new_y)

    def quit_app(self) -> None:
        """Safely quits the QApplication."""
        app_instance = QApplication.instance()
        if app_instance:
            app_instance.quit()

    # --- REFACTORED: Hotkey listener now uses the robust keyboard.HotKey class ---
    def setup_hotkey_listener(self) -> None:
        """
        Sets up and runs the pynput keyboard listener using the HotKey class
        for robust, system-wide hotkey registration and suppression.
        """
        # Define hotkeys and the functions they should call.
        # The functions emit signals to the main GUI thread.
        hotkey_actions: Dict[str, Callable[[], None]] = {
            '<cmd>+b': lambda: self.toggle_visibility_signal.emit(),
            '<cmd>+q': lambda: self.quit_app_signal.emit(),
            '<cmd>+<up>': lambda: self.move_window_signal.emit("up"),
            '<cmd>+<down>': lambda: self.move_window_signal.emit("down"),
            '<cmd>+<left>': lambda: self.move_window_signal.emit("left"),
            '<cmd>+<right>': lambda: self.move_window_signal.emit("right"),
        }

        # Create a pynput global hotkey listener.
        # This listener is more reliable for this specific task.
        listener = keyboard.GlobalHotKeys(hotkey_actions)
        listener.start()
        listener.join()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DeskiraApp()
    sys.exit(app.exec())
