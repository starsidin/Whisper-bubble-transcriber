"""
音频录制模块

该模块提供了音频录制功能，使用sounddevice和soundfile库进行音频捕获和保存。
主要包含AudioRecorder类，用于在后台线程中录制音频并保存为临时WAV文件。
"""
import os
import tempfile
import sounddevice as sd
import soundfile as sf
from PyQt6.QtCore import QThread, pyqtSignal

class AudioRecorder(QThread):
    """
    音频录制器类，继承自QThread实现后台录制
    
    属性:
        finished: pyqtSignal信号，录制完成时发射，携带临时WAV文件路径
        fs: 采样率，默认16000Hz
        recording: 录制状态标志
        audio: 存储录制的音频数据
        device_index: 音频设备索引
        temp_wav: 临时WAV文件路径
    """
    finished = pyqtSignal(str)

    def __init__(self, device_index=None):
        """
        初始化音频录制器
        
        参数:
            device_index: 可选，指定音频输入设备索引
        """
        super().__init__()
        self.fs = 16000
        self.recording = False
        self.audio = []
        self.device_index = device_index
        self.temp_wav = None

    def run(self):
        """
        线程运行方法，执行音频录制
        
        1. 设置录制状态标志
        2. 初始化音频数据缓存
        3. 定义音频回调函数，实时捕获音频数据
        4. 使用sounddevice创建输入流进行录制
        5. 录制完成后将音频保存为临时WAV文件
        6. 通过finished信号发射文件路径
        """
        self.recording = True
        self.audio = []

        def callback(indata, frames, time, status):
            """音频数据回调函数，将输入数据添加到缓存"""
            if self.recording:
                self.audio.extend(indata[:, 0])

        try:
            with sd.InputStream(samplerate=self.fs, channels=1, callback=callback, device=self.device_index):
                while self.recording:
                    sd.sleep(100)
        except sd.PortAudioError as e:
            print(f"[AudioRecorder] 音频设备错误: {str(e)}")

        if self.audio:
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
                self.temp_wav = tmp_file.name
            sf.write(self.temp_wav, self.audio, self.fs)
            self.finished.emit(self.temp_wav)

    def stop(self):
        """
        停止录制
        
        设置录制状态标志为False，run方法中的循环将退出
        """
        self.recording = False

def get_available_microphones(include_loopback=False, print_info=False):
    """
    获取可用的音频输入设备（真正可用于录音的），并标记是否为内放设备。

    参数:
        include_loopback (bool): 是否包含 loopback 判断列（默认False，仅返回 index 和 name）
        print_info (bool): 是否打印可用设备列表

    返回:
        list: 每项为 (index, name) 或 (index, name, is_loopback)
    """
    loopback_keywords = ['loopback', 'stereo mix', 'voice meter', 'virtual audio']
    devices = []

    for i, device in enumerate(sd.query_devices()):
        # 只保留真正可用的“输入设备”
        if device['max_input_channels'] > 0:
            name = device['name']
            is_loopback = any(kw in name.lower() for kw in loopback_keywords)
            if include_loopback:
                devices.append((i, name, is_loopback))
            else:
                devices.append((i, name))

    if print_info:
        print("🎙 可用音频输入设备：")
        for d in devices:
            if include_loopback:
                idx, name, is_loop = d
                tag = "✅ 支持内录" if is_loop else ""
                print(f"[{idx}] {name} {tag}")
            else:
                idx, name = d
                print(f"[{idx}] {name}")
    return devices
