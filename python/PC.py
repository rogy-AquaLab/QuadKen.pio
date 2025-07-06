import asyncio
import cv2
from simple_pid import PID
import matplotlib.pyplot as plt
import numpy as np
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

servo_data = DataManager(0x01, 8, DataType.UINT8)
bno_data = DataManager(0x02, 3, DataType.INT8)
config = DataManager(0xFF, 1, DataType.UINT8)

# def button_check():
#     for button in range(20):  # ボタンの数は10個
#         controller.update()  # コントローラーの状態を更新
#         if controller.pushed_button(button):
#             print(f"ボタン {button} が押されました")

async def main():

    if controller.pushed_button(Button.A):  # Aボタン
        print("Aボタンが押されました")
        await asyncio.gather(
            tcp.send(config.identifier(), config.pack()),
            asyncio.sleep(0.1))  # 少し待つ
        return
    if controller.pushed_button(Button.SELECT):  # Bボタン
        raise EOFError("ユーザーがSelectボタンで終了")  # 明示的に終了を伝える


    # スティックの値を取得（例：左スティックX/Y軸）
    data8 = [0] * 8
    controller.update()  # コントローラーの状態を更新
    angle , magnitude = controller.get_angle()
    print(f"角度: {angle:.2f}, 大きさ: {magnitude:.2f}")
    data8[0] = int(angle if angle > 0 else 0)  # 角度を整数に変換
    data8[1] = int(magnitude * 100)  # 大きさを0-100の範囲に変換
    servo_data.update(data8)
    await asyncio.gather(
        tcp.send(servo_data.identifier(), servo_data.pack()),
        asyncio.sleep(0.1)  # 少し待つ
    )


async def Hreceive_Rasp():
    while True:
        try:
            data_type, size, data = await tcp.receive()

            if data_type == 0x00:
                img_array = np.frombuffer(data, dtype=np.uint8)
                frame = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
                cv2.imshow('Async TCP Stream', frame)
                if cv2.waitKey(1) == ord('q'):
                    raise EOFError("ユーザーが'q'で終了")  # 明示的に終了を伝える
            
            received_data = DataManager.unpack(data_type, data)
            print(f"📥 受信 : {received_data}")
        except (asyncio.IncompleteReadError, EOFError) as e:
            raise

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

    except (EOFError, KeyboardInterrupt) as e:
        print(f"⛔ 終了: {e}")
    except (asyncio.IncompleteReadError , EOFError):
        print("🔴 Raspberry Pi側から接続が終了されました")
    except (ConnectionResetError, OSError) as e:
        print("🔌 接続がリセットされました、またはネットワークが利用不可になりました。")
        print(f"⚠️ 詳細: {e}")    
    finally:
        print("🧹 切断処理中...")
        receive_task.cancel()
        try:
            await receive_task
        except Exception:
            pass
        await tcp.close()
        cv2.destroyAllWindows()
        print("✅ 終了しました")

asyncio.run(tcp_client())

