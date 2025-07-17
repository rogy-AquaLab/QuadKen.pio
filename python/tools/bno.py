import board
import busio
import adafruit_bno055

class Bno:
    """
    BNO055センサを使用するためのクラス
    - I2Cバスを使用してセンサと通信します。
    - センサの初期化時にクリスタルオシレータの使用を選択できます。
    - ヨー、ロール、ピッチの角度情報を取得するメソッドを提供します。
    """
    def __init__(self, use_crystal: bool = True, address: int = 0x28):
        """
        コンストラクタ
        :param use_crystal: Trueの場合、クリスタルオシレータを使用します。デフォルトはTrue。
        :param address: BNO055センサのI2Cアドレス。デフォルトは0x28。
        """
        self.i2c = None
        self.sensor = None
        self.use_crystal = use_crystal
        self.address = address
        self._is_connected = False

    def connect(self, use_crystal: bool = True, address: int = 0x28):
        """
        BNO055センサの初期化
        :param use_crystal: Trueの場合、クリスタルオシレータを使用します。デフォルトはTrue。
        :param address: BNO055センサのI2Cアドレス。デフォルトは0x28。
        :raises RuntimeError: センサの初期化に失敗した場合
        """
        try:
            # I2Cバスの初期化
            self.i2c = busio.I2C(board.SCL, board.SDA)
            # BNO055の初期化
            self.sensor = adafruit_bno055.BNO055_I2C(self.i2c, address=address)
            
            if use_crystal:
                self.sensor.use_external_crystal = True
            else:
                self.sensor.use_external_crystal = False
            
            # 接続テスト - センサから温度を読み取って接続を確認
            test_temp = self.sensor.temperature
            if test_temp is not None:
                self._is_connected = True
                print(f"✅ BNO055センサに接続完了 (アドレス: 0x{address:02X})")
            else:
                raise RuntimeError("センサとの通信に失敗しました")
                
        except Exception as e:
            self._is_connected = False
            raise RuntimeError(f"BNO055センサの初期化に失敗しました: {e}")

    def is_connected(self) -> bool:
        """
        センサの接続状態を確認するメソッド
        :return: 接続されている場合True、そうでなければFalse
        """
        if not self._is_connected or self.sensor is None:
            return False
        
        try:
            # 実際にセンサから値を読み取って接続状態を確認
            temp = self.sensor.temperature
            return temp is not None
        except Exception:
            self._is_connected = False
            return False

    def disconnect(self):
        """
        センサとの接続を切断するメソッド
        """
        self._is_connected = False
        self.sensor = None
        self.i2c = None
        print("❌ BNO055センサとの接続を切断しました")

    def ensure_connected(self) -> bool:
        """
        センサの接続を確保するメソッド
        接続されていない場合は自動的に接続を試行する
        :return: 接続に成功した場合True、失敗した場合False
        """
        if self.is_connected():
            return True
        
        try:
            self.connect(use_crystal=self.use_crystal, address=self.address)
            return True
        except RuntimeError:
            return False



    def euler(self):
        """
        ヨー、ロール、ピッチの角度情報を取得するメソッド
        :return: (heading, roll, pitch) = (ヨー, ロール, ピッチ) のタプル
        :raises RuntimeError: センサが接続されていない場合
        :raises ValueError: 角度情報が取得できない場合
        """
        # 接続状態を確認
        if not self.is_connected():
            raise RuntimeError("BNO055センサが接続されていません。先にconnect()メソッドを呼び出してください。")
        
        try:
            euler = self.sensor.euler  # (heading, roll, pitch) = (ヨー, ロール, ピッチ)
            if euler is None:
                raise ValueError("角度情報が取得できません")
            
            return euler
        except Exception as e:
            # 通信エラーが発生した場合、接続状態を無効化
            if "I2C" in str(e) or "communication" in str(e).lower():
                self._is_connected = False
                raise RuntimeError(f"センサとの通信が失われました: {e}")
            else:
                raise ValueError(f"角度情報の取得に失敗しました: {e}")

    def get_status(self) -> dict:
        """
        センサの詳細なステータス情報を取得するメソッド
        :return: ステータス情報の辞書
        :raises RuntimeError: センサが接続されていない場合
        """
        if not self.is_connected():
            raise RuntimeError("BNO055センサが接続されていません。")
        
        try:
            status = {
                "system_status": self.sensor.system_status,
                "system_error": self.sensor.system_error,
                "gyro_status": self.sensor.gyro_status,
                "accel_status": self.sensor.accel_status,
                "mag_status": self.sensor.mag_status,
                "temperature": self.sensor.temperature,
                "calibration_status": self.sensor.calibration_status
            }
            return status
        except Exception as e:
            self._is_connected = False
            raise RuntimeError(f"ステータス情報の取得に失敗しました: {e}")
