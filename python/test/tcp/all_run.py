"""
TCPテスト実行スクリプト
python/test/tcp/内のすべてのTCP関連テストを実行する
"""
import sys
import os
# test/tcpフォルダから2つ上の親ディレクトリを参照するようにパスを調整
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
import asyncio
import subprocess


def run_test_file(test_file: str):
    """テストファイルを実行する"""
    print(f"\n{'='*60}")
    print(f"実行中: {test_file}")
    print('='*60)
    
    try:
        result = subprocess.run([sys.executable, test_file], 
                              capture_output=False, 
                              text=True, 
                              cwd=os.path.dirname(__file__))
        
        if result.returncode == 0:
            print(f"✓ {test_file} - 成功")
            return True
        else:
            print(f"✗ {test_file} - 失敗 (終了コード: {result.returncode})")
            return False
            
    except Exception as e:
        print(f"✗ {test_file} - エラー: {e}")
        return False


def main():
    """メイン関数"""
    print("TCP関連テスト実行開始")
    print(f"実行ディレクトリ: {os.path.dirname(__file__)}")
    
    # テストファイルのリスト
    test_files = [
        "debug.py",
        "integration.py"
    ]
    
    results = []
    
    # 各テストファイルを実行
    for test_file in test_files:
        test_path = os.path.join(os.path.dirname(__file__), test_file)
        if os.path.exists(test_path):
            success = run_test_file(test_path)
            results.append((test_file, success))
        else:
            print(f"警告: {test_file} が見つかりません")
            results.append((test_file, False))
    
    # 結果サマリー
    print(f"\n{'='*60}")
    print("テスト結果サマリー")
    print('='*60)
    
    success_count = 0
    for test_file, success in results:
        status = "✓ 成功" if success else "✗ 失敗"
        print(f"{test_file}: {status}")
        if success:
            success_count += 1
    
    print(f"\n成功: {success_count}/{len(results)}")
    
    if success_count == len(results):
        print("すべてのテストが成功しました! 🎉")
        return 0
    else:
        print("一部のテストが失敗しました。")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)