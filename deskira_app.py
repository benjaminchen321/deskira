import sys
from PyQt6.QtWidgets import QApplication, QWidget
from PyQt6.QtCore import Qt, pyqtSignal
from pynput import keyboard
import threading


class DeskiraApp(QWidget):
    """
    The main application window for Deskira.
    This class creates a semi-transparent, borderless window that stays on top.
    """
    # --- NEW: Signal for thread-safe UI updates ---
    # A signal is used to communicate from the non-GUI hotkey listener thread
    # to the main GUI thread.
    toggle_visibility_signal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Deskira")

        # --- Window Flags ---
        # These flags define the window's appearance and behavior.
        # Qt.WindowType.FramelessWindowHint: Removes the window frame (title bar, buttons).
        # Qt.WindowType.WindowStaysOnTopHint: Ensures the window is always on top of others.
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint
        )

        # --- Appearance ---
        # Set the opacity of the window (0.0 = fully transparent, 1.0 = fully opaque).
        self.setWindowOpacity(0.9)

        # Set the background color of the window using a stylesheet.
        # Without a color, a transparent window would be invisible.
        self.setStyleSheet("background-color: #828282;")

        # --- Size and Position ---
        # Set a default size for the window.
        self.resize(1000, 1000)

        # Center the window on the screen.
        self.center_window()

        # --- NEW: Connect the signal to the slot (the function to execute) ---
        self.toggle_visibility_signal.connect(self.toggle_visibility)

        # --- NEW: Set up and start the hotkey listener in a separate thread ---
        self.hotkey_listener_thread = threading.Thread(target=self.setup_hotkey_listener, daemon=True)
        self.hotkey_listener_thread.start()

        # --- NEW: Keep track of the window's initial state ---
        # We start hidden so the first hotkey press shows the window.
        self.hide()

    def center_window(self):
        """Helper function to center the window on the primary screen."""
        screen_geometry = QApplication.primaryScreen().geometry()
        x = (screen_geometry.width() - self.width()) // 2
        y = (screen_geometry.height() - self.height()) // 2
        self.move(x, y)

    # --- NEW: Slot to toggle window visibility ---
    def toggle_visibility(self):
        """Shows the window if it's hidden, and hides it if it's visible."""
        if self.isVisible():
            self.hide()
        else:
            # We re-center the window every time it's shown.
            self.center_window()
            self.show()
            self.activateWindow()  # Bring window to the front

    # --- NEW: Hotkey listener setup ---
    def setup_hotkey_listener(self):
        """
        Sets up and runs the pynput keyboard listener.
        This function runs in a separate thread.
        """
        # The key combination to listen for.
        # For macOS, Command is keyboard.Key.cmd
        HOTKEYS = {
            keyboard.Key.cmd,
            keyboard.KeyCode(char='b')
        }
        current_keys = set()

        def on_press(key):
            if key in HOTKEYS:
                current_keys.add(key)
                if all(k in current_keys for k in HOTKEYS):
                    # When the combination is pressed, emit the signal.
                    self.toggle_visibility_signal.emit()

        def on_release(key):
            try:
                current_keys.remove(key)
            except KeyError:
                pass  # Key was not in the set

        # The listener will run in this thread until the main app closes.
        with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
            listener.join()


# --- Main Execution Block ---
# This is the entry point of our application.
if __name__ == "__main__":
    # Create the application instance. sys.argv allows command-line arguments.
    app = QApplication(sys.argv)

    # Create an instance of our main window.
    window = DeskiraApp()

    # Show the window on the screen.
    window.show()

    # Start the application's event loop. This keeps the window open.
    # sys.exit() ensures a clean exit.
    sys.exit(app.exec())
