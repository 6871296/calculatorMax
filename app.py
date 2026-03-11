import threading
import time
import webview
from server import run_server, app
from lib.logger import Logger,LogLevel

DEBUG=False#True

if DEBUG:
	Logger.loglevel=LogLevel.debug
	print('\033[0;1;34m[DEBUG MODE]Welcome to use CalculatorMax!')
else:
	print('\033[0;1;32mWelcome to use CalculatorMax!')

def start_server():
	"""在后台线程启动 WSGI 服务器"""
	run_server(debug=False, port=5000,_DEBUG=DEBUG)


def wait_for_server(url: str = "http://127.0.0.1:5000", timeout: int = 10) -> bool:
	"""等待服务器启动"""
	import urllib.request
	start_time = time.time()
	while time.time() - start_time < timeout:
		try:
			urllib.request.urlopen(url, timeout=1)
			return True
		except:
			time.sleep(0.1)
	return False


def main(debug: bool = False):
	# 在后台线程启动服务器
	server_thread = threading.Thread(target=start_server, daemon=True)
	server_thread.start()

	# 等待服务器启动
	Logger.debug("\033[0m[App debug]Starting server...")
	if not wait_for_server():
		Logger.fatal("\033[0;1;37;41m[App FATAL]Timeout when starting the server!")
		return
	Logger.info("\033[0;1;32mServer started!")

	URL='http://127.0.0.1:5000'
	WIDTH=1200
	HEIGHT=800

	# 创建 PyWebview 窗口，加载本地服务器页面
	window = webview.create_window(
		title='CalculatorMax',
		url=URL,
		width=WIDTH,
		height=HEIGHT
	)
	Logger.info('[App info]Created window CalculatorMax')
	Logger.debug(f'[App Debug]Window info: url {URL} size {WIDTH}*{HEIGHT}')
	def on_resized(window):
		# 只有在 debug 模式下这行代码才显得必要
		# 它会在调整大小结束后，强行把页面拉回来
		window.evaluate_js('document.documentElement.scrollTop = 0;')

	if debug:
		# 绑定事件
		window.events.resized += on_resized

	# 启动 webview
	webview.start(debug=debug)
	Logger.info('[App info]Window closed! Stoppng server...')
	server_thread.join(5)
	print('exited')

if __name__ == '__main__':
	Logger.info('Starting main programm...')
	main(False)
