#!/usr/bin/env python3
"""
演示设置脚本 - 创建测试用的目录和文件
"""

import os
import json
from datetime import datetime


def create_demo():
    """创建演示环境"""

    # 创建演示目录
    demo_source = "demo_game_saves"
    demo_backup = "demo_backups"

    # 创建源目录和示例存档文件
    os.makedirs(demo_source, exist_ok=True)

    # 创建示例游戏存档文件
    save_files = [
        "save_slot_1.dat",
        "save_slot_2.dat",
        "player_data.json",
        "settings.cfg"
    ]

    for filename in save_files:
        filepath = os.path.join(demo_source, filename)
        with open(filepath, 'w') as f:
            if filename.endswith('.json'):
                json.dump({
                    "player_name": "TestPlayer",
                    "level": 42,
                    "score": 12345,
                    "last_played": datetime.now().isoformat()
                }, f, indent=2)
            elif filename.endswith('.cfg'):
                f.write("[Game Settings]\nresolution=1920x1080\nfullscreen=true\n")
            else:
                f.write(f"Demo save data for {filename}\nCreated at {datetime.now()}\n")

    print(f"演示环境创建完成！")
    print(f"游戏存档目录: {os.path.abspath(demo_source)}")
    print(f"备份目录: {os.path.abspath(demo_backup)}")
    print(f"\n现在可以启动游戏存档备份工具进行测试了！")
    print(f"建议设置：")
    print(f"   - 源目录: {os.path.abspath(demo_source)}")
    print(f"   - 备份目录: {os.path.abspath(demo_backup)}")
    print(f"   - 备份间隔: 5分钟（演示用）")


if __name__ == "__main__":
    create_demo()