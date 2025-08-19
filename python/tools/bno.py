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
            quat = self.sensor.quaternion

            if quat is None:
                # 接続が切れている可能性
                self.connected = False
                raise Exception("センサーとの接続が切れています")
            w, x, y, z = quat

            # quaternion から直接軸ベクトルを計算
            z_axis = np.array([
                2*(x*z + y*w),
                2*(y*z - x*w),
                1 - 2*(x*x + y*y)
            ])
            x_axis = np.array([
                1 - 2*(y*y + z*z),
                2*(x*y + z*w),
                2*(x*z - y*w)
            ])

            # θ: 倒れ角
            zz = z_axis[2]
            theta = 90 - math.degrees(math.acos(np.clip(zz, -1.0, 1.0)))

            # φ: 倒れ方向（北基準）
            phi = math.degrees(math.atan2(z_axis[0], z_axis[1]))
            if phi < 0:
                phi += 360

            # twist: 特殊ベクトルとX軸ベクトルの角度
            r = np.hypot(z_axis[0], z_axis[1])
            vec = np.array([z_axis[0], z_axis[1], -r*r/zz if zz != 0 else 0.0])

            norm_vec = np.linalg.norm(vec)
            norm_x = np.linalg.norm(x_axis)
            if norm_vec == 0 or norm_x == 0:
                twist = 0.0
            else:
                cos_angle = np.clip(np.dot(vec, x_axis) / (norm_vec * norm_x), -1.0, 1.0)
                twist_angle = math.degrees(math.acos(cos_angle))
                cross_z = np.cross(x_axis, vec)[2]
                twist = twist_angle if cross_z >= 0 else -twist_angle

            return {int(theta), int(phi), int(twist)}

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