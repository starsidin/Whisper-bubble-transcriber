> ⚠️ **重要通知：项目已重定向与全面升级** ⚠️  
> **本仓库已停止更新，后续的全新版本将不再在此库发布！** 新版本仓库链接将在后续发布，敬请期待。

## 🚀 新版本升级亮点预告
为了提供更出色的体验，我们正在进行底层的全面重构：
1. **核心模型全面升级**：当前版本主要基于 **[OpenAI Whisper](https://github.com/openai/whisper)** 与 **[FunASR (阿里达摩院模型)](https://github.com/modelscope/FunASR)**；后续的新版本将全面接入更强大的 **[通义千问 ASR (Qwen-Audio / SenseVoice)](https://github.com/FunAudioLLM/SenseVoice)** 模型，带来更极致的识别准确率和性能。
2. **前后端分离架构**：打破现有的单体架构，拆分为**独立的前端服务**与**后端服务**。
3. **极致轻量的前端**：得益于前后端分离，前端应用将大幅减负，不再需要庞大的本地环境依赖，资源占用极低。
4. **一键开箱即用**：我们将直接提供打包好的 **Release 独立运行版本**，无需繁琐的 Python 环境和依赖配置，支持一键下载、直接使用！

## 📌 相关模型与技术引用 (References & SEO)
为了方便大家学习和搜索引擎收录，以下是本项目及后续版本涉及的核心技术栈与热门引用：
- **Whisper**: [https://github.com/openai/whisper](https://github.com/openai/whisper) - OpenAI 强大的多语言语音识别与翻译系统。
- **FunASR**: [https://github.com/modelscope/FunASR](https://github.com/modelscope/FunASR) - 阿里达摩院开源的端到端语音识别工具包。
- **通义千问 ASR (SenseVoice)**: [https://github.com/FunAudioLLM/SenseVoice](https://github.com/FunAudioLLM/SenseVoice) - 阿里通义千问团队开源的多语言语音大模型，新版核心引擎。
- **热门话题关键字**: `语音转文字`, `Speech-to-Text`, `STT`, `ASR`, `自动语音识别`, `桌面悬浮窗录音`, `AI语音助手`, `前后端分离`, `一键部署`, `效率工具`, `开源语音识别`, `本地化部署`.

---
# 🎙️ Whisper 悬浮窗语音输入助手  
**Whisper Floating Speech Input Assistant**

一个简单易用的 Whisper模型语音转文字（Speech-to-Text, STT）桌面悬浮窗程序，支持本地部署（Windows），数据更安全，适用于快捷语音输入场景。  
A lightweight, local-first floating window tool for voice-to-text using OpenAI Whisper — optimized for quick voice input on Windows.

录音识别后文字自动复制到剪贴板，并以聊天气泡形式显示在界面上。  基于 [OpenAI Whisper](https://github.com/openai/whisper)
it records your voice, transcribes it locally, auto-copies the result, and shows it in a chat-bubble style window.

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

## 🎯 功能特性 | Features 0.0.2

![image](https://github.com/user-attachments/assets/76a60537-4afd-47c6-83ee-e5dcc0af1134)


- 🎤 一键悬浮录音：支持麦克风或者虚拟音频输入  

- 🧠 支持 Whisper 本地模型 (`base`, `large-v3`, `turbo`)  

- 🌐 中英文自动识别  

- 📋 自动复制识别文字到剪贴板，增加在右键菜单中取消自动复制的功能  

- 💬 右键菜单中历史记录自动保存查看  

- 🧩 右键切换模型  

- 🌈 无边框、圆角、可拖动、置顶悬浮窗  

![image](https://github.com/user-attachments/assets/41ac331e-7515-4275-b5c0-6f7ad2792e57)


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
注意：如果系统没有音频输入设备（麦克风、虚拟音频输入）可能会无法打开
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
• 如果需要录制屏幕音，需要虚拟声卡，我用的是https://vb-audio.com/Cable/，在屏幕右下方喇叭选择相应名称扬声器即可捕获声音。 
• 中文标点符号可能无法正确添加

## ✅ 即将添加的功能 | Coming Soon
🧠 支持其他模型

⌨️ 添加快捷键支持（如 F9 开始/停止）


📌 支持翻译到目标语言


☁️ 模型 API 模式（轻量版，无需本地模型）


流式识别、断句、一键翻译。
## 欢迎大家开发想要的功能，或对需要的功能进行留言
