import asyncio
import cv2
import struct
import numpy as np
from tools import tcp
from tools.data_manager import DataManager

HOST = 'takapi.local'
PORT = 5000

async def async_input(prompt: str = "") -> str:
    return await asyncio.to_thread(input, prompt)

servo_data = DataManager(b'\x01', 8, 'BBBBBBBB')
bno_data = DataManager(b'\x02', 3, 'bbb')

async def Hsend_Rasp(writer: asyncio.StreamWriter):
    while True:
        await tcp.send(writer, servo_data.data_type(), servo_data.pack_data())
        print(f"📤 送信 : {servo_data.get_data()}")
        await asyncio.sleep(1)

async def Hreceive_Rasp(reader: asyncio.StreamReader):
    while True:
        data_type, size, data = await tcp.receive(reader)
        print(f"📥 受信 : タイプ={data_type}, サイズ={size}バイト")

        if data_type == 0x00:
            img_array = np.frombuffer(data, dtype=np.uint8)
            frame = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
            cv2.imshow('Async TCP Stream', frame)
            if cv2.waitKey(1) == ord('q'):
                raise EOFError("ユーザーが'q'で終了")  # 明示的に終了を伝える
        elif data_type == 0x02:
            bno_data.unpack(data)
            print(f"📨 受信: {bno_data.get_data()}")
        else:
            raise ValueError(f"未知のデータタイプ: {data_type}")

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

            servo_data.update_data(data8)
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
