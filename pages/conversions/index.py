import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import maliang
from maliang import *

from lib.core import calc
from lib.history import History
from lib.maliang_patch import patch
patch()



def main(root:Tk,history:list[History]):
	win=Toplevel(root,(300,210),title='单位换算 - CalculatorMax')
	win.focus_force()
	win.topmost(True)
	
	cv=Canvas(win)
	cv.place(width=300,height=210,x=0,y=0)
	
	maliang.Text(cv,(20,10),text='单位换算',weight='bold')
	
	[
		Button(cv,(20,40),(120,30),text='📏长度')     ,Button(cv,(280,40),(120,30),anchor='ne',text='◼️面积'),
  		Button(cv,(20,80),(120,30),text='📦体积和容积'),Button(cv,(280,80),(120,30),anchor='ne',text='⚖重量'),
		Button(cv,(20,120),(120,30),text='💰货币')      ,Button(cv,(280,120),(120,30),anchor='ne',text='🕘时间')
	]
	
	maliang.Text(cv,(5,156),text='换算结果仅供参考，日常生活中请依法使用计量单位。\n中国市制单位在历朝历代各有不同，此处市制单位以\n1959年国务院《关于统一计量制度的命令》为准',fontsize=12,justify='center')
 
if __name__=='__main__':
    root=Tk((400,240))
    root.topmost(True)
    cv=Canvas(root)
    cv.place(width=400,height=240,x=0,y=0)
    
    maliang.Text(cv,(10,10),text='CalculatorMax convertion page\nIt should be opening on a separate window.')
    
    root.after_idle(lambda:main(root,[]))
    root.mainloop()