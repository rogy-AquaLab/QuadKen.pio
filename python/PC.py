import asyncio
import cv2
import struct
from simple_pid import PID
import matplotlib.pyplot as plt
import numpy as np
from tools.tcp import Tcp
from tools.data_manager import DataManager , DataType

import pygame

# 初期化
pygame.init()
pygame.joystick.init()
joystick = pygame.joystick.Joystick(0)
joystick.init()
print(f"接続中のジョイスティック: {joystick.get_name()}")

# ジョイスティック接続確認
if pygame.joystick.get_count() == 0:
    print("ジョイスティックが接続されていません。")
    exit()

HOST = 'takapi.local'
PORT = 5000

tcp = Tcp(HOST, PORT)

async def async_input(prompt: str = "") -> str:
    return await asyncio.to_thread(input, prompt)

servo_data = DataManager(0x01, 8, DataType.UINT8)
bno_data = DataManager(0x02, 3, DataType.INT8)
config = DataManager(0xFF, 1, DataType.UINT8)


async def Hsend_Rasp():
    n= 0
    while True:
        if n == 10:
            print("10回送信")
            await tcp.send(config.identifier(), config.pack())
            # n = 0
            await asyncio.sleep(1)
            n +=1
            continue
            
        await tcp.send(servo_data.identifier(), servo_data.pack())
        print(f"📤 送信 : {servo_data.get()}")
        await asyncio.sleep(0.2)
        n += 1

async def Hreceive_Rasp():
    while True:
        data_type, size, data = await tcp.receive()

        if data_type == 0x00:
            img_array = np.frombuffer(data, dtype=np.uint8)
            frame = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
            cv2.imshow('Async TCP Stream', frame)
            if cv2.waitKey(1) == ord('q'):
                raise EOFError("ユーザーが'q'で終了")  # 明示的に終了を伝える
        
        received_data = DataManager.unpack(data_type, data)
        print(f"📥 受信 : {received_data}")

async def Hpid():
    pid = PID(1, 0, 0.05, setpoint=120)
    pid.output_limits = (0, 180)
    pid.sample_time = 1
    await asyncio.sleep(1)


async def tcp_client():
    print("🔵 接続中...")
    
    host , port = await tcp.connect()
    print(f"🔗 接続: {host}:{port}")

    send_task = asyncio.create_task(Hsend_Rasp())
    receive_task = asyncio.create_task(Hreceive_Rasp())
    pid_task = asyncio.create_task(Hpid())

    try:
        while True:
            data8 = [0] * 8
            pygame.event.pump()

            # スティックの値を取得（例：左スティックX/Y軸）
            axis_x = joystick.get_axis(0)
            # print(f"スティック: X={axis_x:.2f}")

            servo_angle = int((axis_x + 1) * 90)
            data8[0] = servo_angle

            
            servo_data.update(data8)
            # print("✅ 入力完了:", data8)
            await asyncio.sleep(0.1)

    except (EOFError, KeyboardInterrupt) as e:
        print(f"⛔ 終了: {e}")
    except asyncio.IncompleteReadError:
        print("🔴 Raspberry Pi側から接続が終了されました")
    except ConnectionRefusedError:
        print("🚫 接続できませんでした（Raspberry Piが起動していない可能性）")
    except Exception as e:
        print(f"⚠️ 予期しないエラー: {e}")
    finally:
        print("🧹 切断処理中...")
        if 'send_task' in locals():
            send_task.cancel()
        if 'receive_task' in locals():
            receive_task.cancel()
        await asyncio.gather(*[t for t in [send_task, receive_task] if t], return_exceptions=True)

        await tcp.close()
        cv2.destroyAllWindows()
        print("✅ 終了しました")

asyncio.run(tcp_client())
