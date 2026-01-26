print("正在安装外部库……")
import subprocess,sys
try:
    subprocess.run([sys.executable,"-m","pip", "install", "--upgrade", "pip"])
    subprocess.run([sys.executable,"-m","pip", "install", "easygui"])
    subprocess.run([sys.executable,'-m','pip','install','simpleeval'])
except Exception as e:
    print("外部库安装失败，请按照说明书手动安装\n"+e[0])
    sys.exit()
#运行这段程序需要使用外部库easygui和simpleeval，通过上述代码安装后可以使用
use_simple_eval=False
print('正在导入模块……')
try:
    import easygui
    from random import *
    from math import *  
    from simpleeval import simple_eval
except ImportError:
    print('导入失败！')
    sys.exit()
except:
    print('导入时发生未知错误！')
    sys.exit()
print('正在初始化……')
def useinfo():
    easygui.msgbox(title='说明书-CalculatorMax',msg='''CalculatorMax 软件说明书
一、专有名词讲解
1. simpleeval模式
simpleeval模式是另一种计算算式的方法。它基于simpleeval库中的simple_eval函数，比eval函数更安全，但功能更少（但少的只有“高级”、“执行类”和Python代码）。该模式尽管是开发的一个累赘但我还是会持续更新，加入新的功能。
二、计算功能
在simpleeval模式下，目前仅已知以下功能和Python关键字可用。（高级、执行类除外）
非simpleeval模式可以执行任何Python代码。
1. 一般功能
a+b: 加法
a-b: 减法
a*b: 乘法
a/b: 除法
a%%b: 取余
m: 记忆
a//b: 整除
a**b: 幂
2. 比较大小
（以下内容结果均为布尔值（真或假），只能用于逻辑运算）
a==b: 等于
a>b: 大于
a<b: 小于
a>=b: 大于等于
a<=b: 小于等于
3. 逻辑运算
（以下内容结果均为布尔值（真或假），只能用于逻辑运算，前后都要加空格）
a or b: 或运算
a and b: 与运算
not a: 非运算
4. 数学常数
pi: 圆周率π（3.1415926...）
e: 自然对数的底数e（2.71828...）
5. 幂函数和开方
pow(x, y): x的y次幂
sqrt(x): x的平方根
6. 对数函数
log(x): x的自然对数
log10(x): x的底数为10的对数
log2(x): x的底数为2的对数（Python 3.3及以上版本）
7. 三角函数
sin(x): 正弦函数
cos(x): 余弦函数
tan(x): 正切函数
asin(x): 正弦的逆函数
acos(x): 余弦的逆函数
atan(x): 正切的逆函数
atan2(y, x): 从x轴到点(x, y)的角度，范围在-π到π
8. 角度和弧度转换
degrees(x): 弧度转换为角度
radians(x): 角度转换为弧度
9. 双曲函数
sinh(x): 双曲正弦函数
cosh(x): 双曲余弦函数
tanh(x): 双曲正切函数
10. 特殊函数
gamma(x): Γ函数（阶乘的推广）
erf(x): 误差函数
erfc(x): 补误差函数
11. 数值操作
ceil(x): 向上取整
floor(x): 向下取整
trunc(x): 向0取整
modf(x): 分离整数部分和小数部分
fabs(x): 绝对值
factorial(x): 阶乘
12. 浮点数信息
isinf(x): 如果x是无穷大，则返回True（布尔值，只能用于逻辑运算）
isnan(x): 如果x不是数字（NaN），则返回True（布尔值，只能用于逻辑运算）
isclose(a, b, *, rel_tol=1e-09, abs_tol=0.0): 测试两个小数是否在给定容忍范围内相等
13. GCD和LCM
gcd(x, y): 计算最大公约数
lcm(x, y): 计算最小公倍数
14. 求几何图形面积
s_tri(bot, high): 计算三角形面积
s_rect(bot, high): 计算矩形面积
s_circle(r): 计算圆形面积
s_tra(bot,top, high): 计算梯形面积
15. 海伦公式与勾股定理
hsf_s_tri(a,b,c): 使用海伦公式计算三角形面积
pt(a,b):使用勾股定理计算直角三角形斜边长度
16. 随机数
randint(a, b): 生成a~b范围内的随机整数
random(): 生成0~1范围内的随机小数
uniform(a, b): 生成a~b范围内的随机小数
17. 高级
重要警告：非调试用途请勿随意使用
use_simple_eval: 是否使用simpleeval模式
f: 上次计算的结果
ev: 上次的算式
err: 上次计算是否报错
history: 以{'算式':'结果'}为格式的历史记录
hr_str: 上次打开历史记录页显示的内容
18. 执行类
*重要警告：非调试用途请勿随意使用
subprocess.run(cmd=['command']): 执行系统命令
break: 强制返回首页
useinfo(): 打开说明书
sys.exit(): 强制退出
三、备注
1. 数字大小不能大于9223372036854775807位（约9京），负数同理。
   一般家用、个人计算机不建议计算或处理1古戈尔（100位）以上的数，否则会导致卡顿甚至崩溃。
2. 小数最高精度约为15位，最大是18e307。
3. 本程序可以捕捉的错误：
   1) 浮点数溢出（OverflowError）：由小数结果过大造成
   2) 除数为零（ZeroDivisionError）：输入1/0之类的算式造成
   3) 浮点数异常（FloatingPointError）：一般不怎么出现
   4) 值错误（ValueError）：调用函数时未输入正确范围内的数据
   5) 类型错误（TypeError）：调用函数时输入的不是数字/浮点数
   6) 结果不是数字（math.isnan()）：错误调用未在本说明书中出示的Python函数（输出结果正常且不是数字时不会引发报错）
   7) 整数溢出（math.isinf()）：计算结果太大（即使Python可以计算古戈尔级的数）
   8) 非算式或其它异常：输入如1=0这样的不合法算式或输入不正确的Python代码造成（最为常见）
    但难免有无法捕捉的错误，请勿恶意造成其它错误。
4. 如发生未能捕捉的异常，请重新运行此程序。
5. 禁止执行不安全的Python代码，否则后果自负。
''')#a%%b那里差点被坑
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
    def s_circle(r)->float:
        return pi()*r*r
    m=0
    history={}
    while True:
        c=easygui.buttonbox(title="calculatorMax",msg="calculatorMax，计算一切结果",choices=['开始计算','使用说明','历史记录','设置','退出'])
        if c=='开始计算':
            while True:
                f='未知错误'
                choices=[]
                try:
                    ev=easygui.enterbox(msg='请输入算式',title='calculatorMax')
                    if use_simple_eval:
                        ev.replace("m","m()")
                        ev.replace("pi","pi()")
                        ev.replace("e","e()")
                        f=str(simple_eval(ev,functions={
                            "m":lambda: m,
                            "pi":lambda: pi,
                            "e":lambda: e,
                            "pow":lambda a,b: pow(a,b),
                            "sqrt":lambda a: sqrt(a),
                            "sin":lambda a: sin(a),
                            "cos":lambda a: cos(a),
                            "tan":lambda a: tan(a),
                            "asin":lambda a: asin(a),
                            "acos":lambda a: acos(a),
                            "atan":lambda a: atan(a),
                            "log":lambda a: log(a),
                            "log10":lambda a: log10(a),
                            "log2":lambda a: log2(a),
                            "exp":lambda a: exp(a),
                            "sinh":lambda a: sinh(a),
                            "cosh":lambda a: cosh(a),
                            "tanh":lambda a: tanh(a),
                            "gamma":lambda a: gamma(a),
                            "erf":lambda a: erf(a),
                            "erfc":lambda a: erfc(a),
                            "ceil":lambda a: ceil(a),
                            "floor":lambda a: floor(a),
                            "trunc":lambda a: trunc(a),
                            "modf":lambda a: modf(a),
                            "fabs":lambda a: fabs(a),
                            "factorial":lambda a: factorial(a),
                            "isinf":lambda a: isinf(a),
                            "isnan":lambda a: isnan(a),
                            "isclose":lambda a, b: isclose(a,b),
                            "gcd":lambda a, b: gcd(a,b),
                            "lcm":lambda a, b: lcm(a,b),
                            "s_tri":lambda a, b: s_tri(a,b),
                            "s_rect":lambda a, b: s_rect(a,b),
                            "s_circle":lambda a: s_circle(a),
                            "s_tra":lambda a, b, c: s_tra(a,b,c),
                            "hsf_s_tri":lambda a, b, c: hsf_s_tri(a,b,c),
                            "pt":lambda a, b: pt(a,b),
                            "randint":lambda a, b: randint(a,b),
                            "random":lambda: random(),
                            "randrange":lambda a, b: randrange(a,b),
                            "uniform":lambda a, b: uniform(a,b),
                            "bitand":lambda a,b:a&b,
                            "bitor":lambda a,b:a|b,
                            "bitnot":lambda a:~a,
                            "bitxor":lambda a,b:a^b
                        }))
                    else:
                        f=str(eval(ev))
                except OverflowError:
                    f='浮点数溢出'
                except ZeroDivisionError:
                    f='除零'
                except FloatingPointError:
                    f='浮点数异常'
                except ValueError:
                    f='值错误'
                except TypeError:
                    f='类型错误'
                except:
                    try:
                        if isnan(f):
                            f='不是数字'
                        elif isinf(f):
                            f='溢出'
                        else:
                            f='未知错误'
                    except:
                        f='可能不是数学算式'
                else:
                    choices.append('记忆')
                history[ev]=f
                choices+=['继续','返回首页','退出']
                c=easygui.buttonbox(title='结果-calculatorMax',msg=ev+'='+f, choices=choices)
                if c=='继续':
                    continue
                elif c=='返回首页':
                    break
                elif c=='退出':
                    if easygui.ynbox(title='calculatorMax',msg='确定退出？'):
                        sys.exit()
                elif c=='记忆':
                    m=f
        elif c=='使用说明':
            useinfo()
        elif c=='历史记录':
            hr_str=''
            for i in history:
                hr_str+=i+'='+history[i]+'\n'
            c=easygui.buttonbox(title='历史记录-calculatorMax',msg=hr_str,choices=['返回','存储'])
            if c=='存储':
                try:
                    f=open(easygui.enterbox(title='claculatorMax',msg='请输入存储文件路径，请确保该文件存在且不为空'),'w')
                    f.write(hr_str)
                    f.close()
                    easygui.msgbox(title='calculatorMax',msg='存储完成！')
                except FileNotFoundError:
                    easygui.msgbox(title='calculatorMax',msg='存储失败！\n原因：该路径不是一个文本文件或不存在。')
                except IOError:
                    easygui.msgbox(title='calculatorMax',msg='存储失败！\n原因：写文件时出错。')
                except:
                    easygui.msgbox(title='calculatorMax',msg='存储失败！\n原因：未知错误。')
                try:
                    f.close()
                finally:#不写会报错所以我就写了
                    pass
        elif c=='设置':
            while True:
                c=easygui.buttonbox(title='设置-calculatorMax',msg='设置',choices=['返回','清空历史记录','simpleeval设置'])
                if c=='清空历史记录' and easygui.ynbox('确定清空历史记录吗？','calculatorMax'):
                    history={}
                elif c=='返回':
                    break
                elif c=='simpleeval设置':
                    while True:
                        c=easygui.buttonbox(title='simpleeval设置-calculatorMax',msg='simpleeval外部库有类似eval的功能，可以“给字符串去掉引号”。但是它比普通eval()函数更加安全，只能执行指定的功能。',choices=['返回','simpleeval模式：'+{'True':'开','False':'关'}[str(use_simple_eval)]])
                        if c=='返回':
                            break
                        elif c=='simpleeval模式：'+{'True':'开','False':'关'}[str(use_simple_eval)]:
                            use_simple_eval=not use_simple_eval
        elif c=='退出':
            break
if easygui.ynbox(title='calculatorMax',msg='确定退出？'):
    sys.exit()
