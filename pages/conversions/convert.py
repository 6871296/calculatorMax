import maliang
from maliang import *

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from lib.core import bf
from lib.betterfloat import BetterFloat
from lib.util import ChooseBox
import lib.settings as settings
from lib.maliang_patch import patch

from maliang.core.virtual import Feature
from tkinter import messagebox as msgbox
from typing import Callable

import pyperclip as clip

patch()

UNITS_LENGTH={
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

def _convert(value:BetterFloat,units:dict[str,dict[str,BetterFloat]],unit_from:tuple[str,str],unit_to:tuple[str,str])->BetterFloat:
	return value*units[unit_from[0]][unit_from[1]]/units[unit_to[0]][unit_to[1]]
	
def main(root:Tk|Toplevel,units:dict[str,dict[str,BetterFloat]],title:str='长度单位换算',_convert:Callable[[BetterFloat,dict[str,dict[str,BetterFloat]],tuple[str,str],tuple[str,str]],BetterFloat]=_convert):
	win=Toplevel(root,(420,170),title=f'{title} - CalculatorMax')
	win.center()
	win.focus_force()
	win.topmost(True)

	cv=Canvas(win)
	cv.place(width=420,height=170,x=0,y=0)
 
	def choose_unit()->tuple[str|None,str|None]:
		category_keys = tuple(units.keys())
		choice = ChooseBox(win, 200, '选择单位', btns=category_keys).wait_answer()
		if choice is not None:
			category = category_keys[choice]
			unit_keys = tuple(units[category].keys())
			choice2 = ChooseBox(win, 230, category, '选择单位', btns=unit_keys).wait_answer()
			if choice2 is not None:
				return category, unit_keys[choice2]
			else:
				return choose_unit()
		return None, None
   
	unit1:tuple[str,str]=()
	unit2:tuple[str,str]=()
 
	def convert():
		if not unit1 or not unit2:
			copy_btn.style.set(fg=('gray','gray','gray'))
			res_too_big.set('')
			return
		value = unit1_input.get()
		if value == '':
			copy_btn.style.set(fg=('gray','gray','gray'))
			unit2_input.set('')
			res_too_big.set('')
			return
		try:
			unit2_input.set(str(_convert(bf(value), units, unit1, unit2)))
			copy_btn.style.set(fg=('black','black','black'))
			if len(unit2_input.get()) > 12:
				res_too_big.set('结果过大，请复制后查看')
			else:
				res_too_big.set('')
		except Exception:
			copy_btn.style.set(fg=('gray','gray','gray'))
			res_too_big.set('')

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

	copy_reset_after = None

	def copy_result():
		nonlocal copy_reset_after
		if copy_reset_after:
			win.after_cancel(copy_reset_after)

		def reset_btn():
			copy_btn.set('复制')
			copy_btn.style.set(fg=('black','black','black'))
			copy_btn.resize((50,25))

		def reset_btn_gray():
			copy_btn.set('复制')
			copy_btn.style.set(fg=('gray','gray','gray'))
			copy_btn.resize((50,25))

		result = unit2_input.get()
		if result == '':
			copy_btn.set('无法复制')
			copy_btn.style.set(fg=('red','red','red'))
			copy_btn.resize((80,25))
			copy_reset_after = win.after(1000, reset_btn_gray)
			return

		try:
			try:
				clip.paste()
			except Exception:
				pass
			else:
				if not settings.get('ignoreClipboardOverwritingWarning'):
					cb = ChooseBox(win, 200, '⚠️剪贴板中含有其他内容。', '剪贴板覆盖警告', '如果现在复制，所有的内容都将丢失。\n确定复制吗？', 30, btns=('确定','确定（不再提醒）','取消'))
					cb.btns[0].style.set(fg='white', bg=('deepskyblue','aqua','aqua'))
					ans = cb.wait_answer()
					if ans == 1:
						settings.set('ignoreClipboardOverwritingWarning', True)
					elif ans == 2 or ans is None:
						return
			clip.copy(result)
			copy_btn.set('复制成功')
			copy_btn.style.set(fg=('green','green','green'))
			copy_btn.resize((80,25))
			copy_reset_after = win.after(1000, reset_btn)
		except Exception as e:
			msgbox.showerror('复制失败', f'复制失败：{e}')
			copy_btn.set('复制失败')
			copy_btn.style.set(fg=('red','red','red'))
			copy_btn.resize((80,25))
			copy_reset_after = win.after(1000, reset_btn)
   

	maliang.Text(cv,(20,15),text=title,weight='bold')
 
	copy_btn = Button(cv,(180,12),(50,25),text='复制',fontsize=16,command=copy_result,justify='center')
	copy_btn.style.set(fg=('gray','gray','gray'))

	unit1_input=InputBox(cv,(20,50),(150,30))
	unit1_chooser=Button(cv,(400,50),(210,30),anchor='ne',justify='center',fontsize=16,text='未选择',command=setunit1)
 
	Text(cv,(150,85),text='=',fontsize=10,justify='center')
 
	unit2_input=InputBox(cv,(20,100),(150,30))
	# 替换为默认 Feature，保持正常外观但不再响应点击/键盘事件（只读展示）
	unit2_input.feature = Feature(unit2_input)
	unit2_chooser=Button(cv,(400,100),(210,30),anchor='ne',justify='center',fontsize=16,text='未选择',command=setunit2)
 
	res_too_big=Text(cv,(200,132),text='',fontsize=10,justify='center',anchor='n')
	Text(cv,(200,140),text='换算结果仅供参考\n带*的单位表示换算值可能不精确',fontsize=10,justify='center',anchor='n')
	

	# 输入时自动重新换算，也支持回车手动触发（绑定到输入框比绑定 Canvas 更可靠）
	unit1_input.bind("<KeyRelease>", lambda e: convert(), auto_detect=False)
	unit1_input.bind("<Return>", lambda e: convert(), auto_detect=False)
	unit1_input.bind('<KP_Enter>', lambda e: convert(), auto_detect=False)

	def _set_input_focus():
		unit1_input.update('active')
		cv.focus_set()
		if unit1_input.texts:
			cv.focus(unit1_input.texts[0].items[0])
	win.after_idle(_set_input_focus)
if __name__=='__main__':
	root=Tk((400,240))
	root.center()
	root.topmost(True)
	
	cv=Canvas(root)
	cv.place(width=400,height=240,x=0,y=0)
	
	Text(cv,(20,20),text='CalculatorMax converter page\nIt should be opening on a separate window.')
	
	root.after_idle(lambda:main(root,UNITS_LENGTH))
	root.mainloop()