import os
from typing import Iterable, Optional, Dict, Sequence

import requests
from dotenv import load_dotenv


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
    orcid_api = OrcidAPI()
    for orcid in orcids:
        result[orcid] = orcid_api.personal_details(orcid_id=orcid)
    return result


def search_matching_orcid(first_name: str, last_name: str, orcids: Dict[str, Dict]) -> Optional[str]:
    first_name = first_name.lower()
    last_name = last_name.lower()
    for orcid_id, orcid_information in orcids.items():
        orcid_name = orcid_information["name"]
        if first_name in orcid_name["given-names"]["value"].lower() and \
                last_name in orcid_name["family-name"]["value"].lower():
            return orcid_id
        # also check other names
        other_names = orcid_information["other-names"]["other-name"]
        for other_name in other_names:
            name = other_name["content"].lower()
            if first_name in name and last_name in name:
                return orcid_id
    return None


class OrcidAPI:
    api_version: str = "v2.1"
    accept_type: str = "application/json"

    def __init__(self):
        self._access_token: str = None
        self._token_type: str = None

    @property
    def token_type(self) -> str:
        if self._token_type is None:
            self._initialize_access_token()
        return self._token_type

    @property
    def access_token(self) -> str:
        if self._access_token is None:
            self._initialize_access_token()
        return self._access_token

    def _initialize_access_token(self):
        assert self._access_token is None and self._token_type is None
        data = {
            "client_id": os.getenv("ORCID_CLIENT_ID"),
            "client_secret": os.getenv("ORCID_CLIENT_SECRET"),
            "grant_type": "client_credentials",
            "scope": "/read-public"
        }
        r = requests.post("https://orcid.org/oauth/token", data=data)
        result = r.json()
        self._access_token = result["access_token"]
        self._token_type = result["token_type"]

    def personal_details(self, orcid_id: str) -> Dict:
        endpoint = "/personal-details"
        headers = {'Accept': self.accept_type,
                   'Authorization': f'{self.token_type} {self.access_token}'}
        r = requests.get(f"https://pub.orcid.org/{self.api_version}/{orcid_id}{endpoint}", headers=headers)
        return r.json()


if __name__ == "__main__":
    load_dotenv()
    orcid = OrcidAPI()
    orcid.personal_details(orcid_id="0000-0002-8034-8837")
