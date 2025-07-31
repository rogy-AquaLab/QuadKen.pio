import board
import busio
import adafruit_bno055


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
            euler_data = self.sensor.euler
            
            if euler_data is None:
                # 接続が切れている可能性
                self.connected = False
                raise Exception("センサーとの接続が切れています")
            
            return euler_data
            
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