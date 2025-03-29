import sys
import os
import datetime
import whisper
import torch
import sounddevice as sd
import soundfile as sf
import pyperclip
from opencc import OpenCC

from PyQt6.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout, QLabel,
    QMenu, QGraphicsDropShadowEffect
)
from PyQt6.QtGui import QColor, QAction
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QPoint


class AudioRecorder(QThread):
    finished = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.fs = 16000
        self.recording = False
        self.audio = []

    def run(self):
        self.recording = True
        self.audio = []

        def callback(indata, frames, time, status):
            if self.recording:
                self.audio.extend(indata[:, 0])

        with sd.InputStream(samplerate=self.fs, channels=1, callback=callback):
            while self.recording:
                sd.sleep(100)

        if self.audio:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            self.filename = f"recording_{timestamp}.wav"
            sf.write(self.filename, self.audio, self.fs)
            self.finished.emit(self.filename)

    def stop(self):
        self.recording = False


class WhisperWorker(QThread):
    finished = pyqtSignal(str)

    def __init__(self, file, model):
        super().__init__()
        self.file = file
        self.model = model
        self.cc = OpenCC("t2s")  # 繁转简

    def run(self):
        result = self.model.transcribe(self.file)
        simplified_text = self.cc.convert(result["text"])
        self.finished.emit(simplified_text)


class FloatingWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🧠 Whisper浮动录音")
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.model_name = "base"
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.whisper_model = self.load_model(self.model_name)

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

        layout = QVBoxLayout(self.container)
        layout.addWidget(self.rec_button)
        layout.addWidget(self.label)
        layout.setContentsMargins(20, 20, 20, 20)
        self.resize(340, 180)
        self.container.resize(340, 180)

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
        pyperclip.copy(text)
        self.rec_button.setText("🎙️ 开始录音")

    def show_context_menu(self, pos: QPoint):
        menu = QMenu(self)

        model_menu = menu.addMenu("🧠 选择模型")
        for name in ["base", "turbo", "large-v3"]:
            action = QAction(name, self)
            action.setCheckable(True)
            action.setChecked(name == self.model_name)
            action.triggered.connect(lambda checked, m=name: self.change_model(m))
            model_menu.addAction(action)

        menu.addSeparator()
        menu.addAction("❌ 关闭悬浮窗", self.close)
        menu.exec(self.mapToGlobal(pos))

    def change_model(self, model_name):
        self.model_name = model_name
        self.label.setText(f"🔄 正在切换模型为：{model_name} ...")
        QApplication.processEvents()
        self.whisper_model = self.load_model(model_name)
        self.label.setText(f"✅ 模型已切换为：{model_name}")

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


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FloatingWidget()
    window.move(100, 100)
    window.show()
    sys.exit(app.exec())