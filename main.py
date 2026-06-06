from lib.betterfloat import *
from lib.core import *
import maliang

def calcr(ev:str):
	err,res=calc(ev)
	if err:
		res_show.set(res)
		titlered()
	else:
		res_show.set('='+res)
		titlegreen()
	

def titlered():
	title.style.set(fg='red')
	root.after(2000, lambda: title.style.set(fg='black'))
def titlegreen():
    title.style.set(fg='green')
    root.after(2000, lambda: title.style.set(fg='black'))
    
def on_enter():
    global ev_input_focused
    print(f'[debug]on_enter() ev_input_focused={ev_input_focused}')
    if ev_input_focused:
        calcr(ev_input.get())




root=maliang.Tk(size=(400,150),title='CalculatorMax')
root.center()
root.focus_force()
root.topmost(True)

cv=maliang.Canvas(root,auto_zoom=True,keep_ratio=None,free_anchor=True)
cv.place(width=1280, height=720, x=640, y=360, anchor="center")

title=maliang.Text(cv,(200,20),text='CalculatorMax',fontsize=24,anchor='center',auto_update=True)
maliang.Text(cv,(200,50),text='计算一切结果',fontsize=16,anchor='center')

ev_input=maliang.InputBox(cv,(140,90),(200,30),placeholder='请输入算式',anchor='center')
ev_input_focused=False
calc_btn=maliang.Button(cv,(310,90),(100,30),text='计算',anchor='center',command=lambda: calcr(ev_input.get()))

res_show=maliang.Text(cv,(200,115),text='',anchor='n')

root.bind("<Return>",on_enter)
root.bind("<KP_Enter>", on_enter)

def ev_input_focus(status:bool):
    global ev_input_focused
    ev_input_focused=status
    print(f'[debug]ev_input_focus({status})')

cv.tag_bind(ev_input, "<FocusIn>",ev_input_focus(True))
cv.tag_bind(ev_input, "<FocusOut>",ev_input_focus(False))

root.mainloop()