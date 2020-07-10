from dataclasses import dataclass
from typing import Sequence


@dataclass
class FilteredModel:
    whitelist: Sequence[str]

    @classmethod
    def from_json(cls, whitelist: Sequence, json_content):
        raise NotImplementedError

    def to_json(self):
        result = {}
        for elem in self.whitelist:
            if isinstance(elem, str):
                value = self.__getattribute__(elem)
                if value is not None:
                    result[elem] = value
            elif isinstance(elem, dict):
                key = next(iter(elem))
                object = self.__getattribute__(key)
                if isinstance(object, list):
                    # persons!
                    result[key] = []
                    for entry in object:
                        result.get(key).append(entry.to_json())
                else:
                    result[key] = object.to_json()
        return result

    def to_md(self, template=None):
        raise NotImplementedError
