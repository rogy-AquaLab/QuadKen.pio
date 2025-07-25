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
bldc_data = DataManager(0x02, 2, DataType.UINT8)
bno_data = DataManager(0x03, 3, DataType.INT8)
config = DataManager(0xFF, 1, DataType.UINT8)


async def main():
    if controller.pushed_button(Button.START):  # STARTボタン
        config.update([1]) # ESPとの接続開始
        await asyncio.gather(
            tcp.send(config.identifier(), config.pack()),
            asyncio.sleep(0.1))  # 少し待つ
        return
    
    if controller.pushed_button(Button.L1):  # L1ボタン
        config.update([2])  # ESPセットアップコマンド
        await asyncio.gather(
            tcp.send(config.identifier(), config.pack()),
            asyncio.sleep(0.1))  # 少し待つ
        return
    
    if controller.pushed_button(Button.R1):  # R1ボタン
        config.update([3])  # ESP設定3コマンド
        await asyncio.gather(
            tcp.send(config.identifier(), config.pack()),
            asyncio.sleep(0.1))  # 少し待つ
        return
    if controller.pushed_button(Button.SELECT):  # SELECTボタン
        raise EOFError("ユーザーがSelectボタンで終了")  # 明示的に終了を伝える



    # コントローラーの状態を更新
    controller.update()
    
    # スティックの値を取得
    angle, magnitude = controller.get_angle()

    # サーボデータの設定（12個のサーボ）
    servo_values = servo_data.get()  # デフォルト位置で初期化
    
    # 左スティックでサーボを制御
    for i in range(12):
        servo_values[i] = max(0, min(180, int(90 + angle * 0.5)))  # 角度に基づくサーボ制御
    
    # Lスティック押し込み状態を取得
    l_stick_pressed = controller.is_button_pressed(Button.L_STICK)
    
    # A、B、X、Yボタンでサーボ12～15番を制御
    # Lスティック押し込み時：10度、非押し込み時：170度
    target_angle_pressed = 10    # Lスティック押し込み時の角度
    target_angle_released = 170  # Lスティック離し時の角度
    
    if controller.pushed_button(Button.A):  # Aボタンでサーボ12番制御
        servo_values[12] = target_angle_pressed if l_stick_pressed else target_angle_released
    
    if controller.pushed_button(Button.B):  # Bボタンでサーボ13番制御
        servo_values[13] = target_angle_pressed if l_stick_pressed else target_angle_released
    
    if controller.pushed_button(Button.X):  # Xボタンでサーボ14番制御
        servo_values[14] = target_angle_pressed if l_stick_pressed else target_angle_released
    
    if controller.pushed_button(Button.Y):  # Yボタンでサーボ15番制御
        servo_values[15] = target_angle_pressed if l_stick_pressed else target_angle_released
    
    # R2ボタンの押し込み量でBLDCモーターを制御（127.5～255の範囲）
    r2_value = controller.r2_push()  # 0.0～1.0の値を取得
    bldc_speed = int(127.5 - (r2_value * 127.5))  # 127.5～255の範囲に変換
    bldc_values = [bldc_speed, bldc_speed]  # 2つのBLDCモーター用
    
    # データを更新して送信
    servo_data.update(servo_values)
    bldc_data.update(bldc_values)
    
    await asyncio.gather(
        tcp.send(servo_data.identifier(), servo_data.pack()),
        tcp.send(bldc_data.identifier(), bldc_data.pack()),
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

