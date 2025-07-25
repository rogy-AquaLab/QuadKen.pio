import board
import busio
import adafruit_bno055
import time

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
                print(f"   温度: {test_temp}°C")
                
                # センサの初期化待機時間
                print("   センサの初期化を待機中...")
                time.sleep(1.0)  # 1秒待機
                
                # キャリブレーション状態を確認
                cal_status = self.get_calibration_status()
                print(f"   キャリブレーション状態: システム={cal_status[0]}, ジャイロ={cal_status[1]}, 加速度={cal_status[2]}, 磁気={cal_status[3]}")
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



    def get_calibration_status(self) -> tuple:
        """
        センサのキャリブレーション状態を取得するメソッド
        :return: (system, gyro, accel, mag) の各キャリブレーション状態（0-3の値）
        """
        if not self._is_connected or self.sensor is None:
            return (0, 0, 0, 0)
        
        try:
            return self.sensor.calibration_status
        except Exception:
            return (0, 0, 0, 0)

    def wait_for_calibration(self, min_system: int = 1, timeout: float = 30.0) -> bool:
        """
        センサのキャリブレーションが完了するまで待機するメソッド
        :param min_system: 必要最小限のシステムキャリブレーション値（0-3）
        :param timeout: タイムアウト時間（秒）
        :return: キャリブレーションが完了した場合True
        """
        if not self.is_connected():
            return False
        
        start_time = time.time()
        print(f"キャリブレーション待機中（最小システム値: {min_system}）...")
        
        while time.time() - start_time < timeout:
            cal_status = self.get_calibration_status()
            system, gyro, accel, mag = cal_status
            
            print(f"キャリブレーション状態: システム={system}, ジャイロ={gyro}, 加速度={accel}, 磁気={mag}")
            
            if system >= min_system:
                print("✅ キャリブレーション完了")
                return True
            
            time.sleep(0.5)
        
        print("⚠️ キャリブレーションがタイムアウトしました")
        return False

    def euler(self, wait_for_data: bool = True, max_retries: int = 5):
        """
        ヨー、ロール、ピッチの角度情報を取得するメソッド
        :param wait_for_data: データが利用可能になるまで待機するかどうか
        :param max_retries: データ取得の最大試行回数
        :return: (heading, roll, pitch) = (ヨー, ロール, ピッチ) のタプル
        :raises RuntimeError: センサが接続されていない場合
        :raises ValueError: 角度情報が取得できない場合
        """
        # 接続状態を確認
        if not self.is_connected():
            raise RuntimeError("BNO055センサが接続されていません。先にconnect()メソッドを呼び出してください。")
        
        for attempt in range(max_retries):
            try:
                euler = self.sensor.euler  # (heading, roll, pitch) = (ヨー, ロール, ピッチ)
                
                if euler is not None:
                    # 有効なデータが取得できた場合
                    return euler
                elif wait_for_data and attempt < max_retries - 1:
                    # データがNoneで、まだリトライできる場合
                    print(f"データ取得待機中... (試行 {attempt + 1}/{max_retries})")
                    
                    # キャリブレーション状態を確認
                    cal_status = self.get_calibration_status()
                    system, gyro, accel, mag = cal_status
                    print(f"キャリブレーション状態: システム={system}, ジャイロ={gyro}, 加速度={accel}, 磁気={mag}")
                    
                    if system == 0:
                        print("ヒント: センサを様々な方向に動かしてキャリブレーションを行ってください")
                    
                    time.sleep(0.2)  # 200ms待機
                else:
                    # 最後の試行でもNoneだった場合
                    cal_status = self.get_calibration_status()
                    system, gyro, accel, mag = cal_status
                    
                    error_msg = f"角度情報が取得できません。キャリブレーション状態: システム={system}, ジャイロ={gyro}, 加速度={accel}, 磁気={mag}"
                    if system == 0:
                        error_msg += "\nヒント: センサを様々な方向に動かしてキャリブレーションを行ってください"
                    
                    raise ValueError(error_msg)
                    
            except Exception as e:
                # 通信エラーが発生した場合、接続状態を無効化
                if "I2C" in str(e) or "communication" in str(e).lower():
                    self._is_connected = False
                    raise RuntimeError(f"センサとの通信が失われました: {e}")
                elif attempt == max_retries - 1:
                    # 最後の試行でもエラーの場合
                    raise ValueError(f"角度情報の取得に失敗しました: {e}")
                else:
                    # まだリトライできる場合は少し待機
                    time.sleep(0.1)
        
        raise ValueError("角度情報の取得に失敗しました（最大試行回数に達しました）")

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

    def euler_with_auto_calibration(self, calibration_timeout: float = 30.0):
        """
        自動キャリブレーション付きで角度情報を取得するメソッド
        :param calibration_timeout: キャリブレーションのタイムアウト時間（秒）
        :return: (heading, roll, pitch) = (ヨー, ロール, ピッチ) のタプル
        """
        if not self.is_connected():
            raise RuntimeError("BNO055センサが接続されていません。")
        
        # キャリブレーション状態を確認
        cal_status = self.get_calibration_status()
        system, gyro, accel, mag = cal_status
        
        if system == 0:
            print("センサのキャリブレーションが必要です。")
            print("センサを以下のように動かしてキャリブレーションを行ってください：")
            print("1. 様々な方向に回転させる")
            print("2. X、Y、Z軸を中心に360度回転させる")
            print("3. 8の字を描くように動かす")
            
            if not self.wait_for_calibration(min_system=1, timeout=calibration_timeout):
                print("⚠️ キャリブレーションが完了しませんでした。部分的なデータで動作を試行します。")
        
        return self.euler(wait_for_data=True, max_retries=10)

    def get_euler_safe(self, default_value: tuple = (0.0, 0.0, 0.0)):
        """
        エラーが発生してもデフォルト値を返すsafeなeuler取得メソッド
        :param default_value: エラー時に返すデフォルト値
        :return: (heading, roll, pitch) のタプル、またはdefault_value
        """
        try:
            return self.euler(wait_for_data=False, max_retries=1)
        except Exception as e:
            print(f"⚠️ 角度データ取得エラー: {e}")
            return default_value


# 使用例
if __name__ == "__main__":
    # BNO055センサの使用例
    bno = Bno()
    
    try:
        # センサに接続
        bno.connect()
        
        # 自動キャリブレーション付きで角度を取得
        print("\n=== 自動キャリブレーション付き角度取得 ===")
        heading, roll, pitch = bno.euler_with_auto_calibration()
        print(f"ヨー: {heading:.2f}°, ロール: {roll:.2f}°, ピッチ: {pitch:.2f}°")
        
        # 通常の角度取得
        print("\n=== 通常の角度取得 ===")
        for i in range(5):
            try:
                heading, roll, pitch = bno.euler()
                print(f"[{i+1}] ヨー: {heading:.2f}°, ロール: {roll:.2f}°, ピッチ: {pitch:.2f}°")
            except ValueError as e:
                print(f"[{i+1}] エラー: {e}")
            time.sleep(1)
        
        # セーフモードでの角度取得
        print("\n=== セーフモードでの角度取得 ===")
        for i in range(3):
            heading, roll, pitch = bno.get_euler_safe()
            print(f"[{i+1}] ヨー: {heading:.2f}°, ロール: {roll:.2f}°, ピッチ: {pitch:.2f}°")
            time.sleep(0.5)
        
    except Exception as e:
        print(f"エラー: {e}")
    finally:
        bno.disconnect()
