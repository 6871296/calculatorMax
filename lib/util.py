from maliang import *

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from lib.maliang_patch import patch

# Common color representations accepted by maliang
#Color = Union[str, tuple[int, int, int], tuple[int, int, int, int]]

class ChooseBox:
	def __init__(self, root: Tk | Toplevel, width: int, title: str, wintitle: str | None = None, info: str | None = None, infoheight: int = 20, *, btns: tuple[str]):
		if wintitle is None:
			wintitle = title
		self.win = Toplevel(root, (width, (40 + infoheight)+len(btns)*40), title=wintitle, grab=True)
		self.win.focus_force()
		self.win.topmost(True)
		self.win.center()
		self.win.resizable(False, False)

		cv = Canvas(self.win)
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