import sys
import os

# tools フォルダをパスに追加
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from tools.controller import Controller
import time

def test_r2_push():
    """
    R2ボタンの押し込み具合をテストする関数
    """
    try:
        # コントローラー初期化
        controller = Controller()
        print("コントローラーが正常に初期化されました。")
        print("R2ボタンを押してテストしてください。")
        print("Ctrl+C で終了します。")
        print("-" * 50)
        
        # メインループ
        while True:
            controller.update()
            
            # R2ボタンの押し込み具合を取得
            r2_value = controller.r2_push()
            
            # バーで視覚的に表示
            bar_length = 20
            filled_length = int(bar_length * r2_value)
            bar = "█" * filled_length + "░" * (bar_length - filled_length)
            
            # 値とバーを表示
            print(f"\rR2押し込み具合: {r2_value:.3f} |{bar}| {r2_value*100:.1f}%", end="", flush=True)
            
            # 少し待機（CPU負荷軽減）
            time.sleep(0.05)
            
    except RuntimeError as e:
        print(f"エラー: {e}")
    except KeyboardInterrupt:
        print("\n\nテスト終了")
    except Exception as e:
        print(f"\n予期しないエラー: {e}")

if __name__ == "__main__":
    test_r2_push()
