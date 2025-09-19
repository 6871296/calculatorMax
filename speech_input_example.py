import speech_recognition as sr

r = sr.Recognizer()
with sr.Microphone() as source:
    print("请说出算式：")
    audio = r.listen(source)
    try:
        text = r.recognize_google(audio, language='zh-CN')
        print("你说的是：", text)
    except sr.UnknownValueError:
        print("无法识别语音")
    except sr.RequestError as e:
        print("语音识别服务出错：", e)