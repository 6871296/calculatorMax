import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import maliang
from maliang import *

from typing import Callable

from lib.maliang_patch import patch
patch()
from lib.history import History
from lib.util import apply_screen_scale, wrap_display_text

import tkinter.font
from maliang.core import configs

# 历史条目的折行宽度（设计坐标像素），避开右侧的操作按钮
_WRAP_WIDTH = 200


class VisionHistory(History):
	def __init__(
		self,
		ev: str,
		err: bool | None,
		res: str,
		cv: Canvas,
		y: int,
		fill_history: Callable,
		on_destroy: Callable[['VisionHistory'], None],
	):
		super().__init__(ev, err, res)
		
		self.cv=Canvas(cv,auto_zoom=True,keep_ratio='min')
		self.cv.place(x=0,y=y,width=300,height=150)
		
		self.y = y
		mark = '❌' if self.err else '= '
		self.text = maliang.Text(self.cv, (20, 0), text='', fontsize=16)
		wrapped = wrap_display_text(f'{self.ev} {mark}{self.res}', self.text.texts[0].font, _WRAP_WIDTH)
		self.text.set(wrapped)
		# 条目占用的设计高度：首行 30，每折一行加 22
		self.step = 30 + wrapped.count('\n')*22
		self.fill_btn = maliang.Button(
			self.cv, (260, 0), anchor='ne', size=(20, 20), text='✍︎',
			command=lambda: fill_history(ev, err, res))
		self.remove_btn = maliang.Button(
			self.cv, (290, 0), anchor='ne', size=(20, 20), text='🗑️',
			command=self.destroy, fontsize=14)
		self.on_destroy = on_destroy

	def set_y(self,y:int):
		self.y = y
		self.cv.place(x=0,y=y,width=300,height=150)

	def destroy(self):
		self.on_destroy(self)
		self.cv.destroy()


class HistoryIO:
	def _entry_step(self, ev: str, err: bool | None, res: str) -> int:
		"""估算一条历史记录在设计坐标下占用的行高（首行 30，每折一行 +22）。"""
		mark = '❌' if err else '= '
		wrapped = wrap_display_text(f'{ev} {mark}{res}', self._font, _WRAP_WIDTH)
		return 30 + wrapped.count('\n')*22

	def _relayout_rows(self) -> None:
		# 子画布（历史条目）的尺寸会随窗口自动缩放（keep_ratio='min'，
		# 统一比例不拉伸），但位置不会，需要按当前统一比例手动调整
		# 条目的纵向位置。
		self.empty_text.moveto(self.win.ratios[0]/2,self.win.ratios[1]/2)
		ratio_y = min(self.win.ratios)
		for item in self.history:
			item.cv.place(x=0, y=item.y * ratio_y)

	def _on_history_destroy(self, item: VisionHistory):
		# 从列表中安全移除被删除的项，并把下方项上移
		if item in self.history:
			idx = self.history.index(item)
			removed_step = item.step
			self.history.remove(item)
			for i in self.history[idx:]:
				i.set_y(i.y - removed_step)
			self._relayout_rows()

	def update(self, history: list[History]):
		# 清空旧条目（连同条目画布一起销毁）
		for i in self.history:
			i.cv.destroy()
		self.history=[]
		if history:
			self.empty_text.forget()
			y = 40
			for i in history:
				self.history.append(VisionHistory(
					i.ev,i.err,i.res,self.cv,y,self.fill_history,
					self._on_history_destroy))
				y += self.history[-1].step
			self._relayout_rows()
			# 新建的条目按当前窗口比例立即缩放（否则要等到下次窗口尺寸变化）
			if self.cv.winfo_viewable():
				self.cv.zoom()
		else:
			# 无历史记录时显示占位文本
			self.empty_text.forget(False)

	def __init__(
		self,
		root: Tk,
		history: list[History],
		fill_history: Callable[[str, bool | None, str], None],
	):
		self.fill_history = fill_history
		self.history:list[VisionHistory]=[]
		self._font = tkinter.font.Font(family=configs.Font.family, size=-16)
		content_height = 40 + sum(self._entry_step(i.ev, i.err, i.res) for i in history)
		design_height = max(150, content_height)
		self.win = Toplevel(root, (300, design_height), title='历史记录 - CalculatorMax')
		self.win.topmost(True)
		self.win.focus_force()
		apply_screen_scale(self.win, 300, design_height)
		self.win.resizable(True, True)

		self.cv = Canvas(self.win, auto_zoom=True, keep_ratio='min')
		self.cv.place(width=300, height=content_height, x=0, y=0)

		# 窗口大小变化（如用户拖拽边框）时重新排布条目位置
		self.win.bind('<Configure>', lambda _e: self._relayout_rows(), add='+')

		self.empty_text = maliang.Text(self.cv, (150, content_height/2), text="空空如也")
		self.empty_text.forget()

		self.update(history)

		maliang.Text(self.cv, (10, 10), text='历史记录', fontsize=24, weight='bold')


if __name__ == '__main__':
	root = Tk((400, 240))
	root.topmost(True)
	root.center()
	root.resizable(False, False)

	cv = Canvas(root)
	cv.place(width=400, height=240, x=0, y=0)

	maliang.Text(cv, (20, 20), text='CalculatorMax history page\nit should be opening on a separate window.')

	root.after_idle(lambda: HistoryIO(
		root,
		[
			History('',None,''),
			History('1+1', False, '2'),
			History('1+2',False,'3'), 
			History('1=1', True, '可能不是数学算式'),
		],
		print))
	root.mainloop()
