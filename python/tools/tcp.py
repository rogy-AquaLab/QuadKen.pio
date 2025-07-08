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
            try:
                self.writer.close()
                await self.writer.wait_closed()
            except (ConnectionResetError, OSError) as e:
                pass
            finally:
                self.writer = None
                self.reader = None
    
    async def send(self, identifier: int, data: bytes):
        """
        データを送信する
        :param identifier: データの種類を示す1バイトの整数
        :param data: 送信するデータのバイト列
        """
        if not self.writer:
            raise ConnectionError("TCP接続が確立されていません。")
        
        size = len(data)
        header = struct.pack('B', identifier) + struct.pack('>I', size)
        self.writer.write(header + data)
        await self.writer.drain()

    async def receive(self):
        """
        データを受信する
        :return: (identifier, size, data)
        """
        if not self.reader:
            raise ConnectionError("TCP接続が確立されていません。")
        # 1バイトの識別子を読み取り、次に4バイトのサイズを読み取り、最後にデータを読み取る
        try:
            header_byte = await self.reader.readexactly(5)
            identifier = struct.unpack('B', header_byte[0:1])[0]
            size = struct.unpack('>I', header_byte[1:5])[0]
            data = await self.reader.readexactly(size)
        except asyncio.IncompleteReadError as e:
            if e.partial == b'':
                # 完全に接続が切断された場合
                raise EOFError("接続が切断されました。") from e
            else:
                # 一部だけ届いたなど他の理由ならそのまま再送出
                raise
        except asyncio.CancelledError:
            pass


        return identifier, size, data


