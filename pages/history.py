import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import maliang
from maliang import *

from typing import Callable

from lib.maliang_patch import patch
patch()
from lib.history import History


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
        
        self.cv=Canvas(cv)
        self.cv.place(x=0,y=y,width=300,height=150)
        
        self.y = y
        mark = '❌' if self.err else '= '
        self.text = maliang.Text(self.cv, (20, 0), text=f'{self.ev} {mark}{self.res}', fontsize=16)
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
    def _on_history_destroy(self, item: VisionHistory):
        # 从列表中安全移除被删除的项，并把下方项上移
        if item in self.history:
            idx = self.history.index(item)
            self.history.remove(item)
            for i in self.history[idx:]:
                i.set_y(i.y - 30)

    def update(self, history: list[History]):
        for i in self.history:
            i.text.destroy()
            i.fill_btn.destroy()
            i.remove_btn.destroy()
        self.history=[]
        y = 40
        for i in history:
            self.history.append(VisionHistory(
                i.ev,i.err,i.res,self.cv,y,self.fill_history,
                self._on_history_destroy))
            y += 30

    def __init__(
        self,
        root: Tk,
        history: list[History],
        fill_history: Callable[[str, bool | None, str], None],
    ):
        self.fill_history = fill_history
        self.history:list[VisionHistory]=[]
        self.win = Toplevel(root, (300, 150), title='历史记录 - CalculatorMax')
        self.win.center()
        self.win.topmost(True)
        self.win.focus_force()
        self.win.resizable(False, False)

        self.cv = Canvas(self.win)
        self.cv.place(width=300, height=150, x=0, y=0)

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
    root.mainloop()
