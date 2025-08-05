"""
KeyMappingManagerの主要テスト
"""

import os
import sys
import tempfile
import yaml
from unittest.mock import Mock

# プロジェクトルートをパスに追加
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from tools.key_mapping import KeyMappingManager, SYSTEM_CONNECT, SERVO_BATT_0
from tools.controller import Controller, Button


def test_file_not_found():
    """ファイル不存在テスト"""
    controller = Mock(spec=Controller)
    manager = KeyMappingManager("/nonexistent/config.yaml", controller)
    
    assert manager.get_current_operation_mode() == "individual_control"
    assert manager.is_function_available(SYSTEM_CONNECT)
    print("✓ ファイル不存在時のフォールバック動作確認")


def test_yaml_syntax_error():
    """YAML構文エラーテスト"""
    controller = Mock(spec=Controller)
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False, encoding='utf-8') as f:
        f.write("key_mapping:\n  invalid_yaml: [unclosed")
        invalid_yaml_path = f.name
    
    try:
        manager = KeyMappingManager(invalid_yaml_path, controller)
        assert manager.get_current_operation_mode() == "individual_control"
        print("✓ YAML構文エラー時のフォールバック動作確認")
    finally:
        os.unlink(invalid_yaml_path)


def test_invalid_settings():
    """無効な設定値テスト"""
    controller = Mock(spec=Controller)
    
    config_data = {
        'key_mapping': {
            'operation_mode': 'invalid_mode',
            'override_mappings': {
                'system_connect': 'INVALID_BUTTON',
                'servo_batt_0': 'A'
            }
        }
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False, encoding='utf-8') as f:
        yaml.dump(config_data, f, default_flow_style=False, allow_unicode=True)
        invalid_settings_path = f.name
    
    try:
        manager = KeyMappingManager(invalid_settings_path, controller)
        
        # 無効な操作モードはデフォルトにフォールバック
        assert manager.get_current_operation_mode() == "individual_control"
        
        # 無効なボタン名はデフォルト値、有効なボタン名は適用
        system_button = manager.get_button_for_function(SYSTEM_CONNECT)
        servo_button = manager.get_button_for_function(SERVO_BATT_0)
        assert system_button == Button.START  # デフォルト値
        assert servo_button == Button.A       # 設定値
        
        print("✓ 無効な設定値の適切な処理確認")
    finally:
        os.unlink(invalid_settings_path)


def test_preset_based_configuration():
    """プリセットベースの設定テスト"""
    controller = Mock(spec=Controller)
    
    config_data = {
        'key_mapping': {
            'operation_preset': 'basic_integrated',
            'override_mappings': {
                'system_connect': 'Y'
            }
        }
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False, encoding='utf-8') as f:
        yaml.dump(config_data, f, default_flow_style=False, allow_unicode=True)
        preset_config_path = f.name
    
    try:
        manager = KeyMappingManager(preset_config_path, controller)
        
        # プリセットが正しく適用されることを確認
        assert manager.get_current_operation_mode() == "integrated_control"
        
        # オーバーライドが適用されることを確認
        system_button = manager.get_button_for_function(SYSTEM_CONNECT)
        assert system_button == Button.Y
        
        print("✓ プリセットベースの設定の適切な処理確認")
    finally:
        os.unlink(preset_config_path)


if __name__ == "__main__":
    print("KeyMappingManager テスト開始")
    test_file_not_found()
    test_yaml_syntax_error()
    test_invalid_settings()
    test_preset_based_configuration()
    print("✓ すべてのテスト完了")