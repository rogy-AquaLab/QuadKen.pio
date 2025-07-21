import asyncio
from tools.tcp import Tcp
from tools.data_manager import DataManager , DataType
from tools.ble import Ble
from tools.bno import Bno
from tools.camera import Picam

# Hto_ESPが複数同時に実行されないようにするため、やむなく実装
esp_task = None

# ESP32デバイスのMACアドレス一覧（必要に応じて追加）
devices = [
    {"num": 1, "address": "78:42:1C:2E:0E:5E" , "char_uuid": "abcd1234-5678-90ab-cdef-123456789001"}, #正方形
    {"num": 2, "address": "78:42:1C:2E:1B:76" , "char_uuid": "abcd1234-5678-90ab-cdef-123456789002"},
    # {"num": 2, "address": "08:D1:F9:36:FF:3E" , "char_uuid": "abcd1234-5678-90ab-cdef-123456789002"}, #正方形
    # {"num": 2, "address": "CC:7B:5C:E8:E3:32" , "char_uuid": "abcd1234-5678-90ab-cdef-123456789002"}, #角なし
]
esps = [Ble(device['num'], device['address'], device['char_uuid']) for device in devices]

HOST = '0.0.0.0'  # 例: '192.168.0.10'
PORT = 5000

tcp = Tcp(HOST, PORT)

bno = Bno(True, 0x28)  # BNO055センサのインスタンス作成（クリスタルオシレータ使用、デフォルトアドレス0x28）

# データ管理インスタンスの作成
servo_data = DataManager(0x01, 16, DataType.UINT8)
bldc_data = DataManager(0x02, 2, DataType.INT8)
bno_data = DataManager(0x03, 3, DataType.INT8)
config = DataManager(0xFF, 1, DataType.UINT8)

async def shutdown():
    print("🧹 シャットダウン処理中...")
    
    # ESP32デバイスとの切断
    for esp in esps:
        await esp.disconnect()
        print(f"❌ 切断: {esp}")
    
    # BNO055センサとの切断
    if bno.is_connected():
        bno.disconnect()
    
    # TCP接続の切断
    await tcp.close()
    print("✅ シャットダウン完了")
    exit(0)

async def main():
    # BNO055センサの接続確保（失敗しても続行）
    if not bno.ensure_connected():
        await asyncio.sleep(1)  # 少し待つ
        return
        # print("⚠️ BNO055センサ接続エラー: センサーなしで続行します")
    
    # BNO055センサからの角度情報取得
    if bno.is_connected():
        try:
            bno_euler = bno.euler()  # BNO055センサからの角度情報取得
            if bno_euler is not None:
                heading, roll, pitch = bno_euler
                print(f"🧭 角度情報: ヘディング={heading}° ロール={roll}° ピッチ={pitch}°")
                if 0 <= heading <= 360 and -180 <= roll <= 180 and -180 <= pitch <= 180:
                    heading = heading if heading <= 180 else heading - 360  # ヘディングを-180〜180に変換
                    bno_data.update([int(heading/2), int(roll/2), int(pitch/2)])
                    # PCにデータを送信
                    await tcp.send(bno_data.identifier(), bno_data.pack())
            else:
                print("⚠️ BNO055センサからの角度情報が取得できません")
                
        except RuntimeError as e:
            print(f"❌ BNO055センサ通信エラー: {e}")
        except ValueError as e:
            print(f"⚠️ BNO055センサデータエラー: {e}")
        except Exception as e:
            print(f"⚠️ BNO055センサ予期しないエラー: {e}")
        
    await asyncio.sleep(1)  # 少し待つ

# 通知を受け取ったときのコールバック
def Hreceive_ESP(device_num , identifier, data):
    print("おかしい")
    # # データを更新
    # received_data = DataManager.unpack(identifier, data)
    # print(f"📨 受信 from ESP-{device_num}: {received_data}")

    # # PCにデータを送信
    # asyncio.create_task(tcp.send(identifier, data))

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
            if identifier == servo_data.identifier():  # サーボデータの場合
                # 16個のサーボデータを分割
                # 最初の12個をESP2（ESP_power）へ送信
                servo_data_esp2 = data[:12]  # 0-11番目のサーボ
                # 残りの4個をESP1（ESP_up）へ送信  
                servo_data_esp1 = data[12:16]  # 12-15番目のサーボ

                # ESPにサーボデータを送信
                await asyncio.gather(
                    esps[1].send(servo_data.identifier(), servo_data_esp2),  # ESP2 (ESP_power) に12個のサーボデータを送信
                    esps[0].send(servo_data.identifier(), servo_data_esp1),  # ESP1 (ESP_up) に4個のサーボデータを送信
                    asyncio.sleep(0.01)  # 少し待機してから次の処理へ
                )

            elif identifier == bldc_data.identifier():  # BLDCデータの場合
                # ESP2 (index 1) にBLDCデータを送信
                if len(esps) > 1:
                    await esps[1].send(identifier, data)
            
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

        print("⏳ カメラ再接続待機中（500秒）...")
        await asyncio.sleep(500)

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
