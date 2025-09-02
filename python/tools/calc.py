import math
from tools.data_manager import DataManager

class Calc:
    fixed_twist = 0
    batt_servo_data = None

    @staticmethod
    def init(batt_servo_data : DataManager):
        Calc.batt_servo_data = batt_servo_data
        return


    @staticmethod
    def legs_power(twist, controller_angle, controller_magnitude, fix_mode):
        if fix_mode==0:
            Calc.fixed_twist = twist
        twist = Calc.fixed_twist

        # ここに脚部のパワー計算ロジックを実装
        controller_angle1 = controller_angle - twist - 45
        ver_power1 = math.sin(math.radians(controller_angle1)) * 180 * controller_magnitude
        hor_power1 = math.cos(math.radians(controller_angle1)) * 180 * controller_magnitude

        controller_angle2 = controller_angle - twist + 45
        ver_power2 = math.sin(math.radians(controller_angle2)) * 180 * controller_magnitude
        hor_power2 = math.cos(math.radians(controller_angle2)) * 180 * controller_magnitude

        up_value = int(ver_power1) if ver_power1 > 0 else 0
        down_value = int(-ver_power1) if ver_power1 < 0 else 0
        left_value = int(-hor_power1) if hor_power1 < 0 else 0
        right_value = int(hor_power1) if hor_power1 > 0 else 0

        up_value += int(ver_power2) if ver_power2 > 0 else 0
        down_value += int(-ver_power2) if ver_power2 < 0 else 0
        left_value += int(-hor_power2) if hor_power2 < 0 else 0
        right_value += int(hor_power2) if hor_power2 > 0 else 0

        up_value = max(0, min(180, up_value))
        down_value = max(0, min(180, down_value))
        left_value = max(0, min(180, left_value))
        right_value = max(0, min(180, right_value))

        return up_value, down_value, left_value, right_value
    
    @staticmethod
    def barast_power(twist, button_num, individual_mode):
        air_angle = 5    # 押し込み時の角度
        water_angle = 175  # 離し時の角度
        batt_servo_values = [air_angle] * 4  # デフォルト位置で初期化


        if individual_mode:  # L1押し込み時
            batt_servo_values[button_num] = water_angle
            Calc.batt_servo_data.update(batt_servo_values)
            return

            
        rd_barast = ld_barast = ru_barast = lu_barast = air_angle

        if button_num == 0:  # Aボタンでバッテリーサーボ0番制御
            rd_barast = ld_barast = water_angle
            ru_barast = lu_barast = air_angle
        
        if button_num == 1:  # Bボタンでバッテリーサーボ1番制御
            rd_barast = ru_barast = water_angle
            ld_barast = lu_barast = air_angle

        if button_num == 2:  # Yボタンでバッテリーサーボ2番制御
            rd_barast = ld_barast = ru_barast = lu_barast = air_angle

        if button_num == 3:  # Xボタンでバッテリーサーボ3番制御
            rd_barast = ru_barast = air_angle
            ld_barast = lu_barast = water_angle

        # twistの値に基づいてdarastを割り当て
        if -45 <= twist < 45:  # 前方向 (0度付近)
            batt_servo_values[0] = lu_barast
            batt_servo_values[1] = ld_barast # rd ld
            batt_servo_values[2] = rd_barast # rd ld
            batt_servo_values[3] = ru_barast
        elif 45 <= twist < 135:  # 右方向 (90度付近)
            batt_servo_values[0] = ld_barast
            batt_servo_values[1] = rd_barast
            batt_servo_values[2] = ru_barast
            batt_servo_values[3] = lu_barast
        elif 135 <= twist <= 180 or -180 <= twist < -135:  # 後方向 (180度付近)
            batt_servo_values[0] = rd_barast
            batt_servo_values[1] = ru_barast
            batt_servo_values[2] = lu_barast
            batt_servo_values[3] = ld_barast
        else:  # -135 <= twist < -45: 左方向 (-90度付近)
            batt_servo_values[0] = ru_barast
            batt_servo_values[1] = lu_barast
            batt_servo_values[2] = ld_barast
            batt_servo_values[3] = rd_barast

        Calc.batt_servo_data.update(batt_servo_values)
