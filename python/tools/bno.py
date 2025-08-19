import board
import busio
import adafruit_bno055
import numpy as np
import math


class BNOSensor:
    """BNO055センサーを制御するクラス"""
    
    def __init__(self):
        """BNOSensorインスタンスを初期化"""
        self.i2c = None
        self.sensor = None
        self.connected = False
    
    def connect(self):
        """BNO055センサーに接続する
        
        Returns:
            bool: 接続成功時True、失敗時False
            
        Raises:
            Exception: I2C接続またはセンサー初期化に失敗した場合
        """
        try:
            # I2C接続を初期化
            self.i2c = busio.I2C(board.SCL, board.SDA)
            
            # BNO055センサーを初期化
            self.sensor = adafruit_bno055.BNO055_I2C(self.i2c)
            self.sensor.axis_remap = (2,1,0,1,1,1)
            
            # 接続テスト（センサーからデータを読み取り）
            test_data = self.sensor.euler
            if test_data is not None:
                self.connected = True
                return True
            else:
                raise Exception("センサーからデータを読み取れません")
                
        except Exception as e:
            self.connected = False
            raise Exception(f"BNO055センサーへの接続に失敗しました: {str(e)}")
    
    def euler(self):
        """オイラー角を取得する

        Returns:
            tuple: (heading, roll, pitch) の角度データ（度単位）

        Raises:
            Exception: センサーが接続されていない、またはデータ取得に失敗した場合
        """
        # 接続状態を確認
        if not self.connected or self.sensor is None:
            raise Exception("センサーが接続されていません。先にconnect()を呼び出してください")

        try:
            # オイラー角データを取得
            q = self.sensor.quaternion  # (heading, roll, pitch)
            if q is None:
                return None
            w, x, y, z = q

            # Roll (x軸回り)
            sinr_cosp = 2.0 * (w * x + y * z)
            cosr_cosp = 1.0 - 2.0 * (x * x + y * y)
            roll = math.atan2(sinr_cosp, cosr_cosp)

            # Pitch (y軸回り)
            sinp = 2.0 * (w * y - z * x)
            if abs(sinp) >= 1:
                pitch = math.copysign(math.pi / 2, sinp)  # ±90° (gimbal lock)
            else:
                pitch = math.asin(sinp)

            # Yaw (z軸回り)
            siny_cosp = 2.0 * (w * z + x * y)
            cosy_cosp = 1.0 - 2.0 * (y * y + z * z)
            yaw = math.atan2(siny_cosp, cosy_cosp)

            return (int(math.degrees(yaw)), int(math.degrees(roll)), int(math.degrees(pitch)))

        except Exception as e:
            self.connected = False
            raise Exception(f"角度データの取得に失敗しました: {str(e)}")
    
    def is_connected(self):
        """接続状態を確認する
        
        Returns:
            bool: 接続中の場合True、切断中の場合False
        """
        return self.connected
    
    def disconnect(self):
        """センサーとの接続を切断する"""
        if self.i2c:
            self.i2c.deinit()
        self.sensor = None
        self.connected = False