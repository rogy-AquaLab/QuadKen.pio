import board # type: ignore
import busio # type: ignore
import adafruit_bno055 # type: ignore

class Bno:
    """
    BNO055センサを使用するためのクラス
    - I2Cバスを使用してセンサと通信します。
    - センサの初期化時にクリスタルオシレータの使用を選択できます。
    - ヨー、ロール、ピッチの角度情報を取得するメソッドを提供します。
    """
    def __init__(self , use_crystal: bool = True):
        """
        BNO055センサの初期化
        :param use_crystal: Trueの場合、クリスタルオシレータを使用します。デフォルトはTrue。
        """
        # I2Cバスの初期化
        self.i2c = busio.I2C(board.SCL, board.SDA)
        # BNO055の初期化
        self.sensor = adafruit_bno055.BNO055_I2C(self.i2c)
        if use_crystal:
            self.sensor.use_crystal = True
        else:
            self.sensor.use_crystal = False

    def euler(self):
        """
        ヨー、ロール、ピッチの角度情報を取得するメソッド
        :return: (heading, roll, pitch) = (ヨー, ロール, ピッチ) のタプル
        :raises ValueError: 角度情報が取得できない場合
        """
        euler = self.sensor.euler  # (heading, roll, pitch) = (ヨー, ロール, ピッチ)
        if euler is None:
            raise ValueError("角度情報が取得できません")
        
        return euler
