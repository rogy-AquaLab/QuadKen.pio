
"""
設定ファイル読み込み機能のテストスクリプト
"""

import sys
import os
# testフォルダから親ディレクトリを参照するようにパスを調整
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from tools.tcp import _load_config, create_tcp

def test_config_loading():
    """設定ファイル読み込みのテスト"""
    print("=== 設定ファイル読み込みテスト ===")
    
    # 設定を読み込み
    config = _load_config()
    print(f"読み込まれた設定: {config}")
    
    # TCP インスタンス作成テスト
    print("\n=== TCP インスタンス作成テスト ===")
    tcp_instance = create_tcp("localhost", 8080)
    print(f"作成されたインスタンス: {tcp_instance}")
    print(f"インスタンスタイプ: {type(tcp_instance).__name__}")

if __name__ == "__main__":
    test_config_loading()