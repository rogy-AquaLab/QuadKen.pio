import math

class Calc:
    fixed_twist = 0
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
    def barast_power(twist, button_num, default_mode):
        pass
        # if (default_mode):

    #         batt_servo_values = batt_servo_data.get()  # デフォルト位置で初期化

    # target_angle_pressed = 10    # 押し込み時の角度
    # target_angle_released = 170  # 離し時の角度

    # if l1:  # L1押し込み時
    #     batt_servo_values[num] = target_angle_pressed
    # else:  # L1離し時
    #     batt_servo_values[num] = target_angle_released

    # right_barast = left_barast = up_barast = down_barast = target_angle_pressed

    # if num == 0:  # Aボタンでバッテリーサーボ0番制御
    #     down_barast = target_angle_pressed if lstick else target_angle_released
    
    # if num == 1:  # Bボタンでバッテリーサーボ1番制御
    #     right_barast = target_angle_pressed if lstick else target_angle_released

    # if num == 2:  # Yボタンでバッテリーサーボ2番制御
    #     up_barast = target_angle_pressed if lstick else target_angle_released

    # if num == 3:  # Xボタンでバッテリーサーボ3番制御
    #     left_barast = target_angle_pressed if lstick else target_angle_released

    # # twistの値に基づいてbarastを割り当て
    # if -45 <= twist < 45:  # 前方向 (0度付近)
    #     batt_servo_values[0] = down_barast
    #     batt_servo_values[1] = right_barast
    #     batt_servo_values[2] = up_barast
    #     batt_servo_values[3] = left_barast
    # elif 45 <= twist < 135:  # 右方向 (90度付近)
    #     batt_servo_values[0] = left_barast
    #     batt_servo_values[1] = down_barast
    #     batt_servo_values[2] = right_barast
    #     batt_servo_values[3] = up_barast
    # elif 135 <= twist <= 180 or -180 <= twist < -135:  # 後方向 (180度付近)
    #     batt_servo_values[0] = up_barast
    #     batt_servo_values[1] = left_barast
    #     batt_servo_values[2] = down_barast
    #     batt_servo_values[3] = right_barast
    # else:  # -135 <= twist < -45: 左方向 (-90度付近)
    #     batt_servo_values[0] = right_barast
    #     batt_servo_values[1] = up_barast
    #     batt_servo_values[2] = left_barast
    #     batt_servo_values[3] = down_barast
