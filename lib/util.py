from maliang import *

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from lib.maliang_patch import patch

# Common color representations accepted by maliang
#Color = Union[str, tuple[int, int, int], tuple[int, int, int, int]]

def apply_screen_scale(win: Tk | Toplevel, design_width: int, design_height: int) -> tuple[int, int]:
	"""按屏幕尺寸等比缩放窗口，并使其在屏幕上居中。

	计算规则：宽 = 原宽 / 2560 * 屏幕宽度，高 = 原高 / 1670 * 屏幕高度。
	窗口需先以设计尺寸创建，再调用本函数；之后 maliang 会按设计尺寸
	与实际尺寸的比例自动缩放窗口内的所有 widget。
	"""
	screen_w = win.winfo_screenwidth()
	screen_h = win.winfo_screenheight()
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

		cv = Canvas(self.win, auto_zoom=True)
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