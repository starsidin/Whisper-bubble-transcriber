import os
import datetime
from PyQt6.QtWidgets import (
    QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QLabel,
    QMenu, QGraphicsDropShadowEffect, QScrollArea, QTextEdit
)
from PyQt6.QtGui import QColor, QAction
from PyQt6.QtCore import Qt, QPoint

from audio_recorder import AudioRecorder, get_available_microphones
from models import ModelManager
from utils import copy_to_clipboard, get_history_dir
from ui.history_viewer import HistoryViewer
from ui.api_key_dialog import APIKeyDialog

class FloatingWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🧠 Whisper浮动录音")
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.drag_position = QPoint()

        self.model_manager = ModelManager()
        self.model_name = "whisper:turbo"
        self.model = self.model_manager.load_model(self.model_name)
        self.auto_copy = True

        self.setup_ui_container()
        self.setup_ui_components()
        self.setup_layout()

        self.recorder = AudioRecorder()
        self.recorder.finished.connect(self.on_recorded)
        self.recording = False

    def setup_ui_container(self):
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

    def setup_ui_components(self):
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

        # ✅ 用 QTextEdit 替换 QLabel
        self.label = QTextEdit()
        self.label.setReadOnly(True)
        self.label.setStyleSheet("""
            QTextEdit {
                background-color: #F2F3F4;
                border-radius: 12px;
                padding: 10px;
                font-size: 14px;
                border: none;
            }
        """)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)  # 不显示滚动条
        self.scroll_area.setStyleSheet("""
            QScrollArea { border: none; }
            QScrollBar:vertical { width: 0px; }
        """)
        self.scroll_area.setWidget(self.label)
        self.scroll_area.setMaximumHeight(150)

        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)

    def setup_layout(self):
        main_layout = QVBoxLayout(self.container)
        main_layout.setContentsMargins(20, 20, 20, 20)

        top_layout = QHBoxLayout()
        top_layout.addWidget(self.rec_button)
        top_layout.addWidget(self.copy_button)
        main_layout.addLayout(top_layout)

        main_layout.addWidget(self.scroll_area)

        self.resize(300, 150)
        self.container.resize(300, 150)

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
        self.label.setPlainText("🎧 正在识别...")  # ✅ 改用 setPlainText
        self.whisper_thread = self.model_manager.create_worker(file)
        self.whisper_thread.finished.connect(self.on_transcribed)
        self.whisper_thread.start()

    def on_transcribed(self, text):
        self.label.setPlainText(f"💬 {text}")  # ✅ 改用 setPlainText
        if self.auto_copy:
            copy_to_clipboard(text)
        self.store_history(text)
        self.rec_button.setText("🎙️ 开始录音")

    def copy_text(self):
        txt = self.label.toPlainText().replace("💬 ", "")  # ✅ 使用 toPlainText
        if txt.strip():
            copy_to_clipboard(txt)

    def store_history(self, text):
        if not text.strip():
            return
        date_str = datetime.datetime.now().strftime("%Y-%m-%d")
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        filepath = os.path.join(get_history_dir(), f"{date_str}.txt")
        if not os.path.exists(filepath):
            with open(filepath, "w", encoding="utf-8") as f:
                f.write("")
        with open(filepath, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] {text}\n")

    def show_context_menu(self, pos: QPoint):
        """
        显示上下文菜单
        
        参数:
            pos: 鼠标点击位置
        
        创建并显示右键菜单，包含模型选择、麦克风选择、自动复制和历史记录查看等功能
        """
        menu = QMenu(self)

        # 模型选择菜单
        model_menu = menu.addMenu("🧠 选择模型")
        for name in self.model_manager.get_available_models():
            action = QAction(name, self)
            action.setCheckable(True)
            action.setChecked(name == self.model_name)
            action.triggered.connect(lambda checked, m=name: self.change_model(m))
            model_menu.addAction(action)

        # 麦克风选择菜单
        mic_menu = menu.addMenu("🎙️ 选择麦克风")
        for idx, name in get_available_microphones():
            action = QAction(name, self)
            action.setCheckable(True)
            action.setChecked(idx == (self.recorder.device_index if self.recorder.device_index is not None else self.get_default_mic_index()))
            action.triggered.connect(lambda checked, idx=idx: self.change_mic_device(idx))
            mic_menu.addAction(action)

        menu.addSeparator()
        # 自动复制选项
        auto_copy_action = QAction("自动复制文字", self)
        auto_copy_action.setCheckable(True)
        auto_copy_action.setChecked(self.auto_copy)
        auto_copy_action.triggered.connect(self.toggle_auto_copy)
        menu.addAction(auto_copy_action)

        # 历史记录查看选项
        history_action = QAction("查看历史记录", self)
        history_action.triggered.connect(self.view_history)
        menu.addAction(history_action)
        
        # API密钥管理选项
        api_key_action = QAction("🔑 管理API密钥", self)
        api_key_action.triggered.connect(self.manage_api_keys)
        menu.addAction(api_key_action)

        menu.addSeparator()
        # 关闭窗口选项
        menu.addAction("❌ 关闭悬浮窗", self.close)
        menu.exec(self.mapToGlobal(pos))

    def get_default_mic_index(self):
        """
        获取默认麦克风设备索引
        
        返回:
            int: 默认麦克风设备索引
        """
        import sounddevice as sd
        return sd.default.device[0]

    def toggle_auto_copy(self):
        """
        切换自动复制功能状态
        
        切换auto_copy标志的状态
        """
        self.auto_copy = not self.auto_copy

    def view_history(self):
        """
        查看历史记录
        
        打开历史记录查看器对话框
        """
        dlg = HistoryViewer(self)
        dlg.exec()
        
    def manage_api_keys(self):
        """
        管理API密钥
        
        打开API密钥管理对话框
        """
        dlg = APIKeyDialog(self)
        dlg.exec()

    def change_model(self, model_name):
        """
        切换Whisper模型
        
        参数:
            model_name: 要切换的模型名称

        
        卸载当前模型，加载新模型并更新UI显示
        """
        self.model_name = model_name
        self.label.setPlainText(f"🔄 正在切换模型为：{model_name} ...")
        
        # 先卸载当前模型
        if self.model is not None:
            self.label.setPlainText(f"🔄 正在卸载当前模型...")
            self.model_manager.unload_model()
            self.model = None
        
        # 加载新模型
        self.model = self.model_manager.load_model(model_name)
        self.label.setPlainText(f"✅ 模型已切换为：{model_name}")

    def change_mic_device(self, device_index):
        """
        切换麦克风设备
        
        参数:
            device_index: 要切换的麦克风设备索引
        
        创建新的录音器实例并更新UI显示
        """
        self.recorder = AudioRecorder(device_index)
        self.recorder.finished.connect(self.on_recorded)
        self.label.setPlainText("✅ 已切换麦克风设备")

    def mousePressEvent(self, event):
        """
        鼠标按下事件处理
        
        参数:
            event: 鼠标事件
        
        记录窗口拖动起始位置
        """
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        """
        鼠标移动事件处理
        
        参数:
            event: 鼠标事件
        
        实现窗口拖动功能
        """
        if event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()
