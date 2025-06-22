import sys
from PyQt6.QtWidgets import QApplication, QWidget
from PyQt6.QtCore import Qt


class DeskiraApp(QWidget):
    """
    The main application window for Deskira.
    This class creates a semi-transparent, borderless window that stays on top.
    """
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

    def center_window(self):
        """Helper function to center the window on the primary screen."""
        screen_geometry = QApplication.primaryScreen().geometry()
        x = (screen_geometry.width() - self.width()) // 2
        y = (screen_geometry.height() - self.height()) // 2
        self.move(x, y)


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
