import os
import sys
import threading
from datetime import datetime
from typing import Optional

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit, QFileDialog, QGroupBox,
    QSpinBox, QCheckBox, QMessageBox, QStatusBar, QTabWidget,
    QComboBox
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QIcon, QFont
import winsound  # Windows提示音

from config_manager import ConfigManager
from backup_manager import BackupManager
from hotkey_manager import HotkeyManager


class GameSaveBackupUI(QMainWindow):
    """游戏存档备份主界面"""

    # 定义信号用于线程间通信
    backup_success_signal = pyqtSignal(str)
    backup_failed_signal = pyqtSignal()
    backup_error_signal = pyqtSignal(str)
    restore_success_signal = pyqtSignal()
    restore_failed_signal = pyqtSignal()
    restore_error_signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.config_manager = ConfigManager()
        self.backup_manager = None
        self.hotkey_manager = HotkeyManager()
        self.auto_backup_timer = None

        self.init_ui()
        self.load_config()
        self.setup_signals()
        self.setup_hotkeys()
        self.start_auto_backup()

    def init_ui(self):
        """初始化用户界面"""
        self.setWindowTitle("游戏存档备份工具")
        self.setGeometry(100, 100, 600, 500)

        # 设置样式
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f2f5;
            }
            QGroupBox {
                font-weight: bold;
                border: 1px solid #d1d5db;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
            QPushButton {
                background-color: #3b82f6;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2563eb;
            }
            QPushButton:pressed {
                background-color: #1d4ed8;
            }
            QLineEdit {
                padding: 8px;
                border: 1px solid #d1d5db;
                border-radius: 6px;
                background-color: white;
            }
            QSpinBox {
                padding: 8px;
                border: 1px solid #d1d5db;
                border-radius: 6px;
                background-color: white;
            }
            QLabel {
                color: #374151;
            }
            QCheckBox {
                color: #374151;
            }
        """)

        # 创建主部件和布局
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # 创建选项卡
        tab_widget = QTabWidget()
        main_layout.addWidget(tab_widget)

        # 主功能选项卡
        main_tab = QWidget()
        tab_widget.addTab(main_tab, "备份设置")
        self.setup_main_tab(main_tab)

        # 备份历史选项卡
        history_tab = QWidget()
        tab_widget.addTab(history_tab, "备份历史")
        self.setup_history_tab(history_tab)

        # 状态栏
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.update_status("就绪")

    def setup_main_tab(self, tab):
        """设置主功能选项卡"""
        layout = QVBoxLayout(tab)

        # 游戏设置组
        game_group = QGroupBox("游戏设置")
        game_layout = QVBoxLayout()

        # 游戏名称
        game_name_layout = QHBoxLayout()
        game_name_label = QLabel("游戏名称:")
        self.game_name_edit = QLineEdit()
        self.game_name_edit.setPlaceholderText("输入游戏名称...")
        self.game_name_btn = QPushButton("切换游戏")
        self.game_name_btn.clicked.connect(self.switch_game)

        game_name_layout.addWidget(game_name_label)
        game_name_layout.addWidget(self.game_name_edit)
        game_name_layout.addWidget(self.game_name_btn)
        game_layout.addLayout(game_name_layout)

        # 游戏列表
        game_list_layout = QHBoxLayout()
        game_list_label = QLabel("游戏列表:")
        self.game_list_combo = QComboBox()
        self.game_list_combo.currentTextChanged.connect(self.on_game_selected)
        self.refresh_game_btn = QPushButton("刷新")
        self.refresh_game_btn.clicked.connect(self.refresh_game_list)

        game_list_layout.addWidget(game_list_label)
        game_list_layout.addWidget(self.game_list_combo)
        game_list_layout.addWidget(self.refresh_game_btn)
        game_layout.addLayout(game_list_layout)

        game_group.setLayout(game_layout)
        layout.addWidget(game_group)

        # 目录设置组
        dir_group = QGroupBox("目录设置")
        dir_layout = QVBoxLayout()

        # 源目录
        source_layout = QHBoxLayout()
        source_label = QLabel("游戏存档目录:")
        self.source_edit = QLineEdit()
        self.source_edit.setPlaceholderText("选择游戏存档目录...")
        source_btn = QPushButton("浏览")
        source_btn.clicked.connect(self.select_source_directory)

        source_layout.addWidget(source_label)
        source_layout.addWidget(self.source_edit)
        source_layout.addWidget(source_btn)
        dir_layout.addLayout(source_layout)

        # 备份目录
        backup_layout = QHBoxLayout()
        backup_label = QLabel("备份保存目录:")
        self.backup_edit = QLineEdit()
        self.backup_edit.setPlaceholderText("选择备份保存目录...")
        backup_btn = QPushButton("浏览")
        backup_btn.clicked.connect(self.select_backup_directory)

        backup_layout.addWidget(backup_label)
        backup_layout.addWidget(self.backup_edit)
        backup_layout.addWidget(backup_btn)
        dir_layout.addLayout(backup_layout)

        dir_group.setLayout(dir_layout)
        layout.addWidget(dir_group)

        # 备份设置组
        settings_group = QGroupBox("备份设置")
        settings_layout = QVBoxLayout()

        # 备份间隔
        interval_layout = QHBoxLayout()
        interval_label = QLabel("自动备份间隔(分钟):")
        self.interval_spin = QSpinBox()
        self.interval_spin.setRange(1, 1440)  # 1分钟到24小时
        self.interval_spin.setValue(30)
        interval_layout.addWidget(interval_label)
        interval_layout.addWidget(self.interval_spin)
        settings_layout.addLayout(interval_layout)

        # 自动备份开关
        self.auto_backup_check = QCheckBox("启用自动备份")
        self.auto_backup_check.setChecked(True)
        settings_layout.addWidget(self.auto_backup_check)
        self.auto_backup_check.stateChanged.connect(self.toggle_auto_backup)

        settings_group.setLayout(settings_layout)
        layout.addWidget(settings_group)

        # 操作按钮组
        button_group = QGroupBox("手动操作")
        button_layout = QHBoxLayout()

        self.backup_btn = QPushButton("立即备份 (F2)")
        self.backup_btn.clicked.connect(self.manual_backup)

        self.restore_btn = QPushButton("恢复最新备份 (F3)")
        self.restore_btn.clicked.connect(self.manual_restore)

        button_layout.addWidget(self.backup_btn)
        button_layout.addWidget(self.restore_btn)
        button_group.setLayout(button_layout)
        layout.addWidget(button_group)

        # 状态信息组
        status_group = QGroupBox("状态信息")
        status_layout = QVBoxLayout()

        self.last_backup_label = QLabel("最后备份时间: 从未备份")
        self.status_label = QLabel("当前状态: 就绪")

        status_layout.addWidget(self.last_backup_label)
        status_layout.addWidget(self.status_label)
        status_group.setLayout(status_layout)
        layout.addWidget(status_group)

        # 保存设置按钮
        self.save_btn = QPushButton("保存设置")
        self.save_btn.clicked.connect(self.save_settings)
        layout.addWidget(self.save_btn)

        layout.addStretch()

    def setup_history_tab(self, tab):
        """设置备份历史选项卡"""
        layout = QVBoxLayout(tab)

        # 备份历史列表标题
        history_title = QLabel("备份历史记录")
        history_title.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        layout.addWidget(history_title)

        # 刷新历史按钮
        refresh_btn = QPushButton("刷新历史")
        refresh_btn.clicked.connect(self.refresh_backup_history)
        layout.addWidget(refresh_btn)

        # 历史记录显示区域
        self.history_label = QLabel("暂无备份历史")
        self.history_label.setWordWrap(True)
        layout.addWidget(self.history_label)

        layout.addStretch()

    def select_source_directory(self):
        """选择源目录"""
        directory = QFileDialog.getExistingDirectory(
            self, "选择游戏存档目录", ""
        )
        if directory:
            self.source_edit.setText(directory)

    def select_backup_directory(self):
        """选择备份目录"""
        directory = QFileDialog.getExistingDirectory(
            self, "选择备份保存目录", ""
        )
        if directory:
            self.backup_edit.setText(directory)

    def load_config(self):
        """加载配置"""
        config = self.config_manager.load_config()

        self.game_name_edit.setText(config.get("game_name", "默认游戏"))
        self.source_edit.setText(config.get("source_directory", ""))
        self.backup_edit.setText(config.get("backup_directory", ""))
        self.interval_spin.setValue(config.get("backup_interval_minutes", 30))
        self.auto_backup_check.setChecked(config.get("auto_backup_enabled", True))

        last_backup = config.get("last_backup_time", "")
        if last_backup:
            self.last_backup_label.setText(f"最后备份时间: {last_backup}")

        self.refresh_game_list()
        self.update_window_title()

    def save_settings(self):
        """保存设置"""
        # 更新配置
        self.config_manager.update_config("game_name", self.game_name_edit.text())
        self.config_manager.update_config("source_directory", self.source_edit.text())
        self.config_manager.update_config("backup_directory", self.backup_edit.text())
        self.config_manager.update_config("backup_interval_minutes", self.interval_spin.value())
        self.config_manager.update_config("auto_backup_enabled", self.auto_backup_check.isChecked())

        # 更新备份管理器
        self.update_backup_manager()

        # 重启自动备份
        self.restart_auto_backup()

        self.update_status("设置已保存")
        self.update_window_title()
        self.refresh_game_list()
        QMessageBox.information(self, "成功", "设置已保存！")

    def update_backup_manager(self):
        """更新备份管理器"""
        source_dir = self.source_edit.text()
        backup_dir = self.backup_edit.text()

        if source_dir and backup_dir:
            self.backup_manager = BackupManager(source_dir, backup_dir)
        else:
            self.backup_manager = None

    def setup_signals(self):
        """设置信号连接"""
        self.backup_success_signal.connect(self._on_backup_success_and_cleanup_normal)
        self.backup_failed_signal.connect(self._on_backup_failed_and_cleanup_normal)
        self.backup_error_signal.connect(self._on_backup_error_and_cleanup_normal)
        self.restore_success_signal.connect(self._on_restore_success_and_cleanup_normal)
        self.restore_failed_signal.connect(self._on_restore_failed_and_cleanup_normal)
        self.restore_error_signal.connect(self._on_restore_error_and_cleanup_normal)

    def setup_hotkeys(self):
        """设置热键"""
        self.hotkey_manager.register_f2_backup(self._hotkey_backup_wrapper)
        self.hotkey_manager.register_f3_restore(self._hotkey_restore_wrapper)
        self.hotkey_manager.start_listening()

    def manual_backup(self):
        """手动备份"""
        # 检查是否已经在执行备份操作
        if hasattr(self, '_backup_in_progress') and self._backup_in_progress:
            return

        if not self.backup_manager:
            self.update_backup_manager()

        if not self.backup_manager:
            QMessageBox.warning(self, "错误", "请先设置源目录和备份目录")
            return

        # 验证目录
        valid, message = self.backup_manager.validate_directories()
        if not valid:
            QMessageBox.warning(self, "错误", message)
            return

        # 设置备份状态标志
        self._backup_in_progress = True

        try:
            self.update_status("正在创建备份...")

            # 在单独的线程中执行备份操作
            def backup_worker():
                try:
                    backup_path = self.backup_manager.create_backup(backup_type="manual")

                    # 使用信号在主线程中更新UI
                    if backup_path:
                        self.backup_success_signal.emit(backup_path)
                    else:
                        self.backup_failed_signal.emit()

                except Exception as e:
                    self.backup_error_signal.emit(str(e))

            # 启动备份线程
            threading.Thread(target=backup_worker, daemon=True).start()

        except Exception as e:
            self._on_backup_error(str(e))
            self._reset_backup_flag()

    def _on_backup_success(self, backup_path):
        """备份成功回调"""
        self.config_manager.update_last_backup_time()
        self.last_backup_label.setText(
            f"最后备份时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        self.update_status(f"备份成功: {os.path.basename(backup_path)}")
        self.play_sound("success")  # 播放成功提示音
        self.refresh_backup_history()

    def _on_backup_success_safe(self, backup_path):
        """备份成功回调（安全版本）"""
        self.config_manager.update_last_backup_time()
        self.last_backup_label.setText(
            f"最后备份时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        self.update_status(f"备份成功: {os.path.basename(backup_path)}")
        self.play_sound_safe("success")  # 播放成功提示音
        self.refresh_backup_history()

    def _on_backup_success_and_cleanup(self, backup_path):
        """备份成功回调并清理"""
        self._on_backup_success_safe(backup_path)
        self._reset_backup_flag()
        self._clear_hotkey_flag()

    def _on_backup_failed_and_cleanup(self):
        """备份失败回调并清理"""
        self._on_backup_failed_safe()
        self._reset_backup_flag()
        self._clear_hotkey_flag()

    def _on_backup_error_and_cleanup(self, error_msg):
        """备份错误回调并清理"""
        self._on_backup_error_safe(error_msg)
        self._reset_backup_flag()
        self._clear_hotkey_flag()

    def _on_backup_success_and_cleanup_normal(self, backup_path):
        """备份成功回调并清理（普通操作）"""
        self._on_backup_success(backup_path)
        self._reset_backup_flag()
        self._clear_hotkey_flag()

    def _on_backup_failed_and_cleanup_normal(self):
        """备份失败回调并清理（普通操作）"""
        self._on_backup_failed()
        self._reset_backup_flag()
        self._clear_hotkey_flag()

    def _on_backup_error_and_cleanup_normal(self, error_msg):
        """备份错误回调并清理（普通操作）"""
        self._on_backup_error(error_msg)
        self._reset_backup_flag()
        self._clear_hotkey_flag()

    def _on_restore_success_and_cleanup(self):
        """恢复成功回调并清理"""
        self._on_restore_success_safe()
        self._reset_restore_flag()
        self._clear_hotkey_flag()

    def _on_restore_failed_and_cleanup(self):
        """恢复失败回调并清理"""
        self._on_restore_failed_safe()
        self._reset_restore_flag()
        self._clear_hotkey_flag()

    def _on_restore_error_and_cleanup(self, error_msg):
        """恢复错误回调并清理"""
        self._on_restore_error_safe(error_msg)
        self._reset_restore_flag()
        self._clear_hotkey_flag()

    def _on_restore_success_and_cleanup_normal(self):
        """恢复成功回调并清理（普通操作）"""
        self._on_restore_success()
        self._reset_restore_flag()
        self._clear_hotkey_flag()

    def _on_restore_failed_and_cleanup_normal(self):
        """恢复失败回调并清理（普通操作）"""
        self._on_restore_failed()
        self._reset_restore_flag()
        self._clear_hotkey_flag()

    def _on_restore_error_and_cleanup_normal(self, error_msg):
        """恢复错误回调并清理（普通操作）"""
        self._on_restore_error(error_msg)
        self._reset_restore_flag()
        self._clear_hotkey_flag()

    def _on_backup_failed(self):
        """备份失败回调"""
        self.update_status("备份失败")
        self.play_sound("error")  # 播放错误提示音
        # 热键操作时不显示弹窗
        if not hasattr(self, '_hotkey_operation') or not self._hotkey_operation:
            QMessageBox.warning(self, "错误", "备份创建失败")

    def _on_backup_failed_safe(self):
        """备份失败回调（安全版本）"""
        self.update_status("备份失败")
        self.play_sound_safe("error")  # 播放错误提示音

    def _on_backup_error(self, error_msg):
        """备份错误回调"""
        self.update_status(f"备份失败: {error_msg}")
        self.play_sound("error")  # 播放错误提示音
        # 热键操作时不显示弹窗
        if not hasattr(self, '_hotkey_operation') or not self._hotkey_operation:
            QMessageBox.critical(self, "错误", f"备份时发生错误: {error_msg}")

    def _on_backup_error_safe(self, error_msg):
        """备份错误回调（安全版本）"""
        self.update_status(f"备份失败: {error_msg}")
        self.play_sound_safe("error")  # 播放错误提示音

    def _reset_backup_flag(self):
        """重置备份状态标志"""
        self._backup_in_progress = False

    def _clear_hotkey_flag(self):
        """清除热键操作标志"""
        if hasattr(self, '_hotkey_operation'):
            self._hotkey_operation = False

    def manual_restore(self):
        """手动恢复"""
        # 检查是否已经在执行恢复操作
        if hasattr(self, '_restore_in_progress') and self._restore_in_progress:
            return

        if not self.backup_manager:
            self.update_backup_manager()

        if not self.backup_manager:
            QMessageBox.warning(self, "错误", "请先设置源目录和备份目录")
            return

        # 设置恢复状态标志
        self._restore_in_progress = True

        try:
            self.update_status("正在恢复备份...")

            # 在单独的线程中执行恢复操作
            def restore_worker():
                try:
                    success = self.backup_manager.restore_latest_backup()

                    # 使用信号在主线程中更新UI
                    if success:
                        self.restore_success_signal.emit()
                    else:
                        self.restore_failed_signal.emit()

                except Exception as e:
                    self.restore_error_signal.emit(str(e))

            # 启动恢复线程
            threading.Thread(target=restore_worker, daemon=True).start()

        except Exception as e:
            self._on_restore_error(str(e))
            self._reset_restore_flag()

    def _on_restore_success(self):
        """恢复成功回调"""
        self.update_status("恢复成功")
        self.play_sound("success")  # 播放成功提示音
        # QMessageBox.information(self, "成功", "备份恢复成功！")

    def _on_restore_success_safe(self):
        """恢复成功回调（安全版本）"""
        self.update_status("恢复成功")
        self.play_sound_safe("success")  # 播放成功提示音

    def _on_restore_failed(self):
        """恢复失败回调"""
        self.update_status("恢复失败")
        self.play_sound("error")  # 播放错误提示音
        # 热键操作时不显示弹窗
        if not hasattr(self, '_hotkey_operation') or not self._hotkey_operation:
            QMessageBox.warning(self, "错误", "备份恢复失败")

    def _on_restore_failed_safe(self):
        """恢复失败回调（安全版本）"""
        self.update_status("恢复失败")
        self.play_sound_safe("error")  # 播放错误提示音

    def _on_restore_error(self, error_msg):
        """恢复错误回调"""
        self.update_status(f"恢复失败: {error_msg}")
        self.play_sound("error")  # 播放错误提示音
        # 热键操作时不显示弹窗
        if not hasattr(self, '_hotkey_operation') or not self._hotkey_operation:
            QMessageBox.critical(self, "错误", f"恢复时发生错误: {error_msg}")

    def _on_restore_error_safe(self, error_msg):
        """恢复错误回调（安全版本）"""
        self.update_status(f"恢复失败: {error_msg}")
        self.play_sound_safe("error")  # 播放错误提示音

    def _reset_restore_flag(self):
        """重置恢复状态标志"""
        self._restore_in_progress = False

    def play_sound(self, sound_type="success"):
        """播放提示音"""
        try:
            if sound_type == "success":
                # 成功提示音 - 系统Asterisk声音
                winsound.MessageBeep(winsound.MB_ICONASTERISK)
            elif sound_type == "error":
                # 错误提示音 - 系统Hand声音
                winsound.MessageBeep(winsound.MB_ICONHAND)
            elif sound_type == "warning":
                # 警告提示音 - 系统Exclamation声音
                winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
        except Exception as e:
            # 如果播放声音失败，忽略错误
            print(f"播放提示音失败: {e}")

    # def play_sound(self, sound_type="success"):
    #     """安全播放提示音（确保在主线程中）"""
    #     QTimer.singleShot(0, lambda: self.play_sound(sound_type))

    def start_auto_backup(self):
        """启动自动备份"""
        if self.auto_backup_timer:
            self.auto_backup_timer.stop()

        if self.auto_backup_check.isChecked():
            interval_ms = self.interval_spin.value() * 60 * 1000  # 转换为毫秒
            self.auto_backup_timer = QTimer()
            self.auto_backup_timer.timeout.connect(self.auto_backup)
            self.auto_backup_timer.start(interval_ms)

    def restart_auto_backup(self):
        """重启自动备份"""
        if self.auto_backup_timer:
            self.auto_backup_timer.stop()
        self.start_auto_backup()

    def toggle_auto_backup(self):
        """切换自动备份状态"""
        if self.auto_backup_check.isChecked():
            self.start_auto_backup()
            self.update_status("自动备份已启用")
        else:
            if self.auto_backup_timer:
                self.auto_backup_timer.stop()
            self.update_status("自动备份已禁用")

    def auto_backup(self):
        """自动备份"""
        if not self.backup_manager:
            self.update_backup_manager()

        if self.backup_manager:
            try:
                backup_path = self.backup_manager.create_backup(backup_type="auto")
                if backup_path:
                    self.config_manager.update_last_backup_time()
                    self.last_backup_label.setText(
                        f"最后备份时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                    )
                    self.update_status(f"自动备份完成: {os.path.basename(backup_path)}")
                    # self.play_sound("success")  # 播放成功提示音
                    self.refresh_backup_history()
            except Exception as e:
                self.update_status(f"自动备份失败: {str(e)}")
                self.play_sound("error")  # 播放错误提示音

    def refresh_backup_history(self):
        """刷新备份历史"""
        if not self.backup_manager:
            self.history_label.setText("请先设置备份目录")
            return

        try:
            backups = self.backup_manager.list_backups()
            if backups:
                history_text = "备份历史:\n\n"
                for i, backup in enumerate(backups[:10], 1):  # 只显示最近10个
                    backup_name = os.path.basename(backup)
                    ctime = datetime.fromtimestamp(os.path.getctime(backup))

                    # 区分手动和自动备份
                    if backup_name.startswith("manual_backup_"):
                        backup_type = "[手动]"
                        display_name = backup_name.replace("manual_backup_", "")
                    elif backup_name.startswith("auto_backup_"):
                        backup_type = "[自动]"
                        display_name = backup_name.replace("auto_backup_", "")
                    else:
                        backup_type = "[未知]"
                        display_name = backup_name

                    history_text += f"{i}. {backup_type} {display_name}\n   创建时间: {ctime.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                self.history_label.setText(history_text)
            else:
                self.history_label.setText("暂无备份历史")
        except Exception as e:
            self.history_label.setText(f"加载备份历史失败: {str(e)}")

    def update_status(self, message: str):
        """更新状态栏"""
        self.status_label.setText(f"当前状态: {message}")
        self.status_bar.showMessage(message, 3000)  # 显示3秒

    def _hotkey_backup_wrapper(self):
        """热键备份包装器 - 确保在主线程中执行UI操作"""
        # 使用QTimer.singleShot确保在主线程中执行
        QTimer.singleShot(0, self._execute_hotkey_backup)

    def _hotkey_restore_wrapper(self):
        """热键恢复包装器 - 确保在主线程中执行UI操作"""
        # 使用QTimer.singleShot确保在主线程中执行
        QTimer.singleShot(0, self._execute_hotkey_restore)

    def _execute_hotkey_backup(self):
        """执行热键备份操作（无弹窗版本）"""
        try:
            self._hotkey_backup_no_dialog()
        except Exception as e:
            print(f"热键备份执行失败: {e}")
            self.update_status(f"热键备份失败: {e}")
            self.play_sound("error")

    def _execute_hotkey_restore(self):
        """执行热键恢复操作（无弹窗版本）"""
        try:
            self._hotkey_restore_no_dialog()
        except Exception as e:
            print(f"热键恢复执行失败: {e}")
            self.update_status(f"热键恢复失败: {e}")
            self.play_sound("error")

    def _hotkey_backup_no_dialog(self):
        """热键备份操作（无弹窗）"""
        # 检查是否已经在执行备份操作
        if hasattr(self, '_backup_in_progress') and self._backup_in_progress:
            return

        if not self.backup_manager:
            self.update_backup_manager()

        if not self.backup_manager:
            self.update_status("错误: 请先设置源目录和备份目录")
            self.play_sound("error")
            return

        # 验证目录
        valid, message = self.backup_manager.validate_directories()
        if not valid:
            self.update_status(f"错误: {message}")
            self.play_sound("error")
            return

        # 设置热键操作标志和备份状态标志
        self._hotkey_operation = True
        self._backup_in_progress = True

        try:
            self.update_status("正在创建备份...")

            # 在单独的线程中执行备份操作
            def backup_worker():
                try:
                    backup_path = self.backup_manager.create_backup(backup_type="manual")

                    # 使用信号在主线程中更新UI
                    if backup_path:
                        self.backup_success_signal.emit(backup_path)
                    else:
                        self.backup_failed_signal.emit()

                except Exception as e:
                    self.backup_error_signal.emit(str(e))

            # 启动备份线程
            threading.Thread(target=backup_worker, daemon=True).start()

        except Exception as e:
            self._on_backup_error(str(e))
            self._reset_backup_flag()
            self._clear_hotkey_flag()

    def _hotkey_restore_no_dialog(self):
        """热键恢复操作（无弹窗）"""
        # 检查是否已经在执行恢复操作
        if hasattr(self, '_restore_in_progress') and self._restore_in_progress:
            return

        if not self.backup_manager:
            self.update_backup_manager()

        if not self.backup_manager:
            self.update_status("错误: 请先设置源目录和备份目录")
            self.play_sound("error")
            return

        # 设置热键操作标志和恢复状态标志
        self._hotkey_operation = True
        self._restore_in_progress = True

        try:
            self.update_status("正在恢复备份...")

            # 在单独的线程中执行恢复操作
            def restore_worker():
                try:
                    success = self.backup_manager.restore_latest_backup()

                    # 使用信号在主线程中更新UI
                    if success:
                        self.restore_success_signal.emit()
                    else:
                        self.restore_failed_signal.emit()

                except Exception as e:
                    self.restore_error_signal.emit(str(e))

            # 启动恢复线程
            threading.Thread(target=restore_worker, daemon=True).start()

        except Exception as e:
            self._on_restore_error(str(e))
            self._reset_restore_flag()
            self._clear_hotkey_flag()

    def switch_game(self):
        """切换游戏"""
        game_name = self.game_name_edit.text().strip()
        if not game_name:
            QMessageBox.warning(self, "错误", "请输入游戏名称")
            return

        if game_name == self.config_manager.get_config("game_name"):
            return  # 已经是当前游戏

        # 尝试切换到现有游戏
        if self.config_manager.switch_game(game_name):
            self.load_config()
            self.update_status(f"已切换到游戏: {game_name}")
        else:
            # 添加新游戏
            reply = QMessageBox.question(
                self, "新游戏",
                f"游戏 '{game_name}' 不存在，是否创建新配置？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )

            if reply == QMessageBox.StandardButton.Yes:
                if self.config_manager.add_game(game_name):
                    self.load_config()
                    self.update_status(f"已创建并切换到游戏: {game_name}")
                else:
                    QMessageBox.warning(self, "错误", "创建新游戏配置失败")

    def on_game_selected(self, game_name):
        """游戏选择变更"""
        if game_name:
            self.game_name_edit.setText(game_name)

    def refresh_game_list(self):
        """刷新游戏列表"""
        game_list = self.config_manager.get_game_list()
        current_game = self.config_manager.get_config("game_name")

        self.game_list_combo.clear()
        self.game_list_combo.addItems(game_list)

        if current_game in game_list:
            index = self.game_list_combo.findText(current_game)
            if index >= 0:
                self.game_list_combo.setCurrentIndex(index)

    def update_window_title(self):
        """更新窗口标题"""
        game_name = self.config_manager.get_config("game_name", "游戏存档备份工具")
        self.setWindowTitle(f"游戏存档备份工具 - {game_name}")

    def closeEvent(self, event):
        """窗口关闭事件"""
        self.hotkey_manager.stop_listening()
        if self.auto_backup_timer:
            self.auto_backup_timer.stop()
        event.accept()


def main():
    """主函数"""
    app = QApplication(sys.argv)
    window = GameSaveBackupUI()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()