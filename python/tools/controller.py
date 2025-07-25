import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "1"
import pygame
import math
from enum import IntEnum

# class Button(IntEnum):
#     A = 0
#     B = 1
#     X = 2
#     Y = 3
#     SELECT = 4
#     HOME = 5
#     START = 6
#     L_STICK = 7 # 左スティック押し込み
#     R_STICK = 8 # 右スティック押し込み
#     L1 = 9
#     R1 = 10
#     UP = 11
#     DOWN = 12
#     LEFT = 13
#     RIGHT = 14
#     L2 = 15
#     R2 = 16

# class Button(IntEnum):
#     A = 1
#     B = 2
#     X = 0
#     Y = 3
#     L1 = 4
#     R1 = 5
#     SELECT = 8
#     START = 9  # 左スティック押し込み
#     L_STICK = 10  # 右スティック押し込み
#     R_STICK = 11
#     HOME = 12 # 以下なし
#     UP = 13 
#     DOWN = 14
#     LEFT = 15
#     RIGHT = 16
#     L2 = 6  
#     R2 = 7  

class Button(IntEnum):  # PS4コントローラー
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

class Controller:
    def __init__(self, joystick_id=0):
        pygame.init()
        pygame.joystick.init()

        if pygame.joystick.get_count() == 0:
            raise RuntimeError("ジョイスティックが接続されていません。")

        self.joystick = pygame.joystick.Joystick(joystick_id)
        self.joystick.init()

        # アナログ軸の数をチェック
        if self.joystick.get_numaxes() < 6:
            raise RuntimeError(f"コントローラーの設定エラー: アナログ軸が不足しています。必要: 6軸、検出: {self.joystick.get_numaxes()}軸")

        self.button_states = [False] * (self.joystick.get_numbuttons() + 2)  # L2, R2を含むため+2

    def update(self):
        # イベント処理（押し始めを検出するため）
        pygame.event.pump()

    def get_angle(self):
        """
        左スティックの角度（ラジアン）と大きさを取得。
        角度は右方向を0、上方向がπ/2。
        """
        x = self.joystick.get_axis(0)
        y = -self.joystick.get_axis(1)  # y軸は上下逆になるため反転

        magnitude = math.hypot(x, y)
        angle = math.atan2(y, x) if magnitude > 0.1 else 0.0  # デッドゾーン処理
        angle = math.degrees(angle)  # ラジアンから度に変換
        return angle, magnitude

    def r2_push(self) -> float:
        """
        R2ボタン（軸5）の押し込み具合を取得。
        戻り値: 0.0（未押下）～ 1.0（最大押下）
        """
        raw_value = self.joystick.get_axis(5)
        # 軸5の値を0~1の範囲に変換（通常-1~1の範囲なので正規化）
        normalized_value = (raw_value + 1.0) / 2.0
        # 0~1の範囲にクランプ
        return max(0.0, min(1.0, normalized_value))

    def pushed_button(self, button_id: int) -> bool:
        """
        ボタンが「押され始めた」かどうかを検出。
        """
        if button_id < 0 or button_id >= len(self.button_states):
            raise ValueError(f"無効なボタンID: {button_id}")
        if button_id == 15 or button_id == 16:
            current_state = self.joystick.get_axis(button_id - 11) > 0.1  # L2, R2はアナログ入力
        else:current_state = self.joystick.get_button(button_id)
        was_pressed = self.button_states[button_id]
        self.button_states[button_id] = current_state

        return current_state and not was_pressed

    def is_button_pressed(self, button_id: int) -> bool:
        """
        ボタンが現在押されているかどうかを取得。
        """
        if button_id < 0 or button_id >= self.joystick.get_numbuttons():
            raise ValueError(f"無効なボタンID: {button_id}")
        return self.joystick.get_button(button_id)
