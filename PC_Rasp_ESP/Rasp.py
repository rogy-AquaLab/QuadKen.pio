import struct
import asyncio
from bleak import BleakClient

# ESP32デバイスのMACアドレス一覧（必要に応じて追加）
devices = [
    {"name": "ESP32-1", "address": "08:D1:F9:36:FF:3E"},
    # {"name": "ESP32-2", "address": "AA:BB:CC:44:55:66"},
]

CHAR_UUID = "abcd1234-5678-90ab-cdef-1234567890ab"

HOST = '0.0.0.0'  # 例: '192.168.0.10'
PORT = 5000

class DataManager:
    def __init__(self, length:int, pack_mode:str):
        self._data = [0] * length  # uint8_t 8個のデータを格納するリスト
        self._length = length
        self._pack_mode = pack_mode
        if len(pack_mode) != length:
            raise ValueError("Invalid pack mode. Length of pack mode must match the numbe")

    def update_data(self, new_data):
        self._data = new_data[:]

    def update_byte(self, byte_data):
        if len(byte_data) != self._length:
            raise ValueError("Invalid byte data length. Length of byte data must match th")
        self._data = list(struct.unpack(self._pack_mode, byte_data))

    def get_data(self):
        return self._data

    def pack_data(self):
        # uint8_t 8個のデータを送る（例: 0〜7）
        return struct.pack(self._pack_mode, *self._data)
        
    


servo_data = DataManager(8, 'BBBBBBBB')
bno_data = DataManager(3, 'bbb')


async def write_ESP(client, data):
    try:
        # データを書き込む
        await client.write_gatt_char(CHAR_UUID, data)
    except Exception as e:
        print(f"⚠️ Failed to write data to {client.address}: {e}")

async def connect_and_listen(device):
    client = BleakClient(device["address"])
    try:
        await client.connect()
        print(f"✅ Connected to {device['name']}")
        await client.start_notify(CHAR_UUID, notification_handler(device["name"]))

        return client
    except Exception as e:
        print(f"⚠️ Failed to connect to {device['name']}: {e}")
        return None

async def send_all_handler(writer: asyncio.StreamWriter , clients):
    while True:
        try:
            writer.write(bno_data.pack_data())
            await writer.drain()
            print(f"📤 送信 to PC: {bno_data.get_data()}")

            for i , client in enumerate(clients):
                await write_ESP(client, servo_data.pack_data())
                print(f"📤 送信 to ESP32-{i}: {servo_data.get_data()}")
            await asyncio.sleep(2.5)  # 少し待つ
        except asyncio.CancelledError:
            break

async def receive_PC_handler(reader: asyncio.StreamReader):
    data = await reader.read(1024)
    while True:
        try:
            data = await reader.read(1024)
            if not data:
                print("🔴 接続が切れました")
                break
            servo_data.update_byte(data)
            print(f"📨 受信 from PC: {servo_data.get_data()}")
        except asyncio.CancelledError:
            print("CancelledError")
            break

# 通知を受け取ったときのコールバック
def notification_handler(device_name):
    def handler(sender, data):
        # データを更新
        bno_data.update_byte(data)
        # データを表示
        print(f"📨 受信 from {device_name}: {bno_data.get_data()}")
    return handler

async def handle_client(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    addr = writer.get_extra_info('peername')
    print(f"🔗 接続: {addr}")

    clients = []
    for dev in devices:
        client = await connect_and_listen(dev)
        if client:
            clients.append(client)
        await asyncio.sleep(1)  # 念のため少し待つと安定

    # PCとの送信と受信を起動
    send_task = asyncio.create_task(send_all_handler(writer,clients))
    receive_PC_task = asyncio.create_task(receive_PC_handler(reader))

    try:
        while True:
            await asyncio.sleep(1)  # メインループで何かをする場合はここに書く
    except asyncio.CancelledError:
        pass
    finally:
        send_task.cancel()
        receive_PC_task.cancel()
        print(f"❌ 切断: {addr}")
        writer.close()
        await writer.wait_closed()

async def main():
    server = await asyncio.start_server(handle_client, HOST, PORT)
    addr = server.sockets[0].getsockname()
    print(f"🚀 サーバー起動中: {addr}")

    async with server:
        await server.serve_forever()

asyncio.run(main())
