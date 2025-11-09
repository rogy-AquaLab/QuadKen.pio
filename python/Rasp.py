import asyncio
from tools.tcp import Tcp
from tools.data_manager import DataManager , DataType
from tools.ble import Ble
from tools.bno import BNOSensor
from tools.camera import Picam

main_interval = 0.1  # メインループの実行間隔（秒）
camera_interval = 0.1  # カメラのフレーム取得間隔（秒）

# Hto_ESPが複数同時に実行されないようにするため、やむなく実装
esp_task = None

# ESP32デバイスのMACアドレス一覧（必要に応じて追加）
devices = [
    {"num": 1, "address": "78:42:1C:2E:0E:5E" , "char_uuid": "abcd1234-5678-90ab-cdef-123456789001"},
    {"num": 2, "address": "78:42:1C:2E:1B:76" , "char_uuid": "abcd1234-5678-90ab-cdef-123456789002"},
    {"num": 3, "address": "B0:81:84:04:A4:D6" , "char_uuid": "abcd1234-5678-90ab-cdef-123456789003"},  # LiPo用esp32c3

    # {"num": 2, "address": "08:D1:F9:36:FF:3E" , "char_uuid": "abcd1234-5678-90ab-cdef-123456789002"}, #正方形
    # {"num": 2, "address": "CC:7B:5C:E8:E3:32" , "char_uuid": "abcd1234-5678-90ab-cdef-123456789002"}, #角なし
]
esps = [Ble(device['num'], device['address'], device['char_uuid']) for device in devices]

HOST = '0.0.0.0'  # 例: '192.168.0.10'
PORT = 5000

tcp = Tcp(HOST, PORT)

bno = BNOSensor()  # BNO055センサのインスタンス作成


# データ管理インスタンスの作成
esp1_servo_data = DataManager(0x11, 4, DataType.UINT8)   # ESP1用サーボ（4個）- 識別子0x11
esp2_servo_data = DataManager(0x12, 12, DataType.UINT8)  # ESP2用サーボ（12個）- 識別子0x12
bldc_data = DataManager(0x02, 2, DataType.INT8)
bno_data = DataManager(0x03, 3, DataType.INT8)
config = DataManager(0xFF, 1, DataType.UINT8)
lipo_data = DataManager(0x04, 3, DataType.UINT8)  # ESP3が送信する3セル電圧用

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

async def ensure_bno_connection():
    """BNO055センサーの接続を確保する（再接続機能付き）"""
    if not bno.is_connected():
        try:
            print("🔄 BNO055センサーに接続中...")
            bno.connect()
            print("✅ BNO055センサー接続成功")
            return True
        except Exception as e:
            print(f"⚠️ BNO055センサー接続失敗: {e}")
            return False
    return True

async def main():
    # BNO055センサの接続確保（再接続機能付き）
    if not await ensure_bno_connection():
        return

    # BNO055センサからの角度情報取得
    try:
        bno_euler = bno.euler()  # BNO055センサからの角度情報取得
        phi, theta, twist = bno_euler
        print(f"θ: {theta}° φ: {phi}° twist: {twist}°")

        # 角度データの範囲チェックと変換
        if theta is not None and phi is not None and twist is not None:
            # ヘディングを-180〜180に変換
#            if theta > 180:
 #               theta = theta - 360

            # データを-90〜90の範囲に制限してint8に変換
            theta_scaled = theta
            phi_scaled = phi//3
            twist_scaled = twist//2


            bno_data.update([theta_scaled, phi_scaled, twist_scaled])
            # PCにデータを送信
            await tcp.send(bno_data.identifier(), bno_data.pack())
            
    except Exception as e:
        print(f"❌ BNO055センサーエラー: {e}")
        # 接続が切れた可能性があるため、次回のループで再接続を試行
        if "接続が切れています" in str(e) or "接続されていません" in str(e):
            print("🔄 次回ループで再接続を試行します")


# 通知を受け取ったときのコールバック
def Hreceive_ESP(device_num, identifier, data):
    try:
        received_data = DataManager.unpack(identifier, data)
        print(f"📨 受信 from ESP-{device_num} (ID={identifier}): {received_data}")

        # LiPo電圧データ（ESP3用）
        if device_num == 3 and identifier == lipo_data.identifier():
            voltage_values = [v/10 for v in received_data]
            print(f"🔋 LiPo Voltages: {voltage_values}")
            # 必要ならTCP経由でPCアプリにも送る
            asyncio.create_task(tcp.send(identifier, data))

        # 既存ESP用処理は従来通り
        else:
            asyncio.create_task(tcp.send(identifier, data))

    except Exception as e:
        print(f"⚠️ BLE受信エラー from ESP-{device_num}: {e}")


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
                # ESP接続後にセットアップコマンドを送信
                await asyncio.sleep(2)  # ESP接続の安定化を待つ
                try:
                    config.update([1])  # セットアップコマンド
                    setup_data = config.pack()
                    # 両方のESPにセットアップコマンドを送信
                    await asyncio.gather(
                        esps[0].send(config.identifier(), setup_data),  # ESP1
                        esps[1].send(config.identifier(), setup_data),  # ESP2
                    )
                    print("✅ ESP両方にセットアップコマンドを送信しました")
                except Exception as e:
                    print(f"⚠️ セットアップコマンド送信エラー: {e}")
                continue
            if data[0] == 2:  # L1ボタンでのセットアップ要求
                try:
                    config.update([1])  # セットアップコマンド
                    setup_data = config.pack()
                    # 両方のESPにセットアップコマンドを送信
                    await asyncio.gather(
                        esps[0].send(config.identifier(), setup_data),  # ESP1
                        esps[1].send(config.identifier(), setup_data),  # ESP2
                    )
                    print("✅ L1ボタンによりESP両方にセットアップコマンドを送信しました")
                except Exception as e:
                    print(f"⚠️ L1セットアップコマンド送信エラー: {e}")
                continue
            if data[0] == 3:  # R1ボタンでのconfig 3要求
                try:
                    config.update([3])  # config 3コマンド
                    config3_data = config.pack()
                    # 両方のESPにconfig 3コマンドを送信
                    await asyncio.gather(
                        esps[0].send(config.identifier(), config3_data),  # ESP1
                        esps[1].send(config.identifier(), config3_data),  # ESP2
                    )
                    print("✅ R1ボタンによりESP両方にconfig 3コマンドを送信しました")
                except Exception as e:
                    print(f"⚠️ config 3コマンド送信エラー: {e}")
                continue
            if data[0] == 0:  # 終了要求
                await shutdown()
                return

        received_data = DataManager.unpack(identifier, data)
        print(f"📨 受信 from PC: {received_data}")
        
        try:
            if identifier == esp1_servo_data.identifier():  # ESP1サーボデータの場合（4個）- 識別子0x11
                # ESP1にサーボデータを送信（識別子を0x01に変換）
                await esps[0].send(0x01, data)  # ESP1に4個のサーボデータを送信
                
            elif identifier == esp2_servo_data.identifier():  # ESP2サーボデータの場合（12個）- 識別子0x12
                # ESP2にサーボデータを送信（識別子を0x01に変換）
                await esps[1].send(0x01, data)  # ESP2に12個のサーボデータを送信

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
                await asyncio.sleep(camera_interval)  # 次のフレームまで待機

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
            await asyncio.gather(
                main(),
                asyncio.sleep(main_interval)  # メインループの実行間隔
            )
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
