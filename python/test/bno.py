import time
from tools.bno import Bno

bno = Bno(use_crystal=True , address=0x28)  # BNO055センサの初期化
bno.connect()  # センサに接続
while True:
    try:
        euler = bno.euler()  # (heading, roll, pitch) = (ヨー, ロール, ピッチ)
        heading, roll, pitch = euler
        print(f"Heading (Yaw): {heading:.2f}°  Roll: {roll:.2f}°  Pitch: {pitch:.2f}°")
    except RuntimeError as e:
        print(e)
    time.sleep(0.1)  # 10Hz

# # I2Cバスの初期化
# i2c = busio.I2C(board.SCL, board.SDA)

# # BNO055の初期化
# sensor = adafruit_bno055.BNO055_I2C(i2c)

# # センサの安定化待ち
# time.sleep(1)

# while True:
#     euler = sensor.euler  # (heading, roll, pitch) = (ヨー, ロール, ピッチ)
#     if euler is not None:
#         heading, roll, pitch = euler
#         print(f"Heading (Yaw): {heading:.2f}°  Roll: {roll:.2f}°  Pitch: {pitch:.2f}°")
#     else:
#         print("角度情報が取得できません")
#     time.sleep(0.1)  # 10Hz
