import struct
from typing import Union, Sequence


# USE PYTHON VERSION 3.7+ FOR THIS CLASS TO WORK PROPERLY

class BaseSerializer:
	"""A class that has static functions which serialize basic types"""

	KEYS: dict = {
			'u': {1: 'B', 2: 'H', 4: 'I', 8: 'Q'},
			's': {1: 'b', 2: 'h', 4: 'i', 8: 'q'},
			'f': {2: 'e', 4: 'f', 8: 'd'},
			'b': '?'
			}

	@staticmethod
	def serialize_base(value, tsid: tuple, length=1) -> bytes:

		# iterable
		if type(tsid[1]) == tuple:
			if tsid[0] == dict:
				value = list(value.items())
			return BaseSerializer.serialize_iterable(value, tsid)

		if tsid[1][:2] == 'u_':
			return BaseSerializer.serialize_unsigned(value, tsid[1], length)

		if tsid[1][:2] == 's_':
			return BaseSerializer.serialize_signed(value, tsid[1], length)

		if tsid[1][:2] == 'f_':
			return BaseSerializer.serialize_float(value, tsid[1], length)

		if tsid[1][:2] == 'b_':
			return BaseSerializer.serialize_boolean(value, length)

		if tsid[1] == 'str':
			return BaseSerializer.serialize_string(value)

		if tsid[1] == 'o':
			return BaseSerializer.serialize_object(value, tsid, length)

	@staticmethod
	def serialize_iterable(value: Sequence, tsid: tuple) -> Union[bytes, None]:
		# Possible inputs for tsid:
		# (int, 'u_1') -> can be [1, 2, 3, 4, 5, 6, 7]
		# (int, 'u_4), (str, 'str') -> should be something like (1, 'hi') or maybe [300, 'yes']

		# First sequence TSID type: Same type for all items in the list; list can be of any length
		if len(tsid) == 2:

			# If each element is not a sequence itself
			if type(tsid[1][1]) != tuple:
				serialized_value = BaseSerializer.serialize_base(value, tsid[1], len(value))
				return struct.pack('<h', len(serialized_value)) + serialized_value

			# If each element is a sequence itself
			serialized_value: bytes = b''
			if tsid[0] == dict:  # For dictionaries length of each element is known already, no need to waste 2 bytes
				for i in value:
					serialized_value += BaseSerializer.serialize_base(i, tsid[1])[2:]
			else:
				for i in value:
					serialized_value += BaseSerializer.serialize_base(i, tsid[1])
			return struct.pack('<h', len(serialized_value)) + serialized_value

		# Error checking
		if len(tsid) - 1 != len(value):
			print('Invalid sequence TSID')
			return

		# Second sequence TSID type
		serialized_value: bytes = b''
		for i, inner_tsid in enumerate(tsid[1:]):
			serialized_value += BaseSerializer.serialize_base(value[i], inner_tsid)
		return struct.pack('<h', len(serialized_value)) + serialized_value

	@staticmethod
	def serialize_unsigned(value: Union[int, Sequence[int]], tsid: str, length) -> bytes:
		"""Can serialize unsigned numbers or iterables of unsigned numbers"""
		size: int = int(tsid[2:])  # The length (in bytes) of the result

		# Simple case; A single value, not a list
		if length == 1:
			return struct.pack(f"<{BaseSerializer.KEYS['u'][8]}", value)[:size]

		# If each item in the list can be easily serialized (e.g., it's of size 1/2/4/8)
		if size in BaseSerializer.KEYS['u'].keys():
			return struct.pack(f"<{length}{BaseSerializer.KEYS['u'][size]}", *value)

		# If the size of each item is not 1/2/4/8
		data: bytes = struct.pack(f"<{length}{BaseSerializer.KEYS['u'][8]}", *value)
		return b''.join([data[i:i + 8][:size] for i in range(0, len(data), 8)])

	@staticmethod
	def serialize_signed(value: Union[int, Sequence[int]], tsid: str, length) -> bytes:
		"""Can serialize signed numbers or iterables of signed numbers"""
		size: int = int(tsid[2:])  # The length (in bytes) of the result

		# Simple case; A single value, not a list
		if length == 1:
			return struct.pack(f"<{BaseSerializer.KEYS['s'][8]}", value)[:size]

		# If each item in the list can be easily serialized (e.g., it's of size 1/2/4/8)
		if size in BaseSerializer.KEYS['s'].keys():
			return struct.pack(f"<{length}{BaseSerializer.KEYS['s'][size]}", *value)

		# If the size of each item is not 1/2/4/8
		data: bytes = struct.pack(f"<{length}{BaseSerializer.KEYS['s'][8]}", *value)
		return b''.join([data[i:i + 8][:size] for i in range(0, len(data), 8)])

	@staticmethod
	def serialize_float(value: Union[float, Sequence[float]], tsid: str, length) -> Union[bytes, None]:
		"""Can serialize float numbers or iterables of float numbers"""
		size: int = int(tsid[2:])  # The length (in bytes) of the result

		if size not in BaseSerializer.KEYS['f'].keys():
			# Error checking: if size is not 2/4/8
			print('ERROR: Cannot serialize a float to a number of bytes which is not 2/4/8')
			return

		# Simple case; A single value, not a list
		if length == 1:
			return struct.pack(f"<{BaseSerializer.KEYS['f'][size]}", value)

		# A list/iterable
		return struct.pack(f"<{length}{BaseSerializer.KEYS['f'][size]}", *value)

	@staticmethod
	def serialize_boolean(value: Union[bool, Sequence[bool]], length) -> bytes:
		"""Can serialize booleans or iterables of booleans"""

		# Simple case; A single value, not a list
		if length == 1:
			return struct.pack(f"<{BaseSerializer.KEYS['b']}", value)

		# A list/iterable
		return struct.pack(f"<{length}{BaseSerializer.KEYS['b']}", *value)

	@staticmethod
	def serialize_string(value: str) -> bytes:
		"""Can serialize strings"""
		serialized_value = value.encode()
		return struct.pack('<h', len(serialized_value)) + serialized_value

	@staticmethod
	def serialize_object(value, tsid, length) -> Union[bytes, None]:
		"""Can serialize objects"""

		if length != 1:
			serialized_value: bytes = b''
			for i in value:
				serialized_value += BaseSerializer.serialize_base(i, tsid)
			return serialized_value

		if not isinstance(value, Serializable):  # Error checking
			print(f'WARNING: Cannot serialize objects that do not inherit Serializable:\n\tValue {value}\n\tTSID {tsid}')
			return

		serialized_value = value.serialize()

		if len(serialized_value) > 0xffff:  # Error checking: Length should be 2 bytes, so make sure it isn't more than that
			print(f'WARNING: Length of serialized object attribute is too long')
			return

		return struct.pack('<h', len(serialized_value)) + serialized_value

class BaseDeserializer:
	"""A class that has static functions which deserialize basic types"""
	pass

class Serializable:
	"""A serializable class. To be inherited by any class that should be serialized."""

	def __init__(self):
		"""If ser is not None,
		creates an object of the subclass based on the serialized input, and the attributes from get_attr()"""

	def __get_type_identifier(self, value) -> tuple:
		"""
		Returns the tuple containing the variable type size identifier (see get_attr() docs for more info).
		:param value: The value
		:return: The type size identifier tuple.
		"""

		# if str
		if type(value) == str:
			return str, 'str'

		if type(value) == dict:
			return type(value), self.__get_type_identifier(tuple(value.items())[0])

		# value is iterable; iterables have their length written before them by default.
		if hasattr(value, '__iter__'):
			if not value:
				return type(value), 'b'  # An empty iterable

			if all(isinstance(x, type(value[0])) for x in value):
				return type(value), self.__get_type_identifier(value[0])

			output = [type(value)]
			for i in value:
				output.append(self.__get_type_identifier(i))
			return tuple(output)

		# value is not iterable: it is a primitive type or an object
		return {
			int: (int, 's_8'),
			float: (float, 'f_8'),
			bool: (bool, 'b'),
		}.get(type(value), (type(value), 'o'))

	def _get_attr(self) -> dict:
		"""
		A function that should be overridden. Provides information about the attributes to serialize, and their size.
		:return: A dictionary describing the parameters to serialize and their size.

				You should use TSIDs (Type Size Identifiers) in this dictionary.
				The possible TSIDs are as follows (x is a number).

				'u_x' - unsigned integer (x bytes).
				's_x' - signed integer (x bytes).
				'f_x' - float (x bytes, can only be 2/4/8).
				'b' - boolean
				'str' - string
				'o' - object

				For example:
					{'name': (str, 'str'),
					'balance': (float, 'f_4'),
					'date': (Date, 'o'),
					'enemies': (list, (Enemy, 'o')),
					'position': (tuple, (int, 'u_8')),
					'is_idle': (bool, 'b'),
					'example_dict': (dict, (tuple, (str, 'str'), (float, 'f_8')))}

					# A dictionary is made up of key-value tuples: [(k1, v1), (k2, v2)]

		"""
		# By default, serialize all of the attributes
		return {name: self.__get_type_identifier(value) for name, value in self.__dict__.items()}

	def _get_attr_default(self) -> dict:
		"""
		Returns the default get_attr() dict (users can use this
		function in get_attr() and override specific attributes).
		"""
		return {name: self.__get_type_identifier(value) for name, value in self.__dict__.items()}

	def serialize(self) -> bytes:
		"""
		Serializes the object's attributes.
		:return: The serialized version of the object.
		"""

		serialized_attr: dict = self._get_attr()  # update serialized_attr

		output = b''
		for attr, tsid in serialized_attr.items():

			# Check that the attribute actually exists
			if not hasattr(self, attr):
				continue

			value = self.__dict__.get(attr)

			serialized_primitive = BaseSerializer.serialize_base(value, tsid)
			if serialized_primitive is None:
				print(f'Could not serialize attribute {attr}.\tTSID: {tsid}\n\tValue: {value}')
				continue

			output += serialized_primitive

		return output

# test class
class Entity(Serializable):
	def __init__(self):
		super().__init__()
		self.x = 255
		self.lis = [Item(), Item(), Item()]
		self.pair = (1, 'hi')

	def _get_attr(self) -> dict:
		return {'lis': (list, (Item, 'o'))}

class Item(Serializable):
	def __init__(self):
		super().__init__()
		self.hello = 4
		self.s = 'string'

	def _get_attr(self) -> dict:
		return {'hello': (int, 'u_1')}


if __name__ == '__main__':
	e = Entity()
	print(e.serialize())
