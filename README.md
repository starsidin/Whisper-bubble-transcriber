# 🎙️ Whisper 悬浮窗语音输入助手  
**Whisper Floating Speech Input Assistant**

一个简单易用的 Whisper 语音转文字（Speech-to-Text, STT）桌面悬浮窗程序，支持本地部署（Windows），数据更安全，适用于快捷语音输入场景。  
A lightweight, local-first floating window tool for voice-to-text using OpenAI Whisper — optimized for quick voice input on Windows.

基于 [OpenAI Whisper](https://github.com/openai/whisper)，录音识别后文字自动复制到剪贴板，并以聊天气泡形式显示在界面上。  
Built with [OpenAI Whisper](https://github.com/openai/whisper), it records your voice, transcribes it locally, auto-copies the result, and shows it in a chat-bubble style window.

---

### 🚀 推荐模型 | Recommended Model

建议使用 `turbo` 或 `large-v3` 模型以获得更高准确率，特别适用于中英文混合语音输入。  
It is highly recommended to use `turbo` or `large-v3` for better accuracy, especially for mixed Chinese-English input.

- ✅ `turbo` 最低配置要求：显存 VRAM ≥ 6GB  
  Minimum for `turbo`: VRAM ≥ 6GB

- ✅ 推荐配置：VRAM ≥ 8GB  
  Recommended: VRAM ≥ 8GB

如果配置较低，可切换使用较小模型，或考虑接入国内免费大模型（开发中）。  
Lower-end devices can use smaller models, or consider future integration of local Chinese large models (WIP).

---

## 🎯 功能特性 | Features

![功能图1](https://github.com/user-attachments/assets/805b7edc-8c0d-417d-a9e7-c3dfee018605)

- 🎤 一键悬浮录音  
  One-click floating voice recorder

- 🧠 支持 Whisper 本地模型 (`tiny`, `base`, `small`, `medium`, `large-v3`, `turbo`)  
  Supports local Whisper models (including turbo)

- 🌐 中英文自动识别  
  Seamless Chinese-English transcription

- 🔁 自动将繁体转换为简体（OpenCC）  
  Auto converts Traditional Chinese → Simplified Chinese (via OpenCC)

- 📋 自动复制识别文字到剪贴板  
  Auto copy transcription to clipboard

- 💬 气泡式文本展示  
  Chat-bubble style result display

- 🧩 右键切换模型  
  Right-click to switch model on the fly

- 🌈 无边框、圆角、可拖动、置顶悬浮窗  
  Borderless, rounded, draggable, always-on-top UI

![功能图2](https://github.com/user-attachments/assets/274580f7-42c2-4e82-8be5-b1167c2c1792)

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

## ✅ 使用方法

1. 运行后，会出现一个小型悬浮窗
2. 点击按钮 🎙️ 开始录音 开始说话
3. 再次点击 🛑 停止录音 结束录音
4. 识别结果会显示在界面，并自动复制到剪贴板
5. 右键弹出菜单，可选择模型或关闭程序
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

📜 历史记录窗口（可查看并复制以前的识别结果）
Recognition history viewer (view/copy past results)

☁️ 模型 API 模式（轻量版，无需本地模型）
Cloud-based Whisper API option for lightweight use


## 欢迎大家开发想要的功能，或对需要的功能进行留言
