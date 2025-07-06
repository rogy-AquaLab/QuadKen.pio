from picamera2 import Picamera2 # type: ignore
import cv2
import asyncio

class Picam:

    def __init__(self):
        self.picam = Picamera2()

    def __repr__(self):
        return "Picamera2"

    def start(self):
        self.picam.configure(self.picam.create_video_configuration(main={"format": 'RGB888'}))
        self.picam.start()

    def close(self):
        if self.picam:
            self.picam.close()
            self.picam = None

    async def get(self, timeout: float = 5.0):
        if not self.picam:
            raise RuntimeError("カメラが初期化されていません。start()を呼び出してください。")
        
        return await asyncio.wait_for(asyncio.to_thread(self._capture), timeout=timeout)
    
    async def _capture(self):
        frame = self.picam.capture_array()
        _, jpeg = cv2.imencode('.jpg', frame)
        data = jpeg.tobytes()
        return data