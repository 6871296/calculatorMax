from lib.betterfloat import *
from lib.core import *
import lib.settings as settings
from lib.history import History
from lib.util import ChooseBox, apply_screen_scale, wrap_display_text

from pages.settings import main as settings_main
from pages.conversions.index import main as convert_main
from pages.history import HistoryIO

from tkinter import messagebox as msgbox
import pyperclip as clip
import maliang

from lib.maliang_patch import patch
patch()

BetterFloat.set_precision(settings.get('floatPrecision',50))

history:list[History]=[]
title_reset_after=''
copy_reset_after=''

last_res=''

history_pages:list[HistoryIO]=[]

def calcr(ev:str):
	global history
	err,res=calc(ev)
	history.append(History(ev,err,res))
	# 清理已关闭的历史页面，避免访问已销毁的 Canvas
	history_pages[:] = [i for i in history_pages if i.win.winfo_exists()]
	for i in history_pages:
		i.update(history)
	show_res(err,res)
 
def fill_history(ev:str,err:bool|None,res:str):
	ev_input.set(ev)
	show_res(err,res)

def _set_window_design_height(design_h:int) -> None:
	"""把主窗口高度设为指定的设计高度（宽度与缩放比例不变）。

	缩放后的高度不超过屏幕高度，且不超过画布设计高度 _CV_DESIGN_H；
	位置只在越界时微调。
	"""
	scale = root.winfo_width() / 400
	design_h = min(design_h, _CV_DESIGN_H, int(root.winfo_screenheight() / scale))
	if design_h * scale != root.winfo_height():
		new_w = round(400 * scale)
		new_h = round(design_h * scale)
		sw, sh = root.winfo_screenwidth(), root.winfo_screenheight()
		x = min(max(root.winfo_x(), 0), max(0, sw - new_w))
		y = min(max(root.winfo_y(), 0), max(0, sh - new_h))
		root.geometry(size=(new_w, new_h), position=(x, y))

def _display_result(text:str, start_y:int) -> None:
	"""显示结果文本，并按行数调整主窗口高度使结果完整展示。

	maliang 的自动测高对多行文本不准确，这里用字体度量手动校正，
	使文本从 start_y 开始向下完整展示；窗口高度随结果行数伸缩
	（画布设计高度固定为 _CV_DESIGN_H，窗口只负责显示其顶部区域，
	缩放比例不变），且窗口高度不超过屏幕高度。
	"""
	font = res_show.texts[0].font
	line_h = font.metrics('linespace')
	line_list = text.split('\n')
	w = max(font.measure(line) for line in line_list) + 4
	h = len(line_list) * line_h
	res_show.set(text)
	res_show.resize((w, h))
	_set_window_design_height(max(250, start_y + h + 6))

def show_res(err:bool|None,res:str):
	global title_reset_after,last_res
	last_res=res
	if title_reset_after:
		root.after_cancel(title_reset_after)
	# 长结果按窗口宽度折行（连续长数字也能折断）
	wrapped = wrap_display_text(res, res_show.texts[0].font, 390)
	if err:
		res_show.moveto(200,205)
		eq_sign.set('')
		_display_result(wrapped, 205)
		title.style.set(fg='red')
		copy_btn.style.set(fg=('gray','gray','gray'))
	elif err==None:
		pass
	else:
		if len(res)<=10:
			res_show.moveto(200,205)
			eq_sign.set('')
			_display_result('='+wrapped, 205)
		elif '\n' in wrapped:
			# 结果折成多行：从上方开始显示，等号并入首行
			res_show.moveto(200,205)
			eq_sign.set('')
			_display_result('='+wrapped, 205)
		else:
			res_show.moveto(200,215)
			eq_sign.set('=')
			_display_result(wrapped, 215)
		title.style.set(fg='green')
		copy_btn.style.set(fg=('black','black','black'))
	title_reset_after=root.after(2000, lambda: title.style.set(fg='black'))

def on_enter():
	global ev_input_focused
	if ev_input_focused and ev_input.get()!='':
		calcr(ev_input.get())

def copy():
	global copy_reset_after
	if copy_reset_after:
		root.after_cancel(copy_reset_after)
	def copy_btn_reset():
		copy_btn.set('复制')
		copy_btn.style.set(fg=('black','black','black'))
		copy_btn.resize((50,25))
	def copy_btn_reset_gray():
		copy_btn.set('复制')
		copy_btn.style.set(fg=('gray','gray','gray'))
		copy_btn.resize((50,25))
	if not history or history[-1].err != False:
		copy_btn.set('无法复制')
		copy_btn.style.set(fg=('red','red','red'))
		copy_btn.resize((80,25))
		copy_reset_after=root.after(1000,copy_btn_reset_gray)
	else:
		try:
			try:
				clip.paste()
			except Exception:
				pass
			else:
				if not settings.get('ignoreClipboardOverwritingWarning'):
					cb=ChooseBox(root,200,'⚠️剪贴板中含有其他内容。','剪贴板覆盖警告','如果现在复制，所有的内容都将丢失。\n确定复制吗？',30,btns=('确定','确定（不再提醒）','取消'))
					cb.btns[0].style.set(fg='white',bg=('deepskyblue','aqua','aqua'))
					ans=cb.wait_answer()
					if ans==1:
						settings.set('ignoreClipboardOverwritingWarning',True)
					elif ans==2 or ans is None:
						return
			clip.copy(last_res)
			copy_btn.set('复制成功')
			copy_btn.style.set(fg=('green','green','green'))
			copy_btn.resize((80,25))
			copy_reset_after=root.after(1000,copy_btn_reset)
		except Exception as e:
			msgbox.showerror('复制失败', f'复制失败：{e}')
			copy_btn.set('复制失败')
			copy_btn.style.set(fg=('red','red','red'))
			copy_btn.resize((80,25))
			copy_reset_after=root.after(1000,copy_btn_reset)

		
def ac():
	res_show.set('')
	title.style.set(fg='black')
	ev_input.set('')
	# 恢复窗口默认大小（设计高度 250）
	_set_window_design_height(250)

root=maliang.Tk(size=(400,250),title='CalculatorMax')
apply_screen_scale(root,400,250)
root.resizable(True, True)
root.center()
root.focus_force()
root.topmost(True)

cv=maliang.Canvas(root,auto_zoom=True,keep_ratio='min',free_anchor=True)
# 画布设计高度大于窗口：结果折行时窗口向下扩展即可显示更多内容，
# 无需改动设计尺寸（避免缩放比例失稳）
_CV_DESIGN_H=960
cv.place(width=400, height=_CV_DESIGN_H,x=0,y=0)

cv_btn=maliang.Canvas(cv,auto_zoom=True,keep_ratio='min')
cv_btn.place(width=400,height=61,x=0,y=0)
#cv_btn.create_rectangle(0,0,400,50,fill='deepskyblue',width=0)

btns:list[maliang.Button]=[
	maliang.Button(cv_btn,(10,10),(30,30),text='🕘',justify='center',command=lambda:history_pages.append(HistoryIO(root,history,fill_history))),
	#maliang.Button(cv_btn,(130,10),(30,30),text='💡'),
	#maliang.Button(cv_btn,(170,10),(30,30),text='♟'),
	maliang.Button(cv_btn,(50,10),(30,30),text='⚖',justify='center',command=lambda:convert_main(root)),
	maliang.Button(cv_btn,(90,10),(30,30),text='⚙️',justify='center',command=lambda:settings_main(root)),

	#maliang.Button(cv_btn,(320,10),(30,30),text='',justify='center',command=lambda:apply_screen_scale(root,400,250))
]

btn_labels:list[maliang.Label]=[
	maliang.Label(cv_btn,(25,50),(50,20),anchor='center',text='历史记录',fontsize=12,capture_events=False),
	maliang.Label(cv_btn,(65,50),(30,20),anchor='center',text='换算',fontsize=12,capture_events=False),
	maliang.Label(cv_btn,(105,50),(30,20),anchor='center',text='设置',fontsize=12,capture_events=False),
 
	#maliang.Label(cv_btn,(335,50),(50,20),anchor='center',text='重置窗口',fontsize=12,capture_events=False),
	#maliang.Label(cv_btn,(375,50),(50,20),anchor='center',text='',fontsize=12,capture_events=False),
]

# 按住 Option（Alt）键显示全部标签，松开时隐藏
def _show_btn_labels(_=None):
	for label in btn_labels:
		label.forget(False)

def _hide_btn_labels(_=None):
	for label in btn_labels:
		label.forget(True)
  
# 默认隐藏所有标签
_hide_btn_labels()
 
for _key in ('<KeyPress-Alt_L>', '<KeyPress-Alt_R>'):
	cv.bind_all(_key, _show_btn_labels)
for _key in ('<KeyRelease-Alt_L>', '<KeyRelease-Alt_R>'):
	cv.bind_all(_key, _hide_btn_labels)

title=maliang.Text(cv,(200,70),text='CalculatorMax',fontsize=24,anchor='center',auto_update=True)
maliang.Text(cv,(200,100),text='计算一切结果',fontsize=16,anchor='center')

ev_input=maliang.InputBox(cv,(140,140),(200,30),placeholder='请输入算式',anchor='center')
ev_input_focused=False
maliang.Button(cv,(310,140),(100,30),text='计算',anchor='center',command=lambda: calcr(ev_input.get())).style.set(fg='white',bg=('deepskyblue','aqua','gray'))

ac_btn=maliang.Button(cv,(190,180),(50,25),text='清空',fontsize=16,command=ac,anchor='e')
copy_btn=maliang.Button(cv,(210,180),(50,25),text='复制',fontsize=16,command=copy,anchor='w')

eq_sign=maliang.Text(cv,(200,195),anchor='n',text='',fontsize=16,justify='center')
res_show=maliang.Text(cv,(200,210),text='',anchor='n',justify='center')

copy_btn.style.set(fg=('gray','gray','gray'))

def ev_input_focus(status:bool):
	global ev_input_focused
	ev_input_focused = status

ev_input.bind('<FocusIn>', lambda e: ev_input_focus(True), auto_detect=False)
ev_input.bind('<FocusOut>', lambda e: ev_input_focus(False), auto_detect=False)

ev_input.bind('<Return>', lambda e: calcr(ev_input.get()), auto_detect=False)
ev_input.bind('<KP_Enter>',lambda e: calcr(ev_input.get()),auto_detect=False)
ev_input.bind('<Escape>',lambda e:ac(),auto_detect=False)


# 启动时让输入框自动获得焦点（maliang 虚拟 widget 需通过 Canvas focus 设置）
def _set_input_focus():
	ev_input.update('active')
	cv.focus_set()
	if ev_input.texts:
		cv.focus(ev_input.texts[0].items[0])

root.after_idle(_set_input_focus)

root.mainloop()