import json
import struct

# USE PYTHON VERSION 3.7+ FOR THIS CLASS TO WORK PROPERLY

class Serializable:
	"""A serializable class. To be inherited by any class that should be serialized."""
	def __init__(self):
		self.serialized_attr: dict = self.get_attr()

	def get_type_identifier(self, value) -> str:
		"""
		Returns the variable type size identifier (see get_attr() docs for more info).
		:param value: The value
		:return: The type size identifier.
		"""

		# value is iterable; iterables have their length written before them by default.
		if hasattr(value, '__iter__'):
			return f'iteN_d'

		# value is not iterable: it is a primitive type or an object
		return {
			int: 's_8',
			float: 'f_8',
			bool: 'b',
		}.get(type(value), 'o_N')

	def get_attr(self) -> dict:
		"""
		A function that should be overridden. Provides information about the attributes to serialize, and their size.
		:return: A dictionary describing the parameters to serialize and their size.

				 Dictionary values options (x is a number):
				 	- 'o': an object (which inherits Serializable): do not write its length
				 	- 'o_N': an object (which inherits Serializable): do write its length - in 2 bytes (always).
				 	- 'u_x': an unsigned integer, x is the number of bytes required for it.
				 	- 's_x': a signed integer, x is the number of bytes required for it.
				 	- 'f_x': a float number with known length (x).
				 	- 'b': bool
				 	- 'iteN_x': a string/iterable, where each of its items is of size x: length is written before the iterable attribute in 2 bytes.
				 	- 'iter_x': an iterable type (list, dict, deque, tuple, string...), each of its items is of length x: length of the iterable is not mentioned

					For example, House class should probably return:
						{'id': 4, 'address': None, 'name': 'iter_1', 'year': 3, 'has_kitchen': 1, rooms: 'iter'}
						Here, id is an integer (max size of 4 bytes); address is an object (which should
						inherit Serializable as well); name is a string which should have its length written in 1 byte
						before its beginning (for x bytes, change to iter_x); year is an integer which should probably be
						less than 2050 (0x802), and thus have a size of 3 bytes maximum; has_kitchen is a boolean which
						should have a size of 1 byte; and rooms is a list.
		"""
		# By default, serialize all of the attributes
		return {name: self.get_type_identifier(value) for name, value in self.__dict__.items() if name != 'serialized_attr'}

	def get_attr_default(self) -> dict:
		"""
		Returns the default get_attr() dict (users can use this
		function in get_attr() and override specific attributes).
		"""
		return {name: self.get_type_identifier(value) for name, value in self.__dict__.items() if name != 'serialized_attr'}

	def serialize(self, formatting='fixed') -> bytes:
		"""
		Serializes the object's attributes.
		:param formatting: The format of the serialized output. Can be either 'json' or 'fixed' (pure byte form).
		:return: The serialized version of the object.
		"""

		self.serialized_attr: dict = self.get_attr()  # update serialized_attr

		# JSON formatting (not recommended, mainly for debugging)
		if formatting == 'json':
			return json.dumps(self, default=lambda
									o: {k: v for k, v in o.__dict__.items()
										if k in self.serialized_attr.keys()}
							  ).encode()

		# fixed formatting (recommended)
		if formatting != 'fixed':
			return None

		output = b''
		for attr, type_id in self.serialized_attr.items():
			# Check that the attribute actually exists
			if not hasattr(self, attr):
				continue

			value = self.__dict__.get(attr)

			# attr (str) - the attribute name
			# type_id (int/str/None) - the attribute type size identifier (TSID), as described in get_attr()
			# value - the actual value of the attribute
			# an object (which inherits Serializable): do not write its length
			if type_id == 'o':
				if isinstance(value, Serializable):
					output += value.serialize()
				else:
					print(f'ERROR: Cannot serialize attribute {attr} of type {type(value)} since it does not inherit Serializable')

			# an object (which inherits Serializable): do write its length - in 2 bytes (always).
			elif type_id == 'o_N':
				if isinstance(value, Serializable):
					serialized_value = value.serialize()
					if len(serialized_value) > 0xffff:  # Length should be 2 bytes, so make sure it isn't more than that
						print(f'Length of serialized attribute {attr} (type {type(value)}) is too long')
						continue
					output += struct.pack('<h', len(serialized_value)) + serialized_value
				else:
					print(f'ERROR: Cannot serialize attribute {attr} of type {type(value)} since it does not inherit Serializable')

			# Not an object: a primitive type or an iterable
			else:
				serialized_primitive = self.serialize_primitive(attr, value, type_id)
				if serialized_primitive is not None:
					output += serialized_primitive

		return output

	def serialize_primitive(self, attr: str, value, type_id: str, length: int = 1) -> bytes:
		"""
		Serializes primitive types (numbers and iterables).
		:param attr: The attribute name (for debugging and error messages).
		:param value: The value to serialize. Must not be a non-iterable object.
		:param type_id: The type size identifier of the value. See get_attr() for more info.
		:param length: Used for iterables recursively. Ignore it.
		:return: The serialized value if possible; else None.
		"""

		# especially for strings (since their element is always a string too)
		if type(value) == str:
			return struct.pack(f'<{len(value)}s', value.encode())

		# an unsigned integer
		if type_id[:2] == 'u_':
			if not type_id[2:].isdigit():  # Make sure that the TSID is valid
				print(
					f'ERROR: Invalid attribute type size identifier\nAttribute: {attr}\nValue: {value}\nTSID: {type_id}')
				return
			var_len = int(type_id[2:])
			return struct.pack(f'<{length}Q', value)[:var_len]

		# a signed integer
		elif type_id[:2] == 's_':
			if not type_id[2:].isdigit():  # Make sure that the TSID is valid
				print(
					f'ERROR: Invalid attribute type size identifier\nAttribute: {attr}\nValue: {value}\nTSID: {type_id}')
				return
			var_len = int(type_id[2:])

			# Signed integers are a little more confusing to work with, so added some stuff just in case

			if length == 1:
				serialized_value = {
					1: struct.pack(f'<b', value),
					2: struct.pack(f'<h', value),
					4: struct.pack(f'<i', value),
					8: struct.pack(f'<q', value)
				}.get(var_len, None)
			else:
				serialized_value = {
					1: struct.pack(f'<{length}b', *value),
					2: struct.pack(f'<{length}h', *value),
					4: struct.pack(f'<{length}i', *value),
					8: struct.pack(f'<{length}q', *value)
				}.get(var_len, None)

			if serialized_value is None:
				print(
					'WARNING: You are trying to serialize a signed value to an arbitrary byte amount. Make sure it works as expected.')
				return struct.pack('<q', value)[:var_len]
			else:
				return serialized_value

		# a float number with known length.
		elif type_id[:2] == 'f_':
			if not type_id[2:].isdigit():  # Make sure that the TSID is valid
				print(
					f'ERROR: Invalid attribute type size identifier\nAttribute: {attr}\nValue: {value}\nTSID: {type_id}')
				return
			var_len = int(type_id[2:])

			if var_len not in (2, 4, 8):
				print(f'ERROR: Invalid attribute type size identifier (float size can only be 2/4/8)'
					  f'\nAttribute: {attr}\nValue: {value}\nTSID: {type_id}')
				return None

			if length == 1:
				return {
					2: struct.pack(f'<e', value),
					4: struct.pack(f'<f', value),
					8: struct.pack(f'<d', value)
				}.get(var_len)
			else:
				return {
					2: struct.pack(f'<{length}e', *value),
					4: struct.pack(f'<{length}f', *value),
					8: struct.pack(f'<{length}d', *value)
				}.get(var_len)

		# bool
		elif type_id == 'b':
			if length == 1:
				return struct.pack(f'<?', value)
			else:
				return struct.pack(f'<{length}?', *value)

		# a string/iterable: length is written before the iterable attribute in 2 bytes.
		elif type_id[:3] == 'ite':
			if type_id[:5] == 'iteN_' and (not type_id[5:].isdigit() and type_id[5] != 'd'):  # Make sure that the TSID is valid if iteN_x
				print(
					f'ERROR: Invalid attribute type size identifier\nAttribute: {attr}\nValue: {value}\nTSID: {type_id}')
				return

			# Check if the iterable is empty
			if not value:
				return b'0000'  # length is 0

			# if all items in the iterable are of the same primitive type
			if all(isinstance(item, (type(value[0]))) for item in value):
				var_tsid = self.get_type_identifier(value[0])
				if type_id[5] != 'd':
					if var_tsid[:5] == 'iteN_':
						var_tsid = var_tsid[:5] + type_id[5:]  # the iterable's items are iterables themselves - pass the size
					elif var_tsid[:5] == 'iter_':
						var_tsid = var_tsid[:5] + type_id[5:]  # the iterable's items are iterables themselves - pass the size
					elif var_tsid[:2] in ('u_', 'f_'):
						var_tsid = var_tsid[:2] + type_id[5:]  # the iterable's items are primitive types

				# Make sure that not all the iterable's items are objects and entered this if by accident
				if var_tsid not in ('o', 'o_N') and var_tsid[:2] != 's_':
					output: bytes = self.serialize_primitive(attr+'.', value, var_tsid, len(value))
					if type_id[:5] == 'iteN':
						if len(output) > 0xffff:  # Length should be 2 bytes, so make sure it isn't more than that
							print(f'Length of serialized attribute {attr} (type {type(value)}) is too long')
							return
						return struct.pack('<h', len(output)) + output  # add length if iteN_x
					return output  # don't add length if iter_

			output: bytes = b''
			for item in value:
				var_tsid = self.get_type_identifier(item)
				if var_tsid == 'o_N':
					output += item.serialize()
					continue
				if type_id[5] != 'd':
					if var_tsid[:5] == 'iteN_':
						var_tsid = var_tsid[:5] + type_id[5:]  # the iterable's items are iterables themselves - pass the size
					elif var_tsid[:5] == 'iter_':
						var_tsid = var_tsid[:5] + type_id[5:]  # the iterable's items are iterables themselves - pass the size
					elif var_tsid[:2] in ('u_', 's_', 'f_'):
						var_tsid = var_tsid[:2] + type_id[5:]  # the iterable's items are primitive types

				output += self.serialize_primitive(attr+'.', item, var_tsid)

			if type_id[:5] == 'iteN_':
				if len(output) > 0xffff:  # Length should be 2 bytes, so make sure it isn't more than that
					print(f'Length of serialized attribute {attr} (type {type(value)}) is too long')
					return
				return struct.pack('<h', len(output)) + output  # add length if iteN_x
			return output  # don't add length if iter_


# test class
class Entity(Serializable):
	def __init__(self):
		super().__init__()
		self.x = 5
		self.y = 3
		self.hi = 'hi'
		self.lis = [0, 1, 2, 3]
		self.inher = Item()

	def get_attr(self) -> dict:
		d: dict = self.get_attr_default()
		d['x'] = 's_1'
		d['y'] = 's_1'
		d['lis'] = 'iteN_1'
		return d


class Item(Serializable):
	def __init__(self):
		super().__init__()
		self.hello = 5
		self.s = 'string'

	def get_attr(self) -> tuple:
		d: dict = self.get_attr_default()
		d['hello'] = 's_1'
		return d


if __name__ == '__main__':
	e = Entity()
	print(e.serialize())
