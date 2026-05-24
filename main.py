from lib.betterfloat import *
from lib.core import *
from time import sleep
import maliang

def calcr(ev:str):
	err,res=calc(ev)
	if err:
		titlered()

def titlered():
	title.style.set(fg='red')
	sleep(2)
	title.style.set(fg='normal')
def titlegreen():
    title.style.set(fg='green')
    sleep(2)
    title.style.set(fg='normal')



root=maliang.Tk(size=(400,150),title='CalculatorMax')
root.center()
root.topmost(True)

cv=maliang.Canvas(root,auto_zoom=True,keep_ratio=None,free_anchor=True)
cv.place(width=1280, height=720, x=640, y=360, anchor="center")

title=maliang.Text(cv,(200,20),text='CalculatorMax',fontsize=24,anchor='center',auto_update=True)
maliang.Text(cv,(200,50),text='计算一切结果',fontsize=16,anchor='center')

ev_input=maliang.InputBox(cv,(140,90),(200,30),placeholder='请输入算式',anchor='center') 
calc_btn=maliang.Button(cv,(310,90),(100,30),text='计算',anchor='center',command=lambda: calc(ev_input.get()))

res=maliang.Text(cv,(200,115),text='=',anchor='n')

root.mainloop()