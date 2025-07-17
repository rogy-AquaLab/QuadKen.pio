import asyncio
import numpy as np
import cv2
# from simple_pid import PID
# import matplotlib.pyplot as plt
from tools.tcp import Tcp
from tools.data_manager import DataManager , DataType
from tools.controller import Controller , Button


# 初期化
try:
    controller = Controller()
except RuntimeError as e:
    print(f"⚠️ ジョイスティックの初期化に失敗: {e}")
    exit(1)
HOST = 'takapi.local'
PORT = 5000

tcp = Tcp(HOST, PORT)

servo_data = DataManager(0x01, 16, DataType.UINT8)
bldc_data = DataManager(0x03, 4, DataType.INT8)
bno_data = DataManager(0x02, 3, DataType.INT8)
config = DataManager(0xFF, 1, DataType.UINT8)


async def main():
    if controller.pushed_button(Button.START):  # Aボタン
        config.update([1]) # ESPとの接続開始
        await asyncio.gather(
            tcp.send(config.identifier(), config.pack()),
            asyncio.sleep(0.1))  # 少し待つ
        return
    # elif controller.pushed_button(Button.HOME):  # Bボタン
    #     config.update([0]) 
    #     await asyncio.gather(
    #         tcp.send(config.identifier(), config.pack()),
    #         asyncio.sleep(0.1))  # 少し待つ
    #     return
    if controller.pushed_button(Button.SELECT):  # Bボタン
        raise EOFError("ユーザーがSelectボタンで終了")  # 明示的に終了を伝える


    # コントローラーの状態を更新
    controller.update()
    
    # スティックの値を取得
    angle, magnitude = controller.get_angle()
    
    # サーボデータの設定（16個のサーボ）
    servo_values = [90] * 16  # デフォルト位置で初期化
    
    # 左スティックでサーボを制御
    servo_values[0] = max(0, min(180, int(90 + angle * 0.5)))  # 角度に基づくサーボ制御
    servo_values[1] = max(0, min(180, int(magnitude * 180)))   # 大きさに基づくサーボ制御
    
    # 他のボタンでサーボを制御
    if controller.pushed_button(Button.A):
        servo_values[2] = 0    # Aボタンで3番目のサーボを0度
    if controller.pushed_button(Button.B):
        servo_values[2] = 180  # Bボタンで3番目のサーボを180度
    if controller.pushed_button(Button.X):
        servo_values[3] = 45   # Xボタンで4番目のサーボを45度
    if controller.pushed_button(Button.Y):
        servo_values[3] = 135  # Yボタンで4番目のサーボを135度
    
    # BLDCモーターデータの設定（4個のBLDCモーター、-127~127の範囲）
    bldc_values = [0] * 4  # 停止状態で初期化
    
    # 方向パッドでBLDCモーターを制御
    if controller.pushed_button(Button.UP):
        bldc_values[0] = 100    # 前進
    if controller.pushed_button(Button.DOWN):
        bldc_values[0] = -100   # 後退
    if controller.pushed_button(Button.LEFT):
        bldc_values[1] = -80    # 左回転
    if controller.pushed_button(Button.RIGHT):
        bldc_values[1] = 80     # 右回転
    
    # 右スティックでBLDCモーターの細かい制御
    # 仮に右スティックのメソッドがあると仮定（実装に応じて調整）
    # right_angle, right_magnitude = controller.get_right_angle()  # もしあれば
    # bldc_values[2] = max(-127, min(127, int(right_angle * 0.7)))
    # bldc_values[3] = max(-127, min(127, int(right_magnitude * 127)))
    
    # データを更新して送信
    servo_data.update(servo_values)
    bldc_data.update(bldc_values)
    
    await asyncio.gather(
        tcp.send(servo_data.identifier(), servo_data.pack()),
        # tcp.send(bldc_data.identifier(), bldc_data.pack()),
        asyncio.sleep(0.1)  # 少し待つ
    )


async def Hreceive_Rasp():
    while True:
        data_type, size, data = await tcp.receive()

        if data_type == 0x00:
            img_array = np.frombuffer(data, dtype=np.uint8)
            frame = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
            cv2.imshow('Async TCP Stream', frame)
            continue
        received_data = DataManager.unpack(data_type, data)
        print(f"📥 受信 : {received_data}")

async def tcp_client():
    print("🔵 接続中...")
    try:
        host , port = await tcp.connect()
    except ConnectionRefusedError as e:
        print(f"🚫 接続エラー: ラズパイのプログラムを起動してない可能性あり")
        print(f"⚠️ 詳細: {e}")
        return

    print(f"🔗 接続: {host}:{port}")

    receive_task = asyncio.create_task(Hreceive_Rasp())

    try:
        while True:
            await main()
            if receive_task.done():
                if receive_task.exception():
                    raise receive_task.exception()

    except (asyncio.IncompleteReadError , EOFError):
        print("🔴 Raspberry Pi側から接続が終了されました")
    except (ConnectionResetError, OSError) as e:
        print("🔌 接続がリセットされました、またはネットワークが利用不可になりました。")
        print(f"⚠️ 詳細: {e}")    
    finally:
        print("🧹 切断処理中...")
        receive_task.cancel()
        await asyncio.gather(receive_task, return_exceptions=True)
        await tcp.close()
        cv2.destroyAllWindows()
        print("✅ 終了しました")

asyncio.run(tcp_client())

