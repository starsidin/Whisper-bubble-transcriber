from typing import Optional
from .whisper_manager import WhisperManager,WhisperWorker
from .modelscope_manager import ModelScopeManager ,ModelScopeWorker
from .api_manager import APIManager, APIWorker

class ModelManager:
    def __init__(self):
        self.whisper_manager = WhisperManager()
        self.modelscope_manager = ModelScopeManager()
        self.api_manager = APIManager()
        self.current_model = None
        self.current_model_type = None
        self.current_model_name = None
        self.api_key = None

    def get_available_models(self):
        """获取所有可用的模型列表

        Returns:
            list: 包含所有可用模型名称的列表，格式为 ["whisper:tiny", "whisper:base", ...]
        """
        whisper_models = [f"whisper:{model}" for model in self.whisper_manager.get_available_models()]
        modelscope_models = [f"modelscope:{model}" for model in self.modelscope_manager.get_available_models()]
        api_models = [f"api:{model}" for model in self.api_manager.get_available_models()]
        return whisper_models + modelscope_models + api_models

    def unload_model(self):
        """卸载当前加载的模型，释放内存"""
        if self.current_model is not None:
            if self.current_model_type == "whisper":
                self.whisper_manager.unload_model()
            elif self.current_model_type == "modelscope":
                self.modelscope_manager.unload_model()
            elif self.current_model_type == "api":
                self.api_manager.unload_model()
            self.current_model = None
            self.current_model_type = None
            self.current_model_name = None

    def load_model(self, model_name: str) -> Optional[object]:
        """加载指定的模型

        Args:
            model_name: 模型名称，格式为 "type:name"，如 "whisper:base"

        Returns:
            object: 加载的模型对象
        """
        try:
            # 如果已有模型加载，先卸载它
            if self.current_model is not None:
                self.unload_model()

            model_type, model_name = model_name.split(":")
            if model_type == "whisper":
                self.current_model = self.whisper_manager.load_model(model_name)
                self.current_model_type = "whisper"
            elif model_type == "modelscope":
                self.current_model = self.modelscope_manager.load_model(model_name)
                self.current_model_type = "modelscope"
            elif model_type == "api":
                if not self.api_key:
                    raise ValueError("使用API模型需要先设置API密钥")
                self.current_model = self.api_manager.load_model(model_name)
                self.current_model_type = "api"
            else:
                raise ValueError(f"不支持的模型类型: {model_type}")
            
            self.current_model_name = model_name
            return self.current_model
        except Exception as e:
            print(f"加载模型时出错: {e}")
            return None

    def transcribe(self, audio_file: str) -> str:
        """使用当前加载的模型转录音频文件

        Args:
            audio_file: 音频文件路径

        Returns:
            str: 转录结果文本
        """
        if self.current_model is None:
            raise ValueError("没有加载任何模型")

        if self.current_model_type == "whisper":
            return self.whisper_manager.transcribe(self.current_model, audio_file)
        elif self.current_model_type == "modelscope":
            return self.modelscope_manager.transcribe(self.current_model, audio_file)
        elif self.current_model_type == "api":
            return self.api_manager.transcribe(audio_file)
        
        raise ValueError(f"不支持的模型类型: {self.current_model_type}")

    def get_current_model_info(self) -> dict:
        """获取当前模型的信息

        Returns:
            dict: 包含当前模型类型和名称的字典
        """
        return {
            "type": self.current_model_type,
            "name": self.current_model_name
        }
        
    def set_api_key(self, api_key: str):
        """设置API密钥

        Args:
            api_key: 达摩院API密钥
        """
        self.api_key = api_key
        self.api_manager.set_api_key(api_key)

    def create_worker(self, audio_file: str, task="transcribe", language='zh') -> object:
        """创建一个用于语音识别的worker实例

        Args:
            audio_file: 音频文件路径
            task: 任务类型：'transcribe'（听写）或 'translate'（翻译成英文）
            language: 语音的语言（如 'zh', 'en'），None 表示自动检测

        Returns:
            object: 创建的worker实例

        Raises:
            ValueError: 当没有加载模型或模型类型不支持时抛出
        """
        if self.current_model is None:
            raise ValueError("没有加载任何模型")

        if self.current_model_type == "whisper":
            return WhisperWorker(audio_file, self.current_model, task, language)
        elif self.current_model_type == "modelscope":
            from .modelscope_manager import ModelScopeWorker
            return ModelScopeWorker(audio_file, self.current_model)
        elif self.current_model_type == "api":
            if not self.api_key:
                raise ValueError("使用API模型需要先设置API密钥")
            return APIWorker(audio_file, self.api_key)
        
        raise ValueError(f"不支持的模型类型: {self.current_model_type}")