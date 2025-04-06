# 🎙️ 悬浮窗语音输入助手 （Whisper+阿里模型版）

一个简单易用的语音转文字（Speech-to-Text, STT）桌面悬浮窗程序，支持本地部署Whisper\modelscope模型（Windows），数据更安全，适用于快捷语音输入场景。  
A lightweight, local-first floating window tool for voice-to-text using OpenAI Whisper — optimized for quick voice input on Windows.

录音识别后文字自动复制到剪贴板，并以聊天气泡形式显示在界面上。  基于 [OpenAI Whisper](https://github.com/openai/whisper)

---
![image](https://github.com/user-attachments/assets/bc7f3880-6049-45d0-8825-d830f2c52513)

### 🚀 推荐模型 | Recommended Model

多语言建议使用 `turbo` 或 `large-v3` 模型以获得更高准确率，特别适用于中英文混合语音输入。  
单一中文建议使用达摩院模型 `speech_paraformer-large_asr_nat-zh-cn-16k-common-vocab8404-pytorch`算力要求低，标点符号准确。
- ✅ `turbo` 最低配置要求：显存 VRAM ≥ 6GB  
- ✅ `paraformer‘` 最低配置要求：显存 VRAM ≥ 4GB
- ✅ 推荐配置：VRAM ≥ 8GB  

如果配置较低，可切换使用较小模型，或使用达摩院模型。  

---

## 🎯 功能特性 | Features 0.0.2


- 🎤 一键悬浮录音  

- 🧠 支持 Whisper 本地模型 (`base`, `large-v3`, `turbo`)、达摩院paraformer长文本版+标点不全+起止点识别。  

- 🌐 中英文自动识别（whisper）  

- 📋 自动复制识别文字到剪贴板，可以在右键菜单中取消  

- 💬 右键菜单中历史记录自动保存查看  

- 🧩 右键切换模型  

- 🌈 无边框、圆角、可拖动、置顶悬浮窗  

---

## 📦 安装依赖 | Install Requirements

确保你的系统安装了 Python ≥ 3.8  
Make sure Python 3.8 or higher is installed.

安装依赖：

```bash
pip install -r requirements.txt
```
注意：
如果安装失败whisper的安装方法详见官方文档：https://github.com/openai/whisper
whisper必须依赖ffmpeg，在官网下载压缩包后，解压缩并添加到系统PATH中才能正常使用，
安装后在命令行输入ffmpeg弹出版本信息就是安装完成了
modelscope的安装在https://www.modelscope.cn/docs/intro/quickstart
pip install modelscope之后需要安装依赖用pip install modelscope[framework]
pip install modelscope[audio]
## ✅ 使用方法

1. 运行后，会出现一个小型悬浮窗
2. 点击按钮 🎙️ 开始录音 开始说话
3. 再次点击 🛑 停止录音 结束录音
4. 识别结果会显示在界面，并自动复制到剪贴板
5. 右键弹出菜单，可选择模型、选择麦克风、查看历史记录、选择是否自动复制或关闭程序
￼
## 💡 注意事项
• 默认使用 GPU（若可用），否则回退到 CPU
• 模型将自动下载缓存到本地（首次运行可能稍慢）
• 若需更高准确率，可切换为 large-v3 模型（需要较高显存）

## ✅ 即将添加的功能 | Coming Soon
🧠 支持其他模型

⌨️ 添加快捷键支持（如 F9 开始/停止）
Global hotkey support (e.g., F9 to start/stop recording)

📌 支持粘贴到目标应用（如微信、Word）
Auto-paste to target apps (e.g., WeChat, Word)


☁️ 模型 API 模式（轻量版，无需本地模型）
Cloud-based Whisper API option for lightweight use

流式识别、一键翻译、音视频识别等功能
## 欢迎大家开发想要的功能，或对需要的功能进行留言
