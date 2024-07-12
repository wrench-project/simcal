import inspect
import types
import typing
import warnings
from functools import wraps

DEEP_STRICT_TYPE_CHECKING = True


def check_arg_type(arg, arg_type, aux):
    # print(arg_type)
    # print(type(arg_type))
    if isinstance(arg_type, typing.TypeAliasType):
        arg_type = arg_type.__value__  # unpack alias
    if arg_type in {typing.Any}:
        return True  # I dont know why isinstance doesnt support typing.Any... just return True for all types...
    if arg_type is None:
        return arg is None
    if arg_type is typing.Self:
        return aux is None or id(arg) == id(aux)
    # if isinstance(arg_type,str):
    #	raise TypeError(f"Typing Error in {function}\n	@strict does not support raw string types")
    origin = typing.get_origin(arg_type)
    # print(origin)
    if origin is None:  # Normal type
        return isinstance(arg, arg_type)
    else:  # subscrpted generic
        if origin in {typing.Union, types.UnionType}:
            return any(check_arg_type(arg, subtype, aux) for subtype in typing.get_args(arg_type))
        if not isinstance(arg, origin):
            return False
        if DEEP_STRICT_TYPE_CHECKING:
            if origin in {tuple, typing.Tuple}:
                item_types = typing.get_args(arg_type)
                if len(item_types) != len(arg):
                    return False
                return all(check_arg_type(o, t, aux) for o, t in zip(arg, item_types))

            elif origin in {list, typing.List, set, typing.Set}:
                item_type = typing.get_args(arg_type)[0]
                return all(check_arg_type(item, item_type, aux) for item in arg)

            elif origin in {dict, typing.Dict}:
                key_type, value_type = typing.get_args(arg_type)
                return all(
                    check_arg_type(k, key_type, aux) and check_arg_type(v, value_type, aux) for k, v in arg.items())

        warnings.warn(f"Generic type '{arg_type}' Not deep checked")
        return True


def type_checked(func):
    @wraps(func)
    def wrapper(*args, **kwargs):

        # Get the argument names and their type hints
        signature = inspect.signature(func)
        parameters = signature.parameters
        function = '"' + func.__name__ + '"'
        try:
            hints = typing.get_type_hints(func)
        except NameError as e:
            warnings.warn(
                f"strict type checking doesnt support functions with hidden type or class definition such as those within functions while `from __future__ import anotations` is active.  In this case, the problem is specifically \"{e.name}\" in function {function}")
            return func(*args, **kwargs)
        # print()
        # Check positional arguments
        issues = []
        if (len(args) > 0):
            aux = args[0]
        else:
            aux = None
        # print(args)
        for i, arg in enumerate(args):
            arg_name = list(parameters.keys())[i]
            if arg_name in hints:
                arg_type = hints[arg_name]
                # print(function,"|",arg,"|",arg_name,"|",arg_type,"|",type(arg_type),"|",isinstance(arg_type,str))
                if not check_arg_type(arg, arg_type, aux):
                    issues.append(
                        f"	Argument '{arg_name}' must be of type '{arg_type}', got '{type(arg).__name__}' instead.")

        # Check keyword arguments
        for arg_name in kwargs:
            # if isinstance(arg_type,str):
            #	raise TypeError(f"Typing Error in {function}\n	@strict does not support raw string types")
            if arg_name in hints:
                arg_value = kwargs[arg_name]
                arg_type = hints[arg_name]
                # print(function,"|",arg_value,"|",arg_name,"|",arg_type,"|",type(arg_type))
                if not check_arg_type(arg_value, arg_type, aux):
                    issues.append(
                        f"	Argument '{arg_name}' must be of type '{arg_type}', got '{type(arg_value).__name__}' instead.")
        if issues:
            # function=inspect.getsourcelines(func)[0][1].strip()[4:].strip()
            raise TypeError(f"Strict Argument Error in {function}\n" + "\n".join(issues))
        # Call the original function
        result = func(*args, **kwargs)
        if 'return' in hints:
            return_type = hints['return']
            # Check the returned value
            if not check_arg_type(result, return_type, aux):
                raise TypeError(f"Function {function} must return a '{return_type}', got '{type(result)}' instead.")
        # print()
        return result

    return wrapper
