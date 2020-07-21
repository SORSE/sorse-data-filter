from typing import Iterable, Optional, Dict, Sequence

import jinja2
import requests


TEXT_REPLACEMENTS = {
    "‘": "'",
    "’": "'",
    "“": '"',
    "”": '"',
    "–": "--",
}
TITLE_REPLACEMENTS = {
    "&": "and"
}


def load_allow_list(name: str, allow_list: Sequence) -> Sequence:
    for elem in allow_list:
        if isinstance(elem, dict):
            first_key = list(elem.keys())[0]
            if name == first_key:
                return elem[name]
    return []


def traverse_into(name, **namespace):
    head = namespace[name[0]]
    for path in name[1:]:
        if isinstance(head, dict):
            head = head[path]
        else:
            head = getattr(head, path)
    return head


def create_template(template_file):
    templateLoader = jinja2.FileSystemLoader(searchpath="./templates")
    templateEnv = jinja2.Environment(loader=templateLoader)
    template = templateEnv.get_template(template_file)
    return template


def to_float(value: str, default: float = 0.0) -> float:
    if value is None:
        return default
    return float(value)


def to_str(value: str, default: Optional[str] = None) -> Optional[str]:
    if value is None or "none" == value.lower():
        return default
    return value


def to_text(value: str) -> Optional[str]:
    """Function ensures proper encoding of entities"""
    return replace_text(value, TEXT_REPLACEMENTS)


def to_title(value:  str) -> Optional[str]:
    """Function  ensures proper encoding of titles"""
    return replace_text(value, TITLE_REPLACEMENTS)


def replace_text(text: str, replacements: Dict[str, str]) -> Optional[str]:
    if text:
        for old, replacement in replacements.items():
            text = text.replace(old, replacement)
    return text


def to_bool(value: str, default: bool = False) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return default
    value = value.lower()
    if "yes" in value or "true" in value:
        return True
    return False


def find_custom_fields_key(keys: Sequence[str], name: str) -> Optional[str]:
    for index, key in enumerate(keys):
        if name in key:
            return keys[index]
    return None


def flatten_custom_fields(elements: Sequence[Dict]) -> Dict:
    if len(elements) == 0:
        return {}
    assert "name" in elements[0] and "value" in elements[0]
    return {element["name"]: element["value"] for element in elements}


def load_orcid_information(orcids: Iterable[str]) -> Dict[str, Dict]:
    result = {}
    for orcid in orcids:
        response = requests.get(f"https://orcid.org/{orcid}/person.json")
        if response.status_code == 200:
            orcid_data = response.json()
            result[orcid] = {
                "displayName": orcid_data["displayName"],
                "publicGroupedOtherNames": orcid_data["publicGroupedOtherNames"]
            }
    return result


def check_name(first, last, to_check):
    if first in to_check and last in to_check:
        return True
    return False


def search_matching_orcid(
        first_name: str, last_name: str, orcids: Dict[str, Dict]) -> Optional[str]:
    first_name = first_name.lower()
    last_name = last_name.lower()
    for orcid_id, orcid_information in orcids.items():
        if check_name(first_name, last_name, orcid_information["displayName"].lower()):
            return orcid_id
        # also check for other names
        for key in orcid_information["publicGroupedOtherNames"]:
            if check_name(first_name, last_name, key.lower()):
                return orcid_id
    return None
