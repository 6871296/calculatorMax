import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import maliang
from maliang import *

import lib.settings as settings
from lib.betterfloat import BetterFloat
from lib.maliang_patch import patch
patch()

from typing import *

SettingsTriggerer=Union[Switch,ToggleButton,CheckBox,RadioBox,Slider,SegmentedButton,OptionButton]

def main(root:Tk):
    win=Toplevel(root,(300,150),title='设置 - CalculatorMax')
    win.topmost(True)
    win.center()

    cv = maliang.Canvas(win)
    cv.place(width=300,height=150,x=0,y=0)

    maliang.Text(cv,(10,10),text='设置',fontsize=24,weight='bold')
    
    Switch(cv,(10,50),40,default=settings.get('ignoreClipboardOverwritingWarning'),command=lambda e:settings.set('ignoreClipboardOverwritingWarning',e))
    maliang.Text(cv,(60,50),text='忽略剪贴板覆盖警告',fontsize=16)
    
    maliang.Text(cv,(10,90),text='浮点数最高精度（位）',fontsize=16)
    precision_spin = SpinBox(cv,(180,85),(100,30),placeholder='50')
    precision_spin.set(str(settings.get('floatPrecision', 50)))

    def _sync_precision(_event=None):
        val = precision_spin.get()
        if val.isdigit():
            settings.set('floatPrecision', int(val))
            BetterFloat.set_precision(int(val))

    # 手敲数字时同步
    precision_spin.children[0].bind('<KeyRelease>', _sync_precision, auto_detect=False)
    # 按上下箭头时同步
    _orig_change = precision_spin.change
    def _change_with_sync(up: bool):
        _orig_change(up)
        _sync_precision()
    precision_spin.change = _change_with_sync

    return win


if __name__ == '__main__':
    root=Tk((400,240))
    root.topmost(True)
    root.center()

    cv=Canvas(root)
    cv.place(width=400,height=240,x=200,y=120,anchor='center')
    maliang.Text(cv,(10,10),text='CalculatorMax settings page\nit should be opening on a separate window.')

    root.after_idle(lambda:main(root))
    root.mainloop()
