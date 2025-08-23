import asyncio
import numpy as np
import cv2
import yaml
import math
# from simple_pid import PID
# import matplotlib.pyplot as plt
from tools.tcp import create_tcp
from tools.data_manager import DataManager , DataType
from tools.controller import Controller , Button
from tools.calc import Calc


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

legs_servo_num = [6,7,8,11]
bno_camera_offset = -130
# bno_legs_offset = 45
# bno_tank_offset = 0


# ESP1用サーボデータ（4個）とESP2用サーボデータ（12個）
batt_servo_data = DataManager(0x11, 4, DataType.UINT8)  # ESP1用サーボ（4個）- 識別子0x11
legs_servo_data = DataManager(0x12, 12, DataType.UINT8)  # ESP2用サーボ（12個）- 識別子0x12

bldc_data = DataManager(0x02, 2, DataType.INT8)
bno_data = DataManager(0x03, 3, DataType.INT8)
config = DataManager(0xFF, 1, DataType.UINT8)

# config.yamlからmain_intervalを読み込み
main_interval = config_data.get('main', {}).get('interval', 0.1)

def batt_servo_control(twist,l1,num):
    batt_servo_values = batt_servo_data.get()  # デフォルト位置で初期化

    target_angle_pressed = 10    # 押し込み時の角度
    target_angle_released = 170  # 離し時の角度

    if l1:  # L1押し込み時
        batt_servo_values[num] = target_angle_pressed
    else:  # L1離し時
        batt_servo_values[num] = target_angle_released

    # right_barast = left_barast = up_barast = down_barast = target_angle_pressed

    # if num == 0:  # Aボタンでバッテリーサーボ0番制御
    #     down_barast = target_angle_pressed if lstick else target_angle_released
    
    # if num == 1:  # Bボタンでバッテリーサーボ1番制御
    #     right_barast = target_angle_pressed if lstick else target_angle_released

    # if num == 2:  # Yボタンでバッテリーサーボ2番制御
    #     up_barast = target_angle_pressed if lstick else target_angle_released

    # if num == 3:  # Xボタンでバッテリーサーボ3番制御
    #     left_barast = target_angle_pressed if lstick else target_angle_released

    # # twistの値に基づいてbarastを割り当て
    # if -45 <= twist < 45:  # 前方向 (0度付近)
    #     batt_servo_values[0] = down_barast
    #     batt_servo_values[1] = right_barast
    #     batt_servo_values[2] = up_barast
    #     batt_servo_values[3] = left_barast
    # elif 45 <= twist < 135:  # 右方向 (90度付近)
    #     batt_servo_values[0] = left_barast
    #     batt_servo_values[1] = down_barast
    #     batt_servo_values[2] = right_barast
    #     batt_servo_values[3] = up_barast
    # elif 135 <= twist <= 180 or -180 <= twist < -135:  # 後方向 (180度付近)
    #     batt_servo_values[0] = up_barast
    #     batt_servo_values[1] = left_barast
    #     batt_servo_values[2] = down_barast
    #     batt_servo_values[3] = right_barast
    # else:  # -135 <= twist < -45: 左方向 (-90度付近)
    #     batt_servo_values[0] = right_barast
    #     batt_servo_values[1] = up_barast
    #     batt_servo_values[2] = left_barast
    #     batt_servo_values[3] = down_barast

    batt_servo_data.update(batt_servo_values)

async def main():
    bno = bno_data.get()
    theta, phi, bno_twist = bno[0], bno[1]*3, bno[2]*2
    twist = bno_twist - bno_camera_offset
    twist = twist if twist <= 180 else twist - 360  # ヘディングを-180〜180に変換
    twist = -twist
    print(f"θ: {theta}° φ: {phi}° twist: {twist}°")

    # コントローラーの状態を更新
    controller.update()

    # L1,R1押し込み状態を取得
    l1_pressed = controller.is_button_pressed(Button.L1)
    r1_pressed = controller.is_button_pressed(Button.R1)

    if controller.pushed_button(Button.START):  # STARTボタン
        config.update([1]) # ESPとの接続開始
        await tcp.send(config.identifier(), config.pack())
        return



    if controller.pushed_button(Button.L_STICK):  # Lスティックボタン
        config.update([2])  # ESPセットアップコマンド
        await tcp.send(config.identifier(), config.pack())
        return

    if controller.pushed_button(Button.R_STICK):  # Rスティックボタン
        config.update([3])  # ESP設定3コマンド
        await tcp.send(config.identifier(), config.pack())
        return
    if controller.pushed_button(Button.SELECT):  # SELECTボタン
        batt_servo_data.update([5,5,5,5])
        await tcp.send(batt_servo_data.identifier(), batt_servo_data.pack()),  # ESP1（4個のサーボ）
        raise EOFError("ユーザーがSelectボタンで終了")  # 明示的に終了を伝える



    
    # スティックの値を取得
    left_angle, left_magnitude = controller.get_left_angle()
    right_angle, right_magnitude = controller.get_right_angle()

    # 脚部サーボデータの設定（12個のサーボ - ESP2用）
    legs_servo_values = legs_servo_data.get()  # デフォルト位置で初期化
        
    # 左スティックで脚部サーボを制御
    if left_magnitude > 0.5:  # スティックが動いている場合
        for i in legs_servo_num:
            legs_servo_values[i] = max(0, min(180, int(90 + left_angle * 0.5)))  # 角度に基づくサーボ制御


    if right_magnitude > 0.2:  # 右スティックが動いている場合
        # controller_angle = right_angle - twist
        # ver_power = math.sin(math.radians(controller_angle)) * 180 * right_magnitude
        # hor_power = math.cos(math.radians(controller_angle)) * 180 * right_magnitude

        up_value, down_value, left_value, right_value = Calc.legs_power(twist, right_angle, right_magnitude, l1_pressed)

        legs_servo_values[legs_servo_num[0]] = up_value
        legs_servo_values[legs_servo_num[3]] = right_value
        legs_servo_values[legs_servo_num[2]] = down_value
        legs_servo_values[legs_servo_num[1]] = left_value


    # バッテリー部サーボデータの設定（4個のサーボ - ESP1用）
    batt_servo_values = batt_servo_data.get()  # デフォルト位置で初期化
    
    # A、B、X、Yボタンでバッテリー部サーボ（0～3番）を制御
    # Lスティック押し込み時：10度、非押し込み時：170度
    target_angle_pressed = 10    # Lスティック押し込み時の角度
    target_angle_released = 170  # Lスティック離し時の角度

    if controller.pushed_button(Button.Y):  # Yボタンでバッテリーサーボ0番制御
        batt_servo_control(twist=twist, l1=l1_pressed, num=0)

    if controller.pushed_button(Button.B):  # Bボタンでバッテリーサーボ1番制御
        batt_servo_control(twist=twist, l1=l1_pressed, num=1)

    if controller.pushed_button(Button.A):  # Aボタンでバッテリーサーボ2番制御
        batt_servo_control(twist=twist, l1=l1_pressed, num=2)

    if controller.pushed_button(Button.X):  # Xボタンでバッテリーサーボ3番制御
        batt_servo_control(twist=twist, l1=l1_pressed, num=3)


    
    # R2/L2ボタンの押し込み量でBLDCモーターを制御（-127～127の範囲）
    r2_value = controller.r2_push()  # 0.0～1.0の値を取得（前進）
    l2_value = controller.l2_push()  # 0.0～1.0の値を取得（後進）
    
    # BLDCの進行方向の指定
    if r1_pressed:
        bldc_speed = int(r2_value * 127)
    else:
        bldc_speed = int(-r2_value * 127)

    bldc_values = [bldc_speed, bldc_speed]  # 2つのBLDCモーター用
    
    print(f"{legs_servo_values}")

    # データを更新
    legs_servo_data.update(legs_servo_values)
    # batt_servo_data.update(batt_servo_values)
    bldc_data.update(bldc_values)
    
    
    await asyncio.gather(
        tcp.send(batt_servo_data.identifier(), batt_servo_data.pack()),  # ESP1（4個のサーボ）
        tcp.send(legs_servo_data.identifier(), legs_servo_data.pack()),  # ESP2（12個のサーボ）
        tcp.send(bldc_data.identifier(), bldc_data.pack())
    )


async def Hreceive_Rasp():
    while True:
        data_type, size, data = await tcp.receive()

        if data_type == 0x00:  # 画像データ
            img_array = np.frombuffer(data, dtype=np.uint8)
            frame = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
            
            if frame is not None:
                cv2.imshow('Async TCP Stream', frame)
                cv2.waitKey(1)
            continue
            
        received_data = DataManager.unpack(data_type, data)
        # print(f"📥 受信 : {received_data}")

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
            # main()とsleepを分離して並行実行
            await asyncio.gather(
                main(),
                asyncio.sleep(main_interval)
            )
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

