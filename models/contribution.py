import re
from dataclasses import dataclass
from typing import List

from models import FilteredModel
from models.person import Person
from models.questionnaire import Questionnaire
from utils import load_orcid_information, find_custom_fields_key, create_template, \
    to_float

ORCID_ID_PATTERN = re.compile(r"\d{4}-\d{4}-\d{4}-\d{4}")


def load_orcid_data(orcid_string):
    matched_orcids = ORCID_ID_PATTERN.findall(orcid_string)
    return load_orcid_information(matched_orcids)


def extract_allow_lists(allow_list):
    person_allow_list = None
    questionnaire_allow_list = None
    for element in allow_list:
        if isinstance(element, dict):
            if "persons" in element:
                person_allow_list = element["persons"]
                continue
            if "questionnaire" in element:
                questionnaire_allow_list = element["questionnaire"]
                continue
    return person_allow_list, questionnaire_allow_list


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
    def contribution_type(self):
        return self.questionnaire.contribution_questions.contribution_type

    @classmethod
    def from_json(cls, allow_list, json_content):
        person_allow_list, questionnaire_allow_list = extract_allow_lists(allow_list)
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
                contact_email=contact_email),
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
        )

    @classmethod
    def to_spreadsheet(cls, template=None, contributions=None):
        template_renderer = create_template(template)
        data = template_renderer.render(contributions=contributions)
        print(data)

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
