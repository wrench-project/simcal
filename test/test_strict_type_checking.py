#from __future__ import annotations
import typing

from simcal import strict_typing
from typing import Union, List, Tuple
import unittest

class TestTypeCheckedDecorator(unittest.TestCase):
	def test_correct_types(self):
		# Test with correct types
		@strict_typing
		def add(x: int, y: int) -> int:
			return x+y
		self.assertEqual(add(2, 3), 5)
	def test_incorrect_argument_type(self):
		# Test with incorrect argument type
		@strict_typing
		def add(x: int, y: int) -> int:
			return x+y
		with self.assertRaises(TypeError):
			add(2, '3')

		
	
	def test_multiple_types_union(self):
		# Test with multiple allowed types
		@strict_typing
		def concat(x: str, y: Union[int, float]) -> str:
			return str(x) + str(y)
		
		self.assertEqual(concat('Hello', 42), 'Hello42')
		self.assertEqual(concat('Hello', 3.14), 'Hello3.14')

		with self.assertRaises(TypeError):
			concat('Hello', [1, 2, 3])

	def test_any_type(self):
		# Test with Any type
		@strict_typing
		def process_data(data: typing.Any) -> bool:
			return True

		self.assertTrue(process_data(42))
		self.assertTrue(process_data('Hello'))
		self.assertTrue(process_data([1, 2, 3]))

		
	def test_child_classes(self):
		# Test with child classes
		class Animal:
			pass

		class Dog(Animal):
			pass

		@strict_typing
		def adopt_pet(pet: Animal) -> bool:
			return True
		animal = Animal()
		dog = Dog()
		self.assertTrue(adopt_pet(animal))
		self.assertTrue(adopt_pet(dog))

		with self.assertRaises(TypeError):
			adopt_pet('cat')

	def test_typed_list(self):
		# Test with generics types like List[int]
		from typing import List

		@strict_typing
		def process_numbers(numbers: list[int]) -> List[int]:
			return [x * 2 for x in numbers]
		
		self.assertEqual(process_numbers([1, 2, 3]), [2, 4, 6])
		
		with self.assertRaises(TypeError):
			process_numbers([1, 2, 'three'])
	def test_typed_dict(self):
		# Test with generics types like List[int]
		from typing import List

		@strict_typing
		def flatten(dictionary: dict[str,int]) -> List[str]:
			return [str(x) for x in dictionary.items()]
		self.assertEqual(flatten({"a":1,"b":2,"c":3}), ["('a', 1)", "('b', 2)", "('c', 3)"])
		
		with self.assertRaises(TypeError):
			flatten({"a":1,"b":2,"c":3.0})
		with self.assertRaises(TypeError):
			flatten({"a":1,"b":2,3:3})
	def test_typed_set(self):
		# Test with generics types like List[int]
		from typing import List

		@strict_typing
		def flatten(the_set: set[str]) -> List[str]:
			return list(the_set)

		self.assertEqual(flatten({"a","b","c"}), list({"a","b","c"}))
		
		with self.assertRaises(TypeError):
			flatten({"a","b",3})
	def test_typed_Tuple(self):
		# Test with generics types like List[int]
		from typing import List

		@strict_typing
		def process_numbers(numbers: tuple[int,float,str]) -> list:
			return [x for x in numbers]
		
		self.assertEqual(process_numbers((1, 2.0, "3")), [1, 2.0, "3"])
		with self.assertRaises(TypeError):
			process_numbers([1, 2.0, "3"])
		with self.assertRaises(TypeError):
			process_numbers((1, 2, 3))
		with self.assertRaises(TypeError):
			process_numbers((1, 2.0))
		with self.assertRaises(TypeError):
			process_numbers((1, 2.0, "3",4))
	def test_multiple_types_union(self):
		# Test with multiple allowed types
		@strict_typing
		def concat(x: str, y: Union[int, float]) -> str:
			return str(x) + str(y)
		
		self.assertEqual(concat('Hello', 42), 'Hello42')
		self.assertEqual(concat('Hello', 3.14), 'Hello3.14')

		with self.assertRaises(TypeError):
			concat('Hello', [1, 2, 3])
	def test_multiple_types_bar(self):
		# Test with multiple allowed types
		@strict_typing
		def concat(x: str, y: int| float) -> str:
			return str(x) + str(y)
		
		self.assertEqual(concat('Hello', 42), 'Hello42')
		self.assertEqual(concat('Hello', 3.14), 'Hello3.14')

		with self.assertRaises(TypeError):
			concat('Hello', [1, 2, 3])
	def test_named(self):
		# Test with multiple allowed types
		@strict_typing
		def echo(x: int=0) -> bool:
			return True
		
		self.assertTrue(echo(1))
		self.assertTrue(echo(x=1))

		with self.assertRaises(TypeError):
			echo(1.0)
	
	def test_self_optional(self):
		# Test with multiple allowed types
		@strict_typing
		def foo(x:bool|None=None):
			return
		foo()
		foo(True)
		with self.assertRaises(TypeError):
			foo(1)
	def test_none_ret(self):
		# Test with multiple allowed types
		@strict_typing
		def foo(x=False) -> None:
			if x is None:
				return 0
			if x:
				return None
			
		foo()
		foo(True)

		with self.assertRaises(TypeError):
			foo(None)
	def test_optional(self):
		# Test with multiple allowed types
		@strict_typing
		def foo(x:typing.Optional[bool]=None):
			return
		foo()
		foo(True)
		with self.assertRaises(TypeError):
			foo(1)		
	def test_complex_typing(self):
		@strict_typing
		def process_data(data: Union[List[int], List[float], float, Tuple[str, List[Union[int, float]], bool]]) -> Union[float, str, List[Union[int, float]]]:
			if isinstance(data, list):
				if all(isinstance(i, int) for i in data):
					return sum(data) / len(data)  # Return average of integer list
				elif all(isinstance(i, float) for i in data):
					return sum(data) / len(data)  # Return average of float list
			elif isinstance(data, float):
				return data ** 2  # Return square of the float
			elif isinstance(data, tuple) and len(data) == 3:
				string_part, num_list, bool_part = data
				if isinstance(string_part, str) and isinstance(num_list, list) and isinstance(bool_part, bool):
					if bool_part:
						return num_list  # Return the list if boolean is True
					else:
						return string_part  # Return the string if boolean is False
			return "Invalid input"  # Fallback for invalid input types
		self.assertEqual(process_data([1, 2, 3]),2.0)  # Should return 2.0
		self.assertEqual(process_data([1.5, 2.5, 3.5]),2.5)  # Should return 2.5
		self.assertEqual(process_data(4.0),16.0)  # Should return 16.0
		self.assertEqual(process_data(("Hello", [1, 2, 3], False)),"Hello")  # Should return "Hello"
		self.assertEqual(process_data(("Hello", [1, 2, 3], True)),[1, 2, 3])  # Should return [1, 2, 3]
		with self.assertRaises(TypeError):
			process_data(2)
			
	def test_class_self(self):
		# Test with multiple allowed types
		class Foo:
			@strict_typing
			def foo(self:typing.Self,x:int)->typing.Self:
				if x==1:
					return Foo() #I self must return... self, not just the same class 
				if x==2:
					return x
				return self
		foo=Foo()
		foo.foo(0)
		with self.assertRaises(TypeError):
			foo.foo(1)
		with self.assertRaises(TypeError):
			foo.foo(2)
	

	def test_alias(self):
		type Vector = list[float]	
		# Test with type alas
		from typing import List

		@strict_typing
		def process_numbers(numbers: Vector) -> Vector:
			return [x * 2 for x in numbers]
		
		self.assertEqual(process_numbers([1.0, 2.0, 3.0]), [2.0, 4.0, 6.0])
		
		with self.assertRaises(TypeError):
			process_numbers([1.0, 2.0, 'three'])			

	#test after from __future__ import annotations
	#switch to using typing.get_type_hints(func) in core code
if __name__ == '__main__':
	unittest.main()