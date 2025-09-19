import pyttsx3

engine = pyttsx3.init()
engine.setProperty('rate', 150)  # 语速
engine.setProperty('voice', 'zh')  # 中文播报，实际效果依赖系统语音库

text = "计算结果是：一百二十三点四五六"
engine.say(text)
engine.runAndWait()
