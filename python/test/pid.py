import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from simple_pid import PID
import time
import threading

# 初期パラメータ
current_value = 0.0
setpoint = 10.0
values = []
times = []
start_time = time.time()

# PIDコントローラ初期化
pid = PID(Kp=10.0, Ki=1, Kd=0.05, setpoint=setpoint)
pid.sample_time = 0.1  # PID更新周期（秒）

# スレッドで目標値をユーザーから受け付ける
def input_thread():
    global setpoint, pid
    while True:
        try:
            new_setpoint = float(input("新しい目標値を入力してください: "))
            setpoint = new_setpoint
            pid.setpoint = new_setpoint
        except ValueError:
            print("数値を入力してください。")

threading.Thread(target=input_thread, daemon=True).start()

# グラフの準備
fig, ax = plt.subplots()
line_actual, = ax.plot([], [], label='Current Value')
line_setpoint, = ax.plot([], [], '--', label='Setpoint')
ax.set_xlim(0, 10)
ax.set_ylim(-10, 50)
ax.set_xlabel('Time (s)')
ax.set_ylabel('Value')
ax.set_title('Real-time PID Control')
ax.legend()
ax.grid(True)

# 制御ループ関数（アニメーション用）
def update(frame):
    global current_value

    now = time.time()
    elapsed = now - start_time

    # PIDによる出力計算
    output = pid(current_value)
    current_value += output * 0.1  # モデルへの影響度

    # データ記録
    values.append(current_value)
    times.append(elapsed)

    # グラフ更新
    line_actual.set_data(times, values)
    line_setpoint.set_data(times, [setpoint] * len(times))

    # 軸を更新
    ax.set_xlim(max(0, elapsed - 10), elapsed + 1)
    ax.set_ylim(min(values[-100:]) - 5, max(values[-100:]) + 5)

    return line_actual, line_setpoint

# アニメーション開始（100msごとに更新）
ani = FuncAnimation(fig, update, interval=100)
plt.show()
