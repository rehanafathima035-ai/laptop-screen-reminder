"""Play the full transparent Pond walking GIF for each water reminder."""
from __future__ import annotations

import base64
import io
import json
import os
import subprocess
import sys
import tkinter as tk
from pathlib import Path

# Pillow is installed in the base Python. Make it visible when this script is
# launched from the project venv, which does not include system site packages.
try:
    from PIL import Image
except ModuleNotFoundError:
    shared_packages = Path(sys.base_prefix) / "Lib" / "site-packages"
    if shared_packages.is_dir():
        sys.path.insert(0, str(shared_packages))
    from PIL import Image


HERE = Path(__file__).resolve().parent
SETTINGS_FILE = HERE / "settings.json"
DEFAULTS = {"interval_minutes": 60, "image": "walk_animation_source.gif"}
TRANSPARENT = "#ff00ff"


def load_settings():
    try:
        values = json.loads(SETTINGS_FILE.read_text(encoding="utf-8"))
        return {**DEFAULTS, **values}
    except (OSError, json.JSONDecodeError):
        return DEFAULTS.copy()


class Reminder:
    def __init__(self):
        self.root = tk.Tk()
        self.root.withdraw()
        self.root.title("Pond Water Reminder")
        self.root.resizable(False, False)
        self.root.configure(bg=TRANSPARENT)
        self.root.attributes("-topmost", True)
        self.root.overrideredirect(True)
        self.root.wm_attributes("-transparentcolor", TRANSPARENT)

        self.settings = load_settings()
        self.frames: list[tk.PhotoImage] = []
        self.frame_delays: list[int] = []
        self.visible_frame_range: tuple[int, int] | None = None
        self.frame_index = 0
        self.image_label = tk.Label(self.root, bg=TRANSPARENT, bd=0, highlightthickness=0)
        self.image_label.pack()
        self._load_animation()

        self.root.bind_all("<Button-3>", self._menu)
        self.root.bind_all("<Escape>", lambda event: self.root.destroy())
        self.root.after(1500, self.remind)

    def _load_animation(self):
        image_path = HERE / self.settings.get("image", DEFAULTS["image"])
        if not image_path.is_file():
            return

        with Image.open(image_path) as gif:
            for frame_number in range(gif.n_frames):
                gif.seek(frame_number)
                # Pillow composes GIF delta frames onto the original full canvas.
                frame = gif.convert("RGBA")
                if frame.getbbox():
                    if self.visible_frame_range is None:
                        self.visible_frame_range = (frame_number, frame_number)
                    else:
                        self.visible_frame_range = (self.visible_frame_range[0], frame_number)
                png = io.BytesIO()
                frame.save(png, format="PNG")
                self.frames.append(
                    tk.PhotoImage(data=base64.b64encode(png.getvalue()).decode("ascii"), format="png")
                )
                # Slow the original walk so it has time to cross the wider screen.
                self.frame_delays.append(max(20, round(int(gif.info.get("duration", 80)) * 1.75)))

    def remind(self):
        self.settings = load_settings()
        self._show_animation()
        minutes = max(1, int(self.settings.get("interval_minutes", 60)))
        self.root.after(minutes * 60_000, self.remind)

    def _show_animation(self):
        if not self.frames:
            return

        self.frame_index = 0
        self.image_label.configure(image=self.frames[0])
        self.root.update_idletasks()
        screen_h = self.root.winfo_screenheight()
        self.screen_width = self.root.winfo_screenwidth()
        self.gif_width = self.frames[0].width()
        gif_h = self.frames[0].height()
        y = max(0, (screen_h - gif_h) // 2)
        self.window_y = y
        self.root.geometry(f"{self.gif_width}x{gif_h}+0+{y}")
        self.root.deiconify()
        self._advance_frame()

    def _advance_frame(self):
        if not self.root.winfo_exists() or not self.root.winfo_viewable():
            return

        self.frame_index += 1
        if self.frame_index >= len(self.frames):
            # Trailing blank frames let Pond finish walking off the right edge.
            self.root.withdraw()
            return

        self.image_label.configure(image=self.frames[self.frame_index])
        self._move_with_the_walk()
        self.root.after(self.frame_delays[self.frame_index], self._advance_frame)

    def _move_with_the_walk(self):
        if not self.visible_frame_range:
            return
        first, last = self.visible_frame_range
        max_x = max(0, self.screen_width - self.gif_width)
        if last <= first or self.frame_index <= first:
            x = 0
        elif self.frame_index >= last:
            x = max_x
        else:
            progress = (self.frame_index - first) / (last - first)
            x = round(max_x * progress)
        self.root.geometry(f"{self.gif_width}x{self.frames[0].height()}+{x}+{self.window_y}")

    def _menu(self, event=None):
        menu = tk.Menu(self.root, tearoff=False)
        menu.add_command(label="Dismiss", command=self.root.withdraw)
        menu.add_command(label="Quit reminder", command=self.root.destroy)
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    # Detach console launches so the PowerShell prompt stays available.
    if os.name == "nt" and Path(sys.executable).name.lower() == "python.exe" and not os.environ.get("POND_REMINDER_DETACHED"):
        pythonw = Path(sys.executable).with_name("pythonw.exe")
        if not pythonw.is_file():
            pythonw = Path(sys.base_prefix) / "pythonw.exe"
        if pythonw.is_file():
            child_env = os.environ.copy()
            child_env["POND_REMINDER_DETACHED"] = "1"
            subprocess.Popen(
                [str(pythonw), str(Path(__file__).resolve())],
                cwd=str(HERE),
                env=child_env,
                close_fds=True,
                creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NO_WINDOW,
            )
        else:
            Reminder().run()
    else:
        Reminder().run()
