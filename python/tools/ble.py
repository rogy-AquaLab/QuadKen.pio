import asyncio
import struct
from bleak import BleakClient

async def connect(devices , CHAR_UUID , Hreceive_ESP):
    """
    ESP32デバイスに接続し、通知を開始する
    :param devices: 接続するデバイスのリスト
    :param CHAR_UUID: 通知を受け取るためのキャラクタリスティックUUID
    :param Hreceive_ESP: データ受信時のコールバック関数
    :return: 接続したクライアントのリスト
    """
    clients = []
    for device in devices:
        try:
            client = BleakClient(device["address"])
            client = await connect()
            if client:
                clients.append(client)
                await client.start_notify(CHAR_UUID, Hreceive_ESP(device["name"]))
        except Exception as e:
            raise Exception(f"{device['name']} ({device['address']}) - {e}")

    return clients    

async def receive(data: bytes):
    """
    データを受信し、データタイプとサイズを取得する  
    :param data: 受信したデータ
    :return: データタイプ、サイズ、データ
    """

    
    return data_type, size, data

async def send(client , data_type: int, data: bytes):
    size = len(data)
    header = data_type.to_bytes() + struct.pack('>I', size)
    writer.write(header + data)
    await writer.drain()

