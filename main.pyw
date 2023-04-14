import os
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog
from PIL import Image, ImageTk
import threading
import time
import cv2
import numpy
import controller
from os import startfile
from functools import partial


class GUI:
    def __init__(self) -> None:
        self.controller = controller.Controller()

        self.stop_thread = False

        # window
        self.root = tk.Tk()
        self.root.geometry("929x484")
        self.root.title("Motion Detector")
        self.root.minsize(width=650, height=400)
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_columnconfigure(2, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=1)

        self.create_menubar()
        self.create_image_label()

        self.create_modifiers_frame()
        self.create_motion_frame()
        self.create_camera_modifiers_frame()

        self.update_frame_label_frame_thread_controller()
        self.first_frame_loaded = False
        self.root.bind("<Configure>", self.resize)

        self.root.mainloop()

    def resize(self, event):
        if event.widget == self.image_label and (
            event.height != self.height or event.width != self.width
        ):
            self.height, self.width = event.height, event.width

    def quit(self):
        # stops threads otherwise they throw errors trying to execute
        # processes when TCL objects are destroyed
        self.controller.stop_thread = True
        self.stop_thread = True

        # if quit first, then root freezes for a couple of seconds before
        # closing
        self.root.destroy()
        quit()

    def create_menubar(self):
        self.menubar = tk.Menu(self.root)
        self.root.config(menu=self.menubar)

        self.populate_menubar()

    def populate_menubar(self):
        # File menu
        file_menu = tk.Menu(self.menubar, tearoff=0)
        file_menu.add_command(label="Exit", command=lambda: self.quit())

        # Rect settings
        rect_settings_menu = tk.Menu(self.menubar, tearoff=0)
        rect_size = tk.Menu(rect_settings_menu, tearoff=0)
        for x in [100, 500, 1000, 2500, 5000, "custom"]:
            rect_size.add_command(
                label=x,
                command=partial(self.custom_val_rect_area_changed, x),
            )
        # menu is created before settings, so self variable has to be created
        # here
        self.rect_draw_checkbox = tk.BooleanVar()
        rect_settings_menu.add_checkbutton(
            label="Enable Rect Drawing",
            command=lambda: self.rect_draw_changed(),
            variable=self.rect_draw_checkbox,
            onvalue=True,
            offvalue=False,
        )
        rect_settings_menu.add_cascade(label="Minimum Rect Size", menu=rect_size)

        self.menubar.add_cascade(label="File", menu=file_menu)
        self.menubar.add_cascade(label="Rect Settings", menu=rect_settings_menu)

    def create_image_label(self):
        self.image_label = tk.Label(self.root, image=None)
        self.image_label.grid(row=0, column=1, sticky="NSEW")

    def create_modifiers_frame(self):
        self.modifiers_frame = tk.Frame(self.root)
        self.modifiers_frame.grid(row=0, column=0, sticky="NSEW", rowspan=2)
        self.modifiers_frame.config(highlightbackground="black")
        self.modifiers_frame.config(highlightthickness=1)

        self.create_modifiers()

    def create_motion_frame(self):
        self.motion_frame = tk.Frame(self.root)
        self.motion_frame.grid(row=0, column=2, sticky="NSEW", rowspan=2)
        self.motion_frame.config(highlightbackground="black")
        self.motion_frame.config(highlightthickness=1)

        tk.Label(self.motion_frame, text="Recent motion detections:").pack()

        self.recent_motions = []
        self.motions_labels = []

        self.open_output_file_button()

        self.update_motions_display_thread_controller()

    def create_camera_modifiers_frame(self):
        self.camera_modifiers_frame = tk.Frame(self.root)
        self.camera_modifiers_frame.grid(row=1, column=1, sticky="NSEW", pady=(10, 10))

        self.create_camera_modifiers()

    def create_camera_modifiers(self):
        self.previous_camera_button = tk.Button(
            self.camera_modifiers_frame,
            text="<-- Previous Camera",
            command=partial(self.changed_camera, "prev"),
        )
        self.previous_camera_button.grid(row=0, column=0, padx=(10, 0))

        self.switch_frame_source_button = tk.Button(
            self.camera_modifiers_frame,
            text="Pick File",
            command=lambda: self.change_frame_source(),
        )
        self.switch_frame_source_button.grid(row=0, column=1)

        self.pause_button = tk.Button(
            self.camera_modifiers_frame,
            text="Pause",
            command=lambda: self.paused_changed(),
        )
        self.pause_button.grid(row=0, column=2)

        self.next_camera_button = tk.Button(
            self.camera_modifiers_frame,
            text="Next Camera -->",
            command=partial(self.changed_camera, "next"),
        )
        self.next_camera_button.grid(row=0, column=3, padx=(0, 10))
        
        for i in range(0, 4):
            self.camera_modifiers_frame.grid_columnconfigure(i, weight=1)

    def paused_changed(self):
        self.pause_button.config(state="disabled")
        print(self.root.winfo_width(), self.root.winfo_height())
        if self.pause_button["text"] == "Pause":
            self.pause_button.config(text="Play")
            self.controller.pause = True

        else:
            self.pause_button.config(text="Pause")
            self.controller.pause = False
        self.pause_button.config(state="normal")

    def load_video_file(self):
        filetypes = (
            ("video files", "*.mp4"),
            ("movie files", "*.mov"),
        )
        return tk.filedialog.askopenfilename(
            initialdir=os.path.join(os.path.join(os.environ["USERPROFILE"]), "Desktop"),
            title="Select a File",
            filetypes=(filetypes),
        )

    def change_frame_source(self):
        self.switch_frame_source_button.config(state="disabled")

        if self.switch_frame_source_button["text"] == "Switch to Camera Mode":
            self.controller.source = "camera"
            self.controller.changed_source("camera")
            self.switch_frame_source_button.config(text="Pick File")

        elif self.switch_frame_source_button["text"] == "Pick File":
            source = self.load_video_file()
            if source != "":
                self.controller.source = source
                self.controller.changed_source("video")
                self.switch_frame_source_button.config(text="Switch to Camera Mode")

        self.switch_frame_source_button.config(state="normal")

    def changed_camera(self, change):
        if change == "prev":
            btn = self.previous_camera_button
            btn.config(state="disabled")
            change = 1
        elif change == "next":
            btn = self.next_camera_button
            btn.config(state="disabled")
            change = -1

        self.controller.camera_num += change
        success = self.controller.create_camera(self.controller.camera_num)
        if not success:
            self.controller.camera_num -= change
        btn.after(100, lambda: btn.config(state="normal"))

    def rect_draw_changed(self):
        if self.rect_draw_checkbox.get() == True:
            self.controller.show_rect = True
        else:
            self.controller.show_rect = False

    def custom_val_rect_area_changed(self, val):
        if val == "custom":
            new_val = tk.IntVar()
            inp = tk.Toplevel()
            tk.Label(inp, text="Please enter an int between 10-5000")
            tk.Entry(inp, textvariable=new_val).pack()
            tk.Button(
                inp,
                text="save",
                command=lambda: self.custom_val_rect_area_changed_callback(
                    new_val, inp
                ),
            ).pack()
        else:
            self.rect_area_changed(val)

    def custom_val_rect_area_changed_callback(self, var, toplevel):
        if controller.SettingChecks().check_rect_area_10to5000(var.get()):
            var = var.get()
            toplevel.destroy()
            self.rect_area_changed(var)
        else:
            messagebox.showerror(
                "Error", "Value must be an integer between 10-5000 inclusive"
            )

    def rect_area_changed(self, val):
        self.controller.rect_area = val
        self.rect_area_scale.set(val)

    def sensitivity_changed(self, val):
        threshold = 100 - int(val)
        self.controller.threshold = threshold
    
    def flip_frame(self):
        self.flip = not self.flip

    def create_modifiers(self):
        tk.Label(self.modifiers_frame, text="DETECTOR MODIFIERS:").grid(
            row=0,
            column=0,
        )
        ttk.Separator(self.modifiers_frame, orient="horizontal").grid(
            row=1, column=0, sticky="EW"
        )

        # Whether or not to draw rects around moving objects
        rect_draw_checkbox = tk.Checkbutton(
            self.modifiers_frame,
            text="Enable Rect Drawing",
            command=lambda: self.rect_draw_changed(),
            variable=self.rect_draw_checkbox,
            onvalue=True,
            offvalue=False,
        )
        rect_draw_checkbox.select()
        rect_draw_checkbox.grid(row=2, column=0)
        ttk.Separator(self.modifiers_frame, orient="horizontal").grid(
            row=3, column=0, sticky="EW"
        )

        # How big the minimum area of a moving object rect has to be to be drawn
        tk.Label(self.modifiers_frame, text="Minimum Rect Area").grid(row=4, column=0)
        self.rect_area_scale = tk.Scale(
            self.modifiers_frame,
            orient="horizontal",
            from_=10,
            to=5000,
            command=lambda val: self.rect_area_changed(val),
        )
        self.rect_area_scale.set(500)
        self.rect_area_scale.grid(row=5, column=0)

        # Threshold for defining image as "different" - higher threshold is
        # lower motion sensitivity
        ttk.Separator(self.modifiers_frame, orient="horizontal").grid(
            row=6, column=0, sticky="EW"
        )
        tk.Label(self.modifiers_frame, text="Motion Sensitivity").grid(row=7, column=0)
        sensitivity_scale = tk.Scale(
            self.modifiers_frame,
            orient="horizontal",
            from_=1,
            to=99,
            command=lambda val: self.sensitivity_changed(val),
        )
        sensitivity_scale.set(80)
        sensitivity_scale.grid(row=8, column=0)
        
        # Flip image
        self.flip = tk.BooleanVar()
        ttk.Separator(self.modifiers_frame, orient="horizontal").grid(
            row=9, column=0, sticky="EW"
        )
        flip_image = tk.Checkbutton(
            self.modifiers_frame,
            text="Flip Image",
            command=lambda: self.flip_frame(),
            variable=self.flip,
            onvalue=True,
            offvalue=False,
        )
        flip_image.grid(row=10, column=0)

    def update_motions_display(self):
        while True:
            if self.stop_thread:
                break
            self.update_motions_internal()
            for child in self.motion_frame.winfo_children():
                if child["text"] == "Recent motion detections:":
                    continue
                elif child["text"] == "Open Output File":
                    continue
                child.destroy()

            for x in self.recent_motions:
                label = tk.Label(self.motion_frame, text=x)
                label.pack()
                self.motions_labels.append(label)

            # if grabbing motion from controller class is done every 0.25s,
            # then 12 will be grabbed in 3s so none are missed, but update speed
            # is less than having to do a widget update every 0.25s which was
            # glitchy
            time.sleep(3)

    def update_motions_internal(self):
        motion = self.controller.get_motion()
        self.recent_motions = motion

    def open_output_file(self):
        startfile(self.controller.output_file_name)

    def open_output_file_button(self):
        open_output_file_button = tk.Button(
            self.motion_frame,
            text="Open Output File",
            command=lambda: self.open_output_file(),
        )
        open_output_file_button.pack(side="bottom", pady=(0, 10))

    def update_motions_display_thread_controller(self):
        self.update_motions_display_thread = threading.Thread(
            target=self.update_motions_display
        )
        self.update_motions_display_thread.daemon = True
        self.update_motions_display_thread.start()

    def update_frame_label_frame(self):
        while True:
            if self.stop_thread:
                break
            frame = self.controller.get_frame()
            if frame is None:
                continue
            else:
                height, width, _ = frame.shape
                if not self.first_frame_loaded:
                    self.height = height
                    self.width = width
                    self.first_frame_loaded = True

                if height != self.height or width != self.width:
                    # take off 3 from self.height,width so that frame borders
                    # are shown clearly with no overlap
                    frame = cv2.resize(frame, (self.width - 3, self.height - 3))
                # image comes in brg format, therefore red would be shown
                # as blue, etc
                b, g, r = cv2.split(frame)
                frame = cv2.merge((r, g, b))
                if self.flip:
                    # flips frame vertically
                    frame = numpy.fliplr(frame)
                frame = Image.fromarray(frame)
                frame = ImageTk.PhotoImage(image=frame)

                # Put it in the display window
                self.image_label.configure(image=frame)
                # https://web.archive.org/web/20201111190625id_/http://effbot.org/pyfaq/why-do-my-tkinter-images-not-appear.htm
                # So if there isn't a reference to the .image, then
                # tkinter will discard it and a white image will be shown instead
                self.image_label.image = frame

    def update_frame_label_frame_thread_controller(self):
        self.update_frame_label_frame_thread = threading.Thread(
            target=self.update_frame_label_frame
        )
        self.update_frame_label_frame_thread.daemon = True
        self.update_frame_label_frame_thread.start()


if __name__ == "__main__":
    GUI()
