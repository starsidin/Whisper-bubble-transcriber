"""
工具函数模块

该模块提供了一些实用工具函数，包括剪贴板操作和历史记录目录管理。
"""
import os
import pyperclip

def copy_to_clipboard(text):
    """
    复制文本到系统剪贴板
    
    参数:
        text: 要复制的文本内容
    
    返回:
        无
    """
    pyperclip.copy(text)

def get_history_dir():
    """
    获取历史记录目录路径
    
    返回:
        str: 历史记录目录的绝对路径
        
    说明:
        如果目录不存在会自动创建
    """
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    history_dir = os.path.join(base_dir, "history")
    if not os.path.exists(history_dir):
        os.makedirs(history_dir)
    return history_dir