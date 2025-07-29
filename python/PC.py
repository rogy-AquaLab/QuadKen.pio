import asyncio
import numpy as np
import cv2
import yaml
# from simple_pid import PID
# import matplotlib.pyplot as plt
from tools.tcp import create_tcp
from tools.data_manager import DataManager , DataType
from tools.controller import Controller , Button


# 設定ファイルの読み込み
with open('config.yaml', 'r', encoding='utf-8') as f:
    config_data = yaml.safe_load(f)

# 初期化
try:
    controller = Controller()
except RuntimeError as e:
    print(f"⚠️ ジョイスティックの初期化に失敗: {e}")
    exit(1)
HOST = 'takapi.local'
PORT = 5000

tcp = create_tcp(HOST, PORT)


# ESP1用サーボデータ（4個）とESP2用サーボデータ（12個）
batt_servo_data = DataManager(0x11, 4, DataType.UINT8)  # ESP1用サーボ（4個）- 識別子0x11
legs_servo_data = DataManager(0x12, 12, DataType.UINT8)  # ESP2用サーボ（12個）- 識別子0x12

bldc_data = DataManager(0x02, 2, DataType.INT8)
bno_data = DataManager(0x03, 3, DataType.INT8)
config = DataManager(0xFF, 1, DataType.UINT8)

# config.yamlからmain_intervalを読み込み
main_interval = config_data.get('main', {}).get('interval', 0.1)

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

    # 脚部サーボデータの設定（12個のサーボ - ESP2用）
    legs_servo_values = legs_servo_data.get()  # デフォルト位置で初期化
    
    # 左スティックで脚部サーボを制御
    for i in range(12):
        legs_servo_values[i] = max(0, min(180, int(90 + angle * 0.5)))  # 角度に基づくサーボ制御
    
    # バッテリー部サーボデータの設定（4個のサーボ - ESP1用）
    batt_servo_values = batt_servo_data.get()  # デフォルト位置で初期化
    
    # Lスティック押し込み状態を取得
    l_stick_pressed = controller.is_button_pressed(Button.L_STICK)
    
    # A、B、X、Yボタンでバッテリー部サーボ（0～3番）を制御
    # Lスティック押し込み時：10度、非押し込み時：170度
    target_angle_pressed = 10    # Lスティック押し込み時の角度
    target_angle_released = 170  # Lスティック離し時の角度
    
    if controller.pushed_button(Button.A):  # Aボタンでバッテリーサーボ0番制御
        batt_servo_values[0] = target_angle_pressed if l_stick_pressed else target_angle_released
    
    if controller.pushed_button(Button.B):  # Bボタンでバッテリーサーボ1番制御
        batt_servo_values[1] = target_angle_pressed if l_stick_pressed else target_angle_released
    
    if controller.pushed_button(Button.X):  # Xボタンでバッテリーサーボ2番制御
        batt_servo_values[2] = target_angle_pressed if l_stick_pressed else target_angle_released
    
    if controller.pushed_button(Button.Y):  # Yボタンでバッテリーサーボ3番制御
        batt_servo_values[3] = target_angle_pressed if l_stick_pressed else target_angle_released
    
    # R2/L2ボタンの押し込み量でBLDCモーターを制御（-127～127の範囲）
    r2_value = controller.r2_push()  # 0.0～1.0の値を取得（前進）
    l2_value = controller.l2_push()  # 0.0～1.0の値を取得（後進）
    
    # 前進と後進の制御を統合（-127～127の範囲）
    bldc_speed = int(r2_value * 127) - int(l2_value * 128)
    # 範囲を-128～127に制限
    bldc_speed = max(-128, min(127, bldc_speed))
    bldc_values = [bldc_speed, bldc_speed]  # 2つのBLDCモーター用
    
    # データを更新
    legs_servo_data.update(legs_servo_values)
    batt_servo_data.update(batt_servo_values)
    bldc_data.update(bldc_values)
    
    await asyncio.gather(
        tcp.send(batt_servo_data.identifier(), batt_servo_data.pack()),  # ESP1（4個のサーボ）
        tcp.send(legs_servo_data.identifier(), legs_servo_data.pack()),  # ESP2（12個のサーボ）
        tcp.send(bldc_data.identifier(), bldc_data.pack()),
        asyncio.sleep(main_interval)  # 少し待つ
    )


async def Hreceive_Rasp():
    while True:
        data_type, size, data = await tcp.receive()

        if data_type == 0x00:  # 画像デー
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

