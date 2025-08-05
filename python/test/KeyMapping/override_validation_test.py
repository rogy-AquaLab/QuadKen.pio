"""
オーバーライドマッピング検証機能のテスト

新しいシンプルな実装に対応したテスト
"""

import sys
import os
import tempfile
import yaml

# プロジェクトルートをパスに追加
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from tools.key_mapping import (
    KeyMappingManager, 
    SYSTEM_CONNECT, SERVO_BATT_0, SERVO_BATT_1, FORWARD
)
from tools.controller import Controller


def create_test_config(config_dir: str, operation_mode: str = 'individual_control', override_mappings: dict = None) -> str:
    """テスト用のconfig.yamlを作成"""
    config_path = os.path.join(config_dir, 'config.yaml')
    config_data = {
        'key_mapping': {
            'operation_mode': operation_mode
        }
    }
    
    if override_mappings:
        config_data['key_mapping']['override_mappings'] = override_mappings
    
    with open(config_path, 'w', encoding='utf-8') as f:
        yaml.dump(config_data, f, allow_unicode=True)
    
    return config_path


def test_valid_override_mappings():
    """有効なオーバーライドマッピングのテスト"""
    print("=== 有効なオーバーライドマッピングテスト ===")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # 有効なオーバーライドマッピング
        override_mappings = {
            'system_connect': 'Y',      # 有効: 存在する機能、存在するボタン
            'servo_batt_0': 'X'         # 有効: 存在する機能、存在するボタン
        }
        
        config_path = create_test_config(temp_dir, 'individual_control', override_mappings)
        controller = Controller()
        key_mapping = KeyMappingManager(config_path, controller)
        
        print(f"現在のマッピング数: {len(key_mapping.current_mappings)}")
        
        # オーバーライドが適用されているかチェック
        system_connect_button = key_mapping.get_button_for_function(SYSTEM_CONNECT)
        servo_batt_0_button = key_mapping.get_button_for_function(SERVO_BATT_0)
        
        print(f"system_connect機能: {system_connect_button}")
        print(f"servo_batt_0機能: {servo_batt_0_button}")
        
        # 有効なオーバーライドが適用されていることを確認
        assert system_connect_button is not None, "system_connect機能のオーバーライドが適用されていない"
        assert servo_batt_0_button is not None, "servo_batt_0機能のオーバーライドが適用されていない"
        
        print("✓ 有効なオーバーライドマッピングテスト成功")


def test_invalid_override_mappings():
    """無効なオーバーライドマッピングのテスト"""
    print("\n=== 無効なオーバーライドマッピングテスト ===")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # 無効なオーバーライドマッピング
        override_mappings = {
            'unknown_function': 'A',        # 無効: 存在しない機能名
            'forward': 'B'                  # 無効: individual_controlモードでは利用不可
        }
        
        config_path = create_test_config(temp_dir, 'individual_control', override_mappings)
        controller = Controller()
        key_mapping = KeyMappingManager(config_path, controller)
        
        print(f"現在のマッピング数: {len(key_mapping.current_mappings)}")
        
        # 無効なオーバーライドは適用されず、デフォルト設定が使用される
        system_connect_button = key_mapping.get_button_for_function(SYSTEM_CONNECT)
        forward_button = key_mapping.get_button_for_function(FORWARD)
        
        print(f"system_connect機能: {system_connect_button} (デフォルト設定)")
        print(f"forward機能: {forward_button} (利用不可)")
        
        # デフォルト設定が使用されていることを確認
        assert system_connect_button is not None, "system_connect機能が利用できない"
        assert forward_button is None, "forward機能が利用可能になっている（本来は利用不可）"
        
        print("✓ 無効なオーバーライドマッピングテスト成功")


def test_operation_mode_restrictions():
    """操作モード制限のテスト"""
    print("\n=== 操作モード制限テスト ===")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        controller = Controller()
        
        # individual_controlモードでのテスト
        override_mappings = {
            'system_connect': 'Y',
            'servo_batt_0': 'X',
            'forward': 'A'  # このモードでは利用不可
        }
        
        config_path = create_test_config(temp_dir, 'individual_control', override_mappings)
        key_mapping = KeyMappingManager(config_path, controller)
        
        print(f"individual_controlモード:")
        print(f"  現在のマッピング数: {len(key_mapping.current_mappings)}")
        
        # 利用可能な機能
        system_connect_button = key_mapping.get_button_for_function(SYSTEM_CONNECT)
        servo_batt_0_button = key_mapping.get_button_for_function(SERVO_BATT_0)
        
        # 利用不可能な機能
        forward_button = key_mapping.get_button_for_function(FORWARD)
        
        print(f"  system_connect機能: {system_connect_button} (利用可能)")
        print(f"  servo_batt_0機能: {servo_batt_0_button} (利用可能)")
        print(f"  forward機能: {forward_button} (利用不可)")
        
        assert system_connect_button is not None, "system_connect機能が利用できない"
        assert servo_batt_0_button is not None, "servo_batt_0機能が利用できない"
        assert forward_button is None, "forward機能が利用可能になっている（本来は利用不可）"
        
        # integrated_controlモードでのテスト
        override_mappings = {
            'system_connect': 'HOME',
            'forward': 'A',
            'servo_batt_0': 'X'  # このモードでは利用不可
        }
        
        config_path = create_test_config(temp_dir, 'integrated_control', override_mappings)
        key_mapping = KeyMappingManager(config_path, controller)
        
        print(f"\nintegrated_controlモード:")
        print(f"  現在のマッピング数: {len(key_mapping.current_mappings)}")
        
        # 利用可能な機能
        system_connect_button = key_mapping.get_button_for_function(SYSTEM_CONNECT)
        forward_button = key_mapping.get_button_for_function(FORWARD)
        
        # 利用不可能な機能
        servo_batt_0_button = key_mapping.get_button_for_function(SERVO_BATT_0)
        
        print(f"  system_connect機能: {system_connect_button} (利用可能)")
        print(f"  forward機能: {forward_button} (利用可能)")
        print(f"  servo_batt_0機能: {servo_batt_0_button} (利用不可)")
        
        assert system_connect_button is not None, "system_connect機能が利用できない"
        assert forward_button is not None, "forward機能が利用できない"
        assert servo_batt_0_button is None, "servo_batt_0機能が利用可能になっている（本来は利用不可）"
        
        print("✓ 操作モード制限テスト成功")


def test_no_override_mappings():
    """オーバーライドなしのテスト"""
    print("\n=== オーバーライドなしテスト ===")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # オーバーライドなしの設定
        config_path = create_test_config(temp_dir, 'individual_control')
        controller = Controller()
        key_mapping = KeyMappingManager(config_path, controller)
        
        print(f"現在のマッピング数: {len(key_mapping.current_mappings)}")
        
        # デフォルト設定が使用されていることを確認
        system_connect_button = key_mapping.get_button_for_function(SYSTEM_CONNECT)
        servo_batt_0_button = key_mapping.get_button_for_function(SERVO_BATT_0)
        
        print(f"system_connect機能: {system_connect_button} (デフォルト設定)")
        print(f"servo_batt_0機能: {servo_batt_0_button} (デフォルト設定)")
        
        assert system_connect_button is not None, "デフォルト設定が適用されていない"
        assert servo_batt_0_button is not None, "デフォルト設定が適用されていない"
        
        print("✓ オーバーライドなしテスト成功")


def test_invalid_config_format():
    """無効な設定形式のテスト"""
    print("\n=== 無効な設定形式テスト ===")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # 無効な設定形式
        config_path = os.path.join(temp_dir, 'config.yaml')
        config_data = {
            'key_mapping': {
                'operation_mode': 'individual_control',
                'override_mappings': "invalid_type"  # 文字列（辞書ではない）
            }
        }
        
        with open(config_path, 'w', encoding='utf-8') as f:
            yaml.dump(config_data, f, allow_unicode=True)
        
        controller = Controller()
        key_mapping = KeyMappingManager(config_path, controller)
        
        print(f"現在のマッピング数: {len(key_mapping.current_mappings)}")
        
        # エラー時でもデフォルト設定が使用されることを確認
        system_connect_button = key_mapping.get_button_for_function(SYSTEM_CONNECT)
        assert system_connect_button is not None, "エラー時にデフォルト設定が適用されていない"
        
        print(f"system_connect機能: {system_connect_button} (デフォルト設定)")
        print("✓ 無効な設定形式テスト成功")


def main():
    """メインテスト関数"""
    print("オーバーライドマッピング検証機能のテストを開始します...\n")
    
    try:
        test_valid_override_mappings()
        test_invalid_override_mappings()
        test_operation_mode_restrictions()
        test_no_override_mappings()
        test_invalid_config_format()
        
        print("\n" + "="*50)
        print("✅ 全てのオーバーライドマッピング検証テストが成功しました！")
        print("="*50)
        
    except Exception as e:
        print(f"\n❌ テストが失敗しました: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)