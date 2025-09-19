# devdocs 使用规范及对话记录

## 文件说明

- `speech_input_example.py`：语音输入转换为算式文本的示例。
- `speech_output_example.py`：将计算结果通过语音播报的示例。
- `ocr_example.py`：识别图片上的算式并输出文本的 OCR 示例。
- `devdocs_conversation.md`：本次对话及文件使用说明。

## 安装推荐扩展包

语音输入：
- SpeechRecognition (`pip install SpeechRecognition`)
- PyAudio (`pip install pyaudio`)

语音播报：
- pyttsx3 (`pip install pyttsx3`)
- 或 gTTS (`pip install gTTS`，需联网)

OCR图片识别：
- pytesseract (`pip install pytesseract`) 需安装 [Tesseract OCR](https://github.com/tesseract-ocr/tesseract)
- Pillow (`pip install Pillow`)
- opencv-python (`pip install opencv-python`)

## 对话记录摘要

- 用户提问如何为 CalculatorMax 增加语音和图片算式识别功能。
- 推荐了 SpeechRecognition、pyttsx3、gTTS、pytesseract、opencv-python、Pillow 等主流 Python 扩展包。
- 分别给出了三个场景的代码示例，并建议如何集成和注意事项。
- 用户要求将所有代码及对话规范文档集成到新分支 devdocs。

## 备注

- 语音输入需麦克风设备，部分环境需安装 PortAudio 支持。
- 语音播报中文效果依赖系统语音库，Windows 支持较好。
- OCR 需安装 Tesseract 软件，环境变量需配置.