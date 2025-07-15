import asyncio
import tkinter as tk

class Gui:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("QuadKen GUI")
        self.label = tk.Label(self.root, text="Hello, QuadKen!")
        self.label.pack()

    async def update(self):
        """メイン関数"""
        self.root.update()  # 100msごとに更新
