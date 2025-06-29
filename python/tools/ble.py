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
            connection = await client.connect()
            if not connection:
                raise ConnectionError(f"ESP32-{self.num} ({self.address}) への接続に失敗しました。")
            
            self.client = client
            await client.start_notify(self.char_uuid, self._receive(receive_func))
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
            identifier_byte = received_data[0:1]
            identifier: int = identifier_byte[0]
            data: bytes = received_data[1:]  # sizeを省略して受信データ全体を取得
            receive_func(self.num , identifier, data)

        return handler

    async def send(self , identifier: int, data: bytes):
        # size = len(data)
        header = struct.pack('B', identifier) # + struct.pack('>I', size)
        if not self.client or not self.client.is_connected:
            raise ConnectionError(f"ESP32-{self.num} ({self.address}) は接続されていません。")
        await self.client.write_gatt_char(self.char_uuid, header + data)

