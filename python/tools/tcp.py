import asyncio
import struct

class Tcp:
    """
    TCP通信を管理するクラス
    """

    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.reader = None
        self.writer = None

    def __repr__(self):
        return f"TCP ({self.host}:{self.port})"
    
    async def connect(self):
        """
        TCPサーバーに接続する
        :return: 接続したreaderとwriter
        """
        self.reader, self.writer = await asyncio.open_connection(self.host, self.port)
        return self.host, self.port
    
    async def start_server(self, handle_client: callable):
        """
        TCPサーバーを開始し、クライアント接続を待機する
        :param handle_client: クライアント接続時に呼び出されるコールバック関数
        """
        server = await asyncio.start_server(self.callback(handle_client), self.host, self.port)
        address = server.sockets[0].getsockname()
        return server , address
    
    def callback(self, handle_client: callable):
        """
        クライアント接続時に呼び出されるコールバック関数を返す
        :param handle_client: クライアント接続時に呼び出されるコールバック関数
        """
        async def client_handler(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
            self.reader = reader
            self.writer = writer
            addr = writer.get_extra_info('peername')
            await handle_client(addr)
        return client_handler
    
    async def close(self):
        """
        TCP接続を閉じる
        """
        if self.writer:
            self.writer.close()
            await self.writer.wait_closed()
            self.writer = None
        if self.reader:
            self.reader = None
    
    async def send(self, data_type: int, data: bytes):
        """
        データを送信する
        :param data_type: データの種類を示す1バイトの整数
        :param data: 送信するデータのバイト列
        """
        if not self.writer:
            raise ConnectionError("TCP接続が確立されていません。")
        
        size = len(data)
        header = struct.pack('B', data_type) + struct.pack('>I', size)
        self.writer.write(header + data)
        await self.writer.drain()

    async def receive(self):
        """
        データを受信する
        :return: (data_type, size, data)
        """
        if not self.reader:
            raise ConnectionError("TCP接続が確立されていません。")
        
        data_type_byte = await self.reader.readexactly(1)
        data_type: int = data_type_byte[0]
        size_bytes = await self.reader.readexactly(4)
        size: int = struct.unpack('>I', size_bytes)[0]
        data: bytes = await self.reader.readexactly(size)
        return data_type, size, data


