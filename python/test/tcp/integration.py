"""
TCP統合テスト（簡略化版）
本番モードとデバッグモードの切り替えテスト
"""
import sys
import os
# test/tcpフォルダから2つ上の親ディレクトリを参照するようにパスを調整
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
import asyncio
import tempfile
import yaml
from tools.tcp import create_tcp, Tcp, DebugTcp


async def test_production_mode():
    """本番モードのテスト"""
    print("=== 本番モードテスト ===")
    
    # 一時的な設定ファイルを作成（本番モード）
    config = {
        'tcp': {
            'mode': 'production',
            'debug_options': {
                'show_timestamp': True,
                'show_colors': True
            }
        }
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        yaml.dump(config, f, default_flow_style=False)
        config_path = f.name
    
    try:
        # 設定ファイルのパスを一時的に変更
        # test/tcp/から見て../../config.yamlが正しいパス
        original_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'config.yaml')
        temp_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'config_temp.yaml')
        
        # 元の設定ファイルをバックアップ
        if os.path.exists(original_path):
            os.rename(original_path, temp_path)
        
        # 一時設定ファイルをコピー
        import shutil
        shutil.copy(config_path, original_path)
        
        # TCP インスタンスを作成
        tcp_instance = create_tcp("localhost", 8080)
        print(f"作成されたインスタンス: {type(tcp_instance).__name__}")
        assert isinstance(tcp_instance, Tcp), "本番モードではTcpインスタンスが作成されるべき"
        print("✓ 本番モードでTcpインスタンスが正常に作成されました")
        
    finally:
        # 設定ファイルを元に戻す
        if os.path.exists(original_path):
            os.remove(original_path)
        if os.path.exists(temp_path):
            os.rename(temp_path, original_path)
        os.unlink(config_path)
    
    print()


async def test_debug_mode():
    """デバッグモードのテスト"""
    print("=== デバッグモードテスト ===")
    
    # 一時的な設定ファイルを作成（デバッグモード）
    config = {
        'tcp': {
            'mode': 'debug',
            'debug_options': {
                'show_timestamp': True,
                'show_colors': True
            }
        }
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        yaml.dump(config, f, default_flow_style=False)
        config_path = f.name
    
    try:
        # 設定ファイルのパスを一時的に変更
        original_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'config.yaml')
        temp_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'config_temp.yaml')
        
        # 元の設定ファイルをバックアップ
        if os.path.exists(original_path):
            os.rename(original_path, temp_path)
        
        # 一時設定ファイルをコピー
        import shutil
        shutil.copy(config_path, original_path)
        
        # TCP インスタンスを作成
        tcp_instance = create_tcp("localhost", 8080)
        print(f"作成されたインスタンス: {type(tcp_instance).__name__}")
        assert isinstance(tcp_instance, DebugTcp), "デバッグモードではDebugTcpインスタンスが作成されるべき"
        print("✓ デバッグモードでDebugTcpインスタンスが正常に作成されました")
        
        # デバッグ機能のテスト
        await tcp_instance.connect()
        await tcp_instance.send(0x11, bytes([90, 45, 135, 0]))
        await tcp_instance.close()
        print("✓ デバッグ出力が正常に動作しました")
        
    finally:
        # 設定ファイルを元に戻す
        if os.path.exists(original_path):
            os.remove(original_path)
        if os.path.exists(temp_path):
            os.rename(temp_path, original_path)
        os.unlink(config_path)
    
    print()


async def test_config_error_handling():
    """設定ファイルエラーハンドリングのテスト"""
    print("=== 設定エラーハンドリングテスト ===")
    
    # 設定ファイルが存在しない場合のテスト
    original_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'config.yaml')
    temp_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'config_temp.yaml')
    
    # 設定ファイルを一時的に移動
    if os.path.exists(original_path):
        os.rename(original_path, temp_path)
    
    try:
        tcp_instance = create_tcp("localhost", 8080)
        print(f"設定ファイル無し: {type(tcp_instance).__name__}")
        assert isinstance(tcp_instance, Tcp), "設定ファイルが無い場合は本番モードになるべき"
        print("✓ 設定ファイルが無い場合のフォールバックが正常に動作しました")
        
    finally:
        # 設定ファイルを元に戻す
        if os.path.exists(temp_path):
            os.rename(temp_path, original_path)
    
    print()


async def main():
    """メインテスト関数"""
    print("TCP統合テスト開始\n")
    
    await test_production_mode()
    await test_debug_mode()
    await test_config_error_handling()
    
    print("すべてのテストが完了しました ✓")


if __name__ == "__main__":
    asyncio.run(main())