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

async def receive(received_data: bytes):
    """
    データを受信し、データタイプとサイズを取得する  
    :param received_data: 受信したデータ
    :return: データタイプ、サイズ、データ
    """
    data_type_byte = received_data[0:1]
    data_type: int = data_type_byte[0]
    size_bytes = received_data[1:5]
    size: int = struct.unpack('>I', size_bytes)[0]
    data: bytes = received_data[5:5 + size]
    if len(data) != size:
        raise ValueError(f"受信データのサイズが不正です: {len(data)} != {size}")
    
    return data_type, size, data

async def send(client , data_type: int, data: bytes):
    size = len(data)
    header = data_type.to_bytes() + struct.pack('>I', size)
    writer.write(header + data)
    await writer.drain()

