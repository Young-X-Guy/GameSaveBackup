# 游戏存档备份工具

一个美观的图形界面应用程序，用于自动和手动备份游戏存档。支持定时自动备份、热键操作和配置持久化。

## 功能特性

- 🎨 **美观的图形界面** - 使用PyQt6构建的现代化UI
- ⏰ **自动备份** - 可配置时间间隔的自动备份功能
- ⌨️ **热键支持** - F2键手动备份，F3键恢复最新备份
- 💾 **配置持久化** - 所有设置保存到JSON配置文件
- 📁 **目录选择** - 支持选择游戏存档目录和备份目录
- 📋 **备份历史** - 查看和管理备份历史记录
- 🔄 **一键恢复** - 快速恢复到最新的备份版本

## 系统要求

- Python 3.13+
- Windows 10/11
- 管理员权限（用于全局热键注册）

## 安装和使用

### 1. 使用uv安装依赖

```bash
# 创建虚拟环境并安装依赖
uv venv .venv
uv pip install -e .
```

### 2. 运行程序

```bash
# 激活虚拟环境 (Windows)
.venv\Scripts\activate

# 运行程序
python main.py
```

### 3. 配置程序

1. 启动程序后，点击"浏览"按钮选择游戏存档目录
2. 选择备份保存目录
3. 设置自动备份间隔（分钟）
4. 启用/禁用自动备份功能
5. 点击"保存设置"保存配置

### 4. 使用热键

- **F2键**: 立即创建备份
- **F3键**: 恢复最新备份

## 界面介绍

### 备份设置选项卡

- **目录设置**: 配置游戏存档源目录和备份保存目录
- **备份设置**: 设置自动备份间隔和启用状态
- **手动操作**: 立即备份和恢复按钮
- **状态信息**: 显示最后备份时间和当前状态

### 备份历史选项卡

- 显示所有备份的历史记录
- 按时间倒序排列，显示最近10个备份
- 支持刷新历史记录

## 配置文件

程序会在运行目录下创建 `config.json` 文件，包含以下配置：

```json
{
  "source_directory": "C:/Users/Player/Documents/GameSaves",
  "backup_directory": "D:/GameBackups",
  "backup_interval_minutes": 30,
  "auto_backup_enabled": true,
  "last_backup_time": "2024-05-16 14:30:00",
  "created_date": "2024-05-16"
}
```

## 备份命名规则

备份文件夹使用以下格式命名：
- `backup_YYYY-MM-DD_HH-MM-SS`
- 例如：`backup_2024-05-16_14-30-00`

## 打包为可执行文件

### 方法1: 使用打包脚本（推荐）
```bash
# 方法1a: 运行Python打包脚本
uv run python build_exe.py

# 方法1b: 使用批处理文件（Windows）
run.bat
```

### 方法2: 手动打包
```bash
# 安装PyInstaller
uv pip install pyinstaller

# 打包程序
pyinstaller --onefile --windowed --name=GameSaveBackup main.py

# 生成的可执行文件
dist/GameSaveBackup.exe
```

### 打包结果
- **文件大小**: ~36 MB
- **输出位置**: `dist/GameSaveBackup.exe`
- **依赖**: 无需Python环境，独立运行

### 分发说明
打包完成后，只需分发 `dist/GameSaveBackup.exe` 文件即可。用户可以直接双击运行，无需安装Python或任何其他依赖。

### 打包脚本功能
- ✅ 自动安装PyInstaller（如果未安装）
- ✅ 清理旧的打包文件
- ✅ 详细的打包进度提示
- ✅ 错误处理和用户反馈
- ✅ 打包结果统计
- ✅ 使用说明

## 项目结构

```
game-save-backup/
├── main.py                 # 程序入口
├── ui_main.py             # 主界面
├── config_manager.py       # 配置管理
├── backup_manager.py       # 备份管理
├── hotkey_manager.py       # 热键管理
├── demo_setup.py          # 演示设置脚本
├── build_exe.py           # 打包脚本
├── config.json            # 配置文件
├── pyproject.toml         # 项目配置
├── setup.py               # 安装配置
├── run.bat                # 运行批处理文件
└── README.md              # 说明文档
```

## 常见问题

### Q: 热键不起作用？
A: 确保程序以管理员权限运行，某些安全软件可能会阻止全局热键注册。

### Q: 备份失败怎么办？
A: 检查源目录和备份目录的权限，确保有足够的磁盘空间。

### Q: 如何恢复特定时间的备份？
A: 目前只支持恢复到最新备份。可以手动从备份目录中选择特定时间的备份文件夹进行恢复。

## 开发计划

- [ ] 添加云备份支持
- [ ] 支持备份压缩
- [ ] 多游戏配置支持
- [ ] 备份历史管理（删除旧备份）
- [ ] 邮件通知功能
- [ ] 备份验证功能

## 许可证

MIT License

## 作者

Young-X-Guy