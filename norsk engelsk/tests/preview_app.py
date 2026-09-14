"""Render our own settings window for visual review; no model calls or hotkeys."""
import ctypes
from pathlib import Path
import sys
import tkinter as tk
from PIL import ImageGrab
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app import App
root = tk.Tk()
app = App(root, prepare=False, show_settings=True)
app.badge.set('READY')
app.status.set('Active: Norwegian → English. Ready for Right Ctrl + Enter.')
app.start_button.configure(state='normal')
app.stop_button.configure(state='normal')
root.update()
def capture():
    root.update_idletasks()
    user32 = ctypes.windll.user32
    user32.GetParent.argtypes = [ctypes.c_void_p]
    user32.GetParent.restype = ctypes.c_void_p
    hwnd = user32.GetParent(root.winfo_id())
    output = Path(__file__).resolve().parents[1] / '.runtime' / 'app-preview.png'
    output.parent.mkdir(exist_ok=True)
    ImageGrab.grab(window=hwnd).save(output)
    print(output)
    # Every visible control must fit vertically in the window.
    def check(widget):
        if widget.winfo_ismapped():
            assert widget.winfo_rooty() + widget.winfo_height() <= root.winfo_rooty() + root.winfo_height() + 1, str(widget)
        for child in widget.winfo_children(): check(child)
    check(root)
    app.close()
root.after(400, capture)
root.mainloop()
