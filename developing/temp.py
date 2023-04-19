# This module is for testing the custom scale to get it right
# It is not implemented yet
# See accepted answer at https://stackoverflow.com/questions/59678715/python-tkinter-slider-customization

import os
from pathlib import Path
import tkinter as tk
from tkinter import ttk

from PIL import Image, ImageTk

class CustomScale(ttk.Scale):
    def __init__(self, master=None, **kw):
        kw.setdefault("orient", "horizontal")
        self.variable = kw.pop('variable', tk.IntVar(master))
        ttk.Scale.__init__(self, master, variable=self.variable, style="custom.Horizontal.TScale", **kw)
        self._style_name = '{}.custom.{}.TScale'.format(self, kw['orient'].capitalize()) # unique style name to handle the text
        self['style'] = self._style_name
        self.variable.trace_add('write', self._update_text)
        self._update_text()

    def _update_text(self, *args):
        # style.configure(self._style_name, text="{}".format(self.variable.get())) # This causes errors and glitching to ends
        print(self.variable.get())
        pass

# Widget Images Directory
parent_dir = Path(__file__).resolve().parents[1]
widget_image_dir = os.path.join(parent_dir, "Assets", "Images", "Widget Images")

trough = os.path.join(widget_image_dir, "trough3.png")
slider = os.path.join(widget_image_dir, "slider2.png")

root = tk.Tk()
root.geometry("500x500")

# create images used for the theme, can be resized? maybe this can be done on <Configure> event where frame/window changes size?
image_trough = Image.open(trough)
image_trough = image_trough.resize((root.winfo_width(), 25))
image_slider = Image.open(slider)
image_slider = image_slider.resize((50, 50))
img_trough = ImageTk.PhotoImage(master=root, image=image_trough)
img_slider = ImageTk.PhotoImage(master=root, image=image_slider)
style = ttk.Style(root)

# create scale elements
style.element_create('custom.Scale.trough', 'image', img_trough)
style.element_create('custom.Scale.slider', 'image', img_slider)

# create custom layout
style.layout('custom.Horizontal.TScale',
             [('custom.Scale.trough', {'sticky': 'ew'}),
              ('custom.Scale.slider',
               {'side': 'left', 'sticky': '',
                'children': [('custom.Horizontal.Scale.label', {'sticky': ''})]
                })])

frame = tk.Frame(root, bg="green")
frame.pack(fill="both", expand=True)
frame.pack_propagate(0)

scale1 = CustomScale(frame, from_=0, to=1000)
scale1.pack(expand=1, fill="both")

root.mainloop()
