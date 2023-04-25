# builtins
import datetime
import time
import threading
import os
from tkinter import Tk
from tkinter import messagebox

# non builtins
# import playsound

try:
    import cv2
except ImportError:
    Tk().withdraw()
    messagebox.showerror(
        "Can't import cv2 module. Please install cv2 package. Program will exit"
    )

try:
    import numpy as np
except ImportError:
    Tk().withdraw()
    messagebox.showerror(
        "Can't import numpy module. Please install numpy package. Program will exit"
    )


# https://towardsdatascience.com/image-analysis-for-beginners-creating-a-motion-detector-with-opencv-4ca6faba4b42


class MotionDetector:
    def __init__(self):
        self.frame_count = 0
        self.prev_frame = None
        self.motion = []

    def motion_detector(
        self,
        frame,
        show_rect=True,
        contour_area=500,
        threshold=20,
        output="normal",
        color=(0, 255, 0),
    ):
        if output not in ["normal", "greyscale"]:
            return
        self.frame_count += 1
        # frame = np.array(frame)
        # frame = cv2.cvtColor(src=frame,code=cv2.COLOR_BGR2RGB)

        prepared_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        prepared_frame = cv2.GaussianBlur(src=prepared_frame, ksize=(5, 5), sigmaX=0)

        if self.prev_frame is None:
            self.prev_frame = prepared_frame
            return
        diff_frame = cv2.absdiff(src1=self.prev_frame, src2=prepared_frame)
        self.prev_frame = prepared_frame

        kernel = np.ones((5, 5))
        diff_frame = cv2.dilate(diff_frame, kernel, 1)

        thresh_frame = cv2.threshold(
            src=diff_frame, thresh=threshold, maxval=255, type=cv2.THRESH_BINARY
        )[1]

        contours, _ = cv2.findContours(
            image=thresh_frame,
            mode=cv2.RETR_EXTERNAL,
            method=cv2.CHAIN_APPROX_SIMPLE,
        )
        if output == "greyscale":
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            # convert back to rgb so rect shown can be other colours
            frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2RGB)
        else:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        for contour in contours:
            if cv2.contourArea(contour) < int(contour_area):
                self.motion = []
                continue
            else:
                self.motion = datetime.datetime.now()
            if show_rect:
                # shows rect on camera
                (x, y, w, h) = cv2.boundingRect(contour)
                cv2.rectangle(
                    img=frame,
                    pt1=(x, y),
                    pt2=(x + w, y + h),
                    color=color,
                    thickness=2,
                )

        return frame


class Controller:
    def __init__(self) -> None:
        self.source = "camera"

        self.stop_thread = False
        self.pause = False

        self._init_frame = None
        self.processed_frame = None

        try:
            os.mkdir(os.path.join(os.getenv("localappdata"), "MotionDetector"))
        except FileExistsError:
            pass

        self.output_file_name = os.path.join(
            os.getenv("localappdata"), "MotionDetector", "motion_log.txt"
        )
        self.create_output_file()

        # x most recent motions detected
        self.RECENT_MOTIONS_COUNT = 20
        self.motion = ["-" for _ in range(self.RECENT_MOTIONS_COUNT)]

        self.camera_num = 0
        self.create_camera(self.camera_num)
        # add functionality to cycle thru cameras

        self.detector = MotionDetector()

        # processing modifiers
        self.show_rect = True
        self.rect_area = 500
        self.threshold = 20
        self.frame_type = "normal"  # "normal", "greyscale"

        self.process_frame_thread_controller()
        self.update_motion_thread_controller()

    def changed_source(self, source_type):
        # stop frames to remove any errors when changing detector
        self.stop_thread = True

        # restart frames
        # Sometimes stop thread was being set to true before threads had time to close - caused errors
        while True:
            if (
                self.process_frame_thread.is_alive()
                or self.update_motion_thread.is_alive()
            ):
                continue
            self.stop_thread = False
            break

        # reset detector to remove any existing data from other sources
        self.detector = MotionDetector()

        # create new camera
        if source_type == "camera":
            self.create_camera(0)
        elif source_type == "video":
            self.create_camera(None, True, self.source)
            self.start_video_processing()

        self.process_frame_thread_controller()
        self.update_motion_thread_controller()

    def create_camera(self, cam_num, video=False, vidpath=None):
        if video:
            self.camera = cv2.VideoCapture(vidpath)
        else:
            camera = cv2.VideoCapture(cam_num, cv2.CAP_DSHOW)
            if camera is not None and camera.isOpened():
                self.camera = camera
                return True
            else:
                return False

    def get_webcam_frame(self):
        _, frame = self.camera.read()
        self._init_frame = frame

    def get_video_frame(self):
        self.camera.set(cv2.CAP_PROP_POS_FRAMES, self.frame_num - 1)
        _, frame = self.camera.read()
        self._init_frame = frame
        self.frame_num += 1

    def start_video_processing(self):
        self.frame_num = 0
        self.total_frames = self.camera.get(cv2.CAP_PROP_FRAME_COUNT)

    def process_frame(self):
        while True:
            if self.stop_thread:
                break
            if self.pause:
                continue

            if self.source == "camera":
                self.get_webcam_frame()
            else:
                self.get_video_frame()

            if self._init_frame is None:
                continue

            frame = self.detector.motion_detector(
                self._init_frame,
                contour_area=self.rect_area,
                threshold=self.threshold,
                show_rect=self.show_rect,
                output=self.frame_type,
            )

            if frame is None:
                continue
            else:
                self.processed_frame = frame

    def get_frame(self):
        return self.processed_frame

    def get_motion(self):
        return self.motion

    def update_motion(self):
        while True:
            if self.stop_thread:
                break
            # temp motion created as otherwise the GUI may get the motion when there is > 5 elements
            # because of threading and them executing at different times
            temp_motion = []
            for x in self.motion:
                temp_motion.append(x)

            motion = self.detector.motion
            if motion != []:
                temp_motion.append(motion)
                self.update_output_file(motion)
                # playsound.playsound("beep.mp3")

            if len(temp_motion) > self.RECENT_MOTIONS_COUNT:
                temp_motion.pop(0)

            self.motion = temp_motion
            time.sleep(0.05)

    def create_output_file(self):
        try:
            f = open(self.output_file_name, "r")
            f.close()
        except FileNotFoundError:
            f = open(self.output_file_name, "w")
            f.close()

    def update_output_file(self, motion):
        with open(self.output_file_name, "a") as f:
            f.write(str(motion) + "\n")

    def update_motion_thread_controller(self):
        self.update_motion_thread = threading.Thread(target=self.update_motion)
        self.update_motion_thread.daemon = True
        self.update_motion_thread.start()

    def process_frame_thread_controller(self):
        self.process_frame_thread = threading.Thread(target=self.process_frame)
        self.process_frame_thread.daemon = True
        self.process_frame_thread.start()


class SettingChecks:
    def __init__(self) -> None:
        pass

    def check_rect_area_10to5000(self, rect_area):
        if rect_area < 10 or rect_area > 5000 or type(rect_area) != int:
            return False
        return True
