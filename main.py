from lib.betterfloat import *
from lib.core import *
import lib.settings as settings
from lib.history import History
from lib.util import ChooseBox

from pages.settings import main as settings_main
from pages.conversions.index import main as convert_main
from pages.history import HistoryIO

from tkinter import messagebox as msgbox
import maliang

from lib.maliang_patch import patch
patch()

BetterFloat.set_precision(settings.get('floatPrecision',50))

history:list[History]=[History('',None,'')]
title_reset_after=''
copy_reset_after=''

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

def show_res(err:bool|None,res:str):
	global title_reset_after
	if title_reset_after:
		root.after_cancel(title_reset_after)
	if err:
		res_show.set(res)
		title.style.set(fg='red')
		copy_btn.style.set(fg=('gray','gray','gray'))
	elif err==None:
		pass
	else:
		res_show.set('='+res)
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
				root.clipboard_get()
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
			# 对话框关闭后把焦点抢回主窗口，避免 macOS 上剪贴板操作不生效
			root.focus_force()
			root.clipboard_clear()
			root.clipboard_append(res_show.get())
			root.update()
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


root=maliang.Tk(size=(400,240),title='CalculatorMax')
root.center()
root.focus_force()
#root.topmost(True)

cv=maliang.Canvas(root,auto_zoom=True,keep_ratio=None,free_anchor=True)
cv.place(width=1280, height=720, x=640, y=360, anchor="center")

btns=[
	maliang.Button(cv,(10,10),(30,30),text='🕘',command=lambda:history_pages.append(HistoryIO(root,history,fill_history))),
	#maliang.Button(cv,(130,10),(30,30),text='💡'),
	#maliang.Button(cv,(170,10),(30,30),text='♟'),
	maliang.Button(cv,(40,10),(30,30),text='⚖',justify='center',command=lambda:convert_main(root)),
	maliang.Button(cv,(90,10),(30,30),text='⚙️',command=lambda:settings_main(root))
	#maliang.IconButton(cv,(360,10),(30,30),image=maliang.PhotoImage(file='assets/github.png').resize(20,30))
]

title=maliang.Text(cv,(200,70),text='CalculatorMax',fontsize=24,anchor='center',auto_update=True)
maliang.Text(cv,(200,100),text='计算一切结果',fontsize=16,anchor='center')

ev_input=maliang.InputBox(cv,(140,140),(200,30),placeholder='请输入算式',anchor='center')
ev_input_focused=False
maliang.Button(cv,(310,140),(100,30),text='计算',anchor='center',command=lambda: calcr(ev_input.get())).style.set(fg='white',bg=('deepskyblue','aqua','cyan'))


res_show=maliang.Text(cv,(200,205),text='',anchor='n')

ac_btn=maliang.Button(cv,(190,180),(50,25),text='清空',fontsize=16,command=ac,anchor='e')
copy_btn=maliang.Button(cv,(210,180),(50,25),text='复制',fontsize=16,command=copy,anchor='w')
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