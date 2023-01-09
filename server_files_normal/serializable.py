import json
import struct
from copy import deepcopy


class Serializable:
	"""A serializable class. To be inherited by any class that should be serialized."""
	def __init__(self):
		self.FORMATS_TABLE: dict = {int: "q", bool: "?", float: "d"}

	def get_attr(self) -> tuple:
		"""
		Should be overrun by classes that inherit from this class if some of their attributes
		should not be serialized.
		:return: A tuple of strings representing the object's attribute to be serialized.
		"""
		attr: dict = deepcopy(self.__dict__)
		attr.pop('FORMATS_TABLE')
		return tuple(attr.keys())

	def serialize(self, attributes: tuple = None, formatting: str = 'json', fixes: dict = {}) -> bytes:
		"""
		Serializes the attributes of an object (converts them to a byte format).
		:param fixes: A dictionary of the attributes that have known fixed size which is different from their type size
					  (for example, if an integer attribute is known to be smaller than 256 then its entry would be
					  {'num': 1}). Can also be used for dynamic serializing if the value is 'dynamic' (for example,
					  writing the length of a string before it).
		:param formatting: The format of the output. Can be either 'json' (json format, strings) or 'fixed' (binary).
		:param attributes: A tuple of strings representing the attributes to be included in the serialized output.
		:return: The serialized object.
		"""

		if attributes is None:
			attributes = self.get_attr()

		# JSON formatting
		if formatting == 'json':
			return json.dumps(self, default=lambda o: {k: v for k, v in o.__dict__.items() if k in attributes}).encode()

		# fixed formatting
		if formatting == 'fixed':
			output = b''
			attr_values: dict = self.__dict__
			for attr in attributes:
				value = attr_values.get(attr)

				# check if the value is actually in the object's attributes
				if value is None:
					continue

				# Check if the value is either primitive or iterable, and thus can be handled by serialize_primitive()
				if isinstance(value, tuple(self.FORMATS_TABLE.keys())) or hasattr(value, '__iter__'):
					print(f'calling primitive on {value}')
					output += self.serialize_primitive(value, fixes.get(attr))
					print(f'Output is now {output}')
				# Check if the value inherits from Serializable, and thus can be serialized recursively
				elif isinstance(value, Serializable):
					output += value.serialize(formatting='fixed', fixes=fixes.get(value, {}))
				# Print an error message if the value cannot be serialized
				else:
					print(f"ERROR: Cannot serialize object {value} of type {type(value)}")

			return output

	def serialize_primitive(self, value, size=None) -> bytes:
		"""
		Serializes a primitive-type variable: int, float, bool, or iterable.
		:param value: The value to serialize
		:param size: The fixed size of the value to serialize. If zero, does not slice it.
		:return:
		"""

		# Check if the value is actually primitive or iterable; return if not
		if type(value) not in self.FORMATS_TABLE.keys() and not hasattr(value, '__iter__'):
			print(f'value is {value} of type {type(value)}, returning none')
			return None

		# value is primitive
		if type(value) in self.FORMATS_TABLE.keys():
			size = size if size is not None else struct.calcsize(f'{self.FORMATS_TABLE.get(type(value))}')
			return struct.pack(f'<{self.FORMATS_TABLE.get(type(value))}', value)[:size]

		# value is iterable (string, list, tuple, deque, etc.)
		if hasattr(value, '__iter__'):
			# If all items in list are primitive type
			if all(isinstance(x, tuple(self.FORMATS_TABLE.keys())) for x in value) and type(value[0]) in self.FORMATS_TABLE.keys():
				# If there is no need to slice the elements
				if size == 0:
					return struct.pack(f'<{len(value)}{self.FORMATS_TABLE.get(type(value[0]))}', *value)
				else:
					output: bytes = b''
					for element in value:
						size = size if size is not None else struct.calcsize(f'{self.FORMATS_TABLE.get(type(element))}')
						output += struct.pack(f'{self.FORMATS_TABLE.get(type(element))}', element)[:size]
					return output

			# if values in iterable are not all primitive
			else:
				output: bytes = b''
				for element in value:
					if isinstance(element, tuple(self.FORMATS_TABLE.keys())) or hasattr(value, '__iter__'):
						print(f'trying to serialize {element} which is part of value {value}')
						output += self.serialize_primitive(element, size)
					elif isinstance(element, Serializable):
						output += element.serialize(formatting='fixed')
					else:
						print(f"ERROR: Cannot serialize object {element} of type {type(element)}")
				return output


# test class
class Entity(Serializable):
	def __init__(self):
		super().__init__()
		self.x = 5
		self.y = 3
		self.hi = [1, 2, 3]
		self.inher = Item(8)


class Item(Serializable):
	def __init__(self, val):
		super().__init__()
		self.hello = val

	def get_attr(self) -> tuple:
		return 'hello',


if __name__ == '__main__':
	e = Entity()
	print(e.serialize(('x', 'y', 'hi', 'inher'), formatting='fixed', fixes={'x': 1, 'y': 1, 'hi': 1}))
