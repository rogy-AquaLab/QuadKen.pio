import pygame

# 初期化
pygame.init()
pygame.joystick.init()

# ジョイスティック接続確認
if pygame.joystick.get_count() == 0:
    print("ジョイスティックが接続されていません。")
    exit()

joystick = pygame.joystick.Joystick(0)
joystick.init()

print(f"接続中のジョイスティック: {joystick.get_name()}")

# メインループ
while True:
    pygame.event.pump()

    # 全ての軸の値を取得
    axes = []
    for axis_index in range(joystick.get_numaxes()):
        axis_value = joystick.get_axis(axis_index)
        axes.append(axis_value)

    # 全ての軸の状態を表示
    axes_str = ", ".join([f"軸{i}={axes[i]:.2f}" for i in range(len(axes))])
    print(f"全スティック: {axes_str}")

    # ボタンが押されたかを確認（例：全ボタンを確認）
    for button_index in range(joystick.get_numbuttons()):
        if joystick.get_button(button_index):
            print(f"ボタン {button_index} が押されました")

    pygame.time.wait(100)  # CPU負荷軽減のため100ms待つ
