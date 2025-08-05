"""
config.yaml読み込み機能の包括的なバリデーションテスト
Task 2.1の要件を検証
"""

import sys
import os
import yaml
import tempfile
from unittest.mock import Mock

# パスを追加してモジュールをインポート
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from tools.key_mapping import KeyMappingManager, SYSTEM_CONNECT, SERVO_BATT_0, FORWARD


def create_mock_controller():
    """モックコントローラーを作成"""
    mock_controller = Mock()
    mock_controller.pushed_button = Mock(return_value=False)
    mock_controller.is_button_pressed = Mock(return_value=False)
    mock_controller.r2_push = Mock(return_value=0.0)
    mock_controller.l2_push = Mock(return_value=0.0)
    return mock_controller


def test_key_mapping_section_reading():
    """key_mappingセクションの読み込み処理テスト"""
    print("=== key_mappingセクション読み込みテスト ===")
    
    # テスト用設定データ
    test_config = {
        'tcp': {'debug_mode': 'off'},
        'controller': {'type': 'logi_x'},
        'main': {'interval': 0.1},
        'key_mapping': {
            'operation_mode': 'integrated_control',
            'override_mappings': {
                'system_connect': 'HOME',
                'forward': 'A'
            }
        }
    }
    
    # 一時ファイルに設定を書き込み
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False, encoding='utf-8') as f:
        yaml.dump(test_config, f, default_flow_style=False)
        temp_config_path = f.name
    
    try:
        mock_controller = create_mock_controller()
        key_mapping = KeyMappingManager(temp_config_path, mock_controller)
        
        # 読み込み結果の検証
        assert key_mapping.get_current_operation_mode() == "integrated_control", "操作モードが正しく読み込まれていません"
        assert key_mapping.current_mappings[SYSTEM_CONNECT] == "HOME", "オーバーライドマッピングが適用されていません"
        assert key_mapping.current_mappings[FORWARD] == "A", "オーバーライドマッピングが適用されていません"
        
        print("✓ key_mappingセクションが正しく読み込まれました")
        print(f"  - 操作モード: {key_mapping.get_current_operation_mode()}")
        print(f"  - オーバーライド適用数: 2個")
        
    except Exception as e:
        print(f"✗ テスト失敗: {e}")
        raise
    finally:
        os.unlink(temp_config_path)


def test_operation_mode_parsing():
    """operation_modeの解析テスト"""
    print("\n=== operation_mode解析テスト ===")
    
    test_cases = [
        ('individual_control', 'individual_control'),
        ('integrated_control', 'integrated_control'),
        ('nonexistent_mode', 'individual_control')  # 存在しないモードはデフォルトに
    ]
    
    for mode_name, expected_mode in test_cases:
        test_config = {
            'key_mapping': {
                'operation_mode': mode_name
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False, encoding='utf-8') as f:
            yaml.dump(test_config, f, default_flow_style=False)
            temp_config_path = f.name
        
        try:
            mock_controller = create_mock_controller()
            key_mapping = KeyMappingManager(temp_config_path, mock_controller)
            
            actual_mode = key_mapping.get_current_operation_mode()
            assert actual_mode == expected_mode, f"操作モード '{mode_name}' が期待値と異なります: {actual_mode} != {expected_mode}"
            
            print(f"✓ 操作モード '{mode_name}' -> '{actual_mode}'")
            
        except Exception as e:
            print(f"✗ 操作モード '{mode_name}' のテスト失敗: {e}")
            raise
        finally:
            os.unlink(temp_config_path)


def test_override_mappings_parsing():
    """override_mappingsの解析テスト"""
    print("\n=== override_mappings解析テスト ===")
    
    test_config = {
        'key_mapping': {
            'operation_mode': 'individual_control',
            'override_mappings': {
                'system_connect': 'Y',
                'servo_batt_0': 'UP',
                'servo_batt_1': 'DOWN',
                'invalid_function': 'LEFT'  # 無効な機能名
            }
        }
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False, encoding='utf-8') as f:
        yaml.dump(test_config, f, default_flow_style=False)
        temp_config_path = f.name
    
    try:
        mock_controller = create_mock_controller()
        key_mapping = KeyMappingManager(temp_config_path, mock_controller)
        
        # 有効なオーバーライドの確認
        assert key_mapping.current_mappings[SYSTEM_CONNECT] == "Y", "system_connectのオーバーライドが適用されていません"
        assert key_mapping.current_mappings[SERVO_BATT_0] == "UP", "servo_batt_0のオーバーライドが適用されていません"
        
        print("✓ override_mappingsが正しく解析されました")
        print(f"  - 適用されたオーバーライド数: {len([k for k in key_mapping.current_mappings.keys() if str(k) in ['system_connect', 'servo_batt_0', 'servo_batt_1']])}")
        
    except Exception as e:
        print(f"✗ テスト失敗: {e}")
        raise
    finally:
        os.unlink(temp_config_path)


def test_missing_key_mapping_section():
    """key_mappingセクションが存在しない場合のテスト"""
    print("\n=== key_mappingセクション不存在テスト ===")
    
    test_config = {
        'tcp': {'debug_mode': 'off'},
        'controller': {'type': 'logi_x'},
        'main': {'interval': 0.1}
        # key_mappingセクションなし
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False, encoding='utf-8') as f:
        yaml.dump(test_config, f, default_flow_style=False)
        temp_config_path = f.name
    
    try:
        mock_controller = create_mock_controller()
        key_mapping = KeyMappingManager(temp_config_path, mock_controller)
        
        # デフォルト設定が適用されているか確認
        assert key_mapping.get_current_operation_mode() == "individual_control", "デフォルト操作モードが適用されていません"
        assert len(key_mapping.current_mappings) > 0, "デフォルトマッピングが適用されていません"
        
        print("✓ key_mappingセクション不存在時にデフォルト設定が適用されました")
        print(f"  - デフォルト操作モード: {key_mapping.get_current_operation_mode()}")
        print(f"  - デフォルトマッピング数: {len(key_mapping.current_mappings)}")
        
    except Exception as e:
        print(f"✗ テスト失敗: {e}")
        raise
    finally:
        os.unlink(temp_config_path)


def test_invalid_yaml_syntax():
    """無効なYAML構文の処理テスト"""
    print("\n=== 無効なYAML構文処理テスト ===")
    
    invalid_yaml = """
tcp:
  debug_mode: off
key_mapping:
  operation_mode: "individual_control"
  override_mappings:
    system_connect: "Y"
    invalid_syntax: [unclosed_bracket
"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False, encoding='utf-8') as f:
        f.write(invalid_yaml)
        temp_config_path = f.name
    
    try:
        mock_controller = create_mock_controller()
        key_mapping = KeyMappingManager(temp_config_path, mock_controller)
        
        # エラー時にデフォルト設定が適用されているか確認
        assert key_mapping.get_current_operation_mode() == "individual_control", "YAML構文エラー時にデフォルト設定が適用されていません"
        
        print("✓ 無効なYAML構文時にデフォルト設定が適用されました")
        
    except Exception as e:
        print(f"✗ テスト失敗: {e}")
        raise
    finally:
        os.unlink(temp_config_path)


def test_invalid_key_mapping_structure():
    """無効なkey_mapping構造の処理テスト"""
    print("\n=== 無効なkey_mapping構造処理テスト ===")
    
    test_cases = [
        # key_mappingが文字列（辞書でない）
        {'key_mapping': 'invalid_string'},
        # operation_modeが数値
        {'key_mapping': {'operation_mode': 123}},
        # override_mappingsが配列
        {'key_mapping': {'override_mappings': ['invalid', 'array']}}
    ]
    
    for i, test_config in enumerate(test_cases):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False, encoding='utf-8') as f:
            yaml.dump(test_config, f, default_flow_style=False)
            temp_config_path = f.name
        
        try:
            mock_controller = create_mock_controller()
            key_mapping = KeyMappingManager(temp_config_path, mock_controller)
            
            # エラー時にデフォルト設定が適用されているか確認
            assert key_mapping.get_current_operation_mode() == "individual_control", f"テストケース{i+1}: 無効な構造時にデフォルト設定が適用されていません"
            
            print(f"✓ テストケース{i+1}: 無効な構造時にデフォルト設定が適用されました")
            
        except Exception as e:
            print(f"✗ テストケース{i+1} 失敗: {e}")
            raise
        finally:
            os.unlink(temp_config_path)


def run_all_tests():
    """全テストを実行"""
    print("=== config.yaml読み込み機能 包括テスト開始 ===\n")
    
    try:
        test_key_mapping_section_reading()
        test_operation_mode_parsing()
        test_override_mappings_parsing()
        test_missing_key_mapping_section()
        test_invalid_yaml_syntax()
        test_invalid_key_mapping_structure()
        
        print("\n=== 全テスト成功 ===")
        print("✓ Task 2.1の要件が満たされています:")
        print("  - key_mappingセクションの読み込み処理")
        print("  - operation_modeとoverride_mappingsの解析")
        print("  - エラーハンドリングとフォールバック処理")
        
    except Exception as e:
        print(f"\n=== テスト失敗 ===")
        print(f"エラー: {e}")
        raise


if __name__ == "__main__":
    run_all_tests()