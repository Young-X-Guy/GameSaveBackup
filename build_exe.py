#!/usr/bin/env python3
"""
游戏存档备份工具打包脚本

这个脚本可以将Python程序打包成独立的exe文件，用户无需安装Python即可运行。
"""

import os
import sys
import subprocess
import shutil


def run_command(cmd, description):
    """运行命令并处理错误"""
    print(f"执行: {description}...")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"完成: {description}")
            return True
        else:
            print(f"失败: {description}")
            print(f"错误信息: {result.stderr}")
            return False
    except Exception as e:
        print(f"异常: {description} - {e}")
        return False


def build_exe():
    """打包程序"""
    print("=" * 50)
    print("游戏存档备份工具打包脚本")
    print("=" * 50)
    print()

    # 检查PyInstaller是否安装
    try:
        import PyInstaller
        print("PyInstaller已安装")
    except ImportError:
        print("安装PyInstaller...")
        if not run_command("uv pip install pyinstaller", "安装PyInstaller"):
            return False

    # 清理旧的打包文件
    print("\n清理旧的打包文件...")
    for folder in ["build", "dist"]:
        if os.path.exists(folder):
            shutil.rmtree(folder)
            print(f"  已删除: {folder}/")

    for file in ["GameSaveBackup.spec"]:
        if os.path.exists(file):
            os.remove(file)
            print(f"  已删除: {file}")

    # 打包命令
    cmd = (
        "pyinstaller --onefile --windowed --name=\"GameSaveBackup\" "
        "--add-data \"config.json;.\" "
        "--hidden-import PyQt6 "
        "--hidden-import keyboard "
        "--hidden-import json "
        "--hidden-import os "
        "--hidden-import shutil "
        "--hidden-import threading "
        "--collect-all PyQt6 "
        "main.py"
    )

    # 执行打包
    print("\n开始打包程序...")
    print(f"命令: {cmd}")
    print("\n这可能需要几分钟时间，请耐心等待...")

    if not run_command(cmd, "打包程序"):
        return False

    # 检查输出
    exe_path = "dist/GameSaveBackup.exe"
    if os.path.exists(exe_path):
        file_size = os.path.getsize(exe_path)
        print(f"\n打包成功完成！")
        print(f"可执行文件: {exe_path}")
        print(f"文件大小: {file_size:,} 字节 ({file_size/1024/1024:.1f} MB)")
        print(f"\n使用说明:")
        print(f"  1. 将 {exe_path} 复制到任意位置")
        print(f"  2. 双击运行即可，无需Python环境")
        print(f"  3. 首次运行会自动创建配置文件")
        print(f"\n注意: 某些杀毒软件可能会误报，这是正常现象")
        return True
    else:
        print(f"\n打包失败，未找到输出文件: {exe_path}")
        return False


def main():
    """主函数"""
    print("游戏存档备份工具 - 打包脚本")
    print("将Python程序打包为独立的exe文件")
    print()

    # 询问用户确认
    response = input("是否开始打包？(y/N): ")
    if response.lower() != 'y':
        print("取消打包")
        return

    try:
        success = build_exe()
        if success:
            print(f"\n打包完成，可以分发使用了！")
            print(f"\n生成的文件位置: dist/GameSaveBackup.exe")
        else:
            print(f"\n打包失败，请检查错误信息")
            sys.exit(1)
    except KeyboardInterrupt:
        print(f"\n\n打包被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n打包过程中发生异常: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()