from typing import Iterable, Optional, Dict, Sequence

import requests


def to_str(value: str, default: Optional[str] = None) -> Optional[str]:
    if value is None or "none" in value:
        return default
    return value


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
