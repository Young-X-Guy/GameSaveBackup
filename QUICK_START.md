# 快速开始指南

## 🚀 立即开始

### 1. 创建演示环境（可选）
```bash
# 激活虚拟环境
.venv\Scripts\activate

# 创建演示用的游戏存档和备份目录
python demo_setup.py
```

### 2. 启动程序
```bash
# 方法1：使用批处理文件
run.bat

# 方法2：手动启动
.venv\Scripts\activate
python main.py
```

### 3. 配置程序
1. 点击"浏览"选择游戏存档目录（演示环境可用 `demo_game_saves`）
2. 选择备份保存目录（演示环境可用 `demo_backups`）
3. 设置备份间隔（建议演示时设为1-5分钟）
4. 点击"保存设置"

### 4. 测试功能
- 点击"立即备份"或按 **F2** 创建备份
- 查看"备份历史"选项卡
- 点击"恢复最新备份"或按 **F3** 测试恢复功能

## 📦 打包为exe文件

### 1. 使用打包脚本
```bash
build_exe.bat
```

### 2. 手动打包
```bash
# 安装PyInstaller
uv pip install pyinstaller

# 打包程序
pyinstaller --onefile --windowed --name="GameSaveBackup" main.py
```

打包完成后，`dist/GameSaveBackup.exe` 就是独立的可执行文件。

## 🔧 常见问题

### 程序无法启动
- 确保已激活虚拟环境：`.venv\Scripts\activate`
- 确保依赖已安装：`uv pip install -e .`

### 热键不起作用
- 以管理员身份运行程序
- 检查是否有其他程序占用了F2/F3键

### 备份失败
- 检查目录权限
- 确保有足够的磁盘空间
- 检查防病毒软件是否阻止了文件操作

## 📁 项目文件说明

- `main.py` - 程序入口点
- `ui_main.py` - 主界面和核心逻辑
- `config_manager.py` - 配置文件管理
- `backup_manager.py` - 备份和恢复功能
- `hotkey_manager.py` - 全局热键支持
- `run.bat` - Windows启动脚本
- `build_exe.bat` - Windows打包脚本
- `demo_setup.py` - 演示环境创建脚本

## 🎯 下一步

1. ✅ 基本功能已实现
2. 🧪 测试程序功能
3. 📦 打包为exe文件
4. 🚀 部署使用

## 📞 获取帮助

查看 `README.md` 获取完整文档，或检查 `DEVELOPMENT_PLAN.md` 了解技术细节。