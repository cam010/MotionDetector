import threading
import time
import tkinter as tk
from tkinter import ttk
import cv2
import controller
from PIL import Image, ImageTk

class GUI:
    def __init__(self) -> None:
        self.controller = controller.Controller()
    
        # window
        self.root = tk.Tk()
        self.root.title("Motion Detector")
        self.create_image_label()
        self.create_modifiers_frame()
        self.create_modifiers()
        self.create_motion_frame()
        self.get_frame()
        self.root.mainloop()
        
    def create_image_label(self):
        self.image_label = tk.Label(self.root, image=None)
        self.image_label.grid(row=0, column=2, columnspan=1, rowspan=2)
        
    def create_modifiers_frame(self):
        self.modifiers_frame = tk.Frame(self.root)
        self.modifiers_frame.grid(row=0, column=0, columnspan=2, sticky="NSEW")
        self.modifiers_frame.config(highlightbackground="black")
        self.modifiers_frame.config(highlightthickness=1)
    
    def create_motion_frame(self):
        self.motion_frame = tk.Frame(self.root)
        self.motion_frame.grid(row=1, column=0, sticky="NS")
        self.motion_frame.config(highlightbackground="black")
        self.motion_frame.config(highlightthickness=1)
        
        tk.Label(self.motion_frame, text="Recent motion detections:").pack()
        
        self.recent_motions = []
        self.motions_labels = []
        
        for _ in range(12):
            label = tk.Label(self.motion_frame, text="")
            label.pack()
            self.motions_labels.append(label)
            self.recent_motions.append("-")
        
        self.update_motions_internal_thread_controller()
        self.update_motions_display_thread_controller()
            
    def rect_draw_changed(self):
        if self.rect_draw_checkbox.get() == True:
            self.controller.show_rect = True
        else:
            self.controller.show_rect = False
    
    def rect_area_changed(self, val):
        self.controller.rect_area = val
        
    def sensitivity_changed(self, val):
        threshold = 100-int(val)
        self.controller.threshold = threshold
        
    
    def create_modifiers(self):
        tk.Label(self.modifiers_frame, text="DETECTOR MODIFIERS:").grid(row=0, column=0, )
        ttk.Separator(self.modifiers_frame, orient="horizontal").grid(row=1, column=0, sticky="EW")
        
        # Whether or not to draw rects around moving objects
        self.rect_draw_checkbox = tk.BooleanVar()
        rect_draw_checkbox = tk.Checkbutton(self.modifiers_frame,
                                            text="Enable Rect Drawing",
                                            command=lambda: self.rect_draw_changed(),
                                            variable=self.rect_draw_checkbox,
                                            onvalue=True,
                                            offvalue=False)
        rect_draw_checkbox.select()
        rect_draw_checkbox.grid(row=2, column=0)
        ttk.Separator(self.modifiers_frame, orient="horizontal").grid(row=3, column=0, sticky="EW")
        
        # How big the minimum area of a moving object rect has to be to be drawn
        tk.Label(self.modifiers_frame, text="Minimum Rect Area").grid(row=4, column=0)
        rect_area_scale = tk.Scale(self.modifiers_frame, orient="horizontal", from_=10, to=5000, command=lambda val: self.rect_area_changed(val))
        rect_area_scale.set(500)
        rect_area_scale.grid(row=5, column=0)
        
        # Threshold for defining image as "different" - higher threshold is lower motion sensitivity
        ttk.Separator(self.modifiers_frame, orient="horizontal").grid(row=6, column=0, sticky="EW")
        tk.Label(self.modifiers_frame, text="Motion Sensitivity").grid(row=7, column=0)
        sensitivity_scale = tk.Scale(self.modifiers_frame, orient="horizontal", from_=1, to=99, command=lambda val: self.sensitivity_changed(val))
        sensitivity_scale.set(80)
        sensitivity_scale.grid(row=8, column=0)
        
    def update_motions_display(self):
        while True:
            for child in self.motion_frame.winfo_children():
                if child["text"] == "Recent motion detections:":
                    continue
                child.destroy()
            
            for x in self.recent_motions:
                label = tk.Label(self.motion_frame, text=x)
                label.pack()
                self.motions_labels.append(label)
            
            # if grabbing motion from controller class is done every 0.25s, then 12 will be grabbed in 3s so none are missed, but update speed
            # is less than having to do a widget update every 0.25s which was glitchy
            time.sleep(3)
    
    def update_motions_internal(self):
        while True:
            motion = self.controller.get_motion()
            if motion != []:
                self.recent_motions.append(motion)
                
            if len(self.recent_motions) > 12:
                self.recent_motions.pop(0)
                
            time.sleep(0.25)
    
    def update_motions_display_thread_controller(self):
        self.update_motions_display_thread = threading.Thread(target=self.update_motions_display)
        self.update_motions_display_thread.daemon = True
        self.update_motions_display_thread.start()
        
    def update_motions_internal_thread_controller(self):
        self.update_motions_internal_thread = threading.Thread(target=self.update_motions_internal)
        self.update_motions_internal_thread.daemon = True
        self.update_motions_internal_thread.start()
    
    
    def get_frame(self):
        frame = self.controller.processed_frame
        if frame is not None:
            #image comes in brg format, therefore red would be shown as blue, etc
            b,g,r = cv2.split(frame)
            frame = cv2.merge((r,g,b))
            
            frame = Image.fromarray(frame)
            frame = ImageTk.PhotoImage(image=frame) 

            # Put it in the display window
            self.image_label.configure(image=frame)
            # https://web.archive.org/web/20201111190625id_/http://effbot.org/pyfaq/why-do-my-tkinter-images-not-appear.htm
            # So if there isn't a reference to the .image, then tkinter will discard it and a white image will be shown instead
            self.image_label.image = frame
            
        self.root.after(10, self.get_frame)

if __name__ == "__main__":
    GUI()
