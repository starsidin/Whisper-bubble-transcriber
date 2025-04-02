"""
主程序模块

该模块是WhisperSTT应用程序的入口点，负责初始化历史记录目录和启动主窗口。
"""
import sys
import os
from PyQt6.QtWidgets import QApplication
from ui.floating_widget import FloatingWidget

# 创建历史记录目录(如果不存在)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
HISTORY_DIR = os.path.join(BASE_DIR, "history")
if not os.path.exists(HISTORY_DIR):
    os.makedirs(HISTORY_DIR)

def main():
    """
    主函数
    
    初始化Qt应用，创建并显示浮动窗口
    """
    app = QApplication(sys.argv)
    window = FloatingWidget()
    window.move(100, 100)
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()