import flask,webview
from math import *
from random import *
from simpleeval import simple_eval
from threading import Thread
import sys
app = flask.Flask(__name__)

@app.route('/')
def main():
    return flask.render_template('index.html')
@app.route('/<site>')
def page(site):
    return flask.render_template(f'{site}/index.html')
@app.route('/assets/<file>')
def asset(file):
    return flask.send_from_directory('cdn/'+ file)


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

class Api:
    def __init__(self):
        self.m=0
        self.use_simple_eval=False
    def change_settings(self,use_simple_eval):
        self.use_simple_eval=use_simple_eval
    def calc(self,ev):
        try:
            if self.use_simple_eval:
                ev.replace("m","m()")
                ev.replace("pi","pi()")
                ev.replace("e","e()")
                f=str(simple_eval(ev,functions={
                    "m":lambda: self.m,
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
        return f

if __name__ == '__main__':
    api = Api()
    window=webview.create_window('CalculatorMax',app,js_api=api)
    flask_thread = Thread(target=app.run,args=['port=8080'])
    flask_thread.start()
    webview.start()
    flask_thread.join(timeout=5)
    sys.exit()