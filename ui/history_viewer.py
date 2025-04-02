"""
历史记录查看器模块

该模块提供了打开历史记录目录的功能，使用系统默认的文件浏览器打开历史记录文件夹。
主要包含HistoryViewer类，用于在用户请求时打开历史记录目录。
"""
import os
import sys
import subprocess
from PyQt6.QtWidgets import QDialog, QMessageBox
from utils.helpers import get_history_dir

class HistoryViewer(QDialog):
    """
    历史记录查看器类，继承自QDialog
    
    该类负责在用户请求时打开系统默认的文件浏览器显示历史记录目录。
    支持Windows、MacOS和Linux系统。
    """
    def __init__(self, parent=None):
        """
        初始化历史记录查看器
        
        参数:
            parent: 父窗口对象，可选
        """
        super().__init__(parent)
        try:
            # 获取历史记录目录路径
            history_dir = get_history_dir()
            if not os.path.exists(history_dir):
                os.makedirs(history_dir)
                
            # 根据操作系统类型使用不同的命令打开文件浏览器
            if sys.platform == "win32":
                os.startfile(history_dir)
            elif sys.platform == "darwin":
                subprocess.Popen(["open", history_dir])
            else:
                subprocess.Popen(["xdg-open", history_dir])
        except Exception as e:
            # 打开失败时显示错误消息
            QMessageBox.critical(self, "错误", f"无法打开历史记录文件夹：\n{e}")
        self.close()