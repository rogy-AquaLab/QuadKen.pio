"""
TCP Debug機能のテストスクリプト（簡略化版）
基本的なデバッグ出力機能の動作確認
"""
import sys
import os
# test/tcpフォルダから2つ上の親ディレクトリを参照するようにパスを調整
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
import asyncio
import struct
from tools.tcp import DebugTcp, create_tcp

async def test_debug_output():
    """デバッグ出力機能のテスト"""
    print("=== TCP Debug 出力機能テスト ===\n")
    
    # DebugTcpインスタンスを作成
    debug_tcp = DebugTcp("localhost", 8080)
    await debug_tcp.connect()
    
    # テストデータの定義
    test_cases = [
        # ESP1サーボデータ（4個）
        (0x11, bytes([90, 45, 135, 0]), "ESP1サーボデータ"),
        
        # ESP2サーボデータ（12個）
        (0x12, bytes([90, 45, 135, 0, 180, 90, 45, 135, 0, 180, 90, 45]), "ESP2サーボデータ"),
        
        # BLDCモーターデータ
        (0x02, struct.pack('>H', 1500), "BLDCモーター"),
        
        # BNO055角度データ
        (0x03, bytes([180, 90, 45]), "BNO055角度データ"),
        
        # 設定コマンド
        (0xFF, bytes([0x01]), "設定コマンド"),
        
        # カメラ画像データ
        (0x00, bytes([0xFF, 0xD8]) + b"fake_jpeg_data" * 10, "カメラ画像データ"),
        
        # 不明なデータ識別子
        (0x99, bytes([0x01, 0x02, 0x03]), "不明なデータ識別子"),
        
        # 空データ
        (0x03, bytes([]), "空データ"),
        
        # 長いデータ（プレビュー機能テスト）
        (0x00, bytes(range(256)), "長いデータ（256バイト）"),
    ]
    
    # 各テストケースを実行
    for i, (identifier, data, description) in enumerate(test_cases, 1):
        print(f"--- テストケース {i}: {description} ---")
        try:
            await debug_tcp.send(identifier, data)
        except Exception as e:
            print(f"エラー: {e}")
        print()
    
    # データ識別子の確認
    print("=== サポートされているデータ識別子 ===")
    for identifier, name in debug_tcp.data_types.items():
        print(f"0x{identifier:02X}: {name}")
    print()
    
    await debug_tcp.close()
    print("テスト完了")


async def test_create_tcp_function():
    """create_tcp関数のテスト"""
    print("=== create_tcp関数テスト ===\n")
    
    # デフォルト（本番モード）でのインスタンス作成
    tcp_instance = create_tcp("localhost", 8080)
    print(f"デフォルトモード: {type(tcp_instance).__name__}")
    print(f"インスタンス: {tcp_instance}")
    print()


async def test_error_handling():
    """エラーハンドリングのテスト"""
    print("=== エラーハンドリングテスト ===\n")
    
    debug_tcp = DebugTcp("localhost", 8080)
    
    # 接続前の送信テスト（エラーが発生するはず）
    print("--- 接続前の送信テスト ---")
    try:
        await debug_tcp.send(0x11, bytes([90, 45, 135, 0]))
    except ConnectionError as e:
        print(f"期待されるエラー: {e}")
    print()
    
    # 正常な接続後の送信
    await debug_tcp.connect()
    print("--- 正常な送信テスト ---")
    await debug_tcp.send(0x11, bytes([90, 45, 135, 0]))
    print()
    
    await debug_tcp.close()
    print("エラーハンドリングテスト完了")


async def main():
    """メインテスト関数"""
    await test_debug_output()
    print("\n" + "="*50 + "\n")
    await test_create_tcp_function()
    print("\n" + "="*50 + "\n")
    await test_error_handling()


if __name__ == "__main__":
    asyncio.run(main())