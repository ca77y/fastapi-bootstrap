import inspect
from typing import Type

from fastapi.params import Depends as Depends_Type


def find_fastapi_param_name(handler, param_type: Type):
    for param in inspect.signature(handler).parameters.values():
        if (
            param.annotation is param_type
            and type(param.default) is Depends_Type
            and (
                param.kind == inspect.Parameter.POSITIONAL_ONLY or param.kind == inspect.Parameter.POSITIONAL_OR_KEYWORD
            )
        ):
            return param.name
    else:
        raise Exception(
            f"Function {handler.__name__} should have a positional or keyword argument of "
            f"type {param_type} with a dependency"
        )
