# server.py
import struct
import asyncio

HOST = 'takapi.local'
PORT = 5000

class DataManager:
    def __init__(self, length:int, pack_mode:str):
        self._data = [0] * length  # uint8_t 8個のデータを格納するリスト
        self._length = length
        self._pack_mode = pack_mode
        if len(pack_mode) != length:
            raise ValueError("Invalid pack mode. Length of pack mode must match the number of data items.")

    def update_data(self, new_data):
        self._data = new_data[:]

    def update_byte(self, byte_data):
        if len(byte_data) != self._length:
            raise ValueError("Invalid byte data length. Length of byte data must match the number of data items.")
        self._data = list(struct.unpack(self._pack_mode, byte_data))

    def get_data(self):
        return self._data
    
    def pack_data(self):
        # uint8_t 8個のデータを送る（例: 0〜7）
        return struct.pack(self._pack_mode, *self._data)

async def async_input(prompt: str = "") -> str:
    return await asyncio.to_thread(input, prompt)

servo_data = DataManager(8, 'BBBBBBBB')
bno_data = DataManager(3, 'bbb')

async def send_handler(writer: asyncio.StreamWriter):
    while True:
        try:
            writer.write(servo_data.pack_data())
            await writer.drain()
            print(f"📤 送信 to Rasp: {servo_data.get_data()}")
            await asyncio.sleep(1)  # 少し待つ
        except asyncio.CancelledError:
            break

async def receive_handler(reader: asyncio.StreamReader):
    while True:
        try:
            data = await reader.read(1024)
            if not data:
                print("🔴 接続が切れました")
                break
            bno_data.update_byte(data)
            print(f"📨 受信: {bno_data.get_data()}")
        except asyncio.CancelledError:
            break


async def tcp_client():
    reader, writer = await asyncio.open_connection(HOST, PORT)
    
    print("🔵 Connected to Raspberry Pi")

    # 送信と受信を起動
    send_task = asyncio.create_task(send_handler(writer))
    receive_task = asyncio.create_task(receive_handler(reader))


    try:
        while True:
            data8 = [0] * 8
            for i in range(8):
                try:
                    num = int(await async_input(f"{i}番目の整数を入力してください: "))
                    if num < 0 or num > 255:
                        raise ValueError("0〜255の範囲で入力してください。")
                except ValueError:
                    print("整数ではありません。0にします。")
                    num = 0
                data8[i] = num
            servo_data.update_data(data8)
            print("Updated data8:", data8)
            await asyncio.sleep(1)  # 少し待つ

    except KeyboardInterrupt:
        print("⛔ 切断します")
    finally:
        send_task.cancel()
        receive_task.cancel()
        writer.close()
        await writer.wait_closed()

asyncio.run(tcp_client())
