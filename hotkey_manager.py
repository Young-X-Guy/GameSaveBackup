import keyboard
import threading
from typing import Callable


class HotkeyManager:
    """热键管理器，负责注册和处理全局热键"""

    def __init__(self):
        self.f2_callback = None
        self.f3_callback = None
        self.is_running = False

    def register_f2_backup(self, callback: Callable):
        """注册F2备份热键"""
        self.f2_callback = callback
        keyboard.unhook_all()  # 清除之前的热键
        self._register_hotkeys()

    def register_f3_restore(self, callback: Callable):
        """注册F3恢复热键"""
        self.f3_callback = callback
        keyboard.unhook_all()  # 清除之前的热键
        self._register_hotkeys()

    def _register_hotkeys(self):
        """注册所有热键"""
        if self.f2_callback:
            keyboard.add_hotkey('f2', self._on_f2_pressed)

        if self.f3_callback:
            keyboard.add_hotkey('f3', self._on_f3_pressed)

    def _on_f2_pressed(self):
        """F2热键回调"""
        try:
            if self.f2_callback:
                # 在新线程中执行，避免阻塞热键监听
                thread = threading.Thread(target=self.f2_callback, daemon=True)
                thread.start()
        except Exception as e:
            print(f"F2热键执行失败: {e}")

    def _on_f3_pressed(self):
        """F3热键回调"""
        try:
            if self.f3_callback:
                # 在新线程中执行，避免阻塞热键监听
                thread = threading.Thread(target=self.f3_callback, daemon=True)
                thread.start()
        except Exception as e:
            print(f"F3热键执行失败: {e}")

    def start_listening(self):
        """开始监听热键（非阻塞）"""
        if not self.is_running:
            self.is_running = True

    def stop_listening(self):
        """停止监听热键"""
        keyboard.unhook_all()
        self.is_running = False

    def is_listening(self) -> bool:
        """检查是否正在监听热键"""
        return self.is_running