import asyncio
import time
from tools.tcp import Tcp
from tools.data_manager import DataManager , DataType
from tools.ble import Ble
from tools.bno import Bno
from tools.camera import Picam

# Hto_ESPが複数同時に実行されないようにするため、やむなく実装
esp_task = None

# ESP32デバイスのMACアドレス一覧（必要に応じて追加）
devices = [
    {"num": 1, "address": "08:D1:F9:36:FF:3E" , "char_uuid": "abcd1234-5678-90ab-cdef-1234567890cd"},
    # {"num": 2, "address": "CC:7B:5C:E8:E3:32" , "char_uuid": "abcd1234-5678-90ab-cdef-1234567890cd"},
]
esps = [Ble(device['num'], device['address'], device['char_uuid']) for device in devices]

HOST = '0.0.0.0'  # 例: '192.168.0.10'
PORT = 5000

tcp = Tcp(HOST, PORT)

# データ管理インスタンスの作成
servo_data = DataManager(0x01, 8, DataType.UINT8)
bno_data = DataManager(0x02, 3, DataType.INT8)
config = DataManager(0xFF, 1, DataType.UINT8)

async def shutdown():
    print("🧹 シャットダウン処理中...")
    for esp in esps:
        await esp.disconnect()
        print(f"❌ 切断: {esp}")
    await tcp.close()
    print("✅ シャットダウン完了")
    exit(0)

async def main():
    await asyncio.sleep(0.1)  # 少し待つ

# 通知を受け取ったときのコールバック
def Hreceive_ESP(device_num , identifier, data):
    # データを更新
    received_data = DataManager.unpack(identifier, data)
    print(f"📨 受信 from ESP-{device_num}: {received_data}")

    # PCにデータを送信
    asyncio.create_task(tcp.send(identifier, data))

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

    try:
        while True:
            await asyncio.sleep(1000)
    except Exception as e:
        print(f"⚠️ データ送信失敗: {e}")
    except asyncio.CancelledError:
        pass
    finally:
        print(f"❌ 切断")
        for esp in esps:
            await esp.disconnect()
            print(f"❌ 切断: {esp}")

async def Hreceive_PC():
    global esp_task
    while True:
        identifier, size, data = await tcp.receive()
        if identifier == 0xFF:
            if data[0] == 1:  # 接続要求
                esp_task.cancel() if esp_task else None  # 既存のタスクをキャンセル
                esp_task = asyncio.create_task(Hto_ESP())
                continue
            if data[0] == 0:  # 終了要求
                await shutdown()
                return

        received_data = DataManager.unpack(identifier, data)
        print(f"📨 受信 from PC: {received_data}")
        try:
            a = time.time()
            # ESP32にデータを送信
            await asyncio.gather(
                *[esp.send(identifier, data) for esp in esps],
                return_exceptions=True
            )
            b = time.time()
            print(f"📤 ESP32に送信完了 (処理時間: {b-a}")
        except ConnectionError as e:
            print(f"{e}")
            continue


async def Hsend_image_PC():
    while True:
        print("🔄 カメラ初期化中...")
        picam = Picam()
        try:
            # カメラ設定と起動
            picam.start()
            print("✅ カメラ準備完了")

            # フレーム送信ループ
            while True:
                data = await picam.get()  # フレームを取得
                await tcp.send(0x00, data)  # データをPCに送信
                await asyncio.sleep(2.5)  # 次のフレームまで待機
        
        except asyncio.TimeoutError:
            print("⚠ フレーム取得タイムアウト。再試行します。")
        except Exception as e: # エラー取得めんどい
            print(f"❌ : {e}")

        finally:
            picam.close()
            print("📷 カメラ停止")

        print("⏳ カメラ再接続待機中（5秒）...")
        await asyncio.sleep(5)

async def Hto_PC(addr):
    # PCとの接続待機
    print(f"🔗 接続: {addr}")

    # PCとの送受信を起動
    receive_task = asyncio.create_task(Hreceive_PC())
    send_image_task = asyncio.create_task(Hsend_image_PC())

    # PCとの切断時処理
    try:
        while True:
            await main()
            if receive_task.done():
                if receive_task.exception() is not None:
                    raise receive_task.exception()

    except (ConnectionResetError, BrokenPipeError) as e:
        print(f"⚠️ 接続エラー: {e}")
    except (asyncio.IncompleteReadError , EOFError):
        print("🔴 PCから接続が終了されました")
    finally:
        print("🧹 切断処理中...")
        receive_task.cancel()
        send_image_task.cancel()
        await asyncio.gather(receive_task, send_image_task, return_exceptions=True)
        await tcp.close()
        print(f"❌ 切断: {addr}")

async def server():

    print("🔵 TCPサーバー起動中...")
    server , addr = await tcp.start_server(Hto_PC)
    print(f"🚀 サーバー起動: {addr}")
    async with server:
        await server.serve_forever()

asyncio.run(server())
