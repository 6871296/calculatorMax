import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import maliang
from maliang import *

import lib.settings as settings
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
    Switch(cv,(20,50),40,default=settings.get('ignoreClipboardOverwritingWarning'),command=lambda e:settings.set('ignoreClipboardOverwritingWarning',e))
    maliang.Text(cv,(70,50),text='忽略剪贴板覆盖警告',fontsize=16)

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
