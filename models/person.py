from dataclasses import dataclass
from typing import Optional, Dict

from models import FilteredModel
from utils import search_matching_orcid, to_bool


@dataclass
class Person(FilteredModel):
    address: str
    affiliation: str
    author_type:  str
    first_name: str
    last_name: str
    is_speaker: bool
    title: str
    orcid: Optional[str]

    @classmethod
    def from_json(cls, whitelist, json_content, orcids: Dict[str, Dict]):
        first_name = json_content["first_name"]
        last_name = json_content["last_name"]
        orcid_id = search_matching_orcid(first_name, last_name, orcids)
        return Person(
            whitelist=whitelist,
            first_name=json_content["first_name"],
            last_name=json_content["last_name"],
            affiliation=json_content["affiliation"],
            address=json_content["address"],
            author_type=json_content["author_type"],
            is_speaker=to_bool(json_content["is_speaker"]),
            title=json_content["title"],
            orcid=orcid_id
        )

    def __repr__(self):
        return f"{self.__class__.__name__}(address='{self.address}', " \
               f"affiliation='{self.affiliation}', author_type='{self.author_type}', " \
               f"first_name='{self.first_name}', last_name='{self.last_name}', " \
               f"is_speaker='{self.is_speaker}', title='{self.title}', " \
               f"orcid='{self.orcid}')"
