"""API密钥管理模块

该模块提供了API密钥的读取和保存功能，支持多种API服务的密钥管理。
"""
import os
import json

# 支持的API类型
API_TYPES = {
    "openai-whisper": "OpenAI Whisper API",
    "aliyun": "阿里云API",
    "deepseek": "DeepSeek API"
}

def get_api_keys_file_path():
    """
    获取API密钥文件的路径
    
    返回:
        str: API密钥文件的绝对路径
    """
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_dir, "api_keys.txt")

def read_api_keys():
    """
    读取API密钥文件
    
    返回:
        dict: 包含各种API密钥的字典
    """
    api_keys = {}
    api_keys_file = get_api_keys_file_path()
    
    # 如果文件不存在，创建一个空文件
    if not os.path.exists(api_keys_file):
        with open(api_keys_file, "w", encoding="utf-8") as f:
            json.dump({}, f)
        return api_keys
    
    # 读取文件内容
    try:
        with open(api_keys_file, "r", encoding="utf-8") as f:
            content = f.read().strip()
            if content:
                api_keys = json.loads(content)
    except (json.JSONDecodeError, IOError) as e:
        print(f"读取API密钥文件时出错: {e}")
    
    return api_keys

def save_api_key(api_type, api_key):
    """
    保存API密钥
    
    参数:
        api_type: API类型，如 'openai-whisper', 'aliyun', 'deepseek'
        api_key: API密钥
    
    返回:
        bool: 保存成功返回True，否则返回False
    """
    if api_type not in API_TYPES:
        raise ValueError(f"不支持的API类型: {api_type}")
    
    api_keys = read_api_keys()
    api_keys[api_type] = api_key
    
    try:
        with open(get_api_keys_file_path(), "w", encoding="utf-8") as f:
            json.dump(api_keys, f)
        return True
    except IOError as e:
        print(f"保存API密钥时出错: {e}")
        return False

def get_api_key(api_type):
    """
    获取指定类型的API密钥
    
    参数:
        api_type: API类型，如 'openai-whisper', 'aliyun', 'deepseek'
    
    返回:
        str: API密钥，如果不存在则返回None
    """
    if api_type not in API_TYPES:
        raise ValueError(f"不支持的API类型: {api_type}")
    
    api_keys = read_api_keys()
    return api_keys.get(api_type)

def get_api_types():
    """
    获取支持的API类型
    
    返回:
        dict: 支持的API类型字典，键为API类型代码，值为API类型名称
    """
    return API_TYPES.copy()