from PIL import Image, ImageDraw
import pystray
import webbrowser
import threading
from backend.config import PORT

def create_jarvis_icon():
    """Generates an Arc Reactor style glowing icon for the system tray."""
    width, height = 64, 64
    image = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    
    # Outer circle cyan glow
    draw.ellipse([4, 4, 60, 60], outline=(0, 210, 255, 255), width=3)
    # Inner ring
    draw.ellipse([14, 14, 50, 50], outline=(0, 255, 255, 200), width=2)
    # Core circle
    draw.ellipse([22, 22, 42, 42], fill=(0, 220, 255, 255))
    # Highlights
    draw.line([(32, 6), (32, 14)], fill=(255, 255, 255, 255), width=2)
    draw.line([(32, 50), (32, 58)], fill=(255, 255, 255, 255), width=2)
    draw.line([(6, 32), (14, 32)], fill=(255, 255, 255, 255), width=2)
    draw.line([(50, 32), (58, 32)], fill=(255, 255, 255, 255), width=2)
    
    return image

def launch_tray(on_quit_callback=None, toggle_listening_callback=None):
    icon_image = create_jarvis_icon()

    def open_web(icon, item):
        webbrowser.open(f"http://localhost:{PORT}")

    def quit_app(icon, item):
        icon.stop()
        if on_quit_callback:
            on_quit_callback()

    menu = pystray.Menu(
        pystray.MenuItem("J.A.R.V.I.S. Personal AI", None, enabled=False),
        pystray.MenuItem("Open Interface (Mobile/Web)", open_web, default=True),
        pystray.MenuItem("Exit Jarvis", quit_app)
    )

    icon = pystray.Icon("JARVIS", icon_image, "J.A.R.V.I.S. Assistant (Active)", menu)
    icon.run()
