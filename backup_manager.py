import os
import shutil
from datetime import datetime
from typing import List, Optional


class BackupManager:
    """备份管理器，负责处理备份和恢复操作"""

    def __init__(self, source_dir: str, backup_dir: str):
        self.source_dir = source_dir
        self.backup_dir = backup_dir

    def create_backup(self) -> Optional[str]:
        """创建新的备份，返回备份路径"""
        if not self.source_dir or not os.path.exists(self.source_dir):
            raise ValueError("源目录不存在或未设置")

        if not self.backup_dir:
            raise ValueError("备份目录未设置")

        # 确保备份目录存在
        os.makedirs(self.backup_dir, exist_ok=True)

        # 创建带时间戳的备份文件夹名
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        backup_folder_name = f"backup_{timestamp}"
        backup_path = os.path.join(self.backup_dir, backup_folder_name)

        try:
            # 复制源目录到备份目录
            if os.path.isdir(self.source_dir):
                shutil.copytree(self.source_dir, backup_path, dirs_exist_ok=True)
            else:
                # 如果源是文件而不是目录
                shutil.copy2(self.source_dir, backup_path)

            return backup_path
        except Exception as e:
            print(f"创建备份时出错: {e}")
            return None

    def restore_latest_backup(self) -> bool:
        """恢复最新的备份"""
        latest_backup = self.get_latest_backup()
        if not latest_backup:
            raise ValueError("找不到可用的备份")

        if not self.source_dir:
            raise ValueError("源目录未设置")

        try:
            # 清空源目录
            if os.path.exists(self.source_dir):
                if os.path.isdir(self.source_dir):
                    # 删除目录中的所有内容但保留目录本身
                    for item in os.listdir(self.source_dir):
                        item_path = os.path.join(self.source_dir, item)
                        if os.path.isdir(item_path):
                            shutil.rmtree(item_path)
                        else:
                            os.remove(item_path)
                else:
                    os.remove(self.source_dir)

            # 恢复备份
            if os.path.isdir(latest_backup):
                shutil.copytree(latest_backup, self.source_dir, dirs_exist_ok=True)
            else:
                shutil.copy2(latest_backup, self.source_dir)

            return True
        except Exception as e:
            print(f"恢复备份时出错: {e}")
            return False

    def get_latest_backup(self) -> Optional[str]:
        """获取最新的备份路径"""
        if not os.path.exists(self.backup_dir):
            return None

        backup_folders = []
        for item in os.listdir(self.backup_dir):
            item_path = os.path.join(self.backup_dir, item)
            if os.path.isdir(item_path) and item.startswith("backup_"):
                backup_folders.append((item_path, os.path.getctime(item_path)))

        if not backup_folders:
            return None

        # 按创建时间排序，返回最新的
        backup_folders.sort(key=lambda x: x[1], reverse=True)
        return backup_folders[0][0]

    def list_backups(self) -> List[str]:
        """列出所有备份"""
        if not os.path.exists(self.backup_dir):
            return []

        backups = []
        for item in os.listdir(self.backup_dir):
            item_path = os.path.join(self.backup_dir, item)
            if os.path.isdir(item_path) and item.startswith("backup_"):
                backups.append(item_path)

        # 按创建时间排序
        backups.sort(key=lambda x: os.path.getctime(x), reverse=True)
        return backups

    def validate_directories(self) -> tuple[bool, str]:
        """验证目录是否有效"""
        if not self.source_dir:
            return False, "源目录未设置"

        if not os.path.exists(self.source_dir):
            return False, "源目录不存在"

        if not self.backup_dir:
            return False, "备份目录未设置"

        # 检查备份目录的父目录是否存在
        backup_parent = os.path.dirname(os.path.abspath(self.backup_dir))
        if backup_parent and not os.path.exists(backup_parent):
            return False, "备份目录的父目录不存在"

        return True, "目录验证通过"