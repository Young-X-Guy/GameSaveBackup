@echo off
REM 游戏存档备份工具启动脚本

REM 激活虚拟环境
call .venv\Scripts\activate.bat

REM 运行程序
python main.py

pause