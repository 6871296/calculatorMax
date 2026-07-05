import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import maliang
from maliang import *

from pages.conversions.convert import main as convert_main

from lib.betterfloat import bf,BetterFloat
from lib.maliang_patch import patch
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
		'🇬🇧海里': bf(1852)
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
UNITS_AREA={
	'🇺🇳公制':{
		'🇺🇳平方纳米（nm²）':bf(bf('0.001')/1000/1000)**2,
		'🇺🇳平方微米（μm²）':(bf('0.001')/1000)**2,
		'🇺🇳平方毫米（mm²）':(bf('0.001'))**2,
		'🇺🇳平方厘米（cm²）':(bf('0.01'))**2,
		'🇺🇳平方分米（dm²）':(bf('0.1'))**2,
		'🇺🇳平方米（m²）':(bf(1))**2,
		'🇺🇳平方千米（km²）':(bf(1000))**2,
		'🇺🇳公亩（are）':bf(100),
		'🇺🇳公顷（ha）':bf(10000)
  	},
	'🇨🇳市制':{
		'🇨🇳市分':bf(60)/bf(9),#60/9=6.6666... It'll fit your max precision settings.
		'🇨🇳市亩':bf(6000)/bf(9),
		'🇨🇳市顷':bf(600000)/bf(9),
		'🇨🇳平方市里':bf(250000)
	},
	'🇬🇧英制':{
		'🇬🇧平方英寸（in²）':bf('0.00064516'),
		'🇬🇧平方英尺（ft²）':bf('0.09290304'),
		'🇬🇧平方码（yd²）':bf('0.83612736'),
		'🇬🇧英亩（ac）':bf('4046.86'),
		'🇬🇧平方英里（mi²）':bf('2589988.110336')
	}
}
UNITS_VOLUME={
	'🇺🇳公制':{
	   '🇺🇳立方纳米（nm³）':bf(bf('0.001')/1000/1000)**3,
	   '🇺🇳立方微米（μm³）':(bf('0.001')/1000)**3,
	   '🇺🇳立方毫米（mm³）':(bf('0.001'))**3,
	   '🇺🇳立方厘米（cm³）':(bf('0.01'))**3,
	   '🇺🇳立方分米（dm³）':(bf('0.1'))**3,
	   '🇺🇳立方米（m³）':(bf(1))**3,
	   '🇺🇳立方千米（km³）':(bf(1000))**3,
	   '🇺🇳毫升（mL）':(bf('0.01'))**3,
       '🇺🇳升（L）':(bf('0.1'))**3
	},
	'🇬🇧英制':{
		'🇬🇧茶匙（tsp）':bf('0.00000493'),
		'🇬🇧量杯（cup）':bf('0.00023659'),
		'🇺🇸美制液量打兰（US fl dr）':bf('0.0000037'),
		'🇺🇸美制液量盎司（US fl oz）':bf('0.0000295735295625'),
		'🇺🇸美制液量品脱（US pt）':bf('0.000473176473'),
		'🇺🇸美制夸脱（US qt）':bf('0.000946352946'),
		'🇺🇸美制加仑（US gal）':bf('0.003785411784'),
		'🇺🇸美制蒲式耳*（US bu）':bf('0.0352381'),
		'🇬🇧英制液量打兰*（UK fl dr）':bf('0.0000035516328125'),
		'🇬🇧英制液量盎司（UK fl oz）':bf('0.0000284130625'),
		'🇬🇧英制品脱（UK pt）':bf('0.00056826125'),
		'🇬🇧英制夸脱（UK qt）':bf('0.0011365225'),
		'🇬🇧英制加仑（UK gal）':bf('0.00454609'),
		'🇬🇧英制蒲式耳（UK bu）':bf('0.03636872'),
		'🇬🇧立方英寸（in³）':bf('0.02831685'),
		'🇬🇧立方英尺（ft³）':bf('0.16387064'),
		'🇬🇧立方码（yd³）':bf('0.764555')
	}
}

def main(root:Tk):
	win=Toplevel(root,(300,210),title='单位换算 - CalculatorMax')
	win.center()
	win.focus_force()
	win.topmost(True)
	
	cv=Canvas(win)
	cv.place(width=300,height=210,x=0,y=0)
	
	maliang.Text(cv,(20,10),text='单位换算',weight='bold')
	
	[
		Button(cv,(20,40),(120,30),text='📏长度',command=lambda:convert_main(win,UNITS_LENGTH,'长度换算')),          Button(cv,(280,40),(120,30),anchor='ne',text='◼️面积',command=lambda:convert_main(win,UNITS_AREA,'面积单位换算')),
  		Button(cv,(20,80),(120,30),text='📦体积和容积',command=lambda:convert_main(win,UNITS_VOLUME,'体积和容积换算')),Button(cv,(280,80),(120,30),anchor='ne',text='⚖重量').disable(True),
		Button(cv,(20,120),(120,30),text='💰货币').disable(True)                                                   ,Button(cv,(280,120),(120,30),anchor='ne',text='🕒时间').disable(True)
	]
	
	maliang.Text(cv,(5,156),text='换算结果仅供参考，日常生活中请依法使用计量单位。\n中国市制单位在历朝历代各有不同，此处市制单位以\n1959年国务院《关于统一计量制度的命令》为准',fontsize=12,justify='center')
 
if __name__=='__main__':
	root=Tk((400,240))
	root.center()
	root.topmost(True)
	cv=Canvas(root)
	cv.place(width=400,height=240,x=0,y=0)
	
	maliang.Text(cv,(10,10),text='CalculatorMax convertion page\nIt should be opening on a separate window.')
	
	root.after_idle(lambda:main(root))
	root.mainloop()