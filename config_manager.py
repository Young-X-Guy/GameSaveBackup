import json
import os
from datetime import datetime
from typing import Dict, Any


class ConfigManager:
    """配置管理器，负责读取和保存配置文件"""

    def __init__(self, config_file: str = "config.json"):
        self.config_file = config_file
        self.default_config = {
            "game_name": "默认游戏",
            "source_directory": "",
            "backup_directory": "",
            "backup_interval_minutes": 30,
            "auto_backup_enabled": True,
            "last_backup_time": "",
            "created_date": datetime.now().strftime("%Y-%m-%d")
        }
        self.config = self.default_config.copy()
        self.games_config = {}  # 存储多个游戏配置

    def load_config(self) -> Dict[str, Any]:
        """从JSON文件加载配置"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)

                # 检查是否是旧格式的配置文件
                if "games" in loaded_config:
                    # 新格式：支持多个游戏配置
                    self.games_config = loaded_config.get("games", {})
                    # 获取当前选中的游戏配置
                    current_game = loaded_config.get("current_game", "默认游戏")
                    if current_game in self.games_config:
                        self.config = {**self.default_config, **self.games_config[current_game]}
                    else:
                        self.config = self.default_config.copy()
                    self.config["game_name"] = current_game
                else:
                    # 旧格式：单个游戏配置，转换为新的多游戏格式
                    self.config = {**self.default_config, **loaded_config}
                    if "game_name" not in self.config:
                        self.config["game_name"] = "默认游戏"

                    # 保存为新的多游戏格式
                    self.games_config[self.config["game_name"]] = self.config.copy()
                    self.save_config()
            else:
                # 如果配置文件不存在，创建默认配置
                self.save_config()
        except Exception as e:
            print(f"加载配置文件时出错: {e}")
            self.config = self.default_config.copy()

        return self.config

    def save_config(self) -> bool:
        """保存配置到JSON文件"""
        try:
            # 更新当前游戏的配置
            game_name = self.config.get("game_name", "默认游戏")
            self.games_config[game_name] = self.config.copy()

            # 保存多游戏配置格式
            config_data = {
                "current_game": game_name,
                "games": self.games_config,
                "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }

            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"保存配置文件时出错: {e}")
            return False

    def update_config(self, key: str, value: Any) -> bool:
        """更新单个配置项"""
        self.config[key] = value
        return self.save_config()

    def get_config(self, key: str, default=None) -> Any:
        """获取配置值"""
        return self.config.get(key, default)

    def get_all_config(self) -> Dict[str, Any]:
        """获取所有配置"""
        return self.config.copy()

    def switch_game(self, game_name: str) -> bool:
        """切换到指定游戏的配置"""
        if game_name in self.games_config:
            self.config = {**self.default_config, **self.games_config[game_name]}
            self.config["game_name"] = game_name
            return self.save_config()
        return False

    def add_game(self, game_name: str) -> bool:
        """添加新游戏配置"""
        if game_name not in self.games_config:
            new_config = self.default_config.copy()
            new_config["game_name"] = game_name
            self.games_config[game_name] = new_config
            self.config = new_config
            return self.save_config()
        return False

    def get_game_list(self) -> list:
        """获取所有游戏列表"""
        return list(self.games_config.keys())

    def update_last_backup_time(self):
        """更新最后备份时间"""
        self.config["last_backup_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.save_config()