import flask
from flask import request, jsonify
from random import randint as py_randint, random as py_random, randrange as py_randrange, uniform as py_uniform
from simpleeval import simple_eval
from lib.betterfloat import *
import re


app = flask.Flask(__name__)

# 存储内存值
memory_value: BetterFloat = BetterFloat()


def s_tri(bot, high) -> BetterFloat:
    """计算三角形面积"""
    return BetterFloat(bot) * BetterFloat(high) / BetterFloat(2)


def s_rect(bot, high) -> BetterFloat:
    """计算矩形面积"""
    return BetterFloat(bot) * BetterFloat(high)


def s_tra(bot, top, high) -> BetterFloat:
    """计算梯形面积"""
    return (BetterFloat(bot) + BetterFloat(top)) * BetterFloat(high) / BetterFloat(2)


def hsf_s_tri(a, b, c) -> BetterFloat:
    """使用海伦公式计算三角形面积"""
    a_bf = BetterFloat(a)
    b_bf = BetterFloat(b)
    c_bf = BetterFloat(c)
    s = (a_bf + b_bf + c_bf) / BetterFloat(2)
    return BetterFloat.sqrt(s * (s - a_bf) * (s - b_bf) * (s - c_bf))


def pt(a, b) -> BetterFloat:
    """使用勾股定理计算直角三角形斜边"""
    return BetterFloat.sqrt(BetterFloat.pow(a, 2) + BetterFloat.pow(b, 2))


def s_circle(r) -> BetterFloat:
    """计算圆形面积"""
    return BF_PI * BetterFloat(r) * BetterFloat(r)


def bf(x) -> BetterFloat:
    """BetterFloat 简写构造器"""
    return BetterFloat(x)


def convert_expr_to_betterfloat(expr: str) -> str:
    """
    将表达式中的数字字面量转换为 BetterFloat 构造。
    例如: 0.1+0.2 -> bf("0.1")+bf("0.2")
    
    正确处理:
    - 3-2 -> bf("3")-bf("2") (减号是运算符)
    - -5+3 -> bf("-5")+bf("3") (减号是负号)
    - 0.3-0.1 -> bf("0.3")-bf("0.1") (减号是运算符)
    """
    number_pattern = r'(?<![a-zA-Z_\.])((?:-)?(?:\d+\.?\d*|\.\d+)(?:[eE][+-]?\d+)?)(?![a-zA-Z_])'
    
    def replace_number(match):
        num = match.group(1)
        # 检查这个 '-' 是否真的是负号（在开头或跟在运算符/括号后）
        start_pos = match.start()
        if num.startswith('-') and start_pos > 0:
            prev_char = expr[start_pos-1]
            # 如果前一个字符是数字、字母、下划线或右括号，这个 '-' 是运算符
            if prev_char.isalnum() or prev_char == '_' or prev_char == ')':
                # 这是运算符，不是负号，只转换数字部分
                return f'-bf("{num[1:]}")'
        return f'bf("{num}")'
    
    result = re.sub(number_pattern, replace_number, expr)
    return result


@app.route('/<page>')
def index(page):
    return flask.render_template(f'{page}/index.html')


@app.route('/')
def main():
    return flask.render_template('index.html')


@app.route('/assets/<file>')
def cdn(file):
    return flask.send_file(f'./templates/cdn/{file}')


@app.route('/api/calc', methods=['POST'])
def api_calc():
    """API 端点：计算表达式"""
    global memory_value
    data = request.get_json()
    ev = data.get('expression', '')
    
    f = '未知错误'
    err = True
    
    try:
        ev = ev.replace("m", "m()")
        ev = ev.replace("pi", "pi()")
        ev = ev.replace("e", "e()")
        
        # 将数字字面量转换为 BetterFloat
        ev_processed = convert_expr_to_betterfloat(ev)
        
        f = str(simple_eval(ev_processed, functions={
            "bf": bf,
            "m": lambda: memory_value,
            "pi": lambda: BF_PI,
            "e": lambda: BF_E,
            "pow": lambda a, b: BetterFloat.pow(a, b),
            "sqrt": lambda a: BetterFloat.sqrt(a),
            "sin": lambda a: BetterFloat.sin(a),
            "cos": lambda a: BetterFloat.cos(a),
            "tan": lambda a: BetterFloat.tan(a),
            "asin": lambda a: BetterFloat.asin(a),
            "acos": lambda a: BetterFloat.acos(a),
            "atan": lambda a: BetterFloat.atan(a),
            "log": lambda a: BetterFloat.log(a),
            "log10": lambda a: BetterFloat.log10(a),
            "log2": lambda a: BetterFloat.log2(a),
            "exp": lambda a: BetterFloat.exp(a),
            "sinh": lambda a: BetterFloat.sinh(a),
            "cosh": lambda a: BetterFloat.cosh(a),
            "tanh": lambda a: BetterFloat.tanh(a),
            "gamma": lambda a: BetterFloat.gamma(a),
            "erf": lambda a: BetterFloat.erf(a),
            "erfc": lambda a: BetterFloat.erfc(a),
            "ceil": lambda a: BetterFloat.ceil(a),
            "floor": lambda a: BetterFloat.floor(a),
            "trunc": lambda a: BetterFloat.trunc(a),
            "beforef": lambda a: BetterFloat.modf(a)[0],
            "afterf":lambda a: BetterFloat.modf(a)[1],
            "fabs": lambda a: BetterFloat.fabs(a),
            "factorial": lambda a: BetterFloat.factorial(a),
            "isinf": lambda a: BetterFloat.isinf(a),
            "isnan": lambda a: BetterFloat.isnan(a),
            "isclose": lambda a, b: BetterFloat.isclose(a, b),
            "gcd": lambda a, b: BetterFloat.gcd(a, b),
            "lcm": lambda a, b: BetterFloat.lcm(a, b),
            "s_tri": lambda a, b: s_tri(a, b),
            "s_rect": lambda a, b: s_rect(a, b),
            "s_circle": lambda a: s_circle(a),
            "s_tra": lambda a, b, c: s_tra(a, b, c),
            "hsf_s_tri": lambda a, b, c: hsf_s_tri(a, b, c),
            "pt": lambda a, b: pt(a, b),
            "randint": lambda a, b: py_randint(int(BetterFloat(a)), int(BetterFloat(b))),
            "random": lambda: BetterFloat(py_random()),
            "randrange": lambda a, b: py_randrange(int(BetterFloat(a)), int(BetterFloat(b))),
            "uniform": lambda a, b: BetterFloat(py_uniform(float(BetterFloat(a)), float(BetterFloat(b)))),
            "bitand": lambda a, b: int(BetterFloat(a)) & int(BetterFloat(b)),
            "bitor": lambda a, b: int(BetterFloat(a)) | int(BetterFloat(b)),
            "bitnot": lambda a: ~int(BetterFloat(a)),
            "bitxor": lambda a, b: int(BetterFloat(a)) ^ int(BetterFloat(b))
        }))
    except OverflowError:
        f = '浮点数溢出'
    except ZeroDivisionError:
        f = '除零'
    except FloatingPointError:
        f = '浮点数异常'
    except ValueError:
        f = '值错误'
    except TypeError:
        f = '类型错误'
    except:
        try:
            # 尝试检查是否为 NaN 或 Inf
            if isinstance(f, BetterFloat):
                if f._is_nan:
                    f = '不是数字'
                elif f._is_inf:
                    f = '溢出'
                else:
                    f = '未知错误'
            else:
                try:
                    fv = float(f)
                    if BetterFloat.isnan(fv):
                        f = '不是数字'
                    elif BetterFloat.isinf(fv):
                        f = '溢出'
                    else:
                        f = '未知错误'
                except:
                    f = '可能不是数学算式'
        except:
            f = '可能不是数学算式'
    else:
        err = False
    
    return jsonify({'result': f, 'error': err})


@app.route('/api/mem', methods=['POST'])
def api_mem():
    """API 端点：设置内存值"""
    global memory_value
    data = request.get_json()
    memory_value = BetterFloat(data.get('value', 0))
    return jsonify({'success': True})


def run_server(debug: bool = False, port: int = 5000):
    app.run(port=port, debug=debug, use_reloader=False, threaded=True)
