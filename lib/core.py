import sys
from sympy import sympify, Poly, symbols, Eq, solve as sympy_solve, nsolve
import re
from random import *
from simpleeval import simple_eval
from enum import Enum
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from lib.betterfloat import *


class EquationType(Enum):
    LINEAR = 0
    POLYNOMIAL = 1
    NUMERICAL = 2


# sympy 保留的函数名和常量名，变量名不能与这些名称重合
RESERVED_NAMES = {
    'pi', 'e', 'i', 'oo', 'zoo', 'nan',
    'sin', 'cos', 'tan', 'asin', 'acos', 'atan',
    'sinh', 'cosh', 'tanh', 'asinh', 'acosh', 'atanh',
    'exp', 'log', 'ln', 'sqrt', 'abs', 'sign',
    'floor', 'ceiling', 'factorial', 'gamma', 'beta',
    'erf', 'erfc', 'Ei', 'Ci', 'Si',
}

# 占位符映射：把保留名替换为不含保留名子串的占位符
_PROTECTED_MAP = {
    f'__MALIANG_PROTECTED_{i}__': name
    for i, name in enumerate(sorted(RESERVED_NAMES, key=len, reverse=True))
}
_NAME_TO_PLACEHOLDER = {name: placeholder for placeholder, name in _PROTECTED_MAP.items()}


def _protect_reserved(eq: str) -> str:
    """把函数名/常量名替换为占位符，防止预处理时被拆开。

    按保留名长度降序替换，避免短名破坏长名（如 sin 破坏 asin）。
    """
    for name in sorted(RESERVED_NAMES, key=len, reverse=True):
        eq = eq.replace(name, _NAME_TO_PLACEHOLDER[name])
    return eq


def _unprotect_reserved(eq: str) -> str:
    """恢复被保护的函数名/常量名。"""
    for placeholder, name in _PROTECTED_MAP.items():
        eq = eq.replace(placeholder, name)
    return eq


def _convert_solution_value(val):
    """把 sympy 解的值转换为 int 或 BetterFloat；非实数解返回字符串。"""
    # 非实数（复数）解无法转换为 int/BetterFloat，保留字符串形式
    if not val.is_real:
        return str(val)
    if val.is_Integer:
        return int(val)
    f = float(val)
    if f.is_integer():
        return int(f)
    return BetterFloat(f)


def _insert_implicit_mul(equations: list[str], variables: list[str]) -> list[str]:
    """自动补全隐含乘号。

    处理规则：
    - 数字与变量之间：2x -> 2*x
    - 变量与变量之间：xy -> x*y
    - 数字与左括号之间：2(x+1) -> 2*(x+1)
    - 右括号与数字/变量/左括号之间：(x+1)2 -> (x+1)*2, (x+1)(x+2) -> (x+1)*(x+2)
    - 变量与左括号之间：x(x+1) -> x*(x+1)
    - 数字/变量/右括号与函数名/常量名之间：2sin(x) -> 2*sin(x), xsin(x) -> x*sin(x)

    会先保护 sympy 的函数名/常量名，避免 asin 被拆成 a*sin。
    """
    if not variables:
        return list(equations)

    # 按变量名长度降序，避免短变量名错误匹配长变量名的一部分
    sorted_vars = sorted(variables, key=len, reverse=True)
    var_pattern = '|'.join(re.escape(v) for v in sorted_vars)
    placeholder_pattern = '|'.join(re.escape(p) for p in _PROTECTED_MAP.keys())

    # 数字（含小数）
    num = r'\d+(?:\.\d+)?'

    result = []
    for eq in equations:
        # 保护函数名/常量名
        eq = _protect_reserved(eq)

        # 数字 + 变量名
        eq = re.sub(rf'({num})({var_pattern})', r'\1*\2', eq)
        # 变量名 + 变量名（循环处理连续多个变量，如 xyz -> x*y*z）
        prev = None
        while prev != eq:
            prev = eq
            eq = re.sub(rf'({var_pattern})({var_pattern})', r'\1*\2', eq)
        # 数字 + 左括号
        eq = re.sub(rf'({num})(\()', r'\1*\2', eq)
        # 右括号 + 数字
        eq = re.sub(rf'(\))({num})', r'\1*\2', eq)
        # 变量名 + 左括号
        eq = re.sub(rf'({var_pattern})(\()', r'\1*\2', eq)
        # 右括号 + 变量名
        eq = re.sub(rf'(\))({var_pattern})', r'\1*\2', eq)
        # 右括号 + 左括号
        eq = re.sub(rf'(\))(\()', r'\1*\2', eq)

        # 数字/变量/右括号与函数/常量占位符之间补 *
        eq = re.sub(rf'({num})({placeholder_pattern})', r'\1*\2', eq)
        eq = re.sub(rf'({var_pattern})({placeholder_pattern})', r'\1*\2', eq)
        eq = re.sub(rf'(\))({placeholder_pattern})', r'\1*\2', eq)
        eq = re.sub(rf'({placeholder_pattern})({num})', r'\1*\2', eq)

        # 恢复函数名/常量名
        eq = _unprotect_reserved(eq)

        result.append(eq)

    return result


def s_tri(bot:BetterFloat|ConvertibleToBetterFloat, high:BetterFloat|ConvertibleToBetterFloat) -> BetterFloat:
	"""计算三角形面积"""
	return BetterFloat(bot) * BetterFloat(high) / BetterFloat(2)

def s_rect(bot:BetterFloat|ConvertibleToBetterFloat, high:BetterFloat|ConvertibleToBetterFloat) -> BetterFloat:
	"""计算矩形面积"""
	return BetterFloat(bot) * BetterFloat(high)

def s_tra(bot:BetterFloat|ConvertibleToBetterFloat, top:BetterFloat|ConvertibleToBetterFloat, high:BetterFloat|ConvertibleToBetterFloat) -> BetterFloat:
	"""计算梯形面积"""
	return (BetterFloat(bot) + BetterFloat(top)) * BetterFloat(high) / BetterFloat(2)

def hsf_s_tri(a:BetterFloat|ConvertibleToBetterFloat, b:BetterFloat|ConvertibleToBetterFloat, c:BetterFloat|ConvertibleToBetterFloat) -> BetterFloat:
	"""使用海伦公式计算三角形面积"""
	a_bf = BetterFloat(a)
	b_bf = BetterFloat(b)
	c_bf = BetterFloat(c)
	s = (a_bf + b_bf + c_bf) / BetterFloat(2)
	return BetterFloat.sqrt(s * (s - a_bf) * (s - b_bf) * (s - c_bf))

def pt(a:BetterFloat|ConvertibleToBetterFloat, b:BetterFloat|ConvertibleToBetterFloat) -> BetterFloat:
	"""使用勾股定理计算直角三角形斜边"""
	return BetterFloat.sqrt(BetterFloat.pow(a, 2) + BetterFloat.pow(b, 2))

def s_circle(r:BetterFloat|ConvertibleToBetterFloat) -> BetterFloat:
	"""计算圆形面积"""
	return BF_PI * BetterFloat(r) * BetterFloat(r)

def bf(x:ConvertibleToBetterFloat=0) -> BetterFloat:
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


class CalculatorMaxError(Exception):
	'''Error generated in CalculatorMax calculating core.'''
	def __init__(self,info:str|None=None):
		self.info=info
		super().__init__(info)
	def __str__(self):
		return self.info

class CalculatorMaxEvalError(CalculatorMaxError):
	pass
class CalculatorMaxSolveError(CalculatorMaxError):
	pass


def calc(ev:str):
	"""[CalculatorMax]计算表达式"""
	
	f = '未知错误'
	err = True
	
	try:
		# 将数字字面量转换为 BetterFloat
		ev_processed = convert_expr_to_betterfloat(ev).replace('^','**').replace()
		
		f = str(simple_eval(ev_processed, names={
			"pi": BF_PI,
			"pi_hq":BF_PI_HQ,
			"e_hq":BF_E_HQ,
			"e": BF_E,
		}, functions={
			"bf":bf,
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
			"randint": lambda a, b: randint(int(BetterFloat(a)), int(BetterFloat(b))),
			"random": lambda: BetterFloat(random()),
			"randrange": lambda a, b: randrange(int(BetterFloat(a)), int(BetterFloat(b))),
			"uniform": lambda a, b: BetterFloat(uniform(float(BetterFloat(a)), float(BetterFloat(b)))),
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
	return err,f

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
		if v.lower() in RESERVED_NAMES:
			return False, False, f"变量名不能与函数名或常量名重合: {v}"
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
	"""求解线性方程组，返回 (success, equation_type, solution_dict)。"""
	try:
		var_symbols = symbols(variables)
		if not isinstance(var_symbols, (list, tuple)):
			var_symbols = [var_symbols]

		eqs = []
		for eq_str in equations:
			if isinstance(eq_str, str) and '=' in eq_str:
				left, right = eq_str.split('=', 1)
				eqs.append(Eq(sympify(left), sympify(right)))
			else:
				eqs.append(Eq(sympify(eq_str), 0))

		solution = sympy_solve(eqs, var_symbols, dict=True)

		if not solution:
			return True, EquationType.LINEAR, None

		# 取第一个解（线性方程组通常只有一个解）
		sol = solution[0] if isinstance(solution, list) else solution
		result = {str(var): _convert_solution_value(val) for var, val in sol.items()}

		return True, EquationType.LINEAR, result
	except Exception as e:
		return False, EquationType.LINEAR, {"error": str(e)}


def solve_polynomial_system(equations, variables):
	"""求解多项式方程组，返回 (success, equation_type, solution_dict)。

	当多项式方程组存在多组解时，只返回第一组解。
	"""
	try:
		var_symbols = symbols(variables)
		if not isinstance(var_symbols, (list, tuple)):
			var_symbols = [var_symbols]

		eqs = []
		for eq_str in equations:
			if isinstance(eq_str, str) and '=' in eq_str:
				left, right = eq_str.split('=', 1)
				eqs.append(Eq(sympify(left), sympify(right)))
			else:
				eqs.append(Eq(sympify(eq_str), 0))

		solution = sympy_solve(eqs, var_symbols, dict=True)

		if not solution:
			return True, EquationType.POLYNOMIAL, None

		# 取第一个解返回
		sol = solution[0] if isinstance(solution, list) else solution
		result = {str(var): _convert_solution_value(val) for var, val in sol.items()}

		return True, EquationType.POLYNOMIAL, result
	except Exception as e:
		return False, EquationType.POLYNOMIAL, {"error": str(e)}


def solve_numerical_system(equations, variables, initial_guess=None):
	"""使用数值方法求解非线性方程组，返回 (success, equation_type, solution_dict)。"""
	try:
		var_symbols = symbols(variables)
		if not isinstance(var_symbols, (list, tuple)):
			var_symbols = [var_symbols]

		funcs = []
		for eq_str in equations:
			if isinstance(eq_str, str) and '=' in eq_str:
				left, right = eq_str.split('=', 1)
				funcs.append(sympify(f"({left}) - ({right})"))
			else:
				funcs.append(sympify(eq_str))

		if initial_guess is None:
			initial_guess = [0.0] * len(variables)

		solution = nsolve(funcs, var_symbols, initial_guess, tol=1e-14, maxsteps=100)

		result = {}
		for i, var in enumerate(variables):
			val = solution[i]
			result[var] = _convert_solution_value(val)

		return True, EquationType.NUMERICAL, result
	except Exception as e:
		return False, EquationType.NUMERICAL, {"error": str(e)}


def solve_equations(equations: tuple[str], variables: tuple[str], initial_guess: tuple[int] | None = None):
	"""
	[CalculatorMax]求解方程（组）

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
	
	# 1. 验证输入
	is_valid, can_solve, message = validate_equation_input(equations, variables)

	if not is_valid:
		raise CalculatorMaxSolveError(message)

	# 2. 自动补全隐含乘号（如 2x -> 2*x，xy -> x*y）
	equations = _insert_implicit_mul(list(equations), list(variables))

	try:
		# 3. 解析方程为 sympy 表达式以判断类型
		var_symbols = symbols(variables)
		if not isinstance(var_symbols, (list, tuple)):
			var_symbols = [var_symbols]
		
		exprs = []
		for eq_str in equations:
			
			# 转换为表达式
			if '=' in eq_str:
				left, right = eq_str.split('=', 1)
				expr = sympify(f"({left}) - ({right})")
			else:
				expr = sympify(eq_str)
			exprs.append(expr)
		
		# 4. 判断方程类型并求解
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

		# result 已经是 (success, equation_type, solution) 格式
		return result
		
	except Exception as e:
		error_msg = str(e)
		raise CalculatorMaxSolveError(error_msg)
