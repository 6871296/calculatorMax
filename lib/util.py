from maliang import *

import sys
import ctypes
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from lib.maliang_patch import patch
from lib.betterfloat import BetterFloat

# Common color representations accepted by maliang
#Color = Union[str, tuple[int, int, int], tuple[int, int, int, int]]

def _screen_size_px(win: Tk | Toplevel) -> tuple[int, int]:
	"""获取屏幕的物理像素尺寸（面板原生分辨率）。

	macOS 上 ``winfo_screenwidth()`` 返回的是逻辑点（pt）而非物理像素；
	且当前渲染模式（如 1470x956 的缩放模式）的物理像素 (2940x1912)
	也不是面板原生值。遍历显示模式并取带 Native 标志 (0x02000000) 的
	模式，得到面板原生分辨率（如 2560x1664），与公式的分母保持一致。
	"""
	if sys.platform == 'darwin':
		try:
			cg = ctypes.CDLL('/System/Library/Frameworks/CoreGraphics.framework/CoreGraphics')
			cf = ctypes.CDLL('/System/Library/Frameworks/CoreFoundation.framework/CoreFoundation')

			cg.CGMainDisplayID.restype = ctypes.c_uint32
			cg.CGDisplayCopyAllDisplayModes.argtypes = [ctypes.c_uint32, ctypes.c_void_p]
			cg.CGDisplayCopyAllDisplayModes.restype = ctypes.c_void_p
			cg.CGDisplayModeGetPixelWidth.argtypes = [ctypes.c_void_p]
			cg.CGDisplayModeGetPixelWidth.restype = ctypes.c_size_t
			cg.CGDisplayModeGetPixelHeight.argtypes = [ctypes.c_void_p]
			cg.CGDisplayModeGetPixelHeight.restype = ctypes.c_size_t
			cg.CGDisplayModeGetIOFlags.argtypes = [ctypes.c_void_p]
			cg.CGDisplayModeGetIOFlags.restype = ctypes.c_uint32

			cf.CFArrayGetCount.argtypes = [ctypes.c_void_p]
			cf.CFArrayGetCount.restype = ctypes.c_long
			cf.CFArrayGetValueAtIndex.argtypes = [ctypes.c_void_p, ctypes.c_long]
			cf.CFArrayGetValueAtIndex.restype = ctypes.c_void_p
			cf.CFRelease.argtypes = [ctypes.c_void_p]

			display = cg.CGMainDisplayID()
			modes = cg.CGDisplayCopyAllDisplayModes(display, None)
			if modes:
				native = None
				for i in range(cf.CFArrayGetCount(modes)):
					mode = cf.CFArrayGetValueAtIndex(modes, i)
					if cg.CGDisplayModeGetIOFlags(mode) & 0x02000000:
						native = (int(cg.CGDisplayModeGetPixelWidth(mode)),
						          int(cg.CGDisplayModeGetPixelHeight(mode)))
						break
				cf.CFRelease(modes)
				if native:
					return native
		except Exception:
			pass
	return win.winfo_screenwidth(), win.winfo_screenheight()


def set_window_scale(win: Tk | Toplevel, factor: BetterFloat) -> None:
	"""按倍率程序化缩放窗口（1.0 为设计尺寸）。

	大于 1 放大，小于 1 缩小；窗口内容（画布、控件、字体）会随
	maliang 的自动缩放机制同步调整。可在任意时刻调用，例如快捷键
	或按钮命令::

	    set_window_scale(root, 1.5)   # 放大到 1.5 倍
	    set_window_scale(root, 0.75)  # 缩小到 75%
	    set_window_scale(root, 1.0)   # 恢复设计尺寸
	"""
	factor = max(0.1, factor)
	win.geometry(size=(round(win.init_size[0]*factor), round(win.init_size[1]*factor)))


def wrap_display_text(text: str, font, max_width: int) -> str:
	"""按像素宽度对文本折行，返回用换行符连接的多行文本。

	tkinter Canvas 的文本只在空白处折行，无法折断连续的长数字，
	因此这里用字体度量逐字符贪心折行。
	"""
	lines: list[str] = []
	for raw_line in text.split('\n'):
		line = ''
		for ch in raw_line:
			if line and font.measure(line + ch) > max_width:
				lines.append(line)
				line = ch
			else:
				line += ch
		lines.append(line)
	return '\n'.join(lines)


def apply_screen_scale(win: Tk | Toplevel, design_width: int, design_height: int) -> tuple[int, int]:
	"""按屏幕尺寸等比缩放窗口，并使其在屏幕上居中。

	计算规则：宽 = 原宽 / 2560 * 屏幕宽度，高 = 原高 / 1670 * 屏幕高度。
	窗口需先以设计尺寸创建，再调用本函数；之后 maliang 会按设计尺寸
	与实际尺寸的比例自动缩放窗口内的所有 widget。
	"""
	screen_w, screen_h = _screen_size_px(win)
	width = max(1, round(design_width * screen_w / 2560))
	height = max(1, round(design_height * screen_h / 1670))
	win.geometry(size=(width, height), position=((screen_w - width) // 2, (screen_h - height) // 2))

	def _initial_zoom() -> None:
		# 窗口首次显示时 Canvas 可能还未 viewable，导致 Tk._zoom 里的
		# 自动缩放被跳过；在 Map 事件及稍后再次强制对整棵 Canvas 树
		# 应用一次缩放。
		def zoom_tree(canvas) -> None:
			canvas.zoom()
			for child in canvas.canvases:
				zoom_tree(child)

		for canvas in tuple(win.canvases):
			zoom_tree(canvas)

	win.bind("<Map>", lambda _event: _initial_zoom(), add="+")
	win.after(200, _initial_zoom)
	return width, height

class ChooseBox:
	def __init__(self, root: Tk | Toplevel, width: int, title: str, wintitle: str | None = None, info: str | None = None, infoheight: int = 20, *, btns: tuple[str]):
		if wintitle is None:
			wintitle = title
		win_size = (width, (40 + infoheight)+len(btns)*40)
		self.win = Toplevel(root, win_size, title=wintitle, grab=True)
		self.win.focus_force()
		self.win.topmost(True)
		apply_screen_scale(self.win, *win_size)
		self.win.resizable(True, True)

		cv = Canvas(self.win, auto_zoom=True, keep_ratio='min')
		cv.place(width=width, height=(40 + infoheight)+len(btns)*40, x=0, y=0)

		self.title = Text(cv, (10, 10), text=title, weight='bold', fontsize=14, justify='center')
		if info is not None:
			self.info = Text(cv, (10, 30), text=info, fontsize=11)
			Y = 40 + infoheight
		else:
			self.info = None
			Y = 40

		self.btns: list[Button] = []
		self._result: int | None = None
		for i, text in enumerate(btns):
			self.btns.append(Button(
				cv, (10, Y + i * 40), size=(width - 20, 30), text=text,fontsize=16,
				command=lambda i=i: self._on_choose(i)))

	def _on_choose(self, index: int) -> None:
		self._result = index
		self.win.destroy()

	def wait_answer(self) -> int | None:
		'''Show the ChooseBox and wait till the user chooses. Returns the index of the choice.'''
		self._result = None
		self.win.wait_window()
		return self._result


if __name__ == '__main__':
	patch()
	root = Tk((400, 240))
	root.topmost(True)
	root.center()
	root.resizable(False, False)

	cv = Canvas(root)
	cv.place(width=400, height=240, x=0, y=0)

	Text(cv, (10, 10), text='ChooseBox test')

	print(ChooseBox(root, 200, 'TestTitle', 'Choosebox Test', 'TestInfo', btns=('TestBtn1', 'TestBtn2', 'TestBtn3')).wait_answer())