import board
import busio
import adafruit_bno055
import math
import time

def quaternion_to_euler(w, x, y, z):
    """
    クォータニオン (w, x, y, z) からオイラー角 (roll, pitch, yaw) を算出する関数
    roll  : x軸回転
    pitch : y軸回転
    yaw   : z軸回転
    """
    # Roll (x軸回り)
    sinr_cosp = 2.0 * (w * x + y * z)
    cosr_cosp = 1.0 - 2.0 * (x * x + y * y)
    roll = math.atan2(sinr_cosp, cosr_cosp)

    # Pitch (y軸回り)
    sinp = 2.0 * (w * y - z * x)
    if abs(sinp) >= 1:
        pitch = math.copysign(math.pi / 2, sinp)  # ±90° (gimbal lock)
    else:
        pitch = math.asin(sinp)

    # Yaw (z軸回り)
    siny_cosp = 2.0 * (w * z + x * y)
    cosy_cosp = 1.0 - 2.0 * (y * y + z * z)
    yaw = math.atan2(siny_cosp, cosy_cosp)

    # ラジアン→度に変換
    return math.degrees(roll), math.degrees(pitch), math.degrees(yaw)

def main():
    # I2C初期化
    i2c = busio.I2C(board.SCL, board.SDA)
    sensor = adafruit_bno055.BNO055_I2C(i2c)
    sensor.axis_remap = (2,1,0,1,1,1)
    while True:
        quat = sensor.quaternion  # (w, x, y, z)
        if quat is not None:
            w, x, y, z = quat
            roll, pitch, yaw = quaternion_to_euler(w, x, y, z)
            print(f"Roll: {roll:.2f}, Pitch: {pitch:.2f}, Yaw: {yaw:.2f}")
        else:
            print("No quaternion data")

        time.sleep(0.1)

if __name__ == "__main__":
    main()