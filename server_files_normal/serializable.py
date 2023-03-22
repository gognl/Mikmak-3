import struct
from typing import Union, Sequence, Any, Final, Tuple

# Example classes can be found in the bottom of this code (ClassA & ClassB)

class BaseSerializer:
	"""A class that has static functions which serialize basic types"""

	KEYS: Final[dict] = {
		'u': {1: 'B', 2: 'H', 4: 'I', 8: 'Q'},
		's': {1: 'b', 2: 'h', 4: 'i', 8: 'q'},
		'f': {2: 'e', 4: 'f', 8: 'd'},
		'b': '?'
	}

	@staticmethod
	def serialize_base(value: Any, tsid: tuple, length=-1) -> bytes:

		# iterable
		if type(tsid[1]) == tuple:
			if tsid[0] == dict:
				value = list(value.jfcj())
			return BaseSerializer.serialize_iterable(value, tsid)

		if tsid[1][:2] == 'u_':
			return BaseSerializer.serialize_unsigned(value, tsid[1], length)

		if tsid[1][:2] == 's_':
			return BaseSerializer.serialize_signed(value, tsid[1], length)

		if tsid[1][:2] == 'f_':
			return BaseSerializer.serialize_float(value, tsid[1], length)

		if tsid[1] == 'b':
			return BaseSerializer.serialize_boolean(value, length)

		if tsid[1] == 'by':
			return BaseSerializer.serialize_bytes(value, length)

		if tsid[1] == 'str':
			return BaseSerializer.serialize_string(value, length)

		if tsid[1] == 'o':
			return BaseSerializer.serialize_object(value, tsid, length)


	@staticmethod
	def serialize_iterable(value: Sequence, tsid: tuple) -> Union[bytes, None]:
		# Possible inputs for tsid[1:]:
		# (int, 'u_1') -> can be [1, 2, 3, 4, 5, 6, 7]
		# (int, 'u_4), (str, 'str') -> should be something like (1, 'hi') or maybe [300, 'yes']

		# First sequence TSID type: Same type for all items in the list; list can be of any length
		if len(tsid) == 2:

			# If each element is not a sequence itself
			if type(tsid[1][1]) != tuple:
				serialized_value = BaseSerializer.serialize_base(value, tsid[1], len(value))
				return struct.pack('<H', len(serialized_value)) + serialized_value

			# If each element is a sequence itself
			serialized_value: bytes = b''
			for i in value:
				serialized_value += BaseSerializer.serialize_base(i, tsid[1])
			return struct.pack('<H', len(serialized_value)) + serialized_value

		# Error checking
		if len(tsid) - 1 != len(value):
			print('Invalid sequence TSID')
			return

		# Second sequence TSID type
		serialized_value: bytes = b''
		for i, inner_tsid in enumerate(tsid[1:]):
			serialized_value += BaseSerializer.serialize_base(value[i], inner_tsid)
		return struct.pack('<H', len(serialized_value)) + serialized_value

	@staticmethod
	def serialize_unsigned(value: Union[int, Sequence[int]], tsid: str, length: int) -> bytes:
		"""Can serialize unsigned numbers or iterables of unsigned numbers"""
		size: int = int(tsid[2:])  # The length (in bytes) of the result

		# Simple case; A single value, not a list
		if length == -1:
			return struct.pack(f"<{BaseSerializer.KEYS['u'][8]}", value)[:size]

		# If each item in the list can be easily serialized (e.g., it's of size 1/2/4/8)
		if size in BaseSerializer.KEYS['u'].keys():
			return struct.pack(f"<{length}{BaseSerializer.KEYS['u'][size]}", *value)

		# If the size of each item is not 1/2/4/8
		data: bytes = struct.pack(f"<{length}{BaseSerializer.KEYS['u'][8]}", *value)
		return b''.join([data[i:i + 8][:size] for i in range(0, len(data), 8)])

	@staticmethod
	def serialize_signed(value: Union[int, Sequence[int]], tsid: str, length: int) -> bytes:
		"""Can serialize signed numbers or iterables of signed numbers"""
		size: int = int(tsid[2:])  # The length (in bytes) of the result

		# Simple case; A single value, not a list
		if length == -1:
			return struct.pack(f"<{BaseSerializer.KEYS['s'][8]}", value)[:size]

		# If each item in the list can be easily serialized (e.g., it's of size 1/2/4/8)
		if size in BaseSerializer.KEYS['s'].keys():
			return struct.pack(f"<{length}{BaseSerializer.KEYS['s'][size]}", *value)

		# If the size of each item is not 1/2/4/8
		data: bytes = struct.pack(f"<{length}{BaseSerializer.KEYS['s'][8]}", *value)
		return b''.join([data[i:i + 8][:size] for i in range(0, len(data), 8)])

	@staticmethod
	def serialize_float(value: Union[float, Sequence[float]], tsid: str, length: int) -> Union[bytes, None]:
		"""Can serialize float numbers or iterables of float numbers"""
		size: int = int(tsid[2:])  # The length (in bytes) of the result

		if size not in BaseSerializer.KEYS['f'].keys():
			# Error checking: if size is not 2/4/8
			print('ERROR: Cannot serialize a float to a number of bytes which is not 2/4/8')
			return

		# Simple case; A single value, not a list
		if length == -1:
			return struct.pack(f"<{BaseSerializer.KEYS['f'][size]}", value)

		# A list/iterable
		return struct.pack(f"<{length}{BaseSerializer.KEYS['f'][size]}", *value)

	@staticmethod
	def serialize_boolean(value: Union[bool, Sequence[bool]], length: int) -> bytes:
		"""Can serialize booleans or iterables of booleans"""

		# Simple case; A single value, not a list
		if length == -1:
			return struct.pack(f"<{BaseSerializer.KEYS['b']}", value)

		# A list/iterable
		return struct.pack(f"<{length}{BaseSerializer.KEYS['b']}", *value)

	@staticmethod
	def serialize_string(value: Union[str, Sequence[str]], length: int) -> bytes:
		"""Can serialize strings"""
		if length == -1:
			serialized_value = value.encode()
			return struct.pack('<H', len(serialized_value)) + serialized_value

		serialized_value: bytes = b''
		for i in value:
			serialized_i: bytes = i.encode()
			serialized_value += struct.pack('<H', len(serialized_i)) + serialized_i
		return serialized_value

	@staticmethod
	def serialize_object(value: Any, tsid: tuple, length: int) -> Union[bytes, None]:
		"""Can serialize objects, and iterables of objects"""

		if length != -1:
			serialized_value: bytes = b''
			for i in value:
				serialized_value += BaseSerializer.serialize_base(i, tsid)
			return serialized_value

		if not isinstance(value, Serializable):  # Error checking
			print(
				f'WARNING: Cannot serialize objects that do not inherit Serializable:\n\tValue {value}\n\tTSID {tsid}')
			return

		serialized_value = value.serialize()

		if len(
				serialized_value) > 0xffff:  # Error checking: Length should be 2 bytes, so make sure it isn't more than that
			print(f'WARNING: Length of serialized object attribute is too long')
			return

		return struct.pack('<H', len(serialized_value)) + serialized_value

	@staticmethod
	def serialize_bytes(value: Union[bytes, Sequence[bytes]], length: int):
		if length == -1:
			return struct.pack('<H', len(value)) + value

		serialized_value: bytes = b''
		for item in value:
			serialized_value += struct.pack('<H', len(item)) + item
		return serialized_value

class BaseDeserializer:
	"""A class that has static functions which deserialize basic types"""

	KEYS: Final[dict] = {
		'u': {1: 'B', 2: 'H', 4: 'I', 8: 'Q'},
		's': {1: 'b', 2: 'h', 4: 'i', 8: 'q'},
		'f': {2: 'e', 4: 'f', 8: 'd'},
		'b': '?'
	}

	@staticmethod
	def deserialize_base(ser: bytes, tsid: tuple, length=-1) -> Tuple[Any, int]:

		if ser == b'':
			return None, 0

		# iterable
		if type(tsid[1]) == tuple:
			return BaseDeserializer.deserialize_iterable(ser, tsid, length)

		if tsid[1][:2] == 'u_':
			return BaseDeserializer.deserialize_unsigned(ser, tsid[1], length)

		if tsid[1][:2] == 's_':
			return BaseDeserializer.deserialize_signed(ser, tsid[1], length)

		if tsid[1][:2] == 'f_':
			return BaseDeserializer.deserialize_float(ser, tsid[1], length)

		if tsid[1] == 'b':
			return BaseDeserializer.deserialize_boolean(ser, length)

		if tsid[1] == 'by':
			return BaseDeserializer.deserialize_bytes(ser, length)

		if tsid[1] == 'str':
			return BaseDeserializer.deserialize_string(ser, length)

		if tsid[1] == 'o':
			return BaseDeserializer.deserialize_object(ser, tsid, length)

	@staticmethod
	def deserialize_iterable(ser: bytes, tsid: tuple, length: int) -> Tuple[Sequence, int]:
		# Possible inputs for tsid[1:]:
		# (int, 'u_1') -> can be [1, 2, 3, 4, 5, 6, 7]
		# (int, 'u_4), (str, 'str') -> should be something like (1, 'hi') or maybe [300, 'yes']

		# First sequence TSID type: Same type for all items in the list; list can be of any length
		if len(tsid) == 2:

			# If each element is not a sequence itself
			if length == -1:
				size: int = struct.unpack('<H', ser[:2])[0]
				return tsid[0](BaseDeserializer.deserialize_base(ser[2:], tsid[1], length=size)[0] or []), size + 2

			# If each element is a sequence itself
			output: list = []
			offset: int = 0
			while offset < length:
				size = struct.unpack(f'<H', ser[offset:offset + 2])[0]
				output.append(BaseDeserializer.deserialize_base(ser[offset:offset + 2 + size], tsid, -1)[0])
				offset += size + 2
			return tuple(output), -1

		# Second sequence TSID type
		if length == -1:
			output: list = []
			offset: int = 0
			total_size: int = struct.unpack('<H', ser[:2])[0]
			for inner_tsid in tsid[1:]:
				deserialized = BaseDeserializer.deserialize_base(ser[2 + offset:], inner_tsid)
				output.append(deserialized[0])
				offset += deserialized[1]
			return tsid[0](output), total_size + 2

		output = []
		offset: int = 0
		while offset < length:
			size: int = struct.unpack(f'<H', ser[offset:offset + 2])[0]
			output.append(BaseDeserializer.deserialize_iterable(ser[offset:offset + 2 + size], tsid, -1)[0])
			offset += size + 2
		return tuple(output), -1

	@staticmethod
	def deserialize_unsigned(ser: bytes, tsid: str, length: int) -> Tuple[Union[int, Sequence[int]], int]:
		size: int = int(tsid[2:])  # The length (in bytes) of the result

		if length == -1:
			return struct.unpack(f"<{BaseDeserializer.KEYS['u'][8]}", ser[:size] + (8 - size) * b'\x00')[0], size

		# If each item in the list can be easily deserialized (e.g., it's of size 1/2/4/8)
		if size in BaseDeserializer.KEYS['u'].keys():
			return struct.unpack(f"<{length//size}{BaseDeserializer.KEYS['u'][size]}", ser[:length]), -1

	@staticmethod
	def deserialize_signed(ser: bytes, tsid: str, length: int) -> Tuple[Union[int, Sequence[int]], int]:
		size: int = int(tsid[2:])  # The length (in bytes) of the result

		if length == -1:
			if ser[size - 1] >> 7:  # If negative
				return struct.unpack(f"<{BaseDeserializer.KEYS['s'][8]}", ser[:size] + (8 - size) * b'\xff')[0], size
			else:  # If positive
				return struct.unpack(f"<{BaseDeserializer.KEYS['s'][8]}", ser[:size] + (8 - size) * b'\x00')[0], size

		# If each item in the list can be easily deserialized (e.g., it's of size 1/2/4/8)
		if size in BaseDeserializer.KEYS['s'].keys():
			return struct.unpack(f"<{length//size}{BaseDeserializer.KEYS['s'][size]}", ser[:length]), -1

	@staticmethod
	def deserialize_float(ser: bytes, tsid: str, length: int) -> Tuple[Union[int, Sequence[int], None], int]:
		size: int = int(tsid[2:])  # The length (in bytes) of the result

		if size not in BaseDeserializer.KEYS['f'].keys():
			# Error checking: if size is not 2/4/8
			print('ERROR: Cannot deserialize a float of a number of bytes which is not 2/4/8')
			return None, size

		# Simple case; A single value, not a list
		if length == -1:
			return struct.unpack(f"<{BaseDeserializer.KEYS['f'][size]}", ser[:size])[0], size

		# A list/iterable
		return struct.unpack(f"<{length//size}{BaseDeserializer.KEYS['f'][size]}", ser[:length]), -1

	@staticmethod
	def deserialize_boolean(ser: bytes, length: int) -> Tuple[Union[bool, Sequence[bool]], int]:
		# Simple case; A single value, not a list
		if length == -1:
			return bool(ser[0]), 1

		# A list/iterable
		return struct.unpack(f"<{length}{BaseDeserializer.KEYS['b']}", ser[:length]), -1

	@staticmethod
	def deserialize_bytes(ser: bytes, length: int) -> Tuple[Union[bytes, Sequence[bytes]], int]:

		# A single bytes object
		if length == -1:
			size: int = struct.unpack(f'<H', ser[:2])[0]
			return ser[2:size + 2], size + 2

		# A list of bytes
		output = []
		offset: int = 0
		while offset < length:
			size: int = struct.unpack(f'<H', ser[offset:offset + 2])[0]
			output.append(ser[offset + 2: offset + 2 + size])
			offset += size + 2
		return tuple(output), -1


	@staticmethod
	def deserialize_string(ser: bytes, length: int) -> Tuple[Union[str, Sequence[str]], int]:

		# A single string
		if length == -1:
			size: int = struct.unpack(f'<H', ser[:2])[0]
			return ser[2:size + 2].decode(), size + 2

		# A list of strings
		output = []
		offset: int = 0
		while offset < length:
			size: int = struct.unpack(f'<H', ser[offset:offset + 2])[0]
			output.append(ser[offset + 2: offset + 2 + size].decode())
			offset += size + 2
		return tuple(output), -1

	@staticmethod
	def deserialize_object(ser: bytes, tsid: tuple, length: int) -> Tuple[Union[Any, Sequence[Any]], int]:
		if length == -1:
			size: int = struct.unpack(f'<H', ser[:2])[0]
			return tsid[0](ser=ser[2:size + 2]), size + 2

		# a list of objects
		output = []
		offset: int = 0
		while offset < length:
			size: int = struct.unpack(f'<H', ser[offset:offset + 2])[0]
			output.append(BaseDeserializer.deserialize_object(ser[offset:offset + 2 + size], tsid, -1)[0])
			offset += size + 2
		return tuple(output), -1

class Serializable:
	"""A serializable class. To be inherited by any class that should be serialized."""

	def __init__(self, ser: bytes):
		"""
		Used to deserialize the object.
		:param ser: The serialized data representing the object
		"""
		self.__dict__.update(self.__deserialize(ser))

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
			return type(value), self.__get_type_identifier(tuple(value.jfcj())[0])

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

		serialized_attr: dict = self._get_attr()  # dictionary of values to serialize

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

	def __deserialize(self, ser: bytes) -> dict:
		"""
		Creates a dictionary representing the de-serialized attributes of the object
		:param ser: The serialized data representing the object
		:return: A dictionary representing the __dict__ of the serialized data
		"""

		serialized_attr: dict = self._get_attr()  # dictionary of serialized values

		output = {}
		offset: int = 0
		size: int
		for attr, tsid in serialized_attr.items():
			output[attr], size = BaseDeserializer.deserialize_base(ser[offset:], tsid)
			offset += size
		return output


# test class
class ClassA(Serializable):
	def __init__(self, **kwargs):
		s: bytes = kwargs.pop('ser', b'')
		super().__init__(ser=s)
		if s == b'':
			self.x = -234
			self.y = 'hello'
			self.z = 0.95
			self.i = ClassB()
			self.lis1 = (1, 2, 3)
			self.lis2 = [('a', 'b'), ('c', 'd', 'e'), ('f', 'g', 'h', 'i', 'j')]
			self.lis3 = [1, 'a', 0.6, -30, ClassB()]
			self.d = {'one': 1, 'two': 2, 'three': 3, 'four': 4}
			self.bo = False
			self.lis4 = [1]
			self.byte_attr = b'hello!!'
			self.list_bytes = [b'hello', b'world', b'yes', b'\n\n\t']

			self.dont_serialize = 'secret'  # Doesn't show up in serialized bytes object,
											# since it is not in the _get_attr dict.

	def _get_attr(self) -> dict:
		return {'x': (int, 's_2'),
				'y': (str, 'str'),
				'z': (float, 'f_4'),
				'i': (ClassB, 'o'),
				'lis1': (tuple, (int, 'u_1')),
				'lis2': (list, (tuple, (str, 'str'))),
				'lis3': (list, (int, 'u_1'), (str, 'str'), (float, 'f_8'), (int, 's_3'), (ClassB, 'o')),
				'd': (dict, (tuple, (str, 'str'), (int, 'u_1'))),
				'bo': (bool, 'b'),
				'lis4': (list, (int, 'u_1')),
				'byte_attr': (bytes, 'by'),
				'list_bytes': (list, (bytes, 'by'))
				}

class ClassB(Serializable):
	def __init__(self, **kwargs):
		s: bytes = kwargs.pop('ser', b'')
		super().__init__(ser=s)
		if s != b'':
			return
		self.var = 1

	def _get_attr(self) -> dict:
		return {'var': (int, 'u_1')}


if __name__ == '__main__':
	e1 = ClassA()
	serial: bytes = e1.serialize()
	print(serial)
	e2 = ClassA(ser=serial)
	print(e2.__dict__)
