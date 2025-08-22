import asyncio
import struct
import yaml
import os
from typing import Dict, Any, Union
from datetime import datetime


class Tcp:
    """TCP通信を管理するクラス"""

    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.reader = None
        self.writer = None

    def __repr__(self):
        return f"TCP ({self.host}:{self.port})"
    
    async def connect(self):
        """TCPサーバーに接続する"""
        self.reader, self.writer = await asyncio.open_connection(self.host, self.port)
        return self.host, self.port
    
    async def start_server(self, handle_client: callable):
        """TCPサーバーを開始し、クライアント接続を待機する"""
        server = await asyncio.start_server(self.callback(handle_client), self.host, self.port)
        address = server.sockets[0].getsockname()
        return server, address
    
    def callback(self, handle_client: callable):
        """クライアント接続時に呼び出されるコールバック関数を返す"""
        async def client_handler(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
            self.reader = reader
            self.writer = writer
            addr = writer.get_extra_info('peername')
            await handle_client(addr)
        return client_handler
    
    async def close(self):
        """TCP接続を閉じる"""
        if self.writer:
            try:
                self.writer.close()
                await self.writer.wait_closed()
            except (ConnectionResetError, OSError):
                pass
            finally:
                self.writer = None
                self.reader = None
    
    async def send(self, identifier: int, data: bytes):
        """データを送信する"""
        if not self.writer:
            raise ConnectionError("TCP接続が確立されていません。")
        
        size = len(data)
        header = struct.pack('B', identifier) + struct.pack('>I', size)
        self.writer.write(header + data)
        await self.writer.drain()

    async def receive(self):
        """データを受信する"""
        if not self.reader:
            raise ConnectionError("TCP接続が確立されていません。")
        
        try:
            header_byte = await self.reader.readexactly(5)
            identifier = struct.unpack('B', header_byte[0:1])[0]
            size = struct.unpack('>I', header_byte[1:5])[0]
            data = await self.reader.readexactly(size)
        except asyncio.IncompleteReadError as e:
            if e.partial == b'':
                raise EOFError("接続が切断されました。") from e
            else:
                raise
        except asyncio.CancelledError:
            pass

        return identifier, size, data


class DebugTcp:
    """TCP通信のデバッグ版クラス（簡略化版）"""

    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.reader = None
        self.writer = None
        self.connected = False
        
        # 設定を読み込み
        self.config = self._load_debug_config()
        
        # データ識別子の基本マッピング
        self.data_types = {
            0x11: "ESP1サーボ", 0x12: "ESP2サーボ", 0x02: "BLDCモーター",
            0x03: "BNO055角度", 0xFF: "設定コマンド", 0x00: "カメラ画像"
        }

    def __repr__(self):
        return f"DebugTCP ({self.host}:{self.port})"
    
    def _load_debug_config(self) -> Dict[str, bool]:
        """デバッグ設定を読み込む"""
        try:
            config_path = os.path.join(os.path.dirname(__file__), '..', 'config.yaml')
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f)
                    return config.get('tcp', {}).get('debug_options', {
                        'show_timestamp': True, 'show_colors': True
                    })
        except Exception as e:
            print(f"\033[91m[設定エラー] {e}\033[0m")
        
        return {'show_timestamp': True, 'show_colors': True}
    
    async def connect(self):
        """疑似TCP接続"""
        self.connected = True
        self._print_debug("TCP接続を疑似実行", f"{self.host}:{self.port}")
        return self.host, self.port
    
    async def start_server(self, handle_client: callable):
        """疑似TCPサーバー開始"""
        self._print_debug("TCPサーバーを疑似開始", f"{self.host}:{self.port}")
        
        class MockServer:
            def __init__(self, host, port):
                self.sockets = [type('MockSocket', (), {'getsockname': lambda: (host, port)})()]
        
        return MockServer(self.host, self.port), (self.host, self.port)
    
    def callback(self, handle_client: callable):
        """疑似クライアント接続コールバック"""
        async def client_handler(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
            self._print_debug("疑似クライアント接続", "")
            await handle_client(('127.0.0.1', 0))
        return client_handler
    
    async def close(self):
        """疑似TCP接続切断"""
        if self.connected:
            self.connected = False
            self._print_debug("TCP接続を疑似切断", "")
        self.writer = None
        self.reader = None
    
    async def send(self, identifier: int, data: bytes):
        """データ送信のデバッグ出力"""
        if not self.connected:
            raise ConnectionError("TCP接続が確立されていません。")
        
        try:
            data_type = self.data_types.get(identifier, f"不明(0x{identifier:02X})")
            info = f"識別子: 0x{identifier:02X} ({data_type}), サイズ: {len(data)}バイト"
            
            # 簡単なデータプレビュー
            if len(data) > 0:
                preview = ' '.join(f'{b:02X}' for b in data[:min(12, len(data))])
                if len(data) > 12:
                    preview += f" ... (残り{len(data) - 12}バイト)"
                info += f", データ: {preview}"
            
            self._print_debug("TCP送信", info)
            
        except Exception as e:
            self._print_error(f"デバッグ出力エラー: {e}")

    async def receive(self):
        """疑似データ受信"""
        if not self.connected:
            raise ConnectionError("TCP接続が確立されていません。")
        
        self._print_debug("データ受信待機中", "")
        await asyncio.sleep(5)
        return 0x03, 3, b'\x00\x00\xbf'  # 疑似データを返す
    
    def _print_debug(self, action: str, info: str):
        """デバッグメッセージを出力"""
        try:
            timestamp = ""
            if self.config.get('show_timestamp', True):
                timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3] + " "
            
            color = "\033[96m" if self.config.get('show_colors', True) else ""
            reset = "\033[0m" if self.config.get('show_colors', True) else ""
            
            message = f"{color}[DEBUG] {timestamp}{action}"
            if info:
                message += f": {info}"
            message += reset
            
            print(message)
        except Exception:
            print(f"[DEBUG] {action}: {info}")
    
    def _print_error(self, message: str):
        """エラーメッセージを出力"""
        try:
            color = "\033[91m" if self.config.get('show_colors', True) else ""
            reset = "\033[0m" if self.config.get('show_colors', True) else ""
            print(f"{color}[エラー] {message}{reset}")
        except Exception:
            print(f"[エラー] {message}")


def create_tcp(host: str, port: int) -> Union[Tcp, DebugTcp]:
    """設定に基づいてTcpインスタンスを作成する"""
    try:
        config_path = os.path.join(os.path.dirname(__file__), '..', 'config.yaml')
        debug_mode = False  # デフォルト
        
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                debug_mode_value = config.get('tcp', {}).get('debug_mode', 'off')
                # 'on', True, 1 などをTrueとして扱う
                debug_mode = debug_mode_value in ['on', True, 1, 'true', 'True']
        
        if debug_mode:
            return DebugTcp(host, port)
        else:
            return Tcp(host, port)
            
    except Exception as e:
        print(f"\033[91m[設定エラー] {e} - 本番モードで動作します\033[0m")
        return Tcp(host, port)