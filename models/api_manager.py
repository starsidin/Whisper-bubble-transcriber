import os
import requests
import json
from http import HTTPStatus
from dashscope.audio.asr import Transcription
import dashscope
from PyQt6.QtCore import QThread, pyqtSignal
from utils.api_keys import get_api_key, save_api_key, get_api_types


class APIManager:
    """
    DashScope API 语音识别管理类
    负责管理 DashScope API 的调用，提供音频转写功能。
    """
    def __init__(self):
        """初始化 API 管理器"""
        self.api_key = None
        self.current_model = None
        self.model_name = None
        self.api_type = "aliyun"  # 默认使用阿里云API
        # 尝试从文件中读取API密钥
        self._load_api_key_from_file()
    
    def _load_api_key_from_file(self):
        """从文件中加载API密钥"""
        try:
            api_key = get_api_key(self.api_type)
            if api_key:
                self.set_api_key(api_key)
        except Exception as e:
            print(f"加载API密钥时出错: {e}")

    def set_api_key(self, api_key):
        """设置 API 密钥"""
        self.api_key = api_key
        dashscope.api_key = api_key  # 设置全局 API key
        # 保存API密钥到文件
        try:
            save_api_key(self.api_type, api_key)
        except Exception as e:
            print(f"保存API密钥时出错: {e}")

    def transcribe(self, audio_file):
        """转写音频文件

        参数:
            audio_file: 音频文件路径

        返回:
            str: 转写结果文本
        """
        if not self.api_key:
            raise ValueError("API 密钥未设置，请先设置 API 密钥")

        if not isinstance(audio_file, str):
            raise ValueError("音频输入必须是文件路径字符串")

        if not audio_file.lower().endswith(('.wav', '.mp3')):
            raise ValueError("仅支持 WAV 和 MP3 格式的音频文件")

        # 上传本地文件到可访问的地址 (DashScope 需要 URL 地址)  
        # 暂时方案：必须提前将文件放到公开 URL。建议配合 OSS 使用。

        # --- 方案 1：本地文件不支持，需要先上传到 OSS 或者其他公开链接
        raise NotImplementedError("DashScope API 需要可访问的音频 URL，当前未实现文件上传。")

        # --- 方案 2：如果文件已经是 URL（如 OSS 地址），继续执行
        file_url = audio_file

        try:
            # 发起异步识别任务
            task_response = Transcription.async_call(
                model='paraformer-v2',
                file_urls=[file_url],
                language_hints=['zh']  # 可按需填写语言提示
            )

            if task_response.status_code != HTTPStatus.OK:
                raise Exception(f"任务提交失败: {task_response.message}")

            task_id = task_response.output.task_id

            # 等待任务完成
            transcribe_response = Transcription.wait(task=task_id)

            if transcribe_response.status_code != HTTPStatus.OK:
                raise Exception(f"识别失败: {transcribe_response.message}")

            # 提取结果
            results = transcribe_response.output.results
            texts = [item['text'] for item in results]

            return '\n'.join(texts)

        except Exception as e:
            raise Exception(f"API 调用失败: {str(e)}")

    def load_model(self, model_name=None):
        """加载 API 模型"""
        self.model_name = "paraformer-v2"
        self.current_model = self.model_name
        return self.current_model

    def unload_model(self):
        """卸载当前模型"""
        self.current_model = None
        self.model_name = None

    def get_available_models(self):
        """获取可用的 API 模型列表"""
        return ["paraformer-v2"]
        
    def set_api_type(self, api_type):
        """设置API类型
        
        参数:
            api_type: API类型，如 'openai-whisper', 'aliyun', 'deepseek'
        """
        self.api_type = api_type
        # 尝试从文件中读取对应类型的API密钥
        self._load_api_key_from_file()
        
    def get_api_types(self):
        """获取支持的API类型
        
        返回:
            dict: 支持的API类型字典
        """
        return get_api_types()


class APIWorker(QThread):
    """
    DashScope API 后台工作线程类，继承自 QThread
    负责在后台线程中执行语音识别任务，完成后发射结果信号。
    """
    finished = pyqtSignal(str)

    def __init__(self, file, api_key):
        """
        初始化工作线程

        参数:
            file: 音频文件路径（注意：需要是 URL）
            api_key: DashScope API 密钥
        """
        super().__init__()
        self.file = file
        self.api_key = api_key
        self.api_manager = APIManager()
        self.api_manager.set_api_key(api_key)

    def run(self):
        """
        线程运行方法，执行语音识别任务
        """
        text = ""
        try:
            text = self.api_manager.transcribe(self.file)
        except Exception as e:
            text = f"识别失败: {e}"
        finally:
            # 删除临时文件（如果是本地文件，可以删；如果是 URL 则不用删）
            if os.path.exists(self.file):
                try:
                    os.remove(self.file)
                except OSError as err:
                    print(f"[APIWorker] 删除临时文件时出错: {err}")
            self.finished.emit(text)
