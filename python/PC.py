import asyncio
import cv2
import struct
import numpy as np
from tools import tcp
from tools.data_manager import DataManager , DataType


HOST = 'takapi.local'
PORT = 5000

async def async_input(prompt: str = "") -> str:
    return await asyncio.to_thread(input, prompt)

servo_data = DataManager(0x01, 8, DataType.UINT8)
bno_data = DataManager(0x02, 3, DataType.INT8)
config = DataManager(0xFF, 1, DataType.UINT8)


async def Hsend_Rasp(writer: asyncio.StreamWriter):
    n= 0
    while True:
        if n == 10:
            print("10回送信")
            await tcp.send(writer, config.identifier(), config.pack())
            n = 0
            await asyncio.sleep(1)
            continue
            
        await tcp.send(writer, servo_data.identifier(), servo_data.pack())
        # print(f"📤 送信 : {servo_data.get_data()}")
        await asyncio.sleep(1)
        n += 1

async def Hreceive_Rasp(reader: asyncio.StreamReader):
    while True:
        data_type, size, data = await tcp.receive(reader)

        if data_type == 0x00:
            img_array = np.frombuffer(data, dtype=np.uint8)
            frame = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
            cv2.imshow('Async TCP Stream', frame)
            if cv2.waitKey(1) == ord('q'):
                raise EOFError("ユーザーが'q'で終了")  # 明示的に終了を伝える
        
        received_data = DataManager.unpack(data_type, data)
        print(f"📥 受信 : {received_data}")

async def tcp_client():
    print("🔵 接続中...")
    
    reader, writer = await asyncio.open_connection(HOST, PORT)
    print(f"🔗 接続: {HOST}:{PORT}")

    send_task = asyncio.create_task(Hsend_Rasp(writer))
    receive_task = asyncio.create_task(Hreceive_Rasp(reader))
    try:
        while True:
            data8 = [0] * 8
            for i in range(8):
                text = await async_input(f"{i}番目の整数を入力してください（または e で終了）: ")
                if text.lower() == "e":
                    raise EOFError("ユーザーが入力で終了を選択")

                try:
                    num = int(text)
                    if not 0 <= num <= 255:
                        raise ValueError
                except ValueError:
                    print("⚠️ 整数ではありません。0にします。")
                    num = 0
                data8[i] = num

            servo_data.update(data8)
            print("✅ 入力完了:", data8)
            await asyncio.sleep(1)

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

        if 'writer' in locals():
            writer.close()
            await writer.wait_closed()
        cv2.destroyAllWindows()
        print("✅ 終了しました")

asyncio.run(tcp_client())
