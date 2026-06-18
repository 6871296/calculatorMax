from typing import Callable
from pynput.keyboard import *
from pynput import keyboard

keypress2func={}
key_alias={
	"return": "enter",
	"escape": "esc",
	"win": "cmd",
	"windows": "cmd",
	"option": "alt",
	"control": "ctrl",
	"del": "delete",
	"ins": "insert",
	"back": "backspace",
	"pgup": "page_up",
	"pgdn": "page_down",
	"capslock": "caps_lock",
	"numlock": "num_lock",
	"scrolllock": "scroll_lock",
	"prtsc": "print_screen",
	"printscreen": "print_screen",
}

class KeyNotFoundError(Exception):
	'''Error raised when not finding a key in pynput tools.'''
	def __init__(self,key):
		self.key=key
		super().__init__(self.__str__())
	def __str__(self):
		return f'No such key in pynput_tools called {self.key}'

def _str2key(key_str: str):
	"""
	将字符串转换为对应的 pynput.keyboard.Key 枚举常量。
	如果是普通字符（如 'a', '1'），则返回 KeyCode 对象。
	如果无法识别，返回 None。
	"""
	if not key_str or not isinstance(key_str, str):
		return None

	# 1. 处理空格字符的特殊情况
	if key_str == " ":
		return keyboard.Key.space

	# 2. 标准化字符串：去空格、转小写、将空格替换为下划线
	# 例如："Left Ctrl" -> "left_ctrl"，"PAGE DOWN" -> "page_down"
	normalized = key_str.strip().lower().replace(" ", "_")

	# 3. 常见按键别名映射（根据日常习惯补充）
	aliases = key_alias
	
	# 如果是别名，替换为 pynput 的标准名称
	if normalized in aliases:
		normalized = aliases[normalized]

	# 4. 尝试在 Key 枚举中动态查找
	try:
		# Key['enter'] 等价于 Key.enter
		return keyboard.Key[normalized]
	except KeyError:
		pass

	# 5. 如果在功能键中找不到，检查是否是单字符（字母/数字/符号）
	if len(key_str) == 1:
		return keyboard.KeyCode.from_char(key_str)

	# 6. 都不匹配，返回 None
	raise KeyNotFoundError(key_str)


def _on_key_down(key):
	name = getattr(key, 'name', None)
	if name in keypress2func:
		keypress2func[name]()

def init():
	global listener
	listener=Listener(on_press=_on_key_down)
	listener.start()
	listener.wait()
init()

def bind(key:str|Key,func:Callable):
	if isinstance(key,str):
		keypress2func[_str2key(key).name]=func
	else:
		keypress2func[key.name]=func

def unbind(key:str|Key):
	if isinstance(key,str):
		keypress2func.pop(key)
	else:
		keypress2func.pop(key.name)

def stop():
	global listener
	listener.stop()
	listener.join()