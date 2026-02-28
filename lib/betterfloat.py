from __future__ import annotations
from collections.abc import *
import math
from typing import *

# Type aliases for compatibility
ConvertibleToBetterFloat = Union[str, bytes, bytearray, memoryview, int, float]  # Simplified for Python 3.8

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
			self._value = int(value)
			self._exp = max(0, int(exp))
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
					self._value = sign * (int(str(int_part)) * (10 ** len(frac_part)) + int(frac_part))
					self._exp = len(frac_part)
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
			scale = 10 ** (self._exp - other._exp)
			new_value = self._value + other._value * scale
			new_exp = self._exp
		elif self._exp < other._exp:
			# other has more decimal places
			scale = 10 ** (other._exp - self._exp)
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
			scale = 10 ** (self._exp - other._exp)
			new_value = self._value - other._value * scale
			new_exp = self._exp
		elif self._exp < other._exp:
			scale = 10 ** (other._exp - self._exp)
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
		scale = 10 ** (precision + other._exp - self._exp)
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
			scale = 10 ** (self._exp - other._exp)
			sv = self._value
			ov = other._value * scale
		elif self._exp < other._exp:
			scale = 10 ** (other._exp - self._exp)
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
		cls._precision = max(1, precision)
	
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
		scale = 10 ** x._exp
		return BetterFloat(x._value // scale)
	
	@staticmethod
	def ceil(x: 'BetterFloat | int | float | str') -> 'BetterFloat':
		'''Ceiling - smallest integer >= x.'''
		if not isinstance(x, BetterFloat):
			x = BetterFloat(x)
		if x._exp == 0:
			return BetterFloat(x._value)
		scale = 10 ** x._exp
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
		scale = 10 ** x._exp
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
			return BetterFloat(math.gcd(int(a * (10 ** max(a._exp, b._exp))), int(b * (10 ** max(a._exp, b._exp)))))
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
				return BetterFloat(math.lcm(int(a * (10 ** max(a._exp, b._exp))), int(b * (10 ** max(a._exp, b._exp)))))
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
		return 10 ** self._exp
	
	@property
	def decimal_places(self) -> int:
		'''Number of decimal places.'''
		return self._exp


# ==================== Module-level convenience functions ====================

def bf(value: ConvertibleToBetterFloat) -> BetterFloat:
	'''Shorthand for creating BetterFloat.'''
	return BetterFloat(value)

# Constants (as BetterFloat instances for consistency, though they're irrational)
BF_PI = BetterFloat(math.pi)
BF_E = BetterFloat(math.e)
BF_TAU = BetterFloat(math.tau if hasattr(math, 'tau') else 2 * math.pi)
BF_INF = BetterFloat("inf")
BF_NINF = BetterFloat("-inf")
BF_NAN = BetterFloat("nan")
