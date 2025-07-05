import pygame
import math

class Controller:
    def __init__(self, joystick_id=0):
        pygame.init()
        pygame.joystick.init()

        if pygame.joystick.get_count() == 0:
            raise RuntimeError("ジョイスティックが接続されていません。")

        self.joystick = pygame.joystick.Joystick(joystick_id)
        self.joystick.init()

        self.button_states = [False] * self.joystick.get_numbuttons()

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

        return angle, magnitude

    def pushed_button(self, button_id):
        """
        ボタンが「押され始めた」かどうかを検出。
        """
        current_state = self.joystick.get_button(button_id)
        was_pressed = self.button_states[button_id]
        self.button_states[button_id] = current_state

        return current_state and not was_pressed
