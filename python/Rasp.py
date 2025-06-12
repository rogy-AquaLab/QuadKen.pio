import asyncio
import struct
import cv2
from picamera2 import Picamera2
from bleak import BleakClient
from tools import tcp , ble
from tools.data_manager import DataManager

# ESP32デバイスのMACアドレス一覧（必要に応じて追加）
devices = [
    {"name": "ESP32-1", "address": "08:D1:F9:36:FF:3E"},
    # {"name": "ESP32-2", "address": "AA:BB:CC:44:55:66"},
]

CHAR_UUID = "abcd1234-5678-90ab-cdef-1234567890ab"

HOST = '0.0.0.0'  # 例: '192.168.0.10'
PORT = 5000

servo_data = DataManager(0x01, 8, 'BBBBBBBB')
bno_data = DataManager(0x02, 3, 'bbb')
config = DataManager(0xFF, 1, 'B')

async def connect_ESP(device):
    client = BleakClient(device["address"])
    try:
        await client.connect()
        print(f"✅ 接続成功: {device['name']} ({device['address']})")
        await client.start_notify(CHAR_UUID, Hreceive_ESP(device["name"]))

        return client
    except Exception as e:
        print(f"⚠️ 接続失敗: {device['name']} ({device['address']}) - {e}")
        return None

# 通知を受け取ったときのコールバック
def Hreceive_ESP(device_name):
    def handler(sender, data):
        # データを更新
        bno_data.unpack(data)
        # データを表示
        print(f"📨 受信 from {device_name}: {bno_data.get_data()}")
    return handler

async def Hsend_data_ESP(clients):
    while True:
        try:
            if not clients:
                print("⚠️ No ESP32 clients connected.")
                await asyncio.sleep(2.5)
                continue
            # 各ESP32にデータを送信
            for i, client in enumerate(clients):
                if client.is_connected:
                    await client.write_gatt_char(CHAR_UUID, servo_data.pack_data())
                    # print(f"📤 送信 to ESP32-{i}: {servo_data.get_data()}")
                else:
                    print(f"⚠️ ESP32-{i} is not connected.")
            await asyncio.sleep(0.1)  # 1秒おきに送信
        except asyncio.CancelledError:
            break
        except Exception as e:
            print(f"⚠️ データ送信失敗: {e}")

async def Hto_ESP():
    # ESP32との接続
    while True:
        try:
            print("🔄 ESP32との接続を開始...")
            clients = []
            for dev in devices:
                client = await ble.connect(dev, CHAR_UUID)
                if client:
                    clients.append(client)
                await asyncio.sleep(0.2)
            break
        except Exception as e:
            print(f"⚠️ ESP32接続エラー: {e}")
            await asyncio.sleep(2.5)
    
    # ESP32との受信を作成
    for client in clients:
        await client.start_notify(CHAR_UUID, Hreceive_ESP(device["name"]))
    
    # ESP32との送信を起動
    send_data_task = asyncio.create_task(Hsend_data_ESP(clients))

    try:
        await send_data_task
    except Exception as e:
        print(f"⚠️ データ送信失敗 {client.address}: {e}")
    except asyncio.CancelledError:
        pass
    finally:
        send_data_task.cancel()
        print(f"❌ 切断")
        for client in clients:
            if client.is_connected:
                await client.disconnect()
                print(f"❌ 切断: {client.address}")

async def Hreceive_PC(reader: asyncio.StreamReader):
    esp_task = None
    while True:
        try:
            data_type, size, data = await tcp.receive(reader)
            if data_type == 0xFF:
                config.unpack(data)
                print(f"📨 受信 from PC: {config.get_data()}")
                if esp_task is None or esp_task.done():
                # ESP32との接続を開始
                    esp_task = asyncio.create_task(Hto_ESP())
                continue
            print(f"📨 受信 from PC: {servo_data.get_data()}")
            servo_data.unpack(data)
        except asyncio.CancelledError:
            break

async def Hsend_data_PC(writer: asyncio.StreamWriter):
    while True:
        try:
            await tcp.send(writer, bno_data.data_type(), bno_data.pack_data())
            # print(f"📤 送信 to PC: {bno_data.get_data()}")
            await asyncio.sleep(0.05)  # 0.5秒おき
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
