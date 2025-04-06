from modelscope.pipelines import pipeline
from modelscope.utils.constant import Tasks
import torch
from PyQt6.QtCore import QThread, pyqtSignal
import os
class ModelScopeManager:
    """
    ModelScope语音识别模型管理类
    
    负责加载和管理ModelScope语音识别模型，提供音频转写功能。
    
    属性:
        device: 计算设备(cuda/cpu)
        current_model: 当前加载的ModelScope模型
        model_name: 当前模型名称
    """
    def __init__(self):
        """初始化模型管理器，自动检测可用设备"""
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.current_model = None
        self.model_name = None
        
    def transcribe(self, audio_input):
        """
        转写音频文件
        
        参数:
            audio_input: 支持以下格式:
                - wav文件路径 (str)
                - mp3文件路径 (str)
            
        返回:
            str: 转写结果文本
        """
        if self.current_model is None:
            self.load_model()

        if not isinstance(audio_input, str):
            raise ValueError("音频输入必须是文件路径字符串")
            
        if not audio_input.lower().endswith(('.wav', '.mp3')):
            raise ValueError("仅支持WAV和MP3格式的音频文件")
            
        result = self.current_model(audio_input)
        return result['text'] if 'text' in result else result

    def load_model(self, use_vad=True, use_punc=True):
        """
        加载ModelScope语音识别模型
        
        参数:
            use_vad: 是否使用VAD模型
            use_punc: 是否使用标点符号模型
            
        返回:
            加载后的ModelScope模型对象
        """
        self.model_name = 'iic/speech_paraformer-large-vad-punc_asr_nat-zh-cn-16k-common-vocab8404-pytorch'
        model_params = {
            'task': Tasks.auto_speech_recognition,
            'model': self.model_name,
            'device': self.device
        }
        
        if use_vad:
            model_params['vad_model'] = 'iic/speech_fsmn_vad_zh-cn-16k-common-pytorch'
            
        
        if use_punc:
            model_params['punc_model'] = 'iic/punc_ct-transformer_zh-cn-common-vocab272727-pytorch'
            
        
        self.current_model = pipeline(**model_params)
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
        获取可用的ModelScope模型列表
        
        返回:
            list: 可用模型名称列表
        """
        return ["iic/speech_paraformer-large-vad-punc_asr_nat-zh-cn-16k-common-vocab8404-pytorch"]


class ModelScopeWorker(QThread):
    """
    ModelScope后台工作线程类，继承自QThread
    
    负责在后台线程中执行语音识别任务，完成后发射结果信号。
    
    属性:
        finished: pyqtSignal信号，识别完成后发射，携带识别文本
    """
    finished = pyqtSignal(str)

    def __init__(self, file, model, use_vad=True, use_punc=True):
        """
        初始化工作线程
        
        参数:
            file: 音频文件路径
            model: ModelScope 模型对象
            use_vad: 是否使用VAD模型
            use_punc: 是否使用标点符号模型
        """
        super().__init__()
        self.file = file
        self.model = model
        self.use_vad = use_vad
        self.use_punc = use_punc

    def run(self):
        """
        线程运行方法，执行语音识别任务
        
        1. 调用ModelScope模型进行语音识别
        2. 处理识别结果或错误
        3. 删除临时音频文件
        4. 通过finished信号发射识别结果
        """
        text = ""
        try:
            if not isinstance(self.file, str):
                raise ValueError("音频输入必须是文件路径字符串")
                
            if not self.file.lower().endswith(('.wav', '.mp3')):
                raise ValueError("仅支持WAV和MP3格式的音频文件")
                
            result = self.model(self.file)
            print(f"[ModelScopeWorker] 原始识别结果类型: {type(result)}")
            print(f"[ModelScopeWorker] 原始识别结果内容: {result}")
            if isinstance(result, dict):
                text = result['text'] if 'text' in result else str(result)
                print(f"[ModelScopeWorker] 字典处理后的文本: {text}")
            elif isinstance(result, list):
                # 处理列表中的字典项
                text_parts = []
                for item in result:
                    if isinstance(item, dict) and 'text' in item:
                        text_parts.append(item['text'])
                    else:
                        text_parts.append(str(item))
                text = ' '.join(text_parts)  # 将所有文本部分连接成字符串
                print(f"[ModelScopeWorker] 列表处理后的文本: {text}")
            else:
                text = str(result)  # 其他类型转换为字符串
                print(f"[ModelScopeWorker] 其他类型处理后的文本: {text}")
        except Exception as e:
            text = f"识别失败: {e}"
        finally:
            if os.path.exists(self.file):
                try:
                    os.remove(self.file)
                except OSError as err:
                    print(f"[ModelScopeWorker] 删除临时文件时出错: {err}")
            self.finished.emit(text)