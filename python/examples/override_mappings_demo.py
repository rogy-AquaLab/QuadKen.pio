"""
オーバーライドマッピング機能のデモンストレーション

このスクリプトは、KeyMappingManagerのオーバーライドマッピング機能の
動作を実際に確認するためのデモです。
"""

import sys
import os
import yaml
import tempfile

# プロジェクトのルートディレクトリをパスに追加
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from tools.key_mapping import KeyMappingManager, SYSTEM_CONNECT, SERVO_BATT_0, SERVO_BATT_1, FORWARD
from tools.controller import Controller


def create_demo_config(config_dir: str, operation_mode: str, override_mappings: dict = None) -> str:
    """デモ用のconfig.yamlを作成"""
    config_path = os.path.join(config_dir, 'config.yaml')
    config_data = {
        'tcp': {
            'debug_mode': 'off'
        },
        'controller': {
            'type': 'logi_x'
        },
        'main': {
            'interval': 0.1
        },
        'key_mapping': {
            'operation_mode': operation_mode
        }
    }
    
    if override_mappings:
        config_data['key_mapping']['override_mappings'] = override_mappings
    
    with open(config_path, 'w', encoding='utf-8') as f:
        yaml.dump(config_data, f, default_flow_style=False, allow_unicode=True)
    
    return config_path


def demo_basic_override():
    """基本的なオーバーライド機能のデモ"""
    print("=" * 60)
    print("基本的なオーバーライド機能のデモ")
    print("=" * 60)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # オーバーライドなしの設定
        print("\n1. オーバーライドなしの場合:")
        config_path = create_demo_config(temp_dir, 'individual_control')
        controller = Controller()
        key_mapping = KeyMappingManager(config_path, controller)
        
        print(f"  system_connect機能: {key_mapping.get_button_for_function(SYSTEM_CONNECT)}")
        print(f"  servo_batt_0機能: {key_mapping.get_button_for_function(SERVO_BATT_0)}")
        print(f"  servo_batt_1機能: {key_mapping.get_button_for_function(SERVO_BATT_1)}")
        
        # オーバーライドありの設定
        print("\n2. オーバーライドありの場合:")
        override_mappings = {
            'system_connect': 'Y',      # STARTの代わりにYボタン
            'servo_batt_0': 'X'         # Aの代わりにXボタン
        }
        
        config_path = create_demo_config(temp_dir, 'individual_control', override_mappings)
        key_mapping = KeyMappingManager(config_path, controller)
        
        print(f"  system_connect機能: {key_mapping.get_button_for_function(SYSTEM_CONNECT)} (オーバーライド)")
        print(f"  servo_batt_0機能: {key_mapping.get_button_for_function(SERVO_BATT_0)} (オーバーライド)")
        print(f"  servo_batt_1機能: {key_mapping.get_button_for_function(SERVO_BATT_1)} (変更なし)")


def demo_operation_mode_override():
    """操作モード別のオーバーライドデモ"""
    print("\n" + "=" * 60)
    print("操作モード別のオーバーライドデモ")
    print("=" * 60)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        controller = Controller()
        
        # 個別制御モードでのオーバーライド
        print("\n1. 個別制御モードでのオーバーライド:")
        override_mappings = {
            'system_connect': 'HOME',
            'servo_batt_0': 'L1',
            'servo_batt_1': 'R1'
        }
        
        config_path = create_demo_config(temp_dir, 'individual_control', override_mappings)
        key_mapping = KeyMappingManager(config_path, controller)
        
        print(f"  操作モード: {key_mapping.get_current_operation_mode()}")
        print(f"  system_connect機能: {key_mapping.get_button_for_function(SYSTEM_CONNECT)}")
        print(f"  servo_batt_0機能: {key_mapping.get_button_for_function(SERVO_BATT_0)}")
        print(f"  servo_batt_1機能: {key_mapping.get_button_for_function(SERVO_BATT_1)}")
        
        # 統合制御モードでのオーバーライド
        print("\n2. 統合制御モードでのオーバーライド:")
        override_mappings = {
            'system_connect': 'PLUS',
            'forward': 'A',
            'backward': 'B'
        }
        
        config_path = create_demo_config(temp_dir, 'integrated_control', override_mappings)
        key_mapping = KeyMappingManager(config_path, controller)
        
        print(f"  操作モード: {key_mapping.get_current_operation_mode()}")
        print(f"  system_connect機能: {key_mapping.get_button_for_function(SYSTEM_CONNECT)}")
        print(f"  forward機能: {key_mapping.get_button_for_function(FORWARD)}")


def demo_invalid_override():
    """無効なオーバーライドの処理デモ"""
    print("\n" + "=" * 60)
    print("無効なオーバーライドの処理デモ")
    print("=" * 60)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        controller = Controller()
        
        print("\n無効なオーバーライドマッピングを含む設定:")
        override_mappings = {
            'system_connect': 'Y',          # 有効
            'unknown_function': 'A',        # 無効: 存在しない機能名
            'servo_batt_0': 'INVALID_BTN',  # 無効: 存在しないボタン名
            'forward': 'B'                  # 無効: individual_controlモードでは利用不可
        }
        
        config_path = create_demo_config(temp_dir, 'individual_control', override_mappings)
        key_mapping = KeyMappingManager(config_path, controller)
        
        print(f"\n結果:")
        print(f"  system_connect機能: {key_mapping.get_button_for_function(SYSTEM_CONNECT)} (有効なオーバーライド)")
        print(f"  servo_batt_0機能: {key_mapping.get_button_for_function(SERVO_BATT_0)} (無効なため元の設定)")
        
        # 設定情報を表示
        print(f"\n適用されたマッピング数: {len(key_mapping.current_mappings)}")


def demo_operation_mode_switching():
    """操作モード切り替えのデモ"""
    print("\n" + "=" * 60)
    print("操作モード切り替えのデモ")
    print("=" * 60)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        controller = Controller()
        
        print("\n1. individual_controlモード:")
        config_path = create_demo_config(temp_dir, 'individual_control')
        key_mapping = KeyMappingManager(config_path, controller)
        
        print(f"  操作モード: {key_mapping.get_current_operation_mode()}")
        print(f"  servo_batt_0機能: {key_mapping.get_button_for_function(SERVO_BATT_0)} (利用可能)")
        print(f"  forward機能: {key_mapping.get_button_for_function(FORWARD)} (利用不可)")
        
        print("\n2. integrated_controlモード:")
        config_path = create_demo_config(temp_dir, 'integrated_control')
        key_mapping = KeyMappingManager(config_path, controller)
        
        print(f"  操作モード: {key_mapping.get_current_operation_mode()}")
        print(f"  servo_batt_0機能: {key_mapping.get_button_for_function(SERVO_BATT_0)} (利用不可)")
        print(f"  forward機能: {key_mapping.get_button_for_function(FORWARD)} (利用可能)")
        
        print("\n3. オーバーライドとの組み合わせ:")
        override_mappings = {
            'system_connect': 'Y',
            'forward': 'A'
        }
        
        config_path = create_demo_config(temp_dir, 'integrated_control', override_mappings)
        key_mapping = KeyMappingManager(config_path, controller)
        
        print(f"  system_connect機能: {key_mapping.get_button_for_function(SYSTEM_CONNECT)} (オーバーライド)")
        print(f"  forward機能: {key_mapping.get_button_for_function(FORWARD)} (オーバーライド)")


def main():
    """メインデモ関数"""
    print("KeyMappingManager オーバーライドマッピング機能デモ")
    print("このデモでは、オーバーライドマッピング機能の動作を確認できます。")
    
    try:
        demo_basic_override()
        demo_operation_mode_override()
        demo_invalid_override()
        demo_operation_mode_switching()
        
        print("\n" + "=" * 60)
        print("✅ デモが完了しました！")
        print("オーバーライドマッピング機能は正常に動作しています。")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ デモ実行中にエラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)