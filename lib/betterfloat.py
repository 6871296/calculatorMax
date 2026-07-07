from __future__ import annotations
from collections.abc import *
import math
from typing import *
if TYPE_CHECKING:
	from _typeshed import ConvertibleToFloat,ConvertibleToInt
else:
	# Copied from typeshed fallback for VScode
	import sys
	ReadableBuffer: TypeAlias = Buffer
	if sys.version_info >= (3, 14):
		ConvertibleToInt: TypeAlias = str | ReadableBuffer | SupportsInt | SupportsIndex
	else:
		class SupportsTrunc(Protocol):
			def __trunc__(self) -> int: ...
		ConvertibleToInt: TypeAlias = str | ReadableBuffer | SupportsInt | SupportsIndex | SupportsTrunc
	ConvertibleToFloat: TypeAlias = str | ReadableBuffer | SupportsFloat | SupportsIndex
from sys import set_int_max_str_digits as int2strdigits
int2strdigits(5300)


class BetterFloat:
	'''
		BetterFloat is a Python class designed for removing errors generated when converting decimal to binary(i.e.In real life 1.1+2.2=3.3, but in Python 1.1+2.2~=3.3000000000000003).
		It can add, minus, etc., just like int and float, but 1.1+2.2=3.3, not 3.3000000000000003.
		
		Internal representation:
		- _value: int - the integer value without decimal point (e.g., 123 for 1.23 or 12.3)
		- _exp: int - the exponent (10**exp is the divisor), i.e., number of decimal places
		
		Example: 1.23 -> _value=123, _exp=2
				 12.3 -> _value=123, _exp=1
	'''
	
	__slots__ = ('_value', '_exp', '_is_nan', '_is_inf', '_sign')
	
	# Context for decimal operations
	_precision: int = 50  # Default precision for operations
	_max_precision: int = 16384  # Maximum allowed precision to prevent memory issues. If you're using a laptop, you'd better not to change this any bigger. 
	_max_exp: int = 50000  # Maximum allowed exponent (10^50000 is a huge number)
	
	def __init__(self, value: ConvertibleToBetterFloat = 0, *, exp: Optional[int] = None):
		'''
		Initialize BetterFloat from int, float, str, or another BetterFloat.
		If exp is provided, value is treated as an integer and exp is the number of decimal places.
		'''
		# Initialize special attributes first
		self._is_nan = False
		self._is_inf = False
		self._sign = 0
		
		if exp is not None:
			# Direct construction: BetterFloat(123, exp=2) -> 1.23
			exp_int = max(0, int(exp))
			BetterFloat._check_exp(exp_int, "构造BetterFloat")
			self._value = int(value)
			self._exp = exp_int
			self._normalize()
			return
		
		if isinstance(value, BetterFloat):
			self._value = value._value
			self._exp = value._exp
			self._is_nan = value._is_nan
			self._is_inf = value._is_inf
			self._sign = value._sign
		elif isinstance(value, int):
			self._value = value
			self._exp = 0
		elif isinstance(value, float):
			# Convert float to string to get exact decimal representation
			if math.isnan(value):
				self._value = 0
				self._exp = 0
				self._is_nan = True
				return
			if math.isinf(value):
				self._value = 0
				self._exp = 0
				self._is_inf = True
				self._sign = 1 if value > 0 else -1
				return
			# Use repr for precision, but clean it up
			s = repr(value)
			self._from_decimal_str(s)
		elif isinstance(value, str):
			self._from_decimal_str(value.strip())
		elif hasattr(value,'__int__'):
			self.__init__(int(value))
		elif hasattr(value, '__float__'):
			self.__init__(float(value))
		else:
			raise TypeError(f"Cannot convert {type(value).__name__} to BetterFloat")
		
		self._normalize()
	
	def _from_decimal_str(self, s: str) -> None:
		'''Parse decimal string representation.'''
		s = s.strip().lower().replace('_', '')
		
		# Handle special values
		if s in ('nan', '+nan', '-nan'):
			self._value = 0
			self._exp = 0
			self._is_nan = True
			self._is_inf = False
			self._sign = 0
			return
		if s in ('inf', '+inf', 'infinity', '+infinity'):
			self._value = 0
			self._exp = 0
			self._is_nan = False
			self._is_inf = True
			self._sign = 1
			return
		if s in ('-inf', '-infinity'):
			self._value = 0
			self._exp = 0
			self._is_nan = False
			self._is_inf = True
			self._sign = -1
			return
		
		self._is_nan = False
		self._is_inf = False
		self._sign = 0
		
		# Handle scientific notation
		if 'e' in s:
			parts = s.split('e')
			mantissa = parts[0]
			exponent = int(parts[1])
			
			if '.' in mantissa:
				int_part, frac_part = mantissa.split('.')
				significant = int_part + frac_part
				frac_len = len(frac_part)
			else:
				significant = mantissa
				frac_len = 0
			
			# Adjust for scientific notation
			exp_adjust = frac_len - exponent
			if exp_adjust <= 0:
				# Need to add zeros
				significant += '0' * (-exp_adjust)
				self._value = int(significant)
				self._exp = 0
			else:
				self._value = int(significant)
				self._exp = exp_adjust
		else:
			if '.' in s:
				int_part, frac_part = s.split('.')
				# Handle sign
				sign = 1
				if int_part.startswith('-'):
					sign = -1
					int_part = int_part[1:] or '0'
				elif int_part.startswith('+'):
					int_part = int_part[1:] or '0'
				
				# Remove leading zeros from int_part and trailing zeros from frac_part
				frac_part = frac_part.rstrip('0')
				int_part = int(int_part) if int_part else 0
				
				if frac_part:
					exp_val = len(frac_part)
					BetterFloat._check_exp(exp_val, f"解析小数(长度{exp_val})")
					self._value = sign * (int(str(int_part)) * (BetterFloat._safe_power10(exp_val, "解析小数") ) + int(frac_part))
					self._exp = exp_val
				else:
					self._value = sign * int_part
					self._exp = 0
			else:
				self._value = int(s)
				self._exp = 0
	
	def _normalize(self) -> None:
		'''Remove trailing zeros from fractional part and normalize.'''
		if self._value == 0:
			self._exp = 0
			return
		
		# Remove trailing zeros by dividing by 10 while possible
		while self._exp > 0 and self._value % 10 == 0:
			self._value //= 10
			self._exp -= 1
	
	def __float__(self) -> float:
		'''Convert to float.'''
		if hasattr(self, '_is_nan') and self._is_nan:
			return float('nan')
		if hasattr(self, '_is_inf') and self._is_inf:
			return float('inf') * self._sign
		return self._value / (10 ** self._exp)
	
	def __int__(self) -> int:
		'''Convert to int (truncates towards zero).'''
		return int(self.__float__())
	
	def __str__(self) -> str:
		'''String representation.'''
		if hasattr(self, '_is_nan') and self._is_nan:
			return 'nan'
		if hasattr(self, '_is_inf') and self._is_inf:
			return 'inf' if self._sign > 0 else '-inf'
		
		if self._exp == 0:
			return str(self._value)
		
		sign = '-' if self._value < 0 else ''
		v = abs(self._value)
		s = str(v)
		
		# Pad with leading zeros if needed
		if len(s) <= self._exp:
			s = '0' * (self._exp - len(s) + 1) + s
		
		# Insert decimal point
		int_part = s[:-self._exp] if len(s) > self._exp else '0'
		frac_part = s[-self._exp:]
		
		return f"{sign}{int_part}.{frac_part}"
	
	def __repr__(self) -> str:
		'''Repr representation.'''
		if hasattr(self, '_is_nan') and self._is_nan:
			return 'BetterFloat("nan")'
		if hasattr(self, '_is_inf') and self._is_inf:
			return f'BetterFloat("{"inf" if self._sign > 0 else "-inf"}")'
		return f'BetterFloat("{str(self)}")'
	
	def __hash__(self) -> int:
		'''Hash support.'''
		return hash((self._value, self._exp))
	
	# ==================== Arithmetic Operations ====================
	
	def __add__(self, other) -> 'BetterFloat':
		if not isinstance(other, BetterFloat):
			other = BetterFloat(other)
		
		# Handle special values
		if self._is_nan or other._is_nan:
			result = BetterFloat("nan")
			return result
		if self._is_inf:
			if other._is_inf and self._sign != other._sign:
				result = BetterFloat("nan")
			else:
				result = BetterFloat("inf" if self._sign > 0 else "-inf")
			return result
		if other._is_inf:
			return BetterFloat("inf" if other._sign > 0 else "-inf")
		
		# Align exponents
		if self._exp > other._exp:
			# self has more decimal places
			exp_diff = self._exp - other._exp
			BetterFloat._check_exp(exp_diff, "加法对齐指数")
			scale = BetterFloat._safe_power10(exp_diff, "加法对齐指数")
			new_value = self._value + other._value * scale
			new_exp = self._exp
		elif self._exp < other._exp:
			# other has more decimal places
			exp_diff = other._exp - self._exp
			BetterFloat._check_exp(exp_diff, "加法对齐指数")
			scale = BetterFloat._safe_power10(exp_diff, "加法对齐指数")
			new_value = self._value * scale + other._value
			new_exp = other._exp
		else:
			new_value = self._value + other._value
			new_exp = self._exp
		
		return BetterFloat(new_value, exp=new_exp)
	
	def __radd__(self, other) -> 'BetterFloat':
		return self.__add__(other)
	
	def __sub__(self, other) -> 'BetterFloat':
		if not isinstance(other, BetterFloat):
			other = BetterFloat(other)
		
		# Handle special values
		if self._is_nan or other._is_nan:
			return BetterFloat("nan")
		if self._is_inf:
			if other._is_inf:
				if self._sign == other._sign:
					return BetterFloat("nan")
				return BetterFloat("inf" if self._sign > 0 else "-inf")
			return BetterFloat("inf" if self._sign > 0 else "-inf")
		if other._is_inf:
			return BetterFloat("-inf" if other._sign > 0 else "inf")
		
		# Align exponents
		if self._exp > other._exp:
			exp_diff = self._exp - other._exp
			BetterFloat._check_exp(exp_diff, "减法对齐指数")
			scale = BetterFloat._safe_power10(exp_diff, "减法对齐指数")
			new_value = self._value - other._value * scale
			new_exp = self._exp
		elif self._exp < other._exp:
			exp_diff = other._exp - self._exp
			BetterFloat._check_exp(exp_diff, "减法对齐指数")
			scale = BetterFloat._safe_power10(exp_diff, "减法对齐指数")
			new_value = self._value * scale - other._value
			new_exp = other._exp
		else:
			new_value = self._value - other._value
			new_exp = self._exp
		
		return BetterFloat(new_value, exp=new_exp)
	
	def __rsub__(self, other) -> 'BetterFloat':
		if not isinstance(other, BetterFloat):
			other = BetterFloat(other)
		return other.__sub__(self)
	
	def __mul__(self, other) -> 'BetterFloat':
		if not isinstance(other, BetterFloat):
			other = BetterFloat(other)
		
		# Handle special values
		if self._is_nan or other._is_nan:
			return BetterFloat("nan")
		if self._is_inf or other._is_inf:
			if (self._is_inf and other._value == 0) or (other._is_inf and self._value == 0):
				return BetterFloat("nan")
			new_sign = (1 if self._value >= 0 else -1) * (1 if other._value >= 0 else -1)
			if self._is_inf:
				new_sign = self._sign * (1 if other._value >= 0 else -1)
			elif other._is_inf:
				new_sign = (1 if self._value >= 0 else -1) * other._sign
			return BetterFloat("inf" if new_sign > 0 else "-inf")
		
		new_value = self._value * other._value
		new_exp = self._exp + other._exp
		return BetterFloat(new_value, exp=new_exp)
	
	def __rmul__(self, other) -> 'BetterFloat':
		return self.__mul__(other)
	
	def __truediv__(self, other) -> 'BetterFloat':
		if not isinstance(other, BetterFloat):
			other = BetterFloat(other)
		
		# Handle special values
		if self._is_nan or other._is_nan:
			return BetterFloat("nan")
		if other._is_inf:
			if self._is_inf:
				return BetterFloat("nan")
			return BetterFloat(0)
		if self._is_inf:
			new_sign = self._sign * (1 if other._value >= 0 else -1)
			return BetterFloat("inf" if new_sign > 0 else "-inf")
		
		if other._value == 0:
			if self._value == 0:
				return BetterFloat("nan")
			sign = 1 if (self._value > 0) == (other._value > 0) else -1
			return BetterFloat("inf" if sign > 0 else "-inf")
		
		# For division, we need to scale up to maintain precision
		# Use precision limit to avoid infinite expansion
		precision = BetterFloat._precision
		exp_needed = precision + other._exp - self._exp
		BetterFloat._check_exp(exp_needed, "除法运算")
		scale = BetterFloat._safe_power10(exp_needed, "除法运算")
		new_value = (self._value * scale) // other._value
		new_exp = precision
		
		return BetterFloat(new_value, exp=new_exp)
	
	def __rtruediv__(self, other) -> 'BetterFloat':
		if not isinstance(other, BetterFloat):
			other = BetterFloat(other)
		return other.__truediv__(self)
	
	def __pow__(self, other) -> 'BetterFloat':
		if not isinstance(other, BetterFloat):
			other = BetterFloat(other)
		
		# Handle special values
		if self._is_nan or other._is_nan:
			return BetterFloat("nan")
		if self._is_inf:
			if other._value == 0:
				return BetterFloat("nan")
			if other._value > 0:
				return BetterFloat("inf" if (self._sign > 0 or int(other._value) % 2 == 0) else "-inf")
			return BetterFloat(0)
		if other._is_inf:
			if abs(self._value) > 10 ** self._exp:
				return BetterFloat("inf")
			if abs(self._value) < 10 ** self._exp:
				return BetterFloat(0)
			return BetterFloat("nan")
		
		# Use float for non-integer exponents
		if other._exp > 0:
			return BetterFloat(float(self) ** float(other))
		
		exp_int = other._value // (10 ** other._exp)
		if self._value == 0 and exp_int < 0:
			return BetterFloat("inf" if (exp_int % 2 == 0 or 1 if self._value >= 0 else -1) > 0 else "-inf")
		
		# For integer exponents, use exact arithmetic
		new_value = self._value ** exp_int
		new_exp = self._exp * exp_int
		return BetterFloat(new_value, exp=new_exp)
	
	def __rpow__(self, other) -> 'BetterFloat':
		if not isinstance(other, BetterFloat):
			other = BetterFloat(other)
		return other.__pow__(self)
	
	def __neg__(self) -> 'BetterFloat':
		result = BetterFloat(-self._value, exp=self._exp)
		result._is_nan = getattr(self, '_is_nan', False)
		result._is_inf = getattr(self, '_is_inf', False)
		result._sign = -getattr(self, '_sign', 0) if result._is_inf else 0
		return result
	
	def __pos__(self) -> 'BetterFloat':
		return BetterFloat(self._value, exp=self._exp)
	
	def __abs__(self) -> 'BetterFloat':
		return BetterFloat(abs(self._value), exp=self._exp)
	
	def __floordiv__(self, other) -> 'BetterFloat':
		if not isinstance(other, BetterFloat):
			other = BetterFloat(other)
		return BetterFloat(int(self / other))
	
	def __rfloordiv__(self, other) -> 'BetterFloat':
		if not isinstance(other, BetterFloat):
			other = BetterFloat(other)
		return BetterFloat(int(other / self))
	
	def __mod__(self, other) -> 'BetterFloat':
		if not isinstance(other, BetterFloat):
			other = BetterFloat(other)
		if self._is_nan or other._is_nan:
			return BetterFloat("nan")
		if other._is_inf or other._value == 0:
			return BetterFloat("nan")
		div = self // other
		return self - div * other
	
	def __rmod__(self, other) -> 'BetterFloat':
		if not isinstance(other, BetterFloat):
			other = BetterFloat(other)
		return other % self
	
	def __divmod__(self, other) -> tuple['BetterFloat', 'BetterFloat']:
		if not isinstance(other, BetterFloat):
			other = BetterFloat(other)
		div = self // other
		mod = self - div * other
		return (div, mod)
	
	def __rdivmod__(self, other) -> tuple['BetterFloat', 'BetterFloat']:
		if not isinstance(other, BetterFloat):
			other = BetterFloat(other)
		return divmod(other, self)
	
	# ==================== Comparison Operations ====================
	
	def _cmp(self, other) -> int:
		'''Compare self with other. Returns -1, 0, or 1.'''
		if not isinstance(other, BetterFloat):
			try:
				other = BetterFloat(other)
			except (TypeError, ValueError):
				return NotImplemented
		
		# Handle NaN
		if self._is_nan or other._is_nan:
			return 0  # NaN is not equal to anything, including itself
		
		# Handle infinity
		if self._is_inf and other._is_inf:
			return 0 if self._sign == other._sign else (1 if self._sign > other._sign else -1)
		if self._is_inf:
			return self._sign
		if other._is_inf:
			return -other._sign
		
		# Align exponents and compare
		if self._exp > other._exp:
			exp_diff = self._exp - other._exp
			BetterFloat._check_exp(exp_diff, "比较对齐指数")
			scale = BetterFloat._safe_power10(exp_diff, "比较对齐指数")
			sv = self._value
			ov = other._value * scale
		elif self._exp < other._exp:
			exp_diff = other._exp - self._exp
			BetterFloat._check_exp(exp_diff, "比较对齐指数")
			scale = BetterFloat._safe_power10(exp_diff, "比较对齐指数")
			sv = self._value * scale
			ov = other._value
		else:
			sv = self._value
			ov = other._value
		
		if sv < ov:
			return -1
		elif sv > ov:
			return 1
		else:
			return 0
	
	def __eq__(self, other) -> bool:
		if not isinstance(other, (BetterFloat, int, float, str)):
			return NotImplemented
		result = self._cmp(other)
		if result is NotImplemented:
			return NotImplemented
		return result == 0
	
	def __ne__(self, other) -> bool:
		result = self._cmp(other)
		if result is NotImplemented:
			return NotImplemented
		return result != 0
	
	def __lt__(self, other) -> bool:
		result = self._cmp(other)
		if result is NotImplemented:
			return NotImplemented
		# NaN comparisons are always False
		if self._is_nan or (isinstance(other, BetterFloat) and other._is_nan):
			return False
		return result < 0
	
	def __le__(self, other) -> bool:
		result = self._cmp(other)
		if result is NotImplemented:
			return NotImplemented
		if self._is_nan or (isinstance(other, BetterFloat) and other._is_nan):
			return False
		return result <= 0
	
	def __gt__(self, other) -> bool:
		result = self._cmp(other)
		if result is NotImplemented:
			return NotImplemented
		if self._is_nan or (isinstance(other, BetterFloat) and other._is_nan):
			return False
		return result > 0
	
	def __ge__(self, other) -> bool:
		result = self._cmp(other)
		if result is NotImplemented:
			return NotImplemented
		if self._is_nan or (isinstance(other, BetterFloat) and other._is_nan):
			return False
		return result >= 0
	
	# ==================== Math Module Compatibility ====================
	
	@classmethod
	def set_precision(cls, precision: int) -> None:
		'''Set the precision for division operations.'''
		if precision > cls._max_precision:
			raise OverflowError(f"精度不能超过 {cls._max_precision} 位")
		cls._precision = max(10, precision)
	
	@staticmethod
	def _check_exp(exp: int, context: str = "") -> None:
		'''Check if exponent is within safe limits.'''
		if exp > BetterFloat._max_exp:
			raise OverflowError(f"指数过大 ({exp}), 超过最大限制 {BetterFloat._max_exp}{': ' + context if context else ''}")
	
	@staticmethod
	def _safe_power10(exp: int, context: str = "") -> int:
		'''Safely compute 10**exp with overflow check.'''
		BetterFloat._check_exp(exp, context)
		try:
			return 10 ** exp
		except MemoryError:
			raise OverflowError(f"内存不足，无法计算 10^{exp}{': ' + context if context else ''}")
	
	@staticmethod
	def sqrt(x: 'BetterFloat | int | float | str') -> 'BetterFloat':
		'''Square root.'''
		if not isinstance(x, BetterFloat):
			x = BetterFloat(x)
		if x._is_nan or x._is_inf and x._sign < 0:
			return BetterFloat("nan")
		if x._is_inf:
			return BetterFloat("inf")
		if x._value < 0:
			return BetterFloat("nan")
		return BetterFloat(math.sqrt(float(x)))
	
	@staticmethod
	def cbrt(x: 'BetterFloat | int | float | str') -> 'BetterFloat':
		'''Cube root.'''
		if not isinstance(x, BetterFloat):
			x = BetterFloat(x)
		if x._is_nan:
			return BetterFloat("nan")
		if x._is_inf:
			return BetterFloat("inf" if x._sign > 0 else "-inf")
		return BetterFloat(float(x) ** (1/3))
	
	@staticmethod
	def sin(x: 'BetterFloat | int | float | str') -> 'BetterFloat':
		'''Sine function.'''
		if not isinstance(x, BetterFloat):
			x = BetterFloat(x)
		return BetterFloat(math.sin(float(x)))
	
	@staticmethod
	def cos(x: 'BetterFloat | int | float | str') -> 'BetterFloat':
		'''Cosine function.'''
		if not isinstance(x, BetterFloat):
			x = BetterFloat(x)
		return BetterFloat(math.cos(float(x)))
	
	@staticmethod
	def tan(x: 'BetterFloat | int | float | str') -> 'BetterFloat':
		'''Tangent function.'''
		if not isinstance(x, BetterFloat):
			x = BetterFloat(x)
		return BetterFloat(math.tan(float(x)))
	
	@staticmethod
	def asin(x: 'BetterFloat | int | float | str') -> 'BetterFloat':
		'''Arc sine function.'''
		if not isinstance(x, BetterFloat):
			x = BetterFloat(x)
		return BetterFloat(math.asin(float(x)))
	
	@staticmethod
	def acos(x: 'BetterFloat | int | float | str') -> 'BetterFloat':
		'''Arc cosine function.'''
		if not isinstance(x, BetterFloat):
			x = BetterFloat(x)
		return BetterFloat(math.acos(float(x)))
	
	@staticmethod
	def atan(x: 'BetterFloat | int | float | str') -> 'BetterFloat':
		'''Arc tangent function.'''
		if not isinstance(x, BetterFloat):
			x = BetterFloat(x)
		return BetterFloat(math.atan(float(x)))
	
	@staticmethod
	def atan2(y: 'BetterFloat | int | float | str', x: 'BetterFloat | int | float | str') -> 'BetterFloat':
		'''Two-argument arc tangent.'''
		if not isinstance(y, BetterFloat):
			y = BetterFloat(y)
		if not isinstance(x, BetterFloat):
			x = BetterFloat(x)
		return BetterFloat(math.atan2(float(y), float(x)))
	
	@staticmethod
	def sinh(x: 'BetterFloat | int | float | str') -> 'BetterFloat':
		'''Hyperbolic sine.'''
		if not isinstance(x, BetterFloat):
			x = BetterFloat(x)
		return BetterFloat(math.sinh(float(x)))
	
	@staticmethod
	def cosh(x: 'BetterFloat | int | float | str') -> 'BetterFloat':
		'''Hyperbolic cosine.'''
		if not isinstance(x, BetterFloat):
			x = BetterFloat(x)
		return BetterFloat(math.cosh(float(x)))
	
	@staticmethod
	def tanh(x: 'BetterFloat | int | float | str') -> 'BetterFloat':
		'''Hyperbolic tangent.'''
		if not isinstance(x, BetterFloat):
			x = BetterFloat(x)
		return BetterFloat(math.tanh(float(x)))
	
	@staticmethod
	def asinh(x: 'BetterFloat | int | float | str') -> 'BetterFloat':
		'''Inverse hyperbolic sine.'''
		if not isinstance(x, BetterFloat):
			x = BetterFloat(x)
		return BetterFloat(math.asinh(float(x)))
	
	@staticmethod
	def acosh(x: 'BetterFloat | int | float | str') -> 'BetterFloat':
		'''Inverse hyperbolic cosine.'''
		if not isinstance(x, BetterFloat):
			x = BetterFloat(x)
		return BetterFloat(math.acosh(float(x)))
	
	@staticmethod
	def atanh(x: 'BetterFloat | int | float | str') -> 'BetterFloat':
		'''Inverse hyperbolic tangent.'''
		if not isinstance(x, BetterFloat):
			x = BetterFloat(x)
		return BetterFloat(math.atanh(float(x)))
	
	@staticmethod
	def exp(x: 'BetterFloat | int | float | str') -> 'BetterFloat':
		'''Exponential function.'''
		if not isinstance(x, BetterFloat):
			x = BetterFloat(x)
		return BetterFloat(math.exp(float(x)))
	
	@staticmethod
	def expm1(x: 'BetterFloat | int | float | str') -> 'BetterFloat':
		'''exp(x) - 1.'''
		if not isinstance(x, BetterFloat):
			x = BetterFloat(x)
		return BetterFloat(math.expm1(float(x)))
	
	@staticmethod
	def log(x: 'BetterFloat | int | float | str', base: Optional['BetterFloat | int | float | str'] = None) -> 'BetterFloat':
		'''Natural logarithm or logarithm with specified base.'''
		if not isinstance(x, BetterFloat):
			x = BetterFloat(x)
		if base is None:
			return BetterFloat(math.log(float(x)))
		if not isinstance(base, BetterFloat):
			base = BetterFloat(base)
		return BetterFloat(math.log(float(x), float(base)))
	
	@staticmethod
	def log1p(x: 'BetterFloat | int | float | str') -> 'BetterFloat':
		'''log(1 + x).'''
		if not isinstance(x, BetterFloat):
			x = BetterFloat(x)
		return BetterFloat(math.log1p(float(x)))
	
	@staticmethod
	def log10(x: 'BetterFloat | int | float | str') -> 'BetterFloat':
		'''Base-10 logarithm.'''
		if not isinstance(x, BetterFloat):
			x = BetterFloat(x)
		return BetterFloat(math.log10(float(x)))
	
	@staticmethod
	def log2(x: 'BetterFloat | int | float | str') -> 'BetterFloat':
		'''Base-2 logarithm.'''
		if not isinstance(x, BetterFloat):
			x = BetterFloat(x)
		return BetterFloat(math.log2(float(x)))
	
	@staticmethod
	def pow(x: 'BetterFloat | int | float | str', y: 'BetterFloat | int | float | str') -> 'BetterFloat':
		'''Power function.'''
		if not isinstance(x, BetterFloat):
			x = BetterFloat(x)
		if not isinstance(y, BetterFloat):
			y = BetterFloat(y)
		return x ** y
	
	@staticmethod
	def floor(x: 'BetterFloat | int | float | str') -> 'BetterFloat':
		'''Floor - largest integer <= x.'''
		if not isinstance(x, BetterFloat):
			x = BetterFloat(x)
		if x._exp == 0:
			return BetterFloat(x._value)
		# Python's // is already floor division
		scale = BetterFloat._safe_power10(x._exp, "floor运算")
		return BetterFloat(x._value // scale)
	
	@staticmethod
	def ceil(x: 'BetterFloat | int | float | str') -> 'BetterFloat':
		'''Ceiling - smallest integer >= x.'''
		if not isinstance(x, BetterFloat):
			x = BetterFloat(x)
		if x._exp == 0:
			return BetterFloat(x._value)
		scale = BetterFloat._safe_power10(x._exp, "ceil运算")
		# Use the identity: ceil(a/b) = -floor(-a/b)
		return BetterFloat(-(-x._value // scale))
	
	@staticmethod
	def trunc(x: 'BetterFloat | int | float | str') -> 'BetterFloat':
		'''Truncate towards zero.'''
		if not isinstance(x, BetterFloat):
			x = BetterFloat(x)
		if x._exp == 0:
			return BetterFloat(x._value)
		# Truncate towards zero: use int() which truncates towards zero
		scale = BetterFloat._safe_power10(x._exp, "trunc运算")
		if x._value >= 0:
			return BetterFloat(x._value // scale)
		else:
			return BetterFloat(-(-x._value // scale))
	
	@staticmethod
	def fabs(x: 'BetterFloat | int | float | str') -> 'BetterFloat':
		'''Absolute value.'''
		if not isinstance(x, BetterFloat):
			x = BetterFloat(x)
		return abs(x)
	
	@staticmethod
	def modf(x: 'BetterFloat | int | float | str') -> tuple['BetterFloat', 'BetterFloat']:
		'''Return fractional and integer parts.'''
		if not isinstance(x, BetterFloat):
			x = BetterFloat(x)
		int_part = BetterFloat.trunc(x)
		frac_part = x - int_part
		return (frac_part, int_part)
	
	@staticmethod
	def degrees(x: 'BetterFloat | int | float | str') -> 'BetterFloat':
		'''Convert radians to degrees.'''
		if not isinstance(x, BetterFloat):
			x = BetterFloat(x)
		return BetterFloat(math.degrees(float(x)))
	
	@staticmethod
	def radians(x: 'BetterFloat | int | float | str') -> 'BetterFloat':
		'''Convert degrees to radians.'''
		if not isinstance(x, BetterFloat):
			x = BetterFloat(x)
		return BetterFloat(math.radians(float(x)))
	
	@staticmethod
	def factorial(x: 'BetterFloat | int | float | str') -> 'BetterFloat':
		'''Factorial of n.'''
		if not isinstance(x, BetterFloat):
			x = BetterFloat(x)
		if x._exp > 0:
			raise ValueError("factorial() only accepts integral values")
		return BetterFloat(math.factorial(abs(x._value)))
	
	@staticmethod
	def gcd(a: 'BetterFloat | int', b: 'BetterFloat | int') -> 'BetterFloat':
		'''Greatest common divisor.'''
		if not isinstance(a, BetterFloat):
			a = BetterFloat(a)
		if not isinstance(b, BetterFloat):
			b = BetterFloat(b)
		if a._exp > 0 or b._exp > 0:
			# Convert to integer representation
			max_exp = max(a._exp, b._exp)
			BetterFloat._check_exp(max_exp, "GCD运算")
			scale = BetterFloat._safe_power10(max_exp, "GCD运算")
			return BetterFloat(math.gcd(int(a * scale), int(b * scale)))
		return BetterFloat(math.gcd(abs(a._value), abs(b._value)))
	
	@staticmethod
	def lcm(a: 'BetterFloat | int', b: 'BetterFloat | int') -> 'BetterFloat':
		'''Least common multiple.'''
		if not isinstance(a, BetterFloat):
			a = BetterFloat(a)
		if not isinstance(b, BetterFloat):
			b = BetterFloat(b)
		if hasattr(math, 'lcm'):
			# Python 3.9+
			if a._exp > 0 or b._exp > 0:
				max_exp = max(a._exp, b._exp)
				BetterFloat._check_exp(max_exp, "LCM运算")
				scale = BetterFloat._safe_power10(max_exp, "LCM运算")
				return BetterFloat(math.lcm(int(a * scale), int(b * scale)))
			return BetterFloat(math.lcm(abs(a._value), abs(b._value)))
		else:
			# Fallback for older Python
			return BetterFloat(abs(int(a) * int(b)) // int(BetterFloat.gcd(a, b)))
	
	@staticmethod
	def isclose(a: 'BetterFloat | int | float | str', b: 'BetterFloat | int | float | str', *, 
			rel_tol: 'BetterFloat | float' = 1e-09, abs_tol: 'BetterFloat | float' = 0.0) -> bool:
		'''Determine whether two floating point numbers are close in value.'''
		if not isinstance(a, BetterFloat):
			a = BetterFloat(a)
		if not isinstance(b, BetterFloat):
			b = BetterFloat(b)
		return math.isclose(float(a), float(b), rel_tol=float(rel_tol), abs_tol=float(abs_tol))
	
	@staticmethod
	def isinf(x: 'BetterFloat | int | float | str') -> bool:
		'''Check if x is infinity.'''
		if not isinstance(x, BetterFloat):
			x = BetterFloat(x)
		return x._is_inf
	
	@staticmethod
	def isnan(x: 'BetterFloat | int | float | str') -> bool:
		'''Check if x is NaN.'''
		if not isinstance(x, BetterFloat):
			x = BetterFloat(x)
		return x._is_nan
	
	@staticmethod
	def isfinite(x: 'BetterFloat | int | float | str') -> bool:
		'''Check if x is finite.'''
		if not isinstance(x, BetterFloat):
			x = BetterFloat(x)
		return not (x._is_inf or x._is_nan)
	
	@staticmethod
	def copysign(x: 'BetterFloat | int | float | str', y: 'BetterFloat | int | float | str') -> 'BetterFloat':
		'''Return the magnitude of x with the sign of y.'''
		if not isinstance(x, BetterFloat):
			x = BetterFloat(x)
		if not isinstance(y, BetterFloat):
			y = BetterFloat(y)
		return BetterFloat(math.copysign(float(x), float(y)))
	
	@staticmethod
	def fsum(iterable: Iterable['BetterFloat | int | float | str']) -> 'BetterFloat':
		'''Accurate floating point sum of values in the iterable.'''
		total = BetterFloat(0)
		for x in iterable:
			total = total + x
		return total
	
	@staticmethod
	def prod(iterable: Iterable['BetterFloat | int | float | str']) -> 'BetterFloat':
		'''Product of all elements in the iterable.'''
		total = BetterFloat(1)
		for x in iterable:
			total = total * x
		return total
	
	@staticmethod
	def hypot(*coordinates: 'BetterFloat | int | float | str') -> 'BetterFloat':
		'''Euclidean norm.'''
		if not coordinates:
			return BetterFloat(0)
		sum_sq = BetterFloat(0)
		for c in coordinates:
			c_bf = BetterFloat(c)
			sum_sq = sum_sq + c_bf * c_bf
		return BetterFloat.sqrt(sum_sq)
	
	@staticmethod
	def dist(p: Sequence['BetterFloat | int | float | str'], q: Sequence['BetterFloat | int | float | str']) -> 'BetterFloat':
		'''Euclidean distance between two points.'''
		if len(p) != len(q):
			raise ValueError("p and q must have the same dimension")
		sum_sq = BetterFloat(0)
		for pi, qi in zip(p, q):
			diff = BetterFloat(pi) - BetterFloat(qi)
			sum_sq = sum_sq + diff * diff
		return BetterFloat.sqrt(sum_sq)
	
	@staticmethod
	def gamma(x: 'BetterFloat | int | float | str') -> 'BetterFloat':
		'''Gamma function.'''
		if not isinstance(x, BetterFloat):
			x = BetterFloat(x)
		return BetterFloat(math.gamma(float(x)))
	
	@staticmethod
	def lgamma(x: 'BetterFloat | int | float | str') -> 'BetterFloat':
		'''Natural logarithm of absolute value of Gamma function.'''
		if not isinstance(x, BetterFloat):
			x = BetterFloat(x)
		return BetterFloat(math.lgamma(float(x)))
	
	@staticmethod
	def erf(x: 'BetterFloat | int | float | str') -> 'BetterFloat':
		'''Error function.'''
		if not isinstance(x, BetterFloat):
			x = BetterFloat(x)
		return BetterFloat(math.erf(float(x)))
	
	@staticmethod
	def erfc(x: 'BetterFloat | int | float | str') -> 'BetterFloat':
		'''Complementary error function.'''
		if not isinstance(x, BetterFloat):
			x = BetterFloat(x)
		return BetterFloat(math.erfc(float(x)))
	
	@staticmethod
	def comb(n: 'BetterFloat | int', k: 'BetterFloat | int') -> 'BetterFloat':
		'''Number of ways to choose k items from n items without repetition.'''
		if not isinstance(n, BetterFloat):
			n = BetterFloat(n)
		if not isinstance(k, BetterFloat):
			k = BetterFloat(k)
		return BetterFloat(math.comb(int(n), int(k)))
	
	@staticmethod
	def perm(n: 'BetterFloat | int', k: 'BetterFloat | int' = None) -> 'BetterFloat':
		'''Number of ways to choose k items from n items without repetition and with order.'''
		if not isinstance(n, BetterFloat):
			n = BetterFloat(n)
		if k is None:
			return BetterFloat(math.perm(int(n)))
		if not isinstance(k, BetterFloat):
			k = BetterFloat(k)
		return BetterFloat(math.perm(int(n), int(k)))
	
	@staticmethod
	def frexp(x: 'BetterFloat | int | float | str') -> tuple['BetterFloat', int]:
		'''Return mantissa and exponent of x.'''
		if not isinstance(x, BetterFloat):
			x = BetterFloat(x)
		m, e = math.frexp(float(x))
		return (BetterFloat(m), e)
	
	@staticmethod
	def ldexp(x: 'BetterFloat | int | float | str', i: int) -> 'BetterFloat':
		'''Return x * (2**i).'''
		if not isinstance(x, BetterFloat):
			x = BetterFloat(x)
		return BetterFloat(math.ldexp(float(x), i))
	
	@staticmethod
	def nextafter(x: 'BetterFloat | int | float | str', y: 'BetterFloat | int | float | str') -> 'BetterFloat':
		'''Return the next floating-point value after x towards y.'''
		if not isinstance(x, BetterFloat):
			x = BetterFloat(x)
		if not isinstance(y, BetterFloat):
			y = BetterFloat(y)
		return BetterFloat(math.nextafter(float(x), float(y)))
	
	@staticmethod
	def ulp(x: 'BetterFloat | int | float | str') -> 'BetterFloat':
		'''Return the value of the least significant bit of the float x.'''
		if not isinstance(x, BetterFloat):
			x = BetterFloat(x)
		return BetterFloat(math.ulp(float(x)))
	
	# ==================== Class Properties ====================
	
	@property
	def real(self) -> 'BetterFloat':
		'''Real part (for complex compatibility).'''
		return self
	
	@property
	def imag(self) -> 'BetterFloat':
		'''Imaginary part (for complex compatibility).'''
		return BetterFloat(0)
	
	@property
	def numerator(self) -> int:
		'''Numerator of the rational representation.'''
		return self._value
	
	@property
	def denominator(self) -> int:
		'''Denominator of the rational representation.'''
		return BetterFloat._safe_power10(self._exp, "获取分母")
	
	@property
	def decimal_places(self) -> int:
		'''Number of decimal places.'''
		return self._exp


# ==================== Module-level convenience functions ====================

def bf(value: ConvertibleToBetterFloat) -> BetterFloat:
	'''Shorthand for creating BetterFloat.'''
	return BetterFloat(value)

# Type aliases for compatibility
ConvertibleToBetterFloat = Union[BetterFloat,str, bytes, bytearray, memoryview, int, float,ConvertibleToFloat,ConvertibleToInt]  # Simplified for Python 3.8

# Constants (as BetterFloat instances for consistency, though they're irrational)

#π（前50位）
BF_PI=BetterFloat('3.1415926535897932384626433832795028841971693993751')
#π（前10万位）
BF_PI_HQ = BetterFloat('3.14159265358979323846264338327950288419716939937510582097494459230781640628620899862803482534211706798214808651328230664709384460955058223172535940812848111745028410270193852110555964462294895493038196442881097566593344612847564823378678316527120190914564856692346034861045432664821339360726024914127372458700660631558817488152092096282925409171536436789259036001133053054882046652138414695194151160943305727036575959195309218611738193261179310511854807446237996274956735188575272489122793818301194912983367336244065664308602139494639522473719070217986094370277053921717629317675238467481846766940513200056812714526356082778577134275778960917363717872146844090122495343014654958537105079227968925892354201995611212902196086403441815981362977477130996051870721134999999837297804995105973173281609631859502445945534690830264252230825334468503526193118817101000313783875288658753320838142061717766914730359825349042875546873115956286388235378759375195778185778053217122680661300192787661119590921642019893809525720106548586327886593615338182796823030195203530185296899577362259941389124972177528347913151557485724245415069595082953311686172785588907509838175463746493931925506040092770167113900984882401285836160356370766010471018194295559619894676783744944825537977472684710404753464620804668425906949129331367702898915210475216205696602405803815019351125338243003558764024749647326391419927260426992279678235478163600934172164121992458631503028618297455570674983850549458858692699569092721079750930295532116534498720275596023648066549911988183479775356636980742654252786255181841757467289097777279380008164706001614524919217321721477235014144197356854816136115735255213347574184946843852332390739414333454776241686251898356948556209921922218427255025425688767179049460165346680498862723279178608578438382796797668145410095388378636095068006422512520511739298489608412848862694560424196528502221066118630674427862203919494504712371378696095636437191728746776465757396241389086583264599581339047802759009946576407895126946839835259570982582262052248940772671947826848260147699090264013639443745530506820349625245174939965143142980919065925093722169646151570985838741059788595977297549893016175392846813826868386894277415599185592524595395943104997252468084598727364469584865383673622262609912460805124388439045124413654976278079771569143599770012961608944169486855584840635342207222582848864815845602850601684273945226746767889525213852254995466672782398645659611635488623057745649803559363456817432411251507606947945109659609402522887971089314566913686722874894056010150330861792868092087476091782493858900971490967598526136554978189312978482168299894872265880485756401427047755513237964145152374623436454285844479526586782105114135473573952311342716610213596953623144295248493718711014576540359027993440374200731057853906219838744780847848968332144571386875194350643021845319104848100537061468067491927819119793995206141966342875444064374512371819217999839101591956181467514269123974894090718649423196156794520809514655022523160388193014209376213785595663893778708303906979207734672218256259966150142150306803844773454920260541466592520149744285073251866600213243408819071048633173464965145390579626856100550810665879699816357473638405257145910289706414011097120628043903975951567715770042033786993600723055876317635942187312514712053292819182618612586732157919841484882916447060957527069572209175671167229109816909152801735067127485832228718352093539657251210835791513698820914442100675103346711031412671113699086585163983150197016515116851714376576183515565088490998985998238734552833163550764791853589322618548963213293308985706420467525907091548141654985946163718027098199430992448895757128289059232332609729971208443357326548938239119325974636673058360414281388303203824903758985243744170291327656180937734440307074692112019130203303801976211011004492932151608424448596376698389522868478312355265821314495768572624334418930396864262434107732269780280731891544110104468232527162010526522721116603966655730925471105578537634668206531098965269186205647693125705863566201855810072936065987648611791045334885034611365768675324944166803962657978771855608455296541266540853061434443185867697514566140680070023787765913440171274947042056223053899456131407112700040785473326993908145466464588079727082668306343285878569830523580893306575740679545716377525420211495576158140025012622859413021647155097925923099079654737612551765675135751782966645477917450112996148903046399471329621073404375189573596145890193897131117904297828564750320319869151402870808599048010941214722131794764777262241425485454033215718530614228813758504306332175182979866223717215916077166925474873898665494945011465406284336639379003976926567214638530673609657120918076383271664162748888007869256029022847210403172118608204190004229661711963779213375751149595015660496318629472654736425230817703675159067350235072835405670403867435136222247715891504953098444893330963408780769325993978054193414473774418426312986080998886874132604721569516239658645730216315981931951673538129741677294786724229246543668009806769282382806899640048243540370141631496589794092432378969070697794223625082216889573837986230015937764716512289357860158816175578297352334460428151262720373431465319777741603199066554187639792933441952154134189948544473456738')
#e（前50位）
BF_E=BetterFloat('2.7182818284590452353602874713526624977572470936999')
#e（前2000位）
BF_E_HQ = BetterFloat('2.71828182845904523536028747135266249775724709369995957496696762772407663035354759457138217852516642742746639193200305992181741359662904357290033429526059563073813232862794349076323382988075319525101901157383418793070215408914993488416750924476146066808226480016847741185374234544243710753907774499206955170276183860626133138458300075204493382656029760673711320070932870912744374704723069697720931014169283681902551510865746377211125238978442505695369677078544996996794686445490598793163688923009879312773617821542499922957635148220826989519366803318252886939849646510582093923982948879332036250944311730123819706841614039701983767932068328237646480429531180232878250981945581530175671736133206981125099618188159304169035159888851934580727386673858942287922849989208680582574927961048419844436346324496848756023362482704197862320900216099023530436994184914631409343173814364054625315209618369088870701676839642437814059271456354906130310720851038375051011574770417189861068739696552126715468895703503540212340784981933432106817012100562788023519303322474501585390473041995777709350366041699732972508868769664035557071622684471625607988265178713419512466520103059212366771943252786753985589448969709640975459185695638023637016211204774272283648961342251644507818244235294863637214174023889344124796357437026375529444833799801612549227850925778256209262264832627793338656648162772516401910590049164499828931505660472580277863186415519565324425869829469593080191529872117255634754639644791014590409058629849679128740687050489585867174798546677575732056812884592054133405392200011378630094556068816674001698420558040336379537645203040243225661352783695117788386387443966253224985065499588623428189970773327617178392803494650143455889707194258639877275471096295374152111513683506275260232648472870392076431005958411661205452970302364725492966693811513732275364509888903136020572481765851180630364428123149655070475102544650117272115551948668508003685322818315219600373562527944951582841882947876108526398139')
#τ（2π）（前50位）
BF_TAU = 2*BF_PI
#无限大
BF_INF = BetterFloat("inf")
#负无限大
BF_NINF = BetterFloat("-inf")
#不是数字
BF_NAN = BetterFloat("nan")
