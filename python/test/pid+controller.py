import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from simple_pid import PID
import pygame
import threading
import time

# 初期値
current_value = 0.0
setpoint = 0.0
values = []
times = []
start_time = time.time()

# PID初期化
pid = PID(Kp=5.0, Ki=2, Kd=0.0, setpoint=setpoint)
pid.sample_time = 0.1

# pygame初期化とコントローラー接続
pygame.init()
pygame.joystick.init()

if pygame.joystick.get_count() == 0:
    print("コントローラーが接続されていません。")
    exit()

joystick = pygame.joystick.Joystick(0)
joystick.init()
print(f"コントローラー名: {joystick.get_name()}")

# スティックから目標値を更新するスレッド
def joystick_thread():
    global setpoint, pid
    while True:
        pygame.event.pump()  # イベントキューを更新
        axis_val = joystick.get_axis(1)  # 左スティックの上下（-1:上, 1:下）
        setpoint = axis_val * -10  # 感度調整
        setpoint = max(-50, min(50, setpoint))  # 範囲制限
        pid.setpoint = setpoint
        time.sleep(0.1)

threading.Thread(target=joystick_thread, daemon=True).start()

# グラフ描画準備
fig, ax = plt.subplots()
line_actual, = ax.plot([], [], label='Current Value')
line_setpoint, = ax.plot([], [], '--', label='Setpoint')
ax.set_xlim(0, 10)
ax.set_ylim(-10, 20)
ax.set_xlabel('Time (s)')
ax.set_ylabel('Value')
ax.set_title('Real-time PID Control')
ax.legend()
ax.grid(True)

# アニメーション更新関数
def update(frame):
    global current_value
    now = time.time()
    elapsed = now - start_time

    output = pid(current_value)
    current_value += output * 0.1  # 簡単なモデル

    values.append(current_value)
    times.append(elapsed)

    # グラフ更新
    line_actual.set_data(times, values)
    line_setpoint.set_data(times, [setpoint] * len(times))

    ax.set_xlim(max(0, elapsed - 10), elapsed + 1)
    ax.set_ylim(min(values[-100:]) - 5, max(values[-100:]) + 5)

    return line_actual, line_setpoint

# アニメーション開始
ani = FuncAnimation(fig, update, interval=100)
plt.show()
