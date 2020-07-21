from dataclasses import dataclass
from typing import Optional, List, Sequence

import yaml

from models import FilteredModel
from utils import to_str

with open("./affiliations.yaml") as stream:
    AFFILIATION_MAPPING = {}
    affiliations = yaml.safe_load(stream)
    for affiliation, spellings in affiliations.items():
        for spelling in spellings:
            AFFILIATION_MAPPING[spelling] = affiliation


@dataclass
class Affiliation(FilteredModel):
    name: str

    @classmethod
    def from_json(cls, allow_list: Sequence, json_content):
        name = to_str(json_content["affiliation"])
        if name:
            normalised_affiliation = AFFILIATION_MAPPING[name]
            return Affiliation(
                allow_list=allow_list,
                name=normalised_affiliation,
            )
        return None

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        if (isinstance(other, type(self)) and
                self.name == other.name and self.allow_list == other.allow_list):
            return True
        return False

    def __lt__(self, other):
        return self.name < other.name


def search_matching_affiliation(
        name: str, affiliations: List[Affiliation]) -> Optional[int]:
    if name:
        normalised_affiliation = AFFILIATION_MAPPING[name]
        for index, affiliation in enumerate(affiliations):
            if normalised_affiliation == affiliation.name:
                return index
    return None
