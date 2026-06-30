import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import maliang
from maliang import *

from lib.core import calc,bf
from lib.betterfloat import BetterFloat
from lib.history import History
from lib.util import ChooseBox
from lib.maliang_patch import patch
from maliang.core.virtual import Feature
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
 
	'🌌天文':{
		"🌌天文单位（au）":bf(149597870700),
		"🌠光年（ly）":bf(9.4607304725808)*BetterFloat.pow(10,15),
		"🌌秒差距（pc）":bf(3.085677581)*BetterFloat.pow(10,16),
		"🌌千秒差距（kpc）":bf(3.085677581)*BetterFloat.pow(10,16)*BetterFloat.pow(10,3),
		"🌌兆秒差距（Mpc）":bf(3.085677581)*BetterFloat.pow(10,16)*BetterFloat.pow(10,6),
		"☀️名义太阳半径（R⊙N/N⊙）":bf(6.957)*BetterFloat.pow(10,8),
		"🪐名义木星赤道半径（R_jup,N）":bf(7.1492)*BetterFloat.pow(10,7),
		"🌏名义地球赤道半径（R_E,N）":bf(6.3781)*BetterFloat.pow(10,6)
	}
}

def _convert(value:BetterFloat,unit_from:tuple[str,str],unit_to:tuple[str,str])->BetterFloat:
	return value*UNITS[unit_from[0]][unit_from[1]]/UNITS[unit_to[0]][unit_to[1]]
	
def main(root:Tk|Toplevel):
	win=Toplevel(root,(300,150),title='长度单位换算 - CalculatorMax')
	win.center()
	win.focus_force()
	win.topmost(True)

	cv=Canvas(win)
	cv.place(width=300,height=150,x=0,y=0)
 
	def choose_unit()->tuple[str|None,str|None]:
		category_keys = tuple(UNITS.keys())
		choice = ChooseBox(win, 200, '选择单位', btns=category_keys).wait_answer()
		if choice is not None:
			category = category_keys[choice]
			unit_keys = tuple(UNITS[category].keys())
			choice2 = ChooseBox(win, 200, category, '选择单位', btns=unit_keys).wait_answer()
			if choice2 is not None:
				return category, unit_keys[choice2]
			else:
				return choose_unit()
		return None, None
   
	unit1:tuple[str,str]=()
	unit2:tuple[str,str]=()
 
	def convert():
		if not unit1 or not unit2:
			return
		value = unit1_input.get()
		if value == '':
			return
		try:
			unit2_input.set(str(_convert(bf(value), unit1, unit2)))
		except Exception:
			pass

	def setunit1():
		nonlocal unit1
		choice,choice2=choose_unit()
		if choice is None or choice2 is None:
			return
		unit1=(choice,choice2)
		unit1_chooser.set(choice2)
		convert()
	def setunit2():
		nonlocal unit2
		choice,choice2=choose_unit()
		if choice is None or choice2 is None:
			return
		unit2=(choice,choice2)
		unit2_chooser.set(choice2)
		convert()
  
	def swap():
		nonlocal unit2,unit1
		tmp=unit2
		unit2=unit1
		unit1=tmp

		convert()

	maliang.Text(cv,(20,15),text='长度单位换算',weight='bold')
 
	Button(cv,(150,10),(30,30),text='⥮',weight='bold',fontsize=20,command=swap)

	unit1_input=InputBox(cv,(20,50),(100,30))
	unit1_chooser=Button(cv,(280,50),(150,30),anchor='ne',justify='center',fontsize=16,text='未选择',command=setunit1)
 
	Text(cv,(150,85),text='=',fontsize=10,justify='center')
 
	unit2_input=InputBox(cv,(20,100),(100,30))
	# 替换为默认 Feature，保持正常外观但不再响应点击/键盘事件（只读展示）
	unit2_input.feature = Feature(unit2_input)
	unit2_chooser=Button(cv,(280,100),(150,30),anchor='ne',justify='center',fontsize=16,text='未选择',command=setunit2)
 
	Text(cv,(150,130),text='换算结果仅供参考',fontsize=10,justify='center',anchor='n')

	# 在输入框聚焦时按回车自动重新换算
	cv.bind("<KeyPress-Return>", lambda event: convert())

	def _set_input_focus():
		unit1_input.update('active')
		cv.focus_set()
		if unit1_input.texts:
			cv.focus(unit1_input.texts[0].items[0])
	win.after_idle(_set_input_focus)
if __name__=='__main__':
	root=Tk((400,240))
	root.topmost(True)
	
	cv=Canvas(root)
	cv.place(width=400,height=240,x=0,y=0)
	
	Text(cv,(20,20),text='CalculatorMax length converter page\nIt should be opening on a separate window.')
	
	root.after_idle(lambda:main(root))
	root.mainloop()