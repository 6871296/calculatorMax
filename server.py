import flask
from flask import request, jsonify
from math import *
from random import *
from simpleeval import simple_eval

app = flask.Flask(__name__)

# 存储内存值
memory_value = 0


def s_tri(bot, high) -> float:
    return bot * high / 2


def s_rect(bot, high):
    return bot * high


def s_tra(bot, top, high) -> float:
    return (bot + top) * high / 2


def hsf_s_tri(a, b, c) -> float:
    s = (a + b + c) / 2
    return sqrt(s * (s - a) * (s - b) * (s - c))


def pt(a, b) -> float:
    return sqrt(pow(a, 2) + pow(b, 2))


def s_circle(r) -> float:
    return pi * r * r


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
        f = str(simple_eval(ev, functions={
            "m": lambda: memory_value,
            "pi": lambda: pi,
            "e": lambda: e,
            "pow": lambda a, b: pow(a, b),
            "sqrt": lambda a: sqrt(a),
            "sin": lambda a: sin(a),
            "cos": lambda a: cos(a),
            "tan": lambda a: tan(a),
            "asin": lambda a: asin(a),
            "acos": lambda a: acos(a),
            "atan": lambda a: atan(a),
            "log": lambda a: log(a),
            "log10": lambda a: log10(a),
            "log2": lambda a: log2(a),
            "exp": lambda a: exp(a),
            "sinh": lambda a: sinh(a),
            "cosh": lambda a: cosh(a),
            "tanh": lambda a: tanh(a),
            "gamma": lambda a: gamma(a),
            "erf": lambda a: erf(a),
            "erfc": lambda a: erfc(a),
            "ceil": lambda a: ceil(a),
            "floor": lambda a: floor(a),
            "trunc": lambda a: trunc(a),
            "modf": lambda a: modf(a),
            "fabs": lambda a: fabs(a),
            "factorial": lambda a: factorial(a),
            "isinf": lambda a: isinf(a),
            "isnan": lambda a: isnan(a),
            "isclose": lambda a, b: isclose(a, b),
            "gcd": lambda a, b: gcd(a, b),
            "lcm": lambda a, b: lcm(a, b),
            "s_tri": lambda a, b: s_tri(a, b),
            "s_rect": lambda a, b: s_rect(a, b),
            "s_circle": lambda a: s_circle(a),
            "s_tra": lambda a, b, c: s_tra(a, b, c),
            "hsf_s_tri": lambda a, b, c: hsf_s_tri(a, b, c),
            "pt": lambda a, b: pt(a, b),
            "randint": lambda a, b: randint(a, b),
            "random": lambda: random(),
            "randrange": lambda a, b: randrange(a, b),
            "uniform": lambda a, b: uniform(a, b),
            "bitand": lambda a, b: a & b,
            "bitor": lambda a, b: a | b,
            "bitnot": lambda a: ~a,
            "bitxor": lambda a, b: a ^ b
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
            if isnan(float(f)):
                f = '不是数字'
            elif isinf(float(f)):
                f = '溢出'
            else:
                f = '未知错误'
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
    memory_value = data.get('value', 0)
    return jsonify({'success': True})


def run_server(debug: bool = False, port: int = 5000):
    app.run(port=port, debug=debug, use_reloader=False, threaded=True)
