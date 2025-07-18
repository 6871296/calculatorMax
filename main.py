print("正在安装外部库……")
import subprocess,sys
runable=True
try:
    subprocess.run([sys.executable,"-m","pip", "install", "--upgrade", "pip"])
    subprocess.run([sys.executable,"-m","pip", "install", "easygui"])
except (Exception, KeyboardInterrupt) as e:
    print("外部库安装失败，请使用pip手动安装\n"+e[1]+': '+e[2])
    runable=False
#运行这段程序需要使用外部库easygui，通过上述代码安装后可以使用

if runable:
    print('正在导入模块……')
    import easygui
    from random import *
    from math import *  
    print('正在初始化……')
    def useinfo():
        easygui.msgbox(title='科学计算器',msg='''软件说明书

一、执行过程：
1.这个程序会先给你的Python安装一个外部库，如果想要删除，请按照下面的流程操作：
(1)打开终端/命令提示符
(2)输入指令：'''+sys.executable+'''-m pip uninstall easygui
这样，外部库就被成功删除了。
如果执行失败，请检查你的电脑有没有正确安装Python。如果一切正常，请运行安装到的Python文件夹（IDLE的位置）运行“Update Shell Profile.command”。
2.程序会询问“请输入算式”，输入后会给你结果。
*尽管这个程序拥有较强的异常捕捉能力，但也请勿恶意制造异常。
3.软件会把历史记录保存起来，得到结果后可选择“历史记录”查看。
4.想要退出，请在结果显示页选择“退出”，再点击“Yes”。


二、主要功能:

计算:
加法: +
减法: -
乘法: *
除法: /
取余: %
记忆: m
整除: //
幂:**

比较大小:（以下内容结果均为布尔值，无法用于计算）
等于:==
大于:>
小于:<
大于或等于:>=
小于或等于:<=
（以下内容前后都要加空格）
或者: or 
并且: and 
...不成立: not 

数学常数:
pi: 圆周率π（3.14159...）
e: 自然对数的底数e（2.71828...）

幂函数和开方:
pow(x, y): x的y次幂
sqrt(x): x的平方根

对数函数:
log(x): x的自然对数
log10(x): x的底数为10的对数
log2(x): x的底数为2的对数（Python 3.3及以上版本）

三角函数:
sin(x): 正弦函数
cos(x): 余弦函数
tan(x): 正切函数
asin(x): 正弦的逆函数
acos(x): 余弦的逆函数
atan(x): 正切的逆函数
atan2(y, x): 从x轴到点(x, y)的角度，范围在-pi到pi

角度和弧度转换:
degrees(x): 弧度转换为角度
radians(x): 角度转换为弧度

双曲函数:
sinh(x): 双曲正弦函数
cosh(x): 双曲余弦函数
tanh(x): 双曲正切函数

特殊函数:
gamma(x): Γ函数（阶乘的推广）
erf(x): 误差函数
erfc(x): 补误差函数

数值操作:
ceil(x): 向上取整
floor(x): 向下取整
trunc(x): 向0取整
modf(x): 分离整数部分和小数部分
fabs(x): 绝对值
factorial(x): 阶乘

浮点数信息:
isinf(x): 如果x是无穷大，则返回True
isnan(x): 如果x不是数字（NaN），则返回True
isclose(a, b, *, rel_tol=1e-09, abs_tol=0.0): 测试两个浮点数是否在给定容忍范围内相等

GCD和LCM:
gcd(x, y): 计算x和y的最大公约数
lcm(x, y): 计算x和y的最小公倍数

求面积:
s_tri(bot, high): 计算三角形面积
s_rect(bot, high): 计算矩形面积
s_circle(r): 计算圆形面积
s_tra(bot,top, high): 计算梯形面积

海伦公式与勾股定理:
hsf_s_tri(a,b,c): 使用海伦公式计算三角形面积
pt(a,b):使用勾股定理计算直角三角形斜边长度

随机数:
randint(a, b): 生成a~b范围内的随机整数
random(): 生成0~1范围内的随机浮点数
uniform(a, b): 生成a~b范围内的随机浮点数

三、备注:
1.数字大小不能大于9223372036854775807位，负数同理。一般家用、个人计算机不建议计算或处理1古戈尔（100位）以上的数，否则会导致卡顿甚至崩溃，影响使用体验。
2.小数最高精度为15位，最大是18e307。
3.本程序可以捕捉的错误：
1)浮点数溢出（OverflowError）：由小数结果过大造成
2)除数为零（ZeroDivisionError）：输入1/0之类的算式造成
3)浮点数异常（FloatingPointError）：一般不怎么出现
4)值错误（ValueError）：调用函数时未输入正确范围内的数据
5)类型错误（TypeError）：调用函数时输入的不是数字/浮点数
6)结果不是数字（math.isnan()）：错误调用未在本说明书中出示的Python函数（输出结果正常且不是数字时不会引发报错）
7)整数溢出（math.isinf()）：计算结果太大（即使Python可以计算古戈尔级的数）
8)非算式或其它异常：输入如1=0这样的算式或输入不完整/不正确的Python代码造成
但难免有无法捕捉的错误，请勿恶意造成其它错误。
4.如发生未能捕捉的异常，请重新运行此程序。''')
    def s_tri(bot, high)->float:
        return bot*high/2
    def s_rect(bot, high):
        return bot*high
    def s_tra(bot,top, high)->float:
        return (bot+top)*high/2
    def hsf_s_tri(a,b,c)->float:
        s=(a+b+c)/2
        return sqrt(s*(s-a)*(s-b)*(s-c))
    def pt(a,b)->float:
        return sqrt(pow(a,2)+pow(b,2))
    def s_circle(r):
        return 3.14159265358979323846264338327950288419716939987510*r*r
    useinfo()
    history={}
    while True:
        f='未知错误'
        try:
            ev=easygui.enterbox(msg='请输入算式',title='科学计算器')
            f=str(eval(ev))
            err=False
        except OverflowError:
            f='浮点数溢出'
            err=True
        except ZeroDivisionError:
            f='除零'
            err=True
        except FloatingPointError:
            f='浮点数异常'
            err=True
        except ValueError:
            f='值错误'
            err=True
        except TypeError:
            f='类型错误'
            err=True
        except:
            err=True
            try:
                if isnan(f):
                    f='不是数字'
                elif isinf(f):
                    f='溢出'
                else:
                    f='未知错误'
            except:
                f='可能不是数学算式'
        history[ev]=f
        c=easygui.choicebox(title='科学计算器-结果',msg=ev+'='+f, choices=['继续','历史记录','使用说明','退出'])
        if c=='继续':
            continue
        elif c=='退出':
            if easygui.ynbox(title='科学计算器',msg='确定退出？'):
                break
        elif c=='使用说明':
            useinfo()
        elif c=='历史记录':
            hr_str=''
            for i in history:
                hr_str+=i+'='+history[i]+'\n'
            easygui.msgbox(title='科学计算器-历史记录',msg=hr_str)
