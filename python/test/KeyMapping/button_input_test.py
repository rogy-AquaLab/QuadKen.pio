"""
ボタン入力判定機能のテスト

Task 4.2: ボタン入力判定機能を実装
- is_function_pushed()とis_function_pressed()メソッドの実装
- get_analog_value()メソッドの実装
"""

import sys
import os
import tempfile
import yaml

# プロジェクトルートをパスに追加
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from tools.key_mapping import (
    KeyMappingManager, FunctionId,
    SYSTEM_CONNECT, SERVO_BATT_0, MOTOR_FORWARD, MOTOR_BACKWARD, FORWARD
)
from tools.controller import Button


class MockController:
    """テスト用のモックControllerクラス"""
    def __init__(self):
        self.button_pressed_states = {}
        self.button_pushed_states = {}
        self.r2_value = 0.0
        self.l2_value = 0.0
    
    def set_button_pressed(self, button, pressed):
        """ボタンの押下状態を設定"""
        self.button_pressed_states[button] = pressed
    
    def set_button_pushed(self, button, pushed):
        """ボタンの押し始め状態を設定"""
        self.button_pushed_states[button] = pushed
    
    def set_r2_value(self, value):
        """R2の値を設定"""
        self.r2_value = value
    
    def set_l2_value(self, value):
        """L2の値を設定"""
        self.l2_value = value
    
    def pushed_button(self, button):
        """ボタンが押され始めたかを返す"""
        return self.button_pushed_states.get(button, False)
    
    def is_button_pressed(self, button):
        """ボタンが現在押されているかを返す"""
        return self.button_pressed_states.get(button, False)
    
    def r2_push(self):
        """R2の値を返す"""
        return self.r2_value
    
    def l2_push(self):
        """L2の値を返す"""
        return self.l2_value


def test_is_function_pushed():
    """is_function_pushed()メソッドのテスト"""
    print("\n=== is_function_pushed()メソッドのテスト ===")
    
    # テスト用設定ファイルを作成
    config_data = {
        'key_mapping': {
            'operation_mode': 'individual_control',
            'override_mappings': {
                'system_connect': 'START',
                'servo_batt_0': 'A'
            }
        }
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False, encoding='utf-8') as f:
        yaml.dump(config_data, f, allow_unicode=True)
        temp_config_path = f.name
    
    try:
        mock_controller = MockController()
        key_mapping = KeyMappingManager(temp_config_path, mock_controller)
        
        # ボタンが押されていない状態
        result = key_mapping.is_function_pushed(SYSTEM_CONNECT)
        assert result is False, "ボタンが押されていないのにTrueが返された"
        print("✓ ボタンが押されていない状態: False")
        
        # ボタンが押され始めた状態
        mock_controller.set_button_pushed(Button.START, True)
        result = key_mapping.is_function_pushed(SYSTEM_CONNECT)
        assert result is True, "ボタンが押され始めたのにFalseが返された"
        print("✓ ボタンが押され始めた状態: True")
        
        # 利用不可能な機能のテスト
        result = key_mapping.is_function_pushed(FORWARD)  # integrated_control専用
        assert result is False, "利用不可能な機能でTrueが返された"
        print("✓ 利用不可能な機能: False")
        
        print("✓ is_function_pushed()メソッドテスト完了")
        
    finally:
        os.unlink(temp_config_path)


def test_is_function_pressed():
    """is_function_pressed()メソッドのテスト"""
    print("\n=== is_function_pressed()メソッドのテスト ===")
    
    # テスト用設定ファイルを作成
    config_data = {
        'key_mapping': {
            'operation_mode': 'individual_control',
            'override_mappings': {
                'system_connect': 'START',
                'servo_batt_0': 'A'
            }
        }
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False, encoding='utf-8') as f:
        yaml.dump(config_data, f, allow_unicode=True)
        temp_config_path = f.name
    
    try:
        mock_controller = MockController()
        key_mapping = KeyMappingManager(temp_config_path, mock_controller)
        
        # ボタンが押されていない状態
        result = key_mapping.is_function_pressed(SYSTEM_CONNECT)
        assert result is False, "ボタンが押されていないのにTrueが返された"
        print("✓ ボタンが押されていない状態: False")
        
        # ボタンが押されている状態
        mock_controller.set_button_pressed(Button.START, True)
        result = key_mapping.is_function_pressed(SYSTEM_CONNECT)
        assert result is True, "ボタンが押されているのにFalseが返された"
        print("✓ ボタンが押されている状態: True")
        
        # 利用不可能な機能のテスト
        result = key_mapping.is_function_pressed(FORWARD)  # integrated_control専用
        assert result is False, "利用不可能な機能でTrueが返された"
        print("✓ 利用不可能な機能: False")
        
        print("✓ is_function_pressed()メソッドテスト完了")
        
    finally:
        os.unlink(temp_config_path)


def test_get_analog_value():
    """get_analog_value()メソッドのテスト"""
    print("\n=== get_analog_value()メソッドのテスト ===")
    
    # テスト用設定ファイルを作成
    config_data = {
        'key_mapping': {
            'operation_mode': 'individual_control',
            'override_mappings': {
                'motor_forward': 'R2',
                'motor_backward': 'L2',
                'servo_batt_0': 'A'
            }
        }
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False, encoding='utf-8') as f:
        yaml.dump(config_data, f, allow_unicode=True)
        temp_config_path = f.name
    
    try:
        mock_controller = MockController()
        key_mapping = KeyMappingManager(temp_config_path, mock_controller)
        
        # R2アナログ値のテスト
        mock_controller.set_r2_value(0.5)
        result = key_mapping.get_analog_value(MOTOR_FORWARD)
        assert result == 0.5, f"R2の値が正しく取得できない: {result}"
        print("✓ R2アナログ値: 0.5")
        
        # L2アナログ値のテスト
        mock_controller.set_l2_value(0.8)
        result = key_mapping.get_analog_value(MOTOR_BACKWARD)
        assert result == 0.8, f"L2の値が正しく取得できない: {result}"
        print("✓ L2アナログ値: 0.8")
        
        # デジタルボタンのテスト（押されていない）
        result = key_mapping.get_analog_value(SERVO_BATT_0)
        assert result == 0.0, f"デジタルボタン（未押下）の値が正しくない: {result}"
        print("✓ デジタルボタン（未押下）: 0.0")
        
        # デジタルボタンのテスト（押されている）
        mock_controller.set_button_pressed(Button.A, True)
        result = key_mapping.get_analog_value(SERVO_BATT_0)
        assert result == 1.0, f"デジタルボタン（押下）の値が正しくない: {result}"
        print("✓ デジタルボタン（押下）: 1.0")
        
        # 利用不可能な機能のテスト
        result = key_mapping.get_analog_value(FORWARD)  # integrated_control専用
        assert result == 0.0, "利用不可能な機能で0.0以外の値が返された"
        print("✓ 利用不可能な機能: 0.0")
        
        print("✓ get_analog_value()メソッドテスト完了")
        
    finally:
        os.unlink(temp_config_path)


def test_button_mapping_edge_cases():
    """ボタンマッピングのエッジケースのテスト"""
    print("\n=== ボタンマッピングのエッジケースのテスト ===")
    
    # 無効なボタン名を含む設定ファイルを作成
    config_data = {
        'key_mapping': {
            'operation_mode': 'individual_control',
            'override_mappings': {
                'system_connect': 'INVALID_BUTTON',  # 存在しないボタン
                'servo_batt_0': 'A'
            }
        }
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False, encoding='utf-8') as f:
        yaml.dump(config_data, f, allow_unicode=True)
        temp_config_path = f.name
    
    try:
        mock_controller = MockController()
        key_mapping = KeyMappingManager(temp_config_path, mock_controller)
        
        # 無効なボタン名の場合、メソッドはFalse/0.0を返すべき
        result = key_mapping.is_function_pushed(SYSTEM_CONNECT)
        assert result is False, "無効なボタン名でTrueが返された"
        print("✓ 無効なボタン名でのis_function_pushed: False")
        
        result = key_mapping.is_function_pressed(SYSTEM_CONNECT)
        assert result is False, "無効なボタン名でTrueが返された"
        print("✓ 無効なボタン名でのis_function_pressed: False")
        
        result = key_mapping.get_analog_value(SYSTEM_CONNECT)
        assert result == 0.0, "無効なボタン名で0.0以外の値が返された"
        print("✓ 無効なボタン名でのget_analog_value: 0.0")
        
        print("✓ ボタンマッピングのエッジケーステスト完了")
        
    finally:
        os.unlink(temp_config_path)


def run_all_tests():
    """全てのテストを実行"""
    print("ボタン入力判定機能テスト開始")
    print("=" * 50)
    
    try:
        test_is_function_pushed()
        test_is_function_pressed()
        test_get_analog_value()
        test_button_mapping_edge_cases()
        
        print("\n" + "=" * 50)
        print("✅ 全てのボタン入力判定機能テストが成功しました！")
        
    except Exception as e:
        print(f"\n❌ テストエラー: {e}")
        raise


if __name__ == "__main__":
    run_all_tests()