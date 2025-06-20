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

    # スティックの値を取得（例：左スティックX/Y軸）
    axis_x = joystick.get_axis(0)
    axis_y = joystick.get_axis(1)

    # スティックの状態を表示
    print(f"スティック: X={axis_x:.2f}, Y={axis_y:.2f}")

    # ボタンが押されたかを確認（例：全ボタンを確認）
    for button_index in range(joystick.get_numbuttons()):
        if joystick.get_button(button_index):
            print("helloworld")

    pygame.time.wait(100)  # CPU負荷軽減のため100ms待つ
