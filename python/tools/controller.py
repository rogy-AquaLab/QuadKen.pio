import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "1"
import pygame
import math
import yaml
from enum import IntEnum

# Buttonクラス定義
class ProConButton(IntEnum):
    """プロコン用ボタン定義"""
    A = 0
    B = 1
    X = 2
    Y = 3
    SELECT = 4
    HOME = 5
    START = 6
    L_STICK = 7  # 左スティック押し込み
    R_STICK = 8  # 右スティック押し込み
    L1 = 9
    R1 = 10
    UP = 11
    DOWN = 12
    LEFT = 13
    RIGHT = 14
    L2 = 15
    R2 = 16

class LogiXButton(IntEnum):
    """logiコンX用ボタン定義"""
    A = 0
    B = 1
    X = 2
    Y = 3
    L1 = 4
    R1 = 5
    SELECT = 6
    START = 7
    L_STICK = 8  # 左スティック押し込み
    R_STICK = 9  # 右スティック押し込み
    HOME = 10  # ホームボタン

class LogiDButton(IntEnum):
    """logiコンD用ボタン定義"""
    A = 1
    B = 2
    X = 0
    Y = 3
    L1 = 4
    R1 = 5
    SELECT = 8
    START = 9
    L_STICK = 10  # 左スティック押し込み
    R_STICK = 11  # 右スティック押し込み
    L2 = 6
    R2 = 7

def load_config():
    """config.yamlから設定を読み込む"""
    config_path = os.path.join(os.path.dirname(__file__), '..', 'config.yaml')
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        print(f"警告: {config_path} が見つかりません。デフォルト設定を使用します。")
        return {'controller': {'type': 'logi_x'}}
    except Exception as e:
        print(f"設定ファイル読み込みエラー: {e}。デフォルト設定を使用します。")
        return {'controller': {'type': 'logi_x'}}

def get_button_class():
    """設定に基づいて適切なButtonクラスを返す"""
    config = load_config()
    controller_type = config.get('controller', {}).get('type', 'logi_x')
    
    button_classes = {
        'pro_con': ProConButton,
        'logi_x': LogiXButton,
        'logi_d': LogiDButton
    }
    
    if controller_type not in button_classes:
        print(f"警告: 不明なコントローラータイプ '{controller_type}'。'logi_x'を使用します。")
        controller_type = 'logi_x'
    
    return button_classes[controller_type]

# 動的にButtonクラスを設定
Button = get_button_class()

class Controller:
    def __init__(self, joystick_id=0):
        pygame.init()
        pygame.joystick.init()

        if pygame.joystick.get_count() == 0:
            raise RuntimeError("ジョイスティックが接続されていません。")

        self.joystick = pygame.joystick.Joystick(joystick_id)
        self.joystick.init()
        
        # 設定を読み込み
        self.config = load_config()
        self.controller_type = self.config.get('controller', {}).get('type', 'logi_x')
        
        # コントローラータイプに応じた軸設定
        self.axis_config = self._get_axis_config()
        
        # 必要な軸数をチェック
        required_axes = self._get_required_axes()
        if self.joystick.get_numaxes() < required_axes:
            raise RuntimeError(f"コントローラーの設定エラー: アナログ軸が不足しています。必要: {required_axes}軸、検出: {self.joystick.get_numaxes()}軸")

        self.button_states = [False] * (self.joystick.get_numbuttons() + 2)  # L2, R2を含むため+2
    
    def _get_axis_config(self):
        """コントローラータイプに応じた軸設定を返す"""
        if self.controller_type == 'pro_con':
            return {
                'left_stick_x': 0,
                'left_stick_y': 1,
                'right_stick_x': 2,
                'right_stick_y': 3,
                'l2': 4,
                'r2': 5
            }
        elif self.controller_type == 'logi_x':
            return {
                'left_stick_x': 0,
                'left_stick_y': 1,
                'right_stick_x': 2,
                'right_stick_y': 3,
                'l2': 4,
                'r2': 5
            }
        elif self.controller_type == 'logi_d':
            return {
                'left_dpad_x': 0,
                'left_dpad_y': 1,
                'right_stick_x': 2,
                'right_stick_y': 3,
                'l2': None,  # logiDではL2/R2はボタン
                'r2': None
            }
        else:
            # デフォルトはlogi_x
            return {
                'left_stick_x': 0,
                'left_stick_y': 1,
                'right_stick_x': 2,
                'right_stick_y': 3,
                'l2': 4,
                'r2': 5
            }
    
    def _get_required_axes(self):
        """必要な軸数を返す"""
        if self.controller_type == 'logi_d':
            return 4  # logiDはL2/R2がボタンなので4軸
        else:
            return 6  # その他は6軸

    def update(self):
        # イベント処理（押し始めを検出するため）
        pygame.event.pump()

    def get_angle(self):
        """
        左スティック（またはD-pad）の角度（度）と大きさを取得。
        角度は右方向を0、上方向が90度。
        """
        if self.controller_type == 'logi_d':
            # logiDの場合は左十字キー
            x = self.joystick.get_axis(self.axis_config['left_dpad_x'])
            y = -self.joystick.get_axis(self.axis_config['left_dpad_y'])
        else:
            # その他の場合は左スティック
            x = self.joystick.get_axis(self.axis_config['left_stick_x'])
            y = -self.joystick.get_axis(self.axis_config['left_stick_y'])  # y軸は上下逆になるため反転

        magnitude = math.hypot(x, y)
        angle = math.atan2(y, x) if magnitude > 0.1 else 0.0  # デッドゾーン処理
        angle = math.degrees(angle)  # ラジアンから度に変換
        return angle, magnitude

    def r2_push(self) -> float:
        """
        R2ボタンの押し込み具合を取得。
        戻り値: 0.0（未押下）～ 1.0（最大押下）
        """
        if self.controller_type == 'logi_d':
            # logiDの場合はR2はボタン（デジタル入力）
            return 1.0 if self.joystick.get_button(Button.R2) else 0.0
        else:
            # その他の場合はアナログ入力
            r2_axis = self.axis_config['r2']
            if r2_axis is None:
                return 0.0
            
            raw_value = self.joystick.get_axis(r2_axis)
            # 軸の値を0~1の範囲に変換（通常-1~1の範囲なので正規化）
            normalized_value = (raw_value + 1.0) / 2.0
            # 0~1の範囲にクランプ
            return max(0.0, min(1.0, normalized_value))

    def l2_push(self) -> float:
        """
        L2ボタンの押し込み具合を取得。
        戻り値: 0.0（未押下）～ 1.0（最大押下）
        """
        if self.controller_type == 'logi_d':
            # logiDの場合はL2はボタン（デジタル入力）
            return 1.0 if self.joystick.get_button(Button.L2) else 0.0
        else:
            # その他の場合はアナログ入力
            l2_axis = self.axis_config['l2']
            if l2_axis is None:
                return 0.0
            
            raw_value = self.joystick.get_axis(l2_axis)
            # 軸の値を0~1の範囲に変換（通常-1~1の範囲なので正規化）
            normalized_value = (raw_value + 1.0) / 2.0
            # 0~1の範囲にクランプ
            return max(0.0, min(1.0, normalized_value))

    def pushed_button(self, button_id: int) -> bool:
        """
        ボタンが「押され始めた」かどうかを検出。
        """
        if button_id < 0 or button_id >= len(self.button_states):
            raise ValueError(f"無効なボタンID: {button_id}")
        
        # L2/R2の処理をコントローラータイプに応じて変更
        if self._is_analog_trigger(button_id):
            # アナログトリガーの場合
            axis_id = self._get_trigger_axis(button_id)
            if axis_id is not None:
                current_state = self.joystick.get_axis(axis_id) > 0.1
            else:
                current_state = False
        else:
            # 通常のボタンの場合
            current_state = self.joystick.get_button(button_id)
        
        was_pressed = self.button_states[button_id]
        self.button_states[button_id] = current_state

        return current_state and not was_pressed
    
    def _is_analog_trigger(self, button_id: int) -> bool:
        """ボタンIDがアナログトリガー（L2/R2）かどうかを判定"""
        if self.controller_type == 'pro_con':
            return button_id == 15 or button_id == 16  # L2, R2
        elif self.controller_type == 'logi_x':
            # logiXではL2/R2はアナログ軸だが、Buttonクラスには定義されていない
            return False
        elif self.controller_type == 'logi_d':
            return button_id == Button.L2 or button_id == Button.R2
        return False
    
    def _get_trigger_axis(self, button_id: int) -> int:
        """トリガーボタンIDに対応する軸IDを返す"""
        if self.controller_type == 'pro_con':
            if button_id == 15:  # L2
                return self.axis_config['l2']
            elif button_id == 16:  # R2
                return self.axis_config['r2']
        # logiDの場合はボタンなのでNoneを返す
        return None

    def is_button_pressed(self, button_id: int) -> bool:
        """
        ボタンが現在押されているかどうかを取得。
        """
        if button_id < 0 or button_id >= self.joystick.get_numbuttons():
            raise ValueError(f"無効なボタンID: {button_id}")
        return self.joystick.get_button(button_id)

"""
コントローラータイプ別アナログ軸情報:

プロコン (pro_con):
  左スティック X軸: 0
  左スティック Y軸: 1
  右スティック X軸: 2
  右スティック Y軸: 3
  L2: 4 (アナログ入力)
  R2: 5 (アナログ入力)

logiコンX (logi_x):
  左スティック X軸: 0
  左スティック Y軸: 1
  右スティック X軸: 2
  右スティック Y軸: 3
  L2: 4 (アナログ入力)
  R2: 5 (アナログ入力)

logiコンD (logi_d):
  左十字キー X軸: 0
  左十字キー Y軸: 1
  右スティック X軸: 2
  右スティック Y軸: 3
  L2: ボタン6 (デジタル入力)
  R2: ボタン7 (デジタル入力)
"""