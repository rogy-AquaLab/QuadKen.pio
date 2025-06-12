import asyncio
import struct
from bleak import BleakClient

async def connect(device , CHAR_UUID):
    client = BleakClient(device["address"])
    try:
        await client.connect()

        return client
    except Exception as e:
        raise Exception(f"{device['name']} ({device['address']}) - {e}")
    
