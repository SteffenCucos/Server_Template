
from dataclasses import field
from typing import Any, cast


class FieldMetadata():
    """
    Holds a list metadata name+value pairs, supprots merging with 
    other FieldMetadata objects to more easily combine sets of metadata

    Ex:
    min = FieldMetadata(min=0)
    max = FieldMetadata(max=10)

    min | max == FieldMetadata(min=0,max=10)
    """

    def __init__(self, **kwargs: Any):
        self._metadata = {**kwargs}

    def __add__(self, other: 'FieldMetadata') -> 'FieldMetadata':
        return self._merge(other)

    def __or__(self, other: 'FieldMetadata') -> 'FieldMetadata':
        return self._merge(other)

    def _merge(self, other: 'FieldMetadata') -> 'FieldMetadata':
        combined_metadata = {**self._metadata}
        for key in combined_metadata.keys():
            value = combined_metadata[key]
            if key in other._metadata.keys():
                other_value = other._metadata[key]
                if isinstance(value, dict):
                    value = {**value, **other_value} # The 'other' will overwrite any fields they share
                if isinstance(value, bool):
                    value = value or other_value

            combined_metadata[key] = value

        for key in other._metadata.keys():
            if key not in combined_metadata.keys():
                combined_metadata[key] = other._metadata[key]
                
        return FieldMetadata(**combined_metadata)


_keywords = set(["default", "default_factory", "init", "repr", "hash", "compare", "metadata", "kw_only", "doc"])


def cfield(*args: Any, **kwargs: Any) -> Any:  
    """
    Wrapper over dataclasses.field that considers possible FieldMetadata params 
    and merges them into a single metadata parameter
    """
    metadata = dict()
    new_kwargs = dict()
    new_args = []
    for arg in args:
        if isinstance(arg, FieldMetadata):
            metadata = {**arg._metadata}
        else:
            new_args.append(arg)

    for key, value in kwargs.items():
        if key in _keywords and key != "metadata":
            new_kwargs[key] = value
        elif key == "metadata":
            metadata = metadata | cast(dict[str, Any], value)
        else:
            metadata[key] = value

    return field(*new_args, **new_kwargs, metadata=metadata)
