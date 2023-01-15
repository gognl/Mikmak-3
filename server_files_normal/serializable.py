import json
import struct
from typing import Union, Iterable

# USE PYTHON VERSION 3.7+ FOR THIS CLASS TO WORK PROPERLY

class Serializable:
	"""A serializable class. To be inherited by any class that should be serialized."""

	def __init__(self, ser: bytes = None):
		"""If ser is not None,
		creates an object of the subclass based on the serialized input, and the attributes from get_attr()"""
		# On the sender side
		if ser is None:
			self.serialized_attr: dict = self._get_attr()
			return
		# On the receiver side
		self.__deserialize(ser)

	def __deserialize(self, ser: bytes) -> None:
		"""Deserializes the input ser and builds an object of the subclass based on it and on get_attr()"""
		attributes: dict = self.__dict__
		req_attr: dict = self._get_attr()
		for attr, tsid in req_attr.items():

			# attr: str - the name of the attribute
			# tsid: str - the type size id, as described in get_attr()

			if tsid == 'o':
				# TODO: an object. do an object id thing
				pass

			# an object (which inherits Serializable): do write its length - in 2 bytes (always).
			elif tsid == 'o_N':
				# TODO: an object. do an object id thing
				pass

			# Not an object: a primitive type or an iterable
			else:
				value, size = self.__deserialize_primitive(ser, attr, tsid)
				self.__setattr__(attr, value)
				ser = ser[size:]

	def __deserialize_primitive(self, ser: bytes, attr: str, tsid: str):

		# unsigned integers
		if tsid[:2] == 'u_':
			value, size = self.__deserialize_unsigned(ser, tsid)
			return value[0], size

		if tsid[:2] == 's_':
			value, size = self.__deserialize_signed(ser, tsid)
			return value[0], size

		if tsid[:2] == 'f_':
			value, size = self.__deserialize_float(ser, tsid)
			return value[0], size

	@staticmethod
	def __deserialize_unsigned(ser: bytes, tsid: str):
		size: int = int(tsid[2:])
		if size == 1:
			return struct.unpack(f'<B', ser[:1]), size
		if size <= 2:
			return struct.unpack(f'<H', ser[:2]), size
		if size <= 4:
			return struct.unpack(f'<I', ser[:4]+(4-size)*b'\x00'), size
		if size <= 8:
			return struct.unpack(f'<Q', ser[:8]+(8-size)*b'\x00'), size
		return None

	@staticmethod
	def __deserialize_signed(ser: bytes, tsid: str):
		size: int = int(tsid[2:])
		if size == 1:
			return struct.unpack(f'<b', ser[:1]), size
		if size <= 2:
			return struct.unpack(f'<h', ser[:2]), size
		if size <= 4:
			return struct.unpack(f'<i', ser[:4] + (4 - size) * bytes(ser[3])), size
		if size <= 8:
			return struct.unpack(f'<q', ser[:8] + (8 - size) * bytes(ser[7])), size
		return None

	@staticmethod
	def __deserialize_float(ser: bytes, tsid: str):
		size: int = int(tsid[2:])
		if size == 2:
			return struct.unpack(f'<e', ser[:2]), size
		if size == 4:
			return struct.unpack(f'<f', ser[:4]), size
		if size == 8:
			return struct.unpack(f'<d', ser[:8]), size
		return None

	@staticmethod
	def __deserialize_bool(ser: bytes, tsid: str):
		return struct.unpack(f'<?', ser[:1]), 1

	def __deserialize_iterable(self, ser: bytes, tsid: str):
		# Houston, we have a problem
		# TODO: do ite<N/r>_u_1 instead
		pass

	@staticmethod
	def __get_type_identifier(value) -> str:
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

	def _get_attr(self) -> dict:
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
		return {name: self.__get_type_identifier(value) for name, value in self.__dict__.items() if
				name != 'serialized_attr'}

	def _get_attr_default(self) -> dict:
		"""
		Returns the default get_attr() dict (users can use this
		function in get_attr() and override specific attributes).
		"""
		return {name: self.__get_type_identifier(value) for name, value in self.__dict__.items() if
				name != 'serialized_attr'}

	def serialize(self, formatting='fixed') -> bytes:
		"""
		Serializes the object's attributes.
		:param formatting: The format of the serialized output. Can be either 'json' or 'fixed' (pure byte form).
		:return: The serialized version of the object.
		"""

		self.serialized_attr: dict = self._get_attr()  # update serialized_attr

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
					print(
						f'ERROR: Cannot serialize attribute {attr} of type {type(value)} since it does not inherit Serializable')

			# an object (which inherits Serializable): do write its length - in 2 bytes (always).
			elif type_id == 'o_N':
				if isinstance(value, Serializable):
					serialized_value = value.serialize()
					if len(serialized_value) > 0xffff:  # Length should be 2 bytes, so make sure it isn't more than that
						print(f'Length of serialized attribute {attr} (type {type(value)}) is too long')
						continue
					output += struct.pack('<h', len(serialized_value)) + serialized_value
				else:
					print(
						f'ERROR: Cannot serialize attribute {attr} of type {type(value)} since it does not inherit Serializable')

			# Not an object: a primitive type or an iterable
			else:
				serialized_primitive = self.__serialize_primitive(attr, value, type_id)
				if serialized_primitive is not None:
					output += serialized_primitive

		return output

	def __serialize_primitive(self, attr: str, value, type_id: str, length: int = 1) -> bytes:
		"""
		Serializes primitive types (numbers and iterables).
		:param attr: The attribute name (for debugging and error messages).
		:param value: The value to serialize. Must not be a non-iterable object.
		:param type_id: The type size identifier of the value. See get_attr() for more info.
		:param length: Used for iterables recursively. Ignore it.
		:return: The serialized value if possible; else None.
		"""
		# especially for dicts
		if isinstance(value, dict):
			value = list(value.items())

		# especially for strings (since their element is always a string too)
		if isinstance(value, str):
			return self.__serialize_str(value, type_id)

		# an unsigned integer
		elif type_id[:2] == 'u_':
			return self.__serialize_unsigned(value, type_id, length)

		# a signed integer
		elif type_id[:2] == 's_':
			return self.__serialize_signed(value, type_id, length)

		# a float number with known length.
		elif type_id[:2] == 'f_':
			return self.__serialize_float(value, type_id, length)

		# bool
		elif type_id == 'b':
			return self.__serialize_bool(value, length)

		# a string/iterable: length is written before the iterable attribute in 2 bytes.
		elif type_id[:3] == 'ite':
			return self.__serialize_iterable(attr, value, type_id, length)

	@staticmethod
	def __serialize_str(value: str, type_id: str) -> bytes:
		if type_id[:5] == 'iter_':
			return struct.pack(f'<{len(value)}s', value.encode())
		elif type_id[:5] == 'iteN_':
			return struct.pack(f'<h', len(value)) + struct.pack(f'<{len(value)}s', value.encode())

	@staticmethod
	def __serialize_unsigned(value: Union[int, Iterable], type_id: str, length: int) -> bytes:
		if not type_id[2:].isdigit():  # Make sure that the TSID is valid
			print(
				f'ERROR: Invalid attribute type size identifier\nValue: {value}\nTSID: {type_id}')
			return
		var_len = int(type_id[2:])
		return struct.pack(f'<{length}Q', value)[:var_len]

	@staticmethod
	def __serialize_signed(value: Union[int, Iterable], type_id: str, length: int) -> bytes:
		if not type_id[2:].isdigit():  # Make sure that the TSID is valid
			print(
				f'ERROR: Invalid attribute type size identifier\nValue: {value}\nTSID: {type_id}')
			return
		var_len = int(type_id[2:])

		# Signed integers are a little more confusing to work with, so added some stuff just in case
		output: bytes = None

		if length == 1:
			if var_len == 1:
				output = struct.pack(f'<b', value)
			elif var_len == 2:
				output = struct.pack(f'<h', value)
			elif var_len == 4:
				output = struct.pack(f'<i', value)
			elif var_len == 8:
				output = struct.pack(f'<q', value)
		else:
			if var_len == 1:
				output = struct.pack(f'<{length}b', *value)
			elif var_len == 2:
				output = struct.pack(f'<{length}h', *value)
			elif var_len == 4:
				output = struct.pack(f'<{length}i', *value)
			elif var_len == 8:
				output = struct.pack(f'<{length}q', *value)

		if output is None:
			print(
				'WARNING: You are trying to serialize a signed value to an arbitrary byte amount. Make sure it works as expected.')
			return struct.pack('<q', value)[:var_len]
		else:
			return output

	@staticmethod
	def __serialize_float(value: Union[int, Iterable], type_id: str, length: int) -> bytes:
		if not type_id[2:].isdigit():  # Make sure that the TSID is valid
			print(
				f'ERROR: Invalid attribute type size identifier\nnValue: {value}\nTSID: {type_id}')
			return
		var_len = int(type_id[2:])

		if var_len not in (2, 4, 8):
			print(f'ERROR: Invalid attribute type size identifier (float size can only be 2/4/8)'
				  f'\nValue: {value}\nTSID: {type_id}')
			return None

		if length == 1:
			if var_len == 2:
				return struct.pack(f'<e', value)
			if var_len == 4:
				return struct.pack(f'<f', value)
			if var_len == 8:
				return struct.pack(f'<d', value)
		else:
			if var_len == 2:
				return struct.pack(f'<{length}e', *value)
			if var_len == 4:
				return struct.pack(f'<{length}f', *value)
			if var_len == 8:
				return struct.pack(f'<{length}d', *value)

	@staticmethod
	def __serialize_bool(value: Union[int, Iterable], length: int) -> bytes:
		if length == 1:
			return struct.pack(f'<?', value)
		else:
			return struct.pack(f'<{length}?', *value)

	def __serialize_iterable(self, attr: str, value: Iterable, type_id: str, length: int) -> bytes:
		if type_id[:5] == 'iteN_' and (
				not type_id[5:].isdigit() and type_id[5] != 'd'):  # Make sure that the TSID is valid if iteN_x
			print(
				f'ERROR: Invalid attribute type size identifier\nAttribute: {attr}\nValue: {value}\nTSID: {type_id}')
			return

		# Check if the iterable is empty
		if not value:
			return b'0000'  # length is 0

		# if all items in the iterable are of the same primitive type
		if all(isinstance(item, (type(value[0]))) for item in value) and not hasattr(value[0], '__iter__'):
			var_tsid = self.__get_type_identifier(value[0])
			if type_id[5] != 'd':
				if var_tsid[:5] == 'iteN_':
					var_tsid = var_tsid[:5] + type_id[
											  5:]  # the iterable's items are iterables themselves - pass the size
				elif var_tsid[:5] == 'iter_':
					var_tsid = var_tsid[:5] + type_id[
											  5:]  # the iterable's items are iterables themselves - pass the size
				elif var_tsid[:2] in ('u_', 'f_'):
					var_tsid = var_tsid[:2] + type_id[5:]  # the iterable's items are primitive types

			# Make sure that not all the iterable's items are objects and entered this if by accident
			if var_tsid not in ('o', 'o_N') and var_tsid[:2] != 's_':
				output: bytes = self.__serialize_primitive(attr + '.', value, var_tsid, len(value))
				if type_id[:5] == 'iteN':
					if len(output) > 0xffff:  # Length should be 2 bytes, so make sure it isn't more than that
						print(f'Length of serialized attribute {attr} (type {type(value)}) is too long')
						return
					return struct.pack('<h', len(output)) + output  # add length if iteN_x
				return output  # don't add length if iter_

		output: bytes = b''
		for item in value:
			var_tsid = self.__get_type_identifier(item)
			if var_tsid == 'o_N':
				output += item.serialize()
				continue
			if type_id[5] != 'd':
				if var_tsid[:5] == 'iteN_':
					var_tsid = var_tsid[:5] + type_id[
											  5:]  # the iterable's items are iterables themselves - pass the size
				elif var_tsid[:5] == 'iter_':
					var_tsid = var_tsid[:5] + type_id[
											  5:]  # the iterable's items are iterables themselves - pass the size
				elif var_tsid[:2] in ('u_', 's_', 'f_'):
					var_tsid = var_tsid[:2] + type_id[5:]  # the iterable's items are primitive types

			output += self.__serialize_primitive(attr + '.', item, var_tsid)

		if type_id[:5] == 'iteN_':
			if len(output) > 0xffff:  # Length should be 2 bytes, so make sure it isn't more than that
				print(f'Length of serialized attribute {attr} (type {type(value)}) is too long')
				return
			return struct.pack('<h', len(output)) + output  # add length if iteN_x
		return output  # don't add length if iter_

# test class
class Entity(Serializable):
	def __init__(self, ser: bytes = None):
		super().__init__(ser)
		if ser is None:
			self.x = 3
			self.y = 0.65
			self.z = -300
			#self.hi = 'hi'
			#self.lis = [1, -300, 'yes']
			#self.dic = {1: 'a', 2: 'b'}
			#self.inher = Item()

	def _get_attr(self) -> dict:
		#d: dict = self._get_attr_default()
		#d['lis'] = 'iteN_d'
		#d['dic'] = 'iteN_1'

		return {'x': 'u_1', 'y': 'f_8', 'z': 's_2'}


class Item(Serializable):
	def __init__(self, *args):
		super().__init__(args)
		self.hello = 5
		self.s = 'string'

	def _get_attr(self) -> dict:
		d: dict = super()._get_attr_default()
		d['hello'] = 's_1'
		return d


if __name__ == '__main__':
	e1 = Entity()
	ser = e1.serialize()
	print(ser)
	e2 = Entity(ser)
	print(e2.__dict__)
