import datetime
import cv2
import numpy as np
import threading

# https://towardsdatascience.com/image-analysis-for-beginners-creating-a-motion-detector-with-opencv-4ca6faba4b42


class MotionDetector:
    def __init__(self):
        self.frame_count = 0
        self.prev_frame = None
        self.motion = []
    
    def motion_detector(self, frame, show_rect=True, contour_area=500, threshold=20):
        self.frame_count += 1
        # frame = np.array(frame)
        # frame = cv2.cvtColor(src=frame,code=cv2.COLOR_BGR2RGB)
        
        if self.frame_count % 1 == 0:
            prepared_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            prepared_frame = cv2.GaussianBlur(src=prepared_frame, ksize=(5,5), sigmaX=0)
        
            if self.prev_frame is None:
                self.prev_frame = prepared_frame
                return
            diff_frame = cv2.absdiff(src1=self.prev_frame, src2=prepared_frame)
            self.prev_frame = prepared_frame
            
            kernel = np.ones((5,5))
            diff_frame = cv2.dilate(diff_frame, kernel, 1)
            
            thresh_frame = cv2.threshold(src=diff_frame, thresh=threshold, maxval=255, type=cv2.THRESH_BINARY)[1]
            
            contours, _ = cv2.findContours(image=thresh_frame, mode=cv2.RETR_EXTERNAL, method=cv2.CHAIN_APPROX_SIMPLE)
            for contour in contours:
                if cv2.contourArea(contour) < int(contour_area):
                    self.motion = []
                    continue
                else:
                    self.motion = datetime.datetime.now()
                if show_rect:
                    #shows rect on camera
                    (x, y, w, h) = cv2.boundingRect(contour)
                    cv2.rectangle(img=frame, pt1=(x, y), pt2=(x + w, y + h), color=(0, 255, 0), thickness=2)
                        
            return frame

class Controller:
    def __init__(self) -> None:
        self._init_frame = None
        self.processed_frame = None
        
        self.motion = None
        
        self.camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        # add functionality to cycle thru cameras
        
        self.detector = MotionDetector()
        
        # processing modifiers
        self.show_rect = True
        self.rect_area = 500
        self.threshold = 20
        
        self.process_frame_thread_controller()
    
    def get_webcam_frame(self):
        _, frame = self.camera.read()
        self._init_frame = frame
    
    def process_frame(self):
        while True:
            self.get_webcam_frame()
            if self._init_frame is None:
                continue
            
            if self.show_rect:
                frame = self.detector.motion_detector(self._init_frame, contour_area=self.rect_area, threshold=self.threshold)
            else:
                frame = self.detector.motion_detector(self._init_frame, show_rect=False, threshold=self.threshold)
            if frame is None:
                continue
            else:
                self.processed_frame = frame
    
    def get_motion(self):
        return self.detector.motion
    
    def process_frame_thread_controller(self):
        self.process_frame_thread = threading.Thread(target=self.process_frame)
        self.process_frame_thread.daemon = True
        self.process_frame_thread.start()