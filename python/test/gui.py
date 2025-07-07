import sys
import os

# tools/ のパスを追加
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import tkinter as tk
import math
from tools.controller import Controller , Button

# 初期化
try:
    controller = Controller()
except RuntimeError as e:
    print(f"⚠️ ジョイスティックの初期化に失敗: {e}")
    exit(1)

class StatusAndAngleApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ステータスと角度表示")
        self.root.geometry("500x300")
        self.root.configure(bg="black")

        # メイン表示領域
        self.main_frame = tk.Frame(root, bg="black")
        self.main_frame.pack(fill="both", expand=True)

        # 左：角度メーター
        self.canvas = tk.Canvas(self.main_frame, width=300, height=250, bg="black", highlightthickness=0)
        self.canvas.pack(side="left", padx=10, pady=10)
        self.angle_text = self.canvas.create_text(150, 220, text="", font=("Arial", 14), fill="white")

        # 右：ステータス表示
        self.status_canvas = tk.Canvas(self.main_frame, width=180, height=200, bg="black", highlightthickness=0)
        self.status_canvas.pack(side="right", padx=10, pady=10)

        self.status_labels = ["通信", "センサー", "モーター"]
        self.status_circles = []
        self.status_texts = []

        for i, name in enumerate(self.status_labels):
            y = 30 + i * 60
            circle = self.status_canvas.create_oval(20, y, 60, y + 40, fill="gray", outline="")
            text = self.status_canvas.create_text(90, y + 20, text=name, fill="white", font=("Arial", 12), anchor="w")
            self.status_circles.append(circle)
            self.status_texts.append(text)

        # 値（初期化）
        self.angle = 0
        self.status_values = [False] * 3

        self.draw_all()

    def set_angle(self, angle: int):
        """角度を設定し、描画を更新"""
        self.angle = max(0, min(180, angle))  # 範囲制限
        self.draw_meter()

    def set_status(self, index: int, is_ok: bool):
        """ステータスの色を更新（0: 通信, 1: センサー, 2: モーター）"""
        if 0 <= index < len(self.status_circles):
            self.status_values[index] = is_ok
            color = "lime" if is_ok else "red"
            self.status_canvas.itemconfig(self.status_circles[index], fill=color)

    def draw_all(self):
        self.draw_meter()
        for i, is_ok in enumerate(self.status_values):
            self.set_status(i, is_ok)

    def draw_meter(self):
        self.canvas.delete("meter")

        center_x, center_y = 150, 150
        radius = 100

        # メーター円弧
        self.canvas.create_arc(
            center_x - radius, center_y - radius,
            center_x + radius, center_y + radius,
            start=0, extent=180,
            outline="white", width=2, style="arc", tag="meter"
        )

        # 目盛り
        for a in range(0, 181, 10):
            rad = math.radians(180 - a)
            x1 = center_x + (radius - 10) * math.cos(rad)
            y1 = center_y - (radius - 10) * math.sin(rad)
            x2 = center_x + radius * math.cos(rad)
            y2 = center_y - radius * math.sin(rad)
            self.canvas.create_line(x1, y1, x2, y2, fill="white", tag="meter")

        # 針
        rad = math.radians(180 - self.angle)
        x = center_x + (radius - 20) * math.cos(rad)
        y = center_y - (radius - 20) * math.sin(rad)
        self.canvas.create_line(center_x, center_y, x, y, fill="red", width=4, tag="meter")

        # 数値表示
        self.canvas.itemconfig(self.angle_text, text=f"{self.angle}°")

# ------------------------------
# テスト用コード（ランダム更新）
# ------------------------------
def main():
    if controller.pushed_button(Button.START):  # Aボタン
        app.set_status(1, True)
        root.after(10, main)  # 100msごとに更新
        return
    elif controller.pushed_button(Button.HOME):  # Bボタン
        app.set_status(1, False)
        root.after(10, main)  # 100msごとに更新
        return
    if controller.pushed_button(Button.SELECT):  # Bボタン
        for i in range(3):
            app.set_status(i, random.choice([True, False]))
        root.after(10, main)  # 100msごとに更新
        return

    # スティックの値を取得（例：左スティックX/Y軸）
    controller.update()  # コントローラーの状態を更新
    angle , magnitude = controller.get_angle()
    print(f"角度: {angle:.2f}, 大きさ: {magnitude:.2f}")
    app.set_angle(int(180-angle if angle > 0 else 0))  # 角度を整数に変換
    root.after(10, main)  # 100msごとに更新



if __name__ == "__main__":
    import random

    root = tk.Tk()
    app = StatusAndAngleApp(root)
    root.after(500, main)  # 500ms後に最初の更新を開始
    root.mainloop()
