import threading
import webview
from server import run_server, app


def start_server():
    """在后台线程启动 WSGI 服务器"""
    run_server(debug=False, port=5000)


def main(debug:bool=False):
    # 在后台线程启动服务器
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()
    
    # 创建 PyWebview 窗口，加载本地服务器页面
    window = webview.create_window(
        title='CalculatorMax',
        url=app,
        width=1200,
        height=800,
    )
    def on_resized(window):
        # 只有在 debug 模式下这行代码才显得必要
        # 它会在调整大小结束后，强行把页面拉回来
        window.evaluate_js('document.documentElement.scrollTop = 0;')

    if debug:
        # 绑定事件
        window.events.resized += on_resized
    # 启动 webview
    webview.start(debug=debug)


if __name__ == '__main__':
    main(False)
