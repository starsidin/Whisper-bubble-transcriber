import sys
import os
import datetime
import whisper
import torch
import sounddevice as sd
import soundfile as sf
import pyperclip
import tempfile
import shutil
import subprocess

from PyQt6.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QLabel,
    QMenu, QGraphicsDropShadowEffect, QDialog, QTextEdit, QDialogButtonBox, QMessageBox
)
from PyQt6.QtGui import QColor, QAction
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QPoint

# 打印当前Python及 ffmpeg 信息，方便调试
print("=== ffmpeg 位置:", shutil.which("ffmpeg"))

# 在脚本根目录下创建一个 history 文件夹
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
HISTORY_DIR = os.path.join(BASE_DIR, "history")
if not os.path.exists(HISTORY_DIR):
    os.makedirs(HISTORY_DIR)

class AudioRecorder(QThread):
    finished = pyqtSignal(str)

    def __init__(self, device_index=None):
        super().__init__()
        self.fs = 16000
        self.recording = False
        self.audio = []
        self.device_index = device_index
        self.temp_wav = None

    def run(self):
        self.recording = True
        self.audio = []

        def callback(indata, frames, time, status):
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
        self.recording = False


class WhisperWorker(QThread):
    finished = pyqtSignal(str)

    def __init__(self, file, model):
        super().__init__()
        self.file = file
        self.model = model

    def run(self):
        text = ""
        try:
            result = self.model.transcribe(self.file)
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


class HistoryViewer(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        try:
            if not os.path.exists(HISTORY_DIR):
                os.makedirs(HISTORY_DIR)
            if sys.platform == "win32":
                os.startfile(HISTORY_DIR)
            elif sys.platform == "darwin":
                subprocess.Popen(["open", HISTORY_DIR])
            else:
                subprocess.Popen(["xdg-open", HISTORY_DIR])
        except Exception as e:
            QMessageBox.critical(self, "错误", f"无法打开历史记录文件夹：\n{e}")
        self.close()


class FloatingWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🧠 Whisper浮动录音")
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.model_name = "turbo"
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.whisper_model = self.load_model(self.model_name)
        self.auto_copy = True

        self.container = QWidget(self)
        self.container.setObjectName("container")
        self.container.setStyleSheet("""
            QWidget#container {
                background-color: rgba(255, 255, 255, 230);
                border-radius: 15px;
            }
        """)
        self.shadow = QGraphicsDropShadowEffect(self)
        self.shadow.setBlurRadius(20)
        self.shadow.setOffset(0, 0)
        self.shadow.setColor(QColor(0, 0, 0, 80))
        self.container.setGraphicsEffect(self.shadow)

        self.rec_button = QPushButton("🎙️ 开始录音")
        self.rec_button.clicked.connect(self.toggle_recording)
        self.rec_button.setStyleSheet("""
            QPushButton {
                background-color: #5DADE2;
                border: none;
                color: white;
                font-size: 16px;
                padding: 10px 20px;
                border-radius: 20px;
            }
            QPushButton:hover {
                background-color: #3498DB;
            }
        """)

        self.copy_button = QPushButton("复制")
        self.copy_button.setStyleSheet("""
            QPushButton {
                background-color: #B2BABB;
                border: none;
                color: white;
                font-size: 12px;
                padding: 5px 10px;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: #808B96;
            }
        """)
        self.copy_button.clicked.connect(self.copy_text)

        self.label = QLabel("")
        self.label.setWordWrap(True)
        self.label.setStyleSheet("""
            QLabel {
                background-color: #F2F3F4;
                border-radius: 12px;
                padding: 10px;
                font-size: 14px;
            }
        """)

        main_layout = QVBoxLayout(self.container)
        main_layout.setContentsMargins(20, 20, 20, 20)

        top_layout = QHBoxLayout()
        top_layout.addWidget(self.rec_button)
        top_layout.addWidget(self.copy_button)
        main_layout.addLayout(top_layout)

        main_layout.addWidget(self.label)

        self.resize(380, 200)
        self.container.resize(380, 200)

        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)

        self.recorder = AudioRecorder()
        self.recorder.finished.connect(self.on_recorded)
        self.recording = False

    def toggle_recording(self):
        if not self.recording:
            self.rec_button.setText("🛑 停止录音")
            self.recording = True
            self.recorder.start()
        else:
            self.rec_button.setText("🎙️ 开始录音")
            self.recording = False
            self.recorder.stop()

    def on_recorded(self, file):
        self.label.setText("🎧 正在识别...")
        self.whisper_thread = WhisperWorker(file, self.whisper_model)
        self.whisper_thread.finished.connect(self.on_transcribed)
        self.whisper_thread.start()

    def on_transcribed(self, text):
        self.label.setText(f"💬 {text}")
        if self.auto_copy:
            pyperclip.copy(text)
        self.store_history(text)
        self.rec_button.setText("🎙️ 开始录音")

    def copy_text(self):
        txt = self.label.text().replace("💬 ", "")
        if txt.strip():
            pyperclip.copy(txt)

    def store_history(self, text):
        if not text.strip():
            return
        date_str = datetime.datetime.now().strftime("%Y-%m-%d")
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        filepath = os.path.join(HISTORY_DIR, f"{date_str}.txt")
        if not os.path.exists(filepath):
            with open(filepath, "w", encoding="utf-8") as f:
                f.write("")
        with open(filepath, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] {text}\n")

    def show_context_menu(self, pos: QPoint):
        menu = QMenu(self)
        model_menu = menu.addMenu("🧠 选择模型")
        for name in ["base", "turbo", "large-v3"]:
            action = QAction(name, self)
            action.setCheckable(True)
            action.setChecked(name == self.model_name)
            action.triggered.connect(lambda checked, m=name: self.change_model(m))
            model_menu.addAction(action)

        mic_menu = menu.addMenu("🎙️ 选择麦克风")
        for i, device in enumerate(sd.query_devices()):
            if device['max_input_channels'] > 0:
                action = QAction(device['name'], self)
                action.setCheckable(True)
                action.setChecked(i == (self.recorder.device_index if self.recorder.device_index is not None else sd.default.device[0]))
                action.triggered.connect(lambda checked, idx=i: self.change_mic_device(idx))
                mic_menu.addAction(action)

        menu.addSeparator()
        auto_copy_action = QAction("自动复制文字", self)
        auto_copy_action.setCheckable(True)
        auto_copy_action.setChecked(self.auto_copy)
        auto_copy_action.triggered.connect(self.toggle_auto_copy)
        menu.addAction(auto_copy_action)

        history_action = QAction("查看历史记录", self)
        history_action.triggered.connect(self.view_history)
        menu.addAction(history_action)

        menu.addSeparator()
        menu.addAction("❌ 关闭悬浮窗", self.close)
        menu.exec(self.mapToGlobal(pos))

    def toggle_auto_copy(self):
        self.auto_copy = not self.auto_copy

    def view_history(self):
        dlg = HistoryViewer(self)
        dlg.exec()

    def change_model(self, model_name):
        self.model_name = model_name
        self.label.setText(f"🔄 正在切换模型为：{model_name} ...")
        QApplication.processEvents()
        self.whisper_model = self.load_model(model_name)
        self.label.setText(f"✅ 模型已切换为：{model_name}")

    def change_mic_device(self, device_index):
        self.recorder = AudioRecorder(device_index)
        self.recorder.finished.connect(self.on_recorded)
        self.label.setText("✅ 已切换麦克风设备")
        QApplication.processEvents()

    def load_model(self, model_name):
        model = whisper.load_model(model_name)
        model.to(self.device)
        return model

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()

def main():
    app = QApplication(sys.argv)
    window = FloatingWidget()
    window.move(100, 100)
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()