from dataclasses import dataclass
from typing import Dict, Optional
import yaml
import os
from .controller import Controller, Button


@dataclass(frozen=True)
class FunctionId:
    """機能IDを表すデータクラス"""
    name: str
    
    def __str__(self):
        return self.name


# 機能ID定数の定義
SYSTEM_CONNECT = FunctionId("system_connect")
SYSTEM_SETUP = FunctionId("system_setup")
SYSTEM_CONFIG3 = FunctionId("system_config3")
SYSTEM_EXIT = FunctionId("system_exit")
SERVO_BATT_0 = FunctionId("servo_batt_0")
SERVO_BATT_1 = FunctionId("servo_batt_1")
SERVO_BATT_2 = FunctionId("servo_batt_2")
SERVO_BATT_3 = FunctionId("servo_batt_3")
SERVO_ANGLE_SWITCH = FunctionId("servo_angle_switch")
MOTOR_FORWARD = FunctionId("motor_forward")
MOTOR_BACKWARD = FunctionId("motor_backward")
STICK_LEGS_CONTROL = FunctionId("stick_legs_control")
FORWARD = FunctionId("forward")
BACKWARD = FunctionId("backward")


# 操作モードの定義
OPERATION_MODES = {
    "individual_control": [
        SYSTEM_CONNECT, SYSTEM_SETUP, SYSTEM_CONFIG3, SYSTEM_EXIT,
        SERVO_BATT_0, SERVO_BATT_1, SERVO_BATT_2, SERVO_BATT_3,
        SERVO_ANGLE_SWITCH, MOTOR_FORWARD, MOTOR_BACKWARD, STICK_LEGS_CONTROL
    ],
    "integrated_control": [
        SYSTEM_CONNECT, SYSTEM_SETUP, SYSTEM_CONFIG3, SYSTEM_EXIT,
        FORWARD, BACKWARD, SERVO_ANGLE_SWITCH, STICK_LEGS_CONTROL
    ]
}


# デフォルト操作プリセット
DEFAULT_OPERATION_PRESETS = {
    "basic_individual": {
        "operation_mode": "individual_control",
        "mappings": {
            SYSTEM_CONNECT: "START", SYSTEM_SETUP: "L1", SYSTEM_CONFIG3: "R1", SYSTEM_EXIT: "SELECT",
            SERVO_BATT_0: "A", SERVO_BATT_1: "B", SERVO_BATT_2: "X", SERVO_BATT_3: "Y",
            SERVO_ANGLE_SWITCH: "L_STICK", MOTOR_FORWARD: "R2", MOTOR_BACKWARD: "L2",
            STICK_LEGS_CONTROL: "LEFT_STICK"
        }
    },
    "basic_integrated": {
        "operation_mode": "integrated_control",
        "mappings": {
            SYSTEM_CONNECT: "START", SYSTEM_SETUP: "L1", SYSTEM_CONFIG3: "R1", SYSTEM_EXIT: "SELECT",
            FORWARD: "R2", BACKWARD: "L2", SERVO_ANGLE_SWITCH: "L_STICK", STICK_LEGS_CONTROL: "LEFT_STICK"
        }
    }
}

# 後方互換性のためのデフォルトマッピング
DEFAULT_MAPPINGS = {
    "individual_control": DEFAULT_OPERATION_PRESETS["basic_individual"]["mappings"],
    "integrated_control": DEFAULT_OPERATION_PRESETS["basic_integrated"]["mappings"]
}


# 機能名マッピング
FUNCTION_MAP = {
    "system_connect": SYSTEM_CONNECT, "system_setup": SYSTEM_SETUP,
    "system_config3": SYSTEM_CONFIG3, "system_exit": SYSTEM_EXIT,
    "servo_batt_0": SERVO_BATT_0, "servo_batt_1": SERVO_BATT_1,
    "servo_batt_2": SERVO_BATT_2, "servo_batt_3": SERVO_BATT_3,
    "servo_angle_switch": SERVO_ANGLE_SWITCH, "motor_forward": MOTOR_FORWARD,
    "motor_backward": MOTOR_BACKWARD, "stick_legs_control": STICK_LEGS_CONTROL,
    "forward": FORWARD, "backward": BACKWARD
}


class KeyMappingManager:
    """キーマッピング管理クラス"""
    
    def __init__(self, config_path: str, controller: Controller):
        self.config_path = config_path
        self.controller = controller
        self.current_operation_mode = "individual_control"
        self.current_mappings: Dict[FunctionId, str] = {}
        self.available_presets: Dict[str, dict] = {}
        self.custom_presets_path = os.path.join(os.path.dirname(config_path), "presets", "custom_presets.yaml")
        self._load_config()
    
    def _load_config(self) -> None:
        """設定を読み込む"""
        # 利用可能なプリセットを初期化
        self._load_available_presets()
        
        # デフォルト設定で初期化
        self.current_operation_mode = "individual_control"
        self.current_mappings = DEFAULT_MAPPINGS[self.current_operation_mode].copy()
        
        # ファイル存在チェック
        if not os.path.exists(self.config_path):
            print(f"⚠️ キーマッピング警告: 設定ファイル '{self.config_path}' が見つかりません。デフォルト設定を使用します。")
            return
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config_data = yaml.safe_load(f)
                
            # YAMLが空またはNoneの場合
            if config_data is None:
                print(f"⚠️ キーマッピング警告: 設定ファイル '{self.config_path}' が空です。デフォルト設定を使用します。")
                return
                
        except yaml.YAMLError as e:
            print(f"⚠️ キーマッピングエラー: 設定ファイル '{self.config_path}' のYAML構文が無効です。")
            print(f"   エラー詳細: {e}")
            print("   デフォルト設定を使用します。")
            return
            
        except FileNotFoundError:
            print(f"⚠️ キーマッピング警告: 設定ファイル '{self.config_path}' が見つかりません。デフォルト設定を使用します。")
            return
            
        except PermissionError:
            print(f"⚠️ キーマッピングエラー: 設定ファイル '{self.config_path}' の読み込み権限がありません。デフォルト設定を使用します。")
            return
            
        except Exception as e:
            print(f"⚠️ キーマッピングエラー: 設定ファイル '{self.config_path}' の読み込み中に予期しないエラーが発生しました。")
            print(f"   エラー詳細: {e}")
            print("   デフォルト設定を使用します。")
            return
        
        # 設定の適用
        self._apply_config(config_data)
    
    def _load_available_presets(self) -> None:
        """利用可能なプリセットを読み込む"""
        # デフォルトプリセットを追加
        self.available_presets = DEFAULT_OPERATION_PRESETS.copy()
        
        # カスタムプリセットファイルを読み込み
        if os.path.exists(self.custom_presets_path):
            try:
                with open(self.custom_presets_path, 'r', encoding='utf-8') as f:
                    custom_data = yaml.safe_load(f)
                
                if custom_data and 'custom_operation_presets' in custom_data:
                    custom_presets = custom_data['custom_operation_presets']
                    if isinstance(custom_presets, dict):
                        # カスタムプリセットを追加（デフォルトプリセットを上書きしない）
                        for preset_name, preset_config in custom_presets.items():
                            if preset_name not in self.available_presets:
                                self.available_presets[preset_name] = preset_config
                            else:
                                print(f"⚠️ キーマッピング警告: カスタムプリセット '{preset_name}' はデフォルトプリセットと同名のため無視されます。")
                    else:
                        print(f"⚠️ キーマッピング警告: カスタムプリセットファイル '{self.custom_presets_path}' の形式が無効です。")
                        
            except yaml.YAMLError as e:
                print(f"⚠️ キーマッピングエラー: カスタムプリセットファイル '{self.custom_presets_path}' のYAML構文が無効です。")
                print(f"   エラー詳細: {e}")
            except Exception as e:
                print(f"⚠️ キーマッピングエラー: カスタムプリセットファイル '{self.custom_presets_path}' の読み込み中にエラーが発生しました。")
                print(f"   エラー詳細: {e}")

    def _apply_config(self, config_data: dict) -> None:
        """設定データを適用する"""
        key_mapping_config = config_data.get('key_mapping', {})
        
        # key_mappingセクションが存在しない場合の警告
        if not key_mapping_config:
            print("⚠️ キーマッピング警告: 設定ファイルに'key_mapping'セクションが見つかりません。デフォルト設定を使用します。")
            return
        
        # プリセットベースの設定を適用
        preset_name = key_mapping_config.get('operation_preset')
        if preset_name:
            self._apply_preset(preset_name)
        else:
            # 後方互換性: operation_modeが直接指定されている場合
            operation_mode = key_mapping_config.get('operation_mode', 'individual_control')
            if operation_mode not in OPERATION_MODES:
                print(f"⚠️ キーマッピング警告: 操作モード '{operation_mode}' は存在しません。'individual_control'を使用します。")
                operation_mode = 'individual_control'
            
            self.current_operation_mode = operation_mode
            self.current_mappings = DEFAULT_MAPPINGS[self.current_operation_mode].copy()
        
        # オーバーライドマッピングを適用
        override_mappings = key_mapping_config.get('override_mappings', {})
        self._apply_override_mappings(override_mappings)
    
    def _apply_preset(self, preset_name: str) -> None:
        """プリセットを適用する"""
        if preset_name not in self.available_presets:
            available_presets = list(self.available_presets.keys())
            print(f"⚠️ キーマッピングエラー: プリセット '{preset_name}' が見つかりません。")
            print(f"   利用可能なプリセット: {', '.join(available_presets)}")
            print(f"   デフォルトプリセット 'basic_individual' を使用します。")
            preset_name = "basic_individual"
        
        preset_config = self.available_presets[preset_name]
        
        # プリセットの構造を検証
        if not isinstance(preset_config, dict):
            print(f"⚠️ キーマッピングエラー: プリセット '{preset_name}' の設定が無効です。デフォルトプリセット 'basic_individual' を使用します。")
            preset_config = self.available_presets["basic_individual"]
        
        # 操作モードを設定
        operation_mode = preset_config.get('operation_mode', 'individual_control')
        if operation_mode not in OPERATION_MODES:
            print(f"⚠️ キーマッピング警告: プリセット '{preset_name}' の操作モード '{operation_mode}' は存在しません。'individual_control'を使用します。")
            operation_mode = 'individual_control'
        
        self.current_operation_mode = operation_mode
        
        # マッピングを設定
        preset_mappings = preset_config.get('mappings', {})
        if not isinstance(preset_mappings, dict):
            print(f"⚠️ キーマッピング警告: プリセット '{preset_name}' のマッピング設定が無効です。デフォルトマッピングを使用します。")
            self.current_mappings = DEFAULT_MAPPINGS[self.current_operation_mode].copy()
        else:
            # デフォルトマッピングから開始
            self.current_mappings = DEFAULT_MAPPINGS[self.current_operation_mode].copy()
            
            # プリセットのマッピングを適用
            for function_id, button_name in preset_mappings.items():
                if function_id in self.current_mappings:
                    if self._is_valid_button_name(button_name):
                        self.current_mappings[function_id] = button_name
                    else:
                        default_button = DEFAULT_MAPPINGS[self.current_operation_mode].get(function_id, "不明")
                        print(f"⚠️ キーマッピング警告: プリセット '{preset_name}' のボタン '{button_name}' は存在しません。機能 '{function_id}' にはデフォルトの '{default_button}' を使用します。")

    def _apply_override_mappings(self, override_mappings: dict) -> None:
        """オーバーライドマッピングを適用する"""
        if not isinstance(override_mappings, dict):
            print("⚠️ キーマッピング警告: override_mappingsの形式が無効です。オーバーライド設定をスキップします。")
            return
            
        for function_name, button_name in override_mappings.items():
            if not isinstance(function_name, str) or not isinstance(button_name, str):
                print(f"⚠️ キーマッピング警告: 無効なオーバーライド設定をスキップします: {function_name} -> {button_name}")
                continue
                
            function_id = FUNCTION_MAP.get(function_name)
            
            if function_id is None:
                available_functions = list(FUNCTION_MAP.keys())
                print(f"⚠️ キーマッピングエラー: 機能名 '{function_name}' は存在しません。")
                print(f"   利用可能な機能名: {', '.join(available_functions[:5])}{'...' if len(available_functions) > 5 else ''}")
                print("   この設定をスキップします。")
                continue
            
            if not self.is_function_available(function_id):
                available_functions = [f.name for f in OPERATION_MODES[self.current_operation_mode]]
                print(f"⚠️ キーマッピングエラー: 機能 '{function_name}' は現在の操作モード '{self.current_operation_mode}' では利用できません。")
                print(f"   利用可能な機能: {', '.join(available_functions[:5])}{'...' if len(available_functions) > 5 else ''}")
                print("   この設定をスキップします。")
                continue
            
            # ボタン名の検証
            if not self._is_valid_button_name(button_name):
                default_button = self.current_mappings.get(function_id, "不明")
                available_buttons = self._get_available_button_names()
                print(f"⚠️ キーマッピングエラー: ボタン '{button_name}' は存在しません。")
                print(f"   利用可能なボタン: {', '.join(available_buttons[:8])}{'...' if len(available_buttons) > 8 else ''}")
                print(f"   機能 '{function_name}' にはデフォルトの '{default_button}' を使用します。")
                continue
            
            self.current_mappings[function_id] = button_name
    
    def _is_valid_button_name(self, button_name: str) -> bool:
        """ボタン名が有効かどうかをチェック"""
        try:
            getattr(Button, button_name)
            return True
        except AttributeError:
            return False
    
    def _get_available_button_names(self) -> list:
        """利用可能なボタン名のリストを取得"""
        return [name for name in dir(Button) if not name.startswith('_') and isinstance(getattr(Button, name), Button)]
    
    def _button_name_to_button(self, button_name: str) -> Optional[Button]:
        """ボタン名をButtonオブジェクトに変換"""
        try:
            return getattr(Button, button_name)
        except AttributeError:
            # 実行時にボタン名が無効な場合の警告（設定読み込み時にチェック済みだが念のため）
            print(f"⚠️ キーマッピング実行時警告: ボタン '{button_name}' は存在しません。")
            return None
    
    def get_current_operation_mode(self) -> str:
        """現在の操作モードを取得"""
        return self.current_operation_mode
    
    def is_function_available(self, function_id: FunctionId) -> bool:
        """現在の操作モードで指定された機能が利用可能かチェック"""
        return function_id in OPERATION_MODES[self.current_operation_mode]
    
    def get_button_for_function(self, function_id: FunctionId) -> Optional[Button]:
        """機能IDに対応するButtonオブジェクトを取得"""
        if not self.is_function_available(function_id):
            return None
        
        button_name = self.current_mappings.get(function_id)
        if button_name is None:
            return None
        
        return self._button_name_to_button(button_name)
    
    def is_function_pressed(self, function_id: FunctionId) -> bool:
        """機能が現在押されているかチェック"""
        if not self.is_function_available(function_id):
            return False
        
        button = self.get_button_for_function(function_id)
        if button is None:
            return False
        
        return self.controller.is_button_pressed(button)
    
    def is_function_pushed(self, function_id: FunctionId) -> bool:
        """機能が押され始めたかチェック"""
        if not self.is_function_available(function_id):
            return False
        
        button = self.get_button_for_function(function_id)
        if button is None:
            return False
        
        return self.controller.pushed_button(button)
    
    def get_analog_value(self, function_id: FunctionId) -> float:
        """機能に対応するアナログ値を取得（R2/L2用）"""
        if not self.is_function_available(function_id):
            return 0.0
        
        button_name = self.current_mappings.get(function_id)
        if button_name is None:
            return 0.0
        
        # R2/L2の場合はアナログ値を取得
        if button_name == "R2":
            return self.controller.r2_push()
        elif button_name == "L2":
            return self.controller.l2_push()
        else:
            # その他のボタンの場合はデジタル値（0.0 or 1.0）
            button = self._button_name_to_button(button_name)
            if button is not None:
                return 1.0 if self.controller.is_button_pressed(button) else 0.0
            return 0.0
    
    def get_available_presets(self) -> list:
        """利用可能なプリセット名のリストを取得"""
        return list(self.available_presets.keys())
    
    def get_available_functions(self) -> list:
        """現在の操作モードで利用可能な機能名のリストを取得"""
        return [f.name for f in OPERATION_MODES[self.current_operation_mode]]
    
    def reload_config(self) -> None:
        """設定を再読み込み"""
        self._load_config()