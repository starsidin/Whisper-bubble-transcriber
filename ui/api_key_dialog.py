"""API密钥设置对话框模块

该模块提供了一个对话框，用于设置和管理不同类型的API密钥。
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QComboBox, QMessageBox, QFormLayout
)
from PyQt6.QtCore import Qt
from utils.api_keys import get_api_key, save_api_key, get_api_types

class APIKeyDialog(QDialog):
    """API密钥设置对话框
    
    提供一个界面，用于设置和管理不同类型的API密钥。
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("API密钥设置")
        self.setMinimumWidth(400)
        self.setup_ui()
        self.load_api_keys()
        
    def setup_ui(self):
        """设置对话框UI"""
        layout = QVBoxLayout(self)
        
        # 创建表单布局
        form_layout = QFormLayout()
        
        # API类型选择
        self.api_type_combo = QComboBox()
        api_types = get_api_types()
        for api_type, api_name in api_types.items():
            self.api_type_combo.addItem(api_name, api_type)
        self.api_type_combo.currentIndexChanged.connect(self.on_api_type_changed)
        form_layout.addRow("API类型:", self.api_type_combo)
        
        # API密钥输入
        self.api_key_input = QLineEdit()
        self.api_key_input.setEchoMode(QLineEdit.EchoMode.Password)  # 密码模式
        self.api_key_input.setPlaceholderText("请输入API密钥")
        form_layout.addRow("API密钥:", self.api_key_input)
        
        # 显示/隐藏密钥按钮
        self.toggle_visibility_btn = QPushButton("显示")
        self.toggle_visibility_btn.setFixedWidth(60)
        self.toggle_visibility_btn.clicked.connect(self.toggle_key_visibility)
        form_layout.addRow("", self.toggle_visibility_btn)
        
        layout.addLayout(form_layout)
        
        # 按钮布局
        button_layout = QHBoxLayout()
        
        # 保存按钮
        self.save_btn = QPushButton("保存")
        self.save_btn.clicked.connect(self.save_api_key)
        button_layout.addWidget(self.save_btn)
        
        # 取消按钮
        self.cancel_btn = QPushButton("取消")
        self.cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(button_layout)
    
    def load_api_keys(self):
        """加载当前选择的API类型的密钥"""
        current_api_type = self.api_type_combo.currentData()
        api_key = get_api_key(current_api_type)
        if api_key:
            self.api_key_input.setText(api_key)
    
    def on_api_type_changed(self):
        """API类型变更时的处理"""
        self.load_api_keys()
    
    def toggle_key_visibility(self):
        """切换API密钥的可见性"""
        if self.api_key_input.echoMode() == QLineEdit.EchoMode.Password:
            self.api_key_input.setEchoMode(QLineEdit.EchoMode.Normal)
            self.toggle_visibility_btn.setText("隐藏")
        else:
            self.api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
            self.toggle_visibility_btn.setText("显示")
    
    def save_api_key(self):
        """保存API密钥"""
        api_type = self.api_type_combo.currentData()
        api_key = self.api_key_input.text().strip()
        
        if not api_key:
            QMessageBox.warning(self, "警告", "API密钥不能为空")
            return
        
        try:
            save_api_key(api_type, api_key)
            QMessageBox.information(self, "成功", f"API密钥已保存")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "错误", f"保存API密钥失败: {e}")