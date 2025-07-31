import sys
import os
import time

# プロジェクトルートをパスに追加
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from tools.bno import BNOSensor


def test_bno_connection():
    """BNO055センサーの接続テスト"""
    print("=== BNO055センサー接続テスト ===")
    
    sensor = BNOSensor()
    
    try:
        print("センサーに接続中...")
        sensor.connect()
        print("✓ 接続成功")
        
        # 接続状態確認
        if sensor.is_connected():
            print("✓ 接続状態確認OK")
        else:
            print("✗ 接続状態確認NG")
            return False
            
    except Exception as e:
        print(f"✗ 接続失敗: {e}")
        return False
    
    return True


def test_euler_data():
    """オイラー角データ取得テスト"""
    print("\n=== オイラー角データ取得テスト ===")
    
    sensor = BNOSensor()
    
    try:
        # 接続
        sensor.connect()
        print("センサーに接続しました")
        
        # 複数回データを取得してテスト
        for i in range(5):
            try:
                euler_data = sensor.euler()
                heading, roll, pitch = euler_data
                print(f"測定 {i+1}: Heading={heading:.2f}°, Roll={roll:.2f}°, Pitch={pitch:.2f}°")
                time.sleep(0.5)
                
            except Exception as e:
                print(f"✗ データ取得エラー: {e}")
                return False
        
        print("✓ オイラー角データ取得成功")
        
    except Exception as e:
        print(f"✗ テスト失敗: {e}")
        return False
    
    finally:
        sensor.disconnect()
        print("センサー接続を切断しました")
    
    return True


def test_connection_error_handling():
    """接続エラーハンドリングテスト"""
    print("\n=== 接続エラーハンドリングテスト ===")
    
    sensor = BNOSensor()
    
    # 接続前にデータ取得を試行（エラーが発生するはず）
    try:
        sensor.euler()
        print("✗ エラーが発生しませんでした（予期しない動作）")
        return False
    except Exception as e:
        print(f"✓ 期待通りのエラーが発生: {e}")
    
    return True


def main():
    """メインテスト関数"""
    print("BNO055センサーライブラリテスト開始\n")
    
    tests = [
        ("接続テスト", test_bno_connection),
        ("オイラー角データ取得テスト", test_euler_data),
        ("エラーハンドリングテスト", test_connection_error_handling)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        time.sleep(10)
        print(f"\n{'='*50}")
        print(f"実行中: {test_name}")
        print('='*50)
        
        try:
            if test_func():
                print(f"✓ {test_name} 成功")
                passed += 1
            else:
                print(f"✗ {test_name} 失敗")
        except Exception as e:
            print(f"✗ {test_name} 例外発生: {e}")
    
    print(f"\n{'='*50}")
    print(f"テスト結果: {passed}/{total} 成功")
    print('='*50)
    
    if passed == total:
        print("すべてのテストが成功しました！")
    else:
        print("一部のテストが失敗しました。")


if __name__ == "__main__":
    main()