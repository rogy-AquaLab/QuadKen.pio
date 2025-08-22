import math

class Calc:
    fixed_twist = 0
    @staticmethod
    def legs_power(twist, controller_angle, controller_magnitude, fix_mode):
        if fix_mode:
            twist = Calc.fixed_twist
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
    def barast_power():
        pass
