import os
import torch
import whisper
from PyQt6.QtCore import QThread, pyqtSignal

class WhisperManager:
    """
    Whisper模型管理类
    
    负责加载和管理Whisper语音识别模型，提供模型切换功能。
    
    属性:
        device: 计算设备(cuda/cpu)
        current_model: 当前加载的Whisper模型
        model_name: 当前模型名称
    """
    def __init__(self):
        """初始化模型管理器，自动检测可用设备"""
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.current_model = None
        self.model_name = None

    def load_model(self, model_name):
        """
        加载指定名称的Whisper模型 
        
        参数:
            model_name: 模型名称(如"base", "large-v3"等)
        
        返回:
            加载后的Whisper模型对象
        """
        self.model_name = model_name
        self.current_model = whisper.load_model(model_name)
        self.current_model.to(self.device)
        return self.current_model

    def unload_model(self):
        """
        卸载当前加载的模型，释放内存
        """
        if self.current_model is not None:
            del self.current_model
            self.current_model = None
            self.model_name = None
            if torch.cuda.is_available():
                torch.cuda.empty_cache()

    def get_available_models(self):
        """
        获取可用的Whisper模型列表
        
        返回:
            list: 可用模型名称列表
        """
        return ["base", "turbo", "large-v3"]

class WhisperWorker(QThread):
    """
    Whisper后台工作线程类，继承自QThread
    
    负责在后台线程中执行语音识别任务，完成后发射结果信号。
    
    属性:
        finished: pyqtSignal信号，识别完成后发射，携带识别文本
    """
    finished = pyqtSignal(str)

    def __init__(self, file, model, task="transcribe", language='zh'):
        """
        初始化工作线程
        
        参数:
            file: 音频文件路径
            model: Whisper 模型对象
            task: 任务类型：'transcribe'（听写）或 'translate'（翻译成英文）
            language: 语音的语言（如 'zh', 'en'），None 表示自动检测
        """
        super().__init__()
        self.file = file
        self.model = model
        self.task = task
        self.language = language  # 语音所属语言，不是输出语言

    def run(self):
        """
        线程运行方法，执行语音识别任务
        
        1. 调用Whisper模型进行语音识别
        2. 处理识别结果或错误
        3. 删除临时音频文件
        4. 通过finished信号发射识别结果
        """
        text = ""
        try:
            result = self.model.transcribe(
                self.file,
                task=self.task,
                language=self.language  # 设置输入语言，如 'zh'、'en'，None=自动识别
            )
            text = result["text"]
        except Exception as e:
            text = f"识别失败: {e}"
        finally:
            if os.path.exists(self.file):
                try:
                    os.remove(self.file)
                except OSError as err:
                    print(f"[WhisperWorker] 删除临时文件时出错: {err}")

        self.finished.emit(text)