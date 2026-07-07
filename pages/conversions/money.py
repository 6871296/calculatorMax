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
from decimal import Decimal, ROUND_HALF_UP

from forex_python.converter import CurrencyRates
#from forex_python.bitcoin import BtcConverter
import pyperclip as clip

patch()

UNITS_MONEY={
	'🇦🇪阿联酋迪拉姆（د.إ;）':'AED',
	'🇦🇫阿富汗尼（Afs）':'AFN',
	'🇦🇱阿尔巴尼亚列克（L）':'ALL',
	'🇦🇲亚美尼亚德拉姆（AMD）':'AMD',
	'🇳🇱荷属安的列斯盾（NAƒ）':'ANG',
	'🇦🇴安哥拉宽扎（Kz）':'AOA',
	'🇦🇷阿根廷比索（$）':'ARS',
	'🇦🇺澳大利亚元（$）':'AUD',
	'🇦🇼阿鲁巴弗罗林（ƒ）':'AWG',
	'🇦🇿阿塞拜疆马纳特（AZN）':'AZN',
	'🇧🇦波斯尼亚-黑塞哥维那可兑换马克（KM）':'BAM',
	'🇧🇧巴巴多斯元（Bds$）':'BBD',
	'🇧🇩孟加拉塔卡（৳）':'BDT',
	'🇧🇬保加利亚列弗（BGN）':'BGN',
	'🇧🇭巴林第纳尔（.د.ب）':'BHD',
	'🇧🇮布隆迪法郎（FBu）':'BIF',
	'🇧🇲百慕大元（BD$）':'BMD',
	'🇧🇳文莱元（B$）':'BND',
	'🇧🇴玻利维亚诺（Bs.）':'BOB',
	'🇧🇷巴西雷亚尔（R$）':'BRL',
	'🇧🇸巴哈马元（B$）':'BSD',
	'₿比特币（₿）':'BTC',
	'🇧🇹不丹努尔特鲁姆（Nu.）':'BTN',
	'🇧🇼博茨瓦纳普拉（P）':'BWP',
	'🇧🇾白俄罗斯卢布 (2000–2016)（Br）':'BYR',
	'🇧🇿伯利兹元（BZ$）':'BZD',
	'🇨🇦加拿大元（$）':'CAD',
	'🇨🇩刚果法郎（F）':'CDF',
	'🇨🇭瑞士法郎（Fr.）':'CHF',
	'🇨🇱智利比索（$）':'CLP',
	'🇨🇳人民币（¥）':'CNY',
	'🇨🇴哥伦比亚比索（Col$）':'COP',
	'🇨🇷哥斯达黎加科朗（₡）':'CRC',
	'🇨🇺古巴可兑换比索（$）':'CUC',
	'🇨🇻佛得角埃斯库多（Esc）':'CVE',
	'🇨🇿捷克克朗（Kč）':'CZK',
	'🇩🇯吉布提法郎（Fdj）':'DJF',
	'🇩🇰丹麦克朗（Kr）':'DKK',
	'🇩🇴多米尼加比索（RD$）':'DOP',
	'🇩🇿阿尔及利亚第纳尔（د.ج）':'DZD',
	'🇪🇪爱沙尼亚克朗（KR）':'EEK',
	'🇪🇬埃及镑（£）':'EGP',
	'🇪🇷厄立特里亚纳克法（Nfa）':'ERN',
	'🇪🇹埃塞俄比亚比尔（Br）':'ETB',
	'🇪🇺欧元（€）':'EUR',
	'🇫🇯斐济元（FJ$）':'FJD',
	'🇫🇰福克兰群岛镑（£）':'FKP',
	'🇬🇧英镑（£）':'GBP',
	'🇬🇪格鲁吉亚拉里（GEL）':'GEL',
	'🇬🇭加纳塞地（GH₵）':'GHS',
	'🇬🇮直布罗陀镑（£）':'GIP',
	'🇬🇲冈比亚达拉西（D）':'GMD',
	'🇬🇳几内亚法郎（FG）':'GNF',
	'🇬🇶赤道几内亚埃奎勒（CFA）':'GQE',
	'🇬🇹危地马拉格查尔（Q）':'GTQ',
	'🇬🇾圭亚那元（GY$）':'GYD',
	'🇭🇰港元（HK$）':'HKD',
	'🇭🇳洪都拉斯伦皮拉（L）':'HNL',
	'🇭🇷克罗地亚库纳（kn）':'HRK',
	'🇭🇹海地古德（G）':'HTG',
	'🇭🇺匈牙利福林（Ft）':'HUF',
	'🇮🇩印度尼西亚卢比（Rp）':'IDR',
	'🇮🇱以色列新谢克尔（₪）':'ILS',
	'🇮🇳印度卢比（₹）':'INR',
	'🇮🇶伊拉克第纳尔（د.ع）':'IQD',
	'🇮🇷伊朗里亚尔（IRR）':'IRR',
	'🇮🇸冰岛克朗（kr）':'ISK',
	'🇯🇲牙买加元（J$）':'JMD',
	'🇯🇴约旦第纳尔（JOD）':'JOD',
	'🇯🇵日元（円）':'JPY',
	'🇰🇪肯尼亚先令（KSh）':'KES',
	'🇰🇬吉尔吉斯斯坦索姆（сом）':'KGS',
	'🇰🇭柬埔寨瑞尔（៛）':'KHR',
	'🇰🇲科摩罗法郎（KMF）':'KMF',
	'🇰🇵朝鲜元（W）':'KPW',
	'🇰🇷韩元（W）':'KRW',
	'🇰🇼科威特第纳尔（KWD）':'KWD',
	'🇰🇾开曼元（KY$）':'KYD',
	'🇰🇿哈萨克斯坦坚戈（T）':'KZT',
	'🇱🇦老挝基普（KN）':'LAK',
	'🇱🇧黎巴嫩镑（£）':'LBP',
	'🇱🇰斯里兰卡卢比（Rs）':'LKR',
	'🇱🇷利比里亚元（L$）':'LRD',
	'🇱🇸莱索托洛蒂（M）':'LSL',
	'🇱🇹立陶宛立特（Lt）':'LTL',
	'🇱🇻拉脱维亚拉特（Ls）':'LVL',
	'🇱🇾利比亚第纳尔（LD）':'LYD',
	'🇲🇦摩洛哥迪拉姆（MAD）':'MAD',
	'🇲🇩摩尔多瓦列伊（MDL）':'MDL',
	'🇲🇬马达加斯加阿里亚里（FMG）':'MGA',
	'🇲🇰马其顿第纳尔（MKD）':'MKD',
	'🇲🇲缅甸元（K）':'MMK',
	'🇲🇳蒙古图格里克（₮）':'MNT',
	'🇲🇴澳门币（P）':'MOP',
	'🇲🇷毛里塔尼亚乌吉亚 (1973–2017)（UM）':'MRO',
	'🇲🇺毛里求斯卢比（Rs）':'MUR',
	'🇲🇻马尔代夫卢菲亚（Rf）':'MVR',
	'🇲🇼马拉维克瓦查（MK）':'MWK',
	'🇲🇽墨西哥比索（$）':'MXN',
	'🇲🇾马来西亚林吉特（RM）':'MYR',
	'🇲🇿莫桑比克美提卡（MT）':'MZN',
	'🇳🇦纳米比亚元（N$）':'NAD',
	'🇳🇬尼日利亚奈拉（₦）':'NGN',
	'🇳🇮尼加拉瓜科多巴（C$）':'NIO',
	'🇳🇴挪威克朗（kr）':'NOK',
	'🇳🇵尼泊尔卢比（NRs）':'NPR',
	'🇳🇿新西兰元（NZ$）':'NZD',
	'🇴🇲阿曼里亚尔（OMR）':'OMR',
	'🇵🇦巴拿马巴波亚（B./）':'PAB',
	'🇵🇪秘鲁索尔（S/.）':'PEN',
	'🇵🇬巴布亚新几内亚基那（K）':'PGK',
	'🇵🇭菲律宾比索（₱）':'PHP',
	'🇵🇰巴基斯坦卢比（Rs.）':'PKR',
	'🇵🇱波兰兹罗提（zł）':'PLN',
	'🇵🇾巴拉圭瓜拉尼（₲）':'PYG',
	'🇶🇦卡塔尔里亚尔（QR）':'QAR',
	'🇷🇴罗马尼亚列伊（L）':'RON',
	'🇷🇸塞尔维亚第纳尔（din.）':'RSD',
	'🇷🇺俄罗斯卢布（₽）':'RUB',
	'🇷🇼卢旺达法郎（FRw）':'RWF',
	'🇸🇦沙特里亚尔（SR）':'SAR',
	'🇸🇧所罗门群岛元（SI$）':'SBD',
	'🇸🇨塞舌尔卢比（SR）':'SCR',
	'🇸🇩苏丹镑（SDG）':'SDG',
	'🇸🇪瑞典克朗（kr）':'SEK',
	'🇸🇬新加坡元（S$）':'SGD',
	'🇸🇭圣赫勒拿群岛磅（£）':'SHP',
	'🇸🇱塞拉利昂利昂（Le）':'SLL',
	'🇸🇴索马里先令（Sh.）':'SOS',
	'🇸🇷苏里南元（$）':'SRD',
	'🇸🇹圣多美和普林西比多布拉 (1977–2017)（Db）':'STD',
	'🇸🇹圣多美和普林西比多布拉（Db）':'STN',
	'🇸🇾叙利亚镑（LS）':'SYP',
	'🇸🇿斯威士兰里兰吉尼（E）':'SZL',
	'🇹🇭泰铢（฿）':'THB',
	'🇹🇯塔吉克斯坦索莫尼（TJS）':'TJS',
	'🇹🇲土库曼斯坦马纳特（m）':'TMT',
	'🇹🇳突尼斯第纳尔（DT）':'TND',
	'🇹🇴汤加潘加（T$）':'TOP',
	'🇹🇷土耳其里拉（TRY）':'TRY',
	'🇹🇹特立尼达和多巴哥元（TT$）':'TTD',
	'🇨🇳新台币（NT$）':'TWD',
	'🇹🇿坦桑尼亚先令（TZS）':'TZS',
	'🇺🇦乌克兰格里夫纳（UAH）':'UAH',
	'🇺🇬乌干达先令（USh）':'UGX',
	'🇺🇸美元（$）':'USD',
	'🇺🇾乌拉圭比索（$U）':'UYU',
	'🇺🇿乌兹别克斯坦苏姆（UZS）':'UZS',
	'🇻🇪委内瑞拉玻利瓦尔 (1871–2008)（Bs）':'VEB',
	'🇻🇳越南盾（₫）':'VND',
	'🇻🇺瓦努阿图瓦图（VT）':'VUV',
	'🇼🇸萨摩亚塔拉（WS$）':'WST',
	'🌍中非法郎（CFA）':'XAF',
	'🌎东加勒比元（EC$）':'XCD',
	'🇺🇳特别提款权（SDR）':'XDR',
	'🌍西非法郎（CFA）':'XOF',
	'🌏太平洋法郎（F）':'XPF',
	'🇾🇪也门里亚尔（YER）':'YER',
	'🇿🇦南非兰特（R）':'ZAR',
	'🇿🇲赞比亚克瓦查（ZK）':'ZMW',
	'🇿🇼津巴布韦元 (2008)（Z$）':'ZWR'
}

def _money_convert(value:BetterFloat, units:dict, unit_from:str, unit_to:str)->BetterFloat:
	# value 是 BetterFloat；units 是 UNITS_MONEY；unit_from/unit_to 是 UNITS_MONEY 的键
	rate = CurrencyRates().convert(units[unit_from], units[unit_to], float(value))
	# 四舍五入到小数点后两位
	rounded = Decimal(str(rate)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
	return bf(str(rounded))
	
def main(root:Tk|Toplevel,units:dict[str,dict[str,BetterFloat]]=UNITS_MONEY,title:str='货币价值换算',_convert:Callable[[BetterFloat,dict[str,str],str,str],BetterFloat]=_money_convert):
	win=Toplevel(root,(420,180),title=f'{title} - CalculatorMax')
	win.center()
	win.focus_force()
	win.topmost(True)

	cv=Canvas(win)
	cv.place(width=420,height=180,x=0,y=0)
 
	def choose_unit()->str|None:
		category_keys = tuple(units.keys())
		choice=list(units.keys())[ChooseBox(win, 200, '选择单位', btns=category_keys).wait_answer()]
		return choice
   
	unit1:str=''
	unit2:str=''
 
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
		choice=choose_unit()
		if choice is None:
			return
		unit1=choice
		unit1_chooser.set(choice)
		convert()
	def setunit2():
		nonlocal unit2
		choice=choose_unit()
		if choice is None:
			return
		unit2=choice
		unit2_chooser.set(choice)
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
	Text(cv,(200,145),text='换算结果仅供参考 数据来自欧洲央行\n使用本换算功能需要连接互联网 此处荷属安的列斯使用荷兰国旗（🇳🇱）',fontsize=10,justify='center',anchor='n')
	

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
	
	Text(cv,(20,20),text='CalculatorMax money converter page\nIt should be opening on a separate window.')
	
	root.after_idle(lambda:main(root,UNITS_MONEY))
	root.mainloop()