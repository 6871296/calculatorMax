import flask
from flask import request, jsonify
from random import randint as py_randint, random as py_random, randrange as py_randrange, uniform as py_uniform
from simpleeval import simple_eval
from lib.betterfloat import *
from lib.logger import *
import re
import sympy as sp
from sympy import symbols, solve, Eq, sympify, Poly

debugmode=None

app = flask.Flask(__name__)
Logger.info('Created Flask WSGI server')

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


@app.route('/')
def main():
	global debugmode
	return flask.redirect('/maths/calc')
	#return flask.render_template('index.html')

@app.route('/maths/calc')
def calc():
	global debugmode
	return flask.render_template('maths/calc.html')


@app.route('/assets/<file>')
def cdn(file):
	return flask.send_file(f'./templates/cdn/{file}')

@app.route('/a/<path>')
def autoroute(path):
    return flask.render_template(f'a/{path}')


@app.route('/api/maths/calc', methods=['POST'])
def api_calc():
	print('[Server log]Received calculation by web server')
	"""API 端点：计算表达式"""
	global memory_value,debugmode
	data = request.get_json()
	ev = data.get('expression', '')
	
	f = '未知错误'
	err = True
	
	try:
		if debugmode:
			print(f'[Server log]Evauating: {ev}')
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
	if debugmode:
		if err:
			print('\033[0;1;33m[Server warning]Error evaluation!\033[0m')
		else:
			print(f'[Server log]Evaluation result:{f}')
	return jsonify({'result': f, 'error': err})


@app.route('/api/mem', methods=['POST'])
def api_mem():
	"""API 端点：设置内存值"""
	global memory_value,debugmode
	if debugmode:
		Logger.info('[Server info]Received memory_value changing by web server')
	data = request.get_json()
	memory_value = BetterFloat(data.get('value', 0))
	return jsonify({'success': True})


def validate_equation_input(equations, variables):
	"""
	验证输入是否是有效的方程，并检查是否可以用程序求解。
	
	返回: (is_valid, can_solve, message)
	- is_valid: 是否是有效的方程格式
	- can_solve: 是否可以用程序求解
	- message: 说明信息
	"""
	if not equations or not isinstance(equations, list):
		return False, False, "方程必须是列表格式"
	
	if not variables or not isinstance(variables, list):
		return False, False, "变量必须是列表格式"
	
	if len(equations) == 0:
		return False, False, "方程列表不能为空"
	
	if len(variables) == 0:
		return False, False, "变量列表不能为空"
	
	if len(equations) != len(variables):
		return False, False, f"方程数量({len(equations)})必须与变量数量({len(variables)})相等"
	
	# 检查变量名是否合法
	var_names = []
	for v in variables:
		if not isinstance(v, str):
			return False, False, f"变量名必须是字符串: {v}"
		if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', v):
			return False, False, f"非法的变量名: {v}"
		var_names.append(v)
	
	return True, True, "验证通过"


def is_linear_system(exprs, vars):
	"""检查方程组是否是线性方程组"""
	try:
		for expr in exprs:
			# 转换为 sympy 表达式
			if isinstance(expr, str):
				if '=' in expr:
					left, right = expr.split('=', 1)
					expr = sympify(f"({left}) - ({right})")
				else:
					expr = sympify(expr)
			
			# 检查是否为多项式
			if not expr.is_polynomial(*vars):
				return False
			
			# 检查每个变量的次数是否都不超过1
			poly = Poly(expr, *vars)
			for monom in poly.monoms():
				if sum(monom) > 1:
					return False
		return True
	except Exception:
		return False


def is_polynomial_system(exprs, vars):
	"""检查方程组是否是多项式方程组"""
	try:
		for expr in exprs:
			if isinstance(expr, str):
				if '=' in expr:
					left, right = expr.split('=', 1)
					expr = sympify(f"({left}) - ({right})")
				else:
					expr = sympify(expr)
			
			if not expr.is_polynomial(*vars):
				return False
		return True
	except Exception:
		return False


def solve_linear_system(equations, variables):
	"""求解线性方程组"""
	try:
		# 创建符号
		var_symbols = symbols(variables)
		if not isinstance(var_symbols, (list, tuple)):
			var_symbols = [var_symbols]
		
		# 构建 sympy 等式
		eqs = []
		for eq_str in equations:
			if isinstance(eq_str, str) and '=' in eq_str:
				left, right = eq_str.split('=', 1)
				eqs.append(Eq(sympify(left), sympify(right)))
			else:
				eqs.append(Eq(sympify(eq_str), 0))
		
		# 使用线性代数方法求解
		solution = solve(eqs, var_symbols, dict=True)
		
		if not solution:
			return {"success": True, "type": "线性方程组", "solution": "无解"}
		
		# 格式化解
		result = {}
		for sol in solution:
			if isinstance(sol, dict):
				for var, val in sol.items():
					result[str(var)] = str(val)
			else:
				result[str(var_symbols[0])] = str(sol)
		
		return {
			"success": True,
			"type": "线性方程组",
			"solution": result,
			"method": "精确解（线性代数）"
		}
	except Exception as e:
		return {"success": False, "error": f"求解失败: {str(e)}"}


def solve_polynomial_system(equations, variables):
	"""求解多项式方程组"""
	try:
		var_symbols = symbols(variables)
		if not isinstance(var_symbols, (list, tuple)):
			var_symbols = [var_symbols]
		
		# 构建 sympy 等式
		eqs = []
		for eq_str in equations:
			if isinstance(eq_str, str) and '=' in eq_str:
				left, right = eq_str.split('=', 1)
				eqs.append(Eq(sympify(left), sympify(right)))
			else:
				eqs.append(Eq(sympify(eq_str), 0))
		
		# 求解
		solution = solve(eqs, var_symbols, dict=True)
		
		if not solution:
			return {"success": True, "type": "多项式方程组", "solution": "无解"}
		
		# 格式化所有解
		solutions_list = []
		for sol in solution:
			sol_dict = {}
			for var, val in sol.items():
				sol_dict[str(var)] = str(val)
			solutions_list.append(sol_dict)
		
		return {
			"success": True,
			"type": "多项式方程组",
			"solutions": solutions_list,
			"solution_count": len(solutions_list),
			"method": "符号计算（Grobner基/结式）"
		}
	except Exception as e:
		return {"success": False, "error": f"求解失败: {str(e)}"}


def solve_numerical_system(equations, variables, initial_guess=None):
	"""使用数值方法求解非线性方程组"""
	try:
		var_symbols = symbols(variables)
		if not isinstance(var_symbols, (list, tuple)):
			var_symbols = [var_symbols]
		
		# 构建 sympy 等式（转换为 f(x)=0 形式）
		funcs = []
		for eq_str in equations:
			if isinstance(eq_str, str) and '=' in eq_str:
				left, right = eq_str.split('=', 1)
				funcs.append(sympify(f"({left}) - ({right})"))
			else:
				funcs.append(sympify(eq_str))
		
		# 使用 nsolve 进行数值求解
		if initial_guess is None:
			initial_guess = [0.0] * len(variables)
		
		solution = sp.nsolve(funcs, var_symbols, initial_guess, tol=1e-14, maxsteps=100)
		
		# 格式化解
		result = {}
		for i, var in enumerate(variables):
			result[var] = str(solution[i])
		
		return {
			"success": True,
			"type": "非线性方程组",
			"solution": result,
			"method": "数值求解（牛顿迭代法）",#这是数值近似解，精度约为 1e-14
		}
	except Exception as e:
		return {"success": False, "error": f"数值求解失败: {str(e)}"}


@app.route('/api/solvefx', methods=['POST'])
def api_solve():
	"""
	API 端点：求解方程（组）
	
	请求体格式：
	{
		"equations": ["2*x + 3*y = 7", "x - y = 1"],  // 方程列表
		"variables": ["x", "y"],                      // 变量列表
		"initial_guess": [0, 0]                        // （可选）数值求解的初始猜测
	}
	
	返回：
	- 成功：求解结果
	- 失败：错误信息
	"""
	print('[Server log] Received equation solving request')
	
	data = request.get_json()
	equations = data.get('equations', [])
	variables = data.get('variables', [])
	initial_guess = data.get('initial_guess', None)
	
	# 1. 验证输入
	is_valid, can_solve, message = validate_equation_input(equations, variables)
	
	if not is_valid:
		return jsonify({
			'success': False,
			'error': message,
			'error_type': '输入验证失败'
		}), 400
	
	try:
		# 2. 解析方程为 sympy 表达式以判断类型
		var_symbols = symbols(variables)
		if not isinstance(var_symbols, (list, tuple)):
			var_symbols = [var_symbols]
		
		exprs = []
		for eq_str in equations:
			if not isinstance(eq_str, str):
				return jsonify({
					'success': False,
					'error': f'方程必须是字符串: {eq_str}',
					'error_type': '输入格式错误'
				}), 400
			
			# 转换为表达式
			if '=' in eq_str:
				left, right = eq_str.split('=', 1)
				expr = sympify(f"({left}) - ({right})")
			else:
				expr = sympify(eq_str)
			exprs.append(expr)
		
		# 3. 判断方程类型并求解
		if is_linear_system(exprs, var_symbols):
			result = solve_linear_system(equations, variables)
		elif is_polynomial_system(exprs, var_symbols):
			result = solve_polynomial_system(equations, variables)
		else:
			# 非多项式方程组，尝试数值求解
			if initial_guess is not None:
				result = solve_numerical_system(equations, variables, initial_guess)
			else:
				# 默认尝试 [0, 0, ...] 作为初始猜测
				result = solve_numerical_system(equations, variables, [0.0] * len(variables))
		
		if debugmode:
			print(f'[Server log] Equation solve result: {result}')
		
		return jsonify(result)
		
	except Exception as e:
		error_msg = str(e)
		if debugmode:
			print(f'[Server warning] Equation solving error: {error_msg}')
		
		return jsonify({
			'success': False,
			'error': f'求解过程出错: {error_msg}',
			'error_type': '求解错误'
		}), 500


def run_server(debug: bool = False, port: int = 5000,_DEBUG:bool=False):
	global debugmode
	debugmode=_DEBUG
	if debugmode:
		Logger.info(f'[Server info]Starting Flask WSGI server with arguments debug={debug} port={port}')
	app.run(port=port, debug=debug, use_reloader=False, threaded=True)

if __name__=='__main__':
	Logger.info('CalculatrMax server side started!')
	run_server()