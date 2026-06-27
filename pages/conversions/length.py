import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import maliang
from maliang import *

from lib.core import calc,bf
from lib.history import History
from lib.maliang_patch import patch
patch()


UNITS={
	'🇺🇳公制':{
	   '🇺🇳纳米（nm）':bf(bf('0.001')/1000/1000),
	   '🇺🇳微米（μm）': bf('0.001')/1000,
	   '🇺🇳毫米（mm）': bf('0.001'),
	   '🇺🇳厘米（cm）': bf('0.01'),
	   '🇺🇳分米（dm）': bf('0.1'),
	   '🇺🇳米（m）': bf(1),
	   '🇺🇳千米（km）': bf(1000),
	},
	   
	'🇨🇳市制':{ 
	   '🇨🇳毫（市制）': bf('0.0001')/3,
	   '🇨🇳厘（市制）': bf('0.001')/3,
	   '🇨🇳分（市制）': bf('0.01')/3,
	   '🇨🇳寸（市制）': bf('0.1')/3, 
	   '🇨🇳尺（市制）': bf(1)/3,
	   '🇨🇳丈（市制）': bf(10)/3,
	   '🇨🇳引（市制）': bf(100)/3,
	   '🇨🇳里（市制）': bf(500),
	},
	   
	'🇬🇧英制':{
		'🇬🇧密耳（mil）':bf('2.54')*bf('0.01')/1000,
	   '🇬🇧英寸（in）': bf('2.54')*bf('0.01'),
	   '🇬🇧英尺（ft）': bf('0.3048'),
	   '🇬🇧码（yd）': bf('0.9144'),
	   '🇬🇧英寻（fm）':bf('1.8288'),
	   '🇬🇧链（ch）':bf('20.1168'),
	   '🇬🇧英里': bf('1609.344'),
	   '🇬🇧海里': bf('1852')
	},
 
	'':{
		
	}
}

	
def main(root:Tk|Toplevel):
	win=Toplevel(root,(300,150),title='长度单位换算 - CalculatorMax')
	win.focus_force()
	win.topmost(True)

	cv=Canvas(win)
	cv.place(width=300,height=150,x=0,y=0)

	maliang.Text(cv,(20,20),text='长度单位换算',weight='bold')

	InputBox(cv,(20,50),(100,30))
	Button(cv,(280,50),(50,30),anchor='ne',justify='center',fontsize=16)

	maliang.Text(cv,(60,150))
if __name__=='__main__':
	root=Tk((400,240))
	root.topmost(True)
	
	cv=Canvas(root)
	cv.place(width=400,height=240,x=0,y=0)
	
	maliang.Text(cv,(20,20),text='CalculatorMax length converter page\nIt should be opening on a separate window.')
	
	root.after_idle(lambda:main(root))
	root.mainloop()