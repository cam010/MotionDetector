import os
from pathlib import Path
import tkinter
from tkinter.ttk import Style, Scale
from tkinter import IntVar
from PIL import Image, ImageTk


class CustomStyle:
    def __init__(self, root):
        self.root = root

        # init style
        self.style = Style(master=self.root)
        self.style.theme_create("custom_theme", parent="alt")
        self.style.theme_use("custom_theme")

        # Widget Images Directory
        parent_dir = Path(__file__).resolve().parents[1]
        self.widget_image_dir = os.path.join(
            parent_dir, "Assets", "Images", "Widget Images"
        )

        # load widget styles
        self.labelframe()
        self.label()
        self.checkbox()
        self.combobox()
        self.button()
        self.separator()
        self.custom_horizontal_scale()

    def labelframe(self):
        self.style.configure(
            "TLabelframe",
            background="white",
        )
        self.style.configure("TLabelframe.Label", background="white")

    def label(self):
        self.style.configure(
            "TLabel",
            background="white",
        )

    def checkbox(self):
        self.style.configure("TCheckbutton", background="white", focuscolor="white")

    def combobox(self):
        self.style.configure(
            "TCombobox",
            selectbackground="white",
            selectforeground="black",
            fieldbackground="white",
            background="white",
        )

    def button(self):
        self.style.configure("TButton", background="white")

    def separator(self):
        self.style.configure(
            "TSeparator",
        )

    def custom_horizontal_scale(self):
        # https://stackoverflow.com/a/59680262 <-- See this answer regarding custom ttk sliders
        self.image_trough = ImageTk.PhotoImage(
            Image.open(os.path.join(self.widget_image_dir, "trough.png")).resize(
                (25, 25)  # needs to be resized in future
            )
        )
        self.image_slider = ImageTk.PhotoImage(
            Image.open(os.path.join(self.widget_image_dir, "slider.png")).resize(
                (30, 30)  # needs to be resized in future
            )
        )
        self.style.element_create("custom.Scale.trough", "image", self.image_trough)
        self.style.configure(
            "custom.Scale.trough", image=self.image_trough
        )  # This needs to be here, similar to camera frame label as img not stored within tkinter properly

        self.style.element_create("custom.Scale.slider", "image", self.image_slider)
        self.style.configure("custom.Scale.slider", image=self.image_slider)

        self.style.layout(
            "custom.Horizontal.TScale",
            [
                ("custom.Scale.trough", {"sticky": "ew"}),
                (
                    "custom.Scale.slider",
                    {
                        "side": "left",
                        "sticky": "",
                        "children": [("custom.Horizontal.Scale.label", {"sticky": ""})],
                    },
                ),
            ],
        )


class CustomHorizontalScale(Scale):
    # https://stackoverflow.com/a/59680262 <-- See this answer regarding custom ttk sliders
    def __init__(self, root, **kw):
        self.variable = kw.pop("variable")
        super().__init__(root, variable=self.variable, orient="horizontal", **kw)
        self.style = Style(root)
        self._style_name = "{}.custom.Horizontal.TScale".format(self)
        self["style"] = self._style_name

        self.variable.trace_add("write", self._update_text)

    def _update_text(self, *args):
        # print(self.variable.get())
        pass
        # self.style.configure(self._style_name, text="{:.1f}".format(self.variable.get()))
