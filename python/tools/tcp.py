import asyncio
import struct

async def receive(reader: asyncio.StreamReader):
    data_type_byte = await reader.readexactly(1)
    data_type:int = data_type_byte[0]
    size_bytes = await reader.readexactly(4)
    size:int = struct.unpack('>I', size_bytes)[0]
    data:bytes = await reader.readexactly(size)
    return data_type, size, data

async def send(writer: asyncio.StreamWriter, data_type: int, data: bytes):
    size = len(data)
    header = struct.pack('B', data_type) + struct.pack('>I', size)
    writer.write(header + data)
    await writer.drain()

