from setuptools import setup, find_packages

setup(
    name="game-save-backup",
    version="0.1.0",
    description="游戏存档备份软件",
    packages=find_packages(),
    py_modules=["main", "config_manager", "backup_manager", "hotkey_manager", "ui_main"],
    install_requires=[
        "PyQt6>=6.6.0",
        "keyboard>=0.13.5",
    ],
    python_requires=">=3.13",
)