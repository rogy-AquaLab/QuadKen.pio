import asyncio
import struct
import cv2
from picamera2 import Picamera2 # type: ignore
from tools import tcp
from tools.data_manager import DataManager , DataType
from tools.ble import Ble

# ESP32デバイスのMACアドレス一覧（必要に応じて追加）
devices = [
    {"num": 1, "address": "08:D1:F9:36:FF:3E" , "char_uuid": "abcd1234-5678-90ab-cdef-1234567890ab"},
    # {"num": 2, "address": "AA:BB:CC:44:55:66" , "char_uuid": "abcd1234-5678-90ab-cdef-1234567890cd"},
]
esps = [Ble(device['num'], device['address'], device['char_uuid']) for device in devices]


HOST = '0.0.0.0'  # 例: '192.168.0.10'
PORT = 5000

# データ管理インスタンスの作成
servo_data = DataManager(0x01, 8, DataType.UINT8)
bno_data = DataManager(0x02, 3, DataType.INT8)
config = DataManager(0xFF, 1, DataType.UINT8)

# 通知を受け取ったときのコールバック
def Hreceive_ESP(device_num , data_type, size, data):
    # データを更新
    received_data = DataManager.unpack(data_type, data)
    
    # データを表示
    print(f"📨 受信 from ESP-{device_num}: {received_data}")

async def Hsend_data_ESP():
    while True:
        try:
            if not esps:
                print("⚠️ ESP32デバイスが接続されていません。")
                await asyncio.sleep(2.5)
                break
            # 各ESP32にデータを送信
            for i, esp in enumerate(esps):
                await esp.send(servo_data.data_type(), servo_data.pack_data())
                # print(f"📤 送信 to {esp}: {servo_data.get_data()}")
            await asyncio.sleep(0.1)  # 1秒おきに送信
        except asyncio.CancelledError:
            break
        except Exception as e:
            raise Exception(f"{e}")

async def Hto_ESP():
    # ESP32との接続
    while True:
        try:
            print("🔄 ESP32との接続を開始...")
            for esp in esps:
                await esp.connect(Hreceive_ESP)
                print(f"✅ {esp} に接続完了")
            break
        except Exception as e:
            print(f"⚠️ ESP32接続エラー: {e}")
            await asyncio.sleep(2.5)
        
    print("✅ ESP32との接続完了")

    # ESP32との送信を起動
    send_data_task = asyncio.create_task(Hsend_data_ESP())

    try:
        await send_data_task
    except Exception as e:
        print(f"⚠️ データ送信失敗: {e}")
    except asyncio.CancelledError:
        pass
    finally:
        send_data_task.cancel()
        print(f"❌ 切断")
        for esp in esps:
            await esp.disconnect()
            print(f"❌ 切断: {esp}")

async def Hreceive_PC(reader: asyncio.StreamReader):
    esp_task = None
    while True:
        try:
            data_type, size, data = await tcp.receive(reader)
            if data_type == 0xFF:
                if esp_task is None or esp_task.done():
                # ESP32との接続を開始
                    esp_task = asyncio.create_task(Hto_ESP())
                continue

            received_data = DataManager.unpack(data_type, data)
            print(f"📨 受信 from PC: {received_data}")
        except asyncio.CancelledError:
            break

async def Hsend_data_PC(writer: asyncio.StreamWriter):
    while True:
        try:
            await tcp.send(writer, bno_data.data_type(), bno_data.pack_data())
            # print(f"📤 送信 to PC: {bno_data.get_data()}")
            await asyncio.sleep(0.5)  # 0.5秒おき
        except asyncio.CancelledError:
            pass
        except ValueError as e:
            print(f"⚠️ 入力エラー: {e}")

async def capture_frame(picam):
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, picam.capture_array)

async def Hsend_image_PC(writer: asyncio.StreamWriter):
    while True:
        try:
            print("🔄 カメラ初期化中...")
            picam = Picamera2()
            await asyncio.sleep(1)  # 少し待つと安定する

            # カメラ設定と起動
            picam.configure(picam.create_video_configuration(main={"format": 'RGB888'}))
            picam.start()
            print("✅ カメラ準備完了")

            # フレーム送信ループ
            await stream_frames(picam, writer)

        except Exception as e:
            print(f"❌ カメラ初期化失敗: {e}")

        finally:
            if 'picam' in locals():
                picam.close()
                print("📷 カメラ停止")

        print("⏳ カメラ再接続待機中（5秒）...")
        await asyncio.sleep(5)

async def stream_frames(picam, writer):
    """カメラからフレームを取得して送信する処理"""
    while True:
        try:
            frame = await asyncio.wait_for(capture_frame(picam), timeout=5.0)
            _, jpeg = cv2.imencode('.jpg', frame)
            data = jpeg.tobytes()

            # ヘッダー形式: [1バイト: 種別 (0x01)] + [4バイト: データ長]
            await tcp.send(writer, 0x00, data)

            await asyncio.sleep(2.5)  # 次のフレームまで待機

        except asyncio.TimeoutError:
            print("⚠ フレーム取得タイムアウト。再試行します。")
            break
        except Exception as e:
            print(f"⚠ フレーム取得エラー: {e}")
            break

async def Hto_PC(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    # PCとの接続待機
    addr = writer.get_extra_info('peername')
    print(f"🔗 接続: {addr}")

    # PCとの送受信を起動
    receive_task = asyncio.create_task(Hreceive_PC(reader))
    send_data_task = asyncio.create_task(Hsend_data_PC(writer))
    send_image_task = asyncio.create_task(Hsend_image_PC(writer))

    # PCとの切断時処理
    try:
        await receive_task

        await asyncio.gather(send_data_task, send_image_task)
    except asyncio.CancelledError:
        pass
    except (ConnectionResetError, BrokenPipeError) as e:
        print(f"⚠️ 接続エラー: {e}")
    finally:
        receive_task.cancel()
        send_data_task.cancel()
        send_image_task.cancel()
        print(f"❌ 切断: {addr}")
        if not writer.is_closing():
            writer.close()
            await writer.wait_closed()

async def main():
    server = await asyncio.start_server(Hto_PC, HOST, PORT)
    addr = server.sockets[0].getsockname()
    print(f"🚀 サーバー起動: {addr}")

    async with server:
        await server.serve_forever()

asyncio.run(main())
