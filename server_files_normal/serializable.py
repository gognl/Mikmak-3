import json
import struct
from collections import deque

class Serializable:
	"""An entity class"""

	def serialize(self, attributes: tuple, formatting: str = 'json', fixes: dict = {}) -> bytes:
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

		# JSON formatting
		if formatting == 'json':
			return json.dumps(self, default=lambda o: {k: v for k, v in o.__dict__.items() if k in attributes}).encode()

		# fixed formatting
		if formatting == 'fixed':
			output = b''
			attr_values: dict = self.__dict__
			for attr in attributes:
				value = attr_values.get(attr)

				output += self.serialize_primitive(value, fixes.get(attr, 0))

			return output

	def serialize_primitive(self, value, size=0) -> bytes:
		"""
		Serializes a primitive-type variable: int, float, bool, or iterable.
		:param value:
		:param size:
		:return:
		"""

		FORMATS_TABLE: dict = {int: "q", bool: "?", float: "d"}

		# Check if the value is actually primitive or iterable; return if not
		if type(value) not in FORMATS_TABLE.keys() and not hasattr(value, '__iter__'):
			return None

		# value is primitive
		if type(value) in FORMATS_TABLE.keys():
			return struct.pack(f'<{FORMATS_TABLE.get(type(value))}', value)[:size]

		# value is iterable (string, list, tuple, deque, etc.)
		if hasattr(value, '__iter__'):
			# If all items in list are primitive type
			if all(isinstance(x, tuple(FORMATS_TABLE.keys())) for x in value) and type(value[0]) in FORMATS_TABLE.keys():
				return struct.pack(f'<{len(value)}{FORMATS_TABLE.get(type(value[0]))}', *value)

# test class
class Entity(Serializable):
	def __init__(self):
		super().__init__()
		self.x = 5
		self.y = 3
		self.hi = [1, 2, 3]


if __name__ == '__main__':
	e = Entity()
	print(e.serialize(('x', 'y', 'hi'), formatting='fixed', fixes={'x': 1, 'y': 1}))
