import os
from pathlib import Path
import tkinter
from tkinter.ttk import Style, Scale
from tkinter import messagebox
from PIL import Image, ImageTk
from typing import Literal


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

    def set(self, val):
        super().set(val)


class CustomInputWindow(tkinter.Toplevel):
    def __init__(
        self,
        title: str,
        input_message: str,
        error_messages: list[str],
        type: Literal["int", "float", "string"],
        number_low_boundary: float = None,
        number_high_boundary: float = None,
        string_max_len: int = None,
        custom_geometry: str = None,
        *args,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        
        # is input complete and has it passed authorisation
        self.complete = False
        
        # make params class-wide
        self.error_messages = error_messages
        self.number_low_boundary = number_low_boundary
        self.number_high_boundary = number_high_boundary
        self.string_max_len = string_max_len
        self.type = type
        
        # init window
        self.title(title)
        if custom_geometry is not None:
            self.geometry(custom_geometry)
        
        # Create label
        label = tkinter.Label(self, text=input_message)
        label.grid(row=0, column=0)
        
        # Create input
        if self.type == "int":
            self.input_var = tkinter.IntVar()
        elif self.type == "float":
            self.input_var = tkinter.DoubleVar()
        else:
            self.input_var = tkinter.StringVar()
        
        self.input_entry = tkinter.Entry(self, variable=self.input_var)
        self.input_entry.grid(row=1, column=0)

        # Create submit button
        self.submit_button = tkinter.Button(self, text="Submit", command=lambda: self.submit())
        self.submit_button.grid(row=2, column=0)
        
    def submit(self):
        val = self.input_var.get()
        if val is not None:
            is_within_bounds = self.check_within_bounds(val)
            if not is_within_bounds:
                message = "Input contains the follow errors:"
                for m in self.error_messages:
                    message.append("\n\t{}".format(message))
                self.show_error(message)
            else:
                self.complete = True
                self.destroy()
            
        else:
            self.show_error("Please enter a value")
    
    def check_within_bounds(self, val):
        if self.type == "int" or self.type == "float":
            if val <= self.number_low_boundary or val <= self.number_high_boundary:
                return False
        elif self.type == "string" and self.string_max_len != None:
            if len(val) != self.string_max_len:
                return False
    
    def show_error(self, msg):
        messagebox.showerror("Input Error", msg)
    
    def get_val(self):
        """Returns value if user has entered one that has passed authorisation checks, else returns False
        """
        if self.complete == True:
            return self.input_var.get()
        else:
            return False
    