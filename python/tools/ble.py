import asyncio
import struct
from bleak import BleakClient

class Ble:
    """
    BLE通信を管理するクラス
    """
    
    def __init__(self, device_num , mac_address, char_uuid):
        self.num = device_num
        self.address = mac_address
        self.char_uuid = char_uuid
        self.client = None

    def __repr__(self):
        return f"ESP32-{self.num} ({self.address})"

    async def connect(self , receive_func: callable):
        """
        ESP32デバイスに接続し、通知を開始する
        :param devices: 接続するデバイスのリスト
        :param CHAR_UUID: 通知を受け取るためのキャラクタリスティックUUID
        :param Hreceive_ESP: データ受信時のコールバック関数
        :return: 接続したクライアントのリスト
        """
        if self.client and self.client.is_connected:
            print(f"ESP32-{self.num} ({self.address}) はすでに接続されています。")
            return
        try:
            client = BleakClient(self.address)
            client = await client.connect()
            if not client:
                raise ConnectionError(f"ESP32-{self.num} ({self.address}) への接続に失敗しました。")
            
            self.client = client
            await client.start_notify(self.char_uuid, self._receive(self , receive_func))
        except Exception as e:
            raise Exception(f"ESP32-{self.num} ({self.address}) - {e}") 
        
    async def disconnect(self):
        """
        ESP32デバイスから切断する
        """
        if self.client and self.client.is_connected:
            await self.client.disconnect()
            self.client = None

    def _receive(self , receive_func: callable):        
        def handler(sender, received_data):
            data_type_byte = received_data[0:1]
            data_type: int = data_type_byte[0]
            size_bytes = received_data[1:5]
            size: int = struct.unpack('>I', size_bytes)[0]
            data: bytes = received_data[5:5 + size]
            if len(data) != size:
                raise ValueError(f"受信データのサイズが不正です: {len(data)} != {size}")
            
            receive_func(self.num , data_type, size, data)

        return handler

    async def send(self , data_type: int, data: bytes):
        size = len(data)
        header = data_type.to_bytes() + struct.pack('>I', size)
        await self.client.write_gatt_char(self.char_uuid, header + data)

