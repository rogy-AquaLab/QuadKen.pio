"""
プリセット・ボタンエラー処理のテスト
Task 5.2の実装をテストする
"""

import os
import sys
import tempfile
import yaml
from unittest.mock import Mock

# プロジェクトルートをパスに追加
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from tools.key_mapping import KeyMappingManager, SYSTEM_CONNECT, SERVO_BATT_0, FORWARD
from tools.controller import Controller, Button


def test_nonexistent_preset():
    """存在しないプリセット名の処理テスト"""
    controller = Mock(spec=Controller)
    
    config_data = {
        'key_mapping': {
            'operation_preset': 'nonexistent_preset'
        }
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False, encoding='utf-8') as f:
        yaml.dump(config_data, f, default_flow_style=False, allow_unicode=True)
        config_path = f.name
    
    try:
        manager = KeyMappingManager(config_path, controller)
        
        # デフォルトプリセットにフォールバックすることを確認
        assert manager.get_current_operation_mode() == "individual_control"
        assert manager.is_function_available(SYSTEM_CONNECT)
        assert manager.get_button_for_function(SYSTEM_CONNECT) == Button.START
        
        print("✓ 存在しないプリセット名の適切な処理確認")
    finally:
        os.unlink(config_path)


def test_invalid_button_in_preset():
    """プリセット内の無効なボタン名の処理テスト"""
    controller = Mock(spec=Controller)
    
    # カスタムプリセットファイルを作成
    custom_preset_data = {
        'custom_operation_presets': {
            'test_preset': {
                'operation_mode': 'individual_control',
                'mappings': {
                    'system_connect': 'INVALID_BUTTON',
                    'servo_batt_0': 'A'
                }
            }
        }
    }
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # presetsディレクトリを作成
        presets_dir = os.path.join(temp_dir, 'presets')
        os.makedirs(presets_dir)
        
        # カスタムプリセットファイルを作成
        custom_presets_path = os.path.join(presets_dir, 'custom_presets.yaml')
        with open(custom_presets_path, 'w', encoding='utf-8') as f:
            yaml.dump(custom_preset_data, f, default_flow_style=False, allow_unicode=True)
        
        # メイン設定ファイルを作成
        config_data = {
            'key_mapping': {
                'operation_preset': 'test_preset'
            }
        }
        
        config_path = os.path.join(temp_dir, 'config.yaml')
        with open(config_path, 'w', encoding='utf-8') as f:
            yaml.dump(config_data, f, default_flow_style=False, allow_unicode=True)
        
        manager = KeyMappingManager(config_path, controller)
        
        # 無効なボタンはデフォルト値、有効なボタンは設定値を使用することを確認
        system_button = manager.get_button_for_function(SYSTEM_CONNECT)
        servo_button = manager.get_button_for_function(SERVO_BATT_0)
        assert system_button == Button.START  # デフォルト値
        assert servo_button == Button.A       # 設定値
        
        print("✓ プリセット内の無効なボタン名の適切な処理確認")


def test_invalid_button_in_override():
    """オーバーライド設定での無効なボタン名の処理テスト"""
    controller = Mock(spec=Controller)
    
    config_data = {
        'key_mapping': {
            'operation_preset': 'basic_individual',
            'override_mappings': {
                'system_connect': 'INVALID_BUTTON',
                'servo_batt_0': 'B',
                'nonexistent_function': 'A'
            }
        }
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False, encoding='utf-8') as f:
        yaml.dump(config_data, f, default_flow_style=False, allow_unicode=True)
        config_path = f.name
    
    try:
        manager = KeyMappingManager(config_path, controller)
        
        # 無効なボタン名はデフォルト値、有効な設定は適用されることを確認
        system_button = manager.get_button_for_function(SYSTEM_CONNECT)
        servo_button = manager.get_button_for_function(SERVO_BATT_0)
        assert system_button == Button.START  # デフォルト値（無効なボタン名のため）
        assert servo_button == Button.B       # 設定値（有効なボタン名）
        
        print("✓ オーバーライド設定での無効なボタン名の適切な処理確認")
    finally:
        os.unlink(config_path)


def test_invalid_function_name():
    """存在しない機能名の処理テスト"""
    controller = Mock(spec=Controller)
    
    config_data = {
        'key_mapping': {
            'operation_preset': 'basic_individual',
            'override_mappings': {
                'nonexistent_function': 'A',
                'servo_batt_0': 'B'
            }
        }
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False, encoding='utf-8') as f:
        yaml.dump(config_data, f, default_flow_style=False, allow_unicode=True)
        config_path = f.name
    
    try:
        manager = KeyMappingManager(config_path, controller)
        
        # 有効な機能のみ設定されることを確認
        servo_button = manager.get_button_for_function(SERVO_BATT_0)
        assert servo_button == Button.B
        
        print("✓ 存在しない機能名の適切な処理確認")
    finally:
        os.unlink(config_path)


def test_function_not_available_in_mode():
    """現在の操作モードで利用できない機能の処理テスト"""
    controller = Mock(spec=Controller)
    
    config_data = {
        'key_mapping': {
            'operation_preset': 'basic_individual',  # individual_controlモード
            'override_mappings': {
                'forward': 'A',  # integrated_controlモードでのみ利用可能
                'servo_batt_0': 'B'  # individual_controlモードで利用可能
            }
        }
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False, encoding='utf-8') as f:
        yaml.dump(config_data, f, default_flow_style=False, allow_unicode=True)
        config_path = f.name
    
    try:
        manager = KeyMappingManager(config_path, controller)
        
        # 現在のモードで利用可能な機能のみ設定されることを確認
        assert manager.get_current_operation_mode() == "individual_control"
        assert not manager.is_function_available(FORWARD)  # integrated_controlでのみ利用可能
        assert manager.is_function_available(SERVO_BATT_0)  # individual_controlで利用可能
        
        servo_button = manager.get_button_for_function(SERVO_BATT_0)
        assert servo_button == Button.B
        
        print("✓ 操作モードで利用できない機能の適切な処理確認")
    finally:
        os.unlink(config_path)


def test_malformed_custom_preset_file():
    """不正な形式のカスタムプリセットファイルの処理テスト"""
    controller = Mock(spec=Controller)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # presetsディレクトリを作成
        presets_dir = os.path.join(temp_dir, 'presets')
        os.makedirs(presets_dir)
        
        # 不正な形式のカスタムプリセットファイルを作成
        custom_presets_path = os.path.join(presets_dir, 'custom_presets.yaml')
        with open(custom_presets_path, 'w', encoding='utf-8') as f:
            f.write("custom_operation_presets:\n  invalid_yaml: [unclosed")
        
        # メイン設定ファイルを作成
        config_data = {
            'key_mapping': {
                'operation_preset': 'basic_individual'
            }
        }
        
        config_path = os.path.join(temp_dir, 'config.yaml')
        with open(config_path, 'w', encoding='utf-8') as f:
            yaml.dump(config_data, f, default_flow_style=False, allow_unicode=True)
        
        manager = KeyMappingManager(config_path, controller)
        
        # デフォルトプリセットが使用されることを確認
        assert manager.get_current_operation_mode() == "individual_control"
        assert manager.get_button_for_function(SYSTEM_CONNECT) == Button.START
        
        print("✓ 不正な形式のカスタムプリセットファイルの適切な処理確認")


def test_helper_methods():
    """ヘルパーメソッドのテスト"""
    controller = Mock(spec=Controller)
    manager = KeyMappingManager("nonexistent.yaml", controller)
    
    # 利用可能なプリセット名を取得
    presets = manager.get_available_presets()
    assert 'basic_individual' in presets
    assert 'basic_integrated' in presets
    
    # 利用可能な機能名を取得
    functions = manager.get_available_functions()
    assert 'system_connect' in functions
    assert 'servo_batt_0' in functions
    
    print("✓ ヘルパーメソッドの動作確認")


if __name__ == "__main__":
    print("プリセット・ボタンエラー処理テスト開始")
    test_nonexistent_preset()
    test_invalid_button_in_preset()
    test_invalid_button_in_override()
    test_invalid_function_name()
    test_function_not_available_in_mode()
    test_malformed_custom_preset_file()
    test_helper_methods()
    print("✓ すべてのテスト完了")