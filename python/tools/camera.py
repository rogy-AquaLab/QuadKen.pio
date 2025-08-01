from picamera2 import Picamera2 # type: ignore
import cv2
import asyncio
import numpy as np

class Picam:

    def __init__(self):
        self.picam = None

    def __repr__(self):
        return "Picamera2"

    def start(self):
        self.picam = Picamera2()
        self.picam.configure(self.picam.create_video_configuration(main={"format": 'RGB888', "size": (720, 480)}))
        self.picam.start()

    def close(self):
        if self.picam:
            self.picam.close()
            self.picam = None

    async def get(self, timeout: float = 5.0):
        if not self.picam:
            raise RuntimeError("カメラが初期化されていません。start()を呼び出してください。")
        
        return await asyncio.wait_for(asyncio.to_thread(self._capture), timeout=timeout)
    
    def _capture(self):
        frame = self.picam.capture_array()
        _, jpeg = cv2.imencode('.jpg', frame)
        data = jpeg.tobytes()
        return data