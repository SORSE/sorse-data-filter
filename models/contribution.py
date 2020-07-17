import re
from dataclasses import dataclass
from typing import List

import gspread
import yaml

from models import FilteredModel
from models.person import Person
from models.questionnaire import Questionnaire
from utils import load_orcid_information, find_custom_fields_key, create_template, \
    to_float, traverse_into, load_allow_list

ORCID_ID_PATTERN = re.compile(r"\d{4}-\d{4}-\d{4}-\d{4}")
with open("./contributions.yaml") as stream:
    CONTRIBUTION_MAPPING = yaml.safe_load(stream)


def load_orcid_data(orcid_string):
    matched_orcids = ORCID_ID_PATTERN.findall(orcid_string)
    return load_orcid_information(matched_orcids)


@dataclass
class Contribution(FilteredModel):
    id: str
    submission_date: str
    acceptance_date: str
    persons: List[Person]
    questionnaire: Questionnaire
    contact_email: str
    title: str
    content: str
    state: str
    score: float

    @property
    def link(self):
        if CONTRIBUTION_MAPPING is not None:
            return CONTRIBUTION_MAPPING["mapping"][self.id]
        return None

    @property
    def contribution_type(self):
        return self.questionnaire.contribution_questions.contribution_type

    @classmethod
    def from_json(cls, allow_list, json_content):
        person_allow_list = load_allow_list("persons", allow_list)
        questionnaire_allow_list = load_allow_list("questionnaire", allow_list)
        custum_field_keys = list(json_content["custom_fields"].keys())
        extended_orcids = load_orcid_data(json_content["custom_fields"].get(
            find_custom_fields_key(custum_field_keys, "ORCID"), ""))

        # load answers to other questions
        questionnaire = Questionnaire.from_json(questionnaire_allow_list, json_content)
        # get contact email
        contact_email = json_content["custom_fields"].get("Contact Email", None)
        # load authors and speakers
        persons = []
        authors = json_content["persons"]
        for author in authors:
            person = Person.from_json(
                allow_list=person_allow_list,
                json_content=author,
                orcids=extended_orcids,
                email_agreement=questionnaire.agreement_email_publication,
                contact_email=contact_email)
            if person is not None:
                persons.append(person)
        return Contribution(
            id=json_content["friendly_id"],
            allow_list=allow_list,
            submission_date=json_content["submitted_dt"],
            acceptance_date=None,
            persons=persons,
            questionnaire=questionnaire,
            contact_email=contact_email,
            title=json_content["title"],
            content=json_content["content"],
            state=json_content["state"],
            score=to_float(json_content["score"]),
        )

    @classmethod
    def to_spreadsheet(cls, template=None, contributions=None):
        with open(f"./templates/{template}", "r") as stream:
            config_data = yaml.safe_load(stream)
        header_data = config_data["mapping"]
        gc = gspread.oauth()
        sh = gc.create("Test", "1KLDFQ0VR7D16Ju-ir-TjlJXeNsqjNGge")
        worksheet = sh.get_worksheet(0)
        worksheet.append_row(list(header_data.keys()))
        for contribution in contributions:
            worksheet.append_row([traverse_into(value.split("."), contribution=contribution) for value in header_data.values()])

    def to_md(self, template=None):
        contribution = self.to_json()

        template_renderer = create_template(template)
        return template_renderer.render(contribution=contribution)

    def __repr__(self):
        return f"{self.__class__.__name__}(id='{self.id}', " \
               f"submission_date='{self.submission_date}', " \
               f"acceptance_date='{self.acceptance_date}', persons={self.persons}, " \
               f"questionnaire={self.questionnaire}, " \
               f"contact_email='{self.contact_email}', title='{self.title}', " \
               f"content='{self.content}', " \
               f"contribution_type='{self.contribution_type}')"
