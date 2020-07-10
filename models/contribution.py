import os
import re
from dataclasses import dataclass
from typing import List

import jinja2

from models import FilteredModel
from models.person import Person
from models.questionnaire import Questionnaire
from utils import load_orcid_information, find_custom_fields_key, to_bool


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

    @property
    def contribution_type(self):
        return self.questionnaire.contribution_questions.contribution_type

    @classmethod
    def from_json(cls, whitelist, json_content):
        def extract_whitelists(whitelist):
            person_whitelist = None
            questionnaire_whitelist = None
            for element in whitelist:
                if isinstance(element, dict):
                    if "persons" in element:
                        person_whitelist = element["persons"]
                        continue
                    if "questionnaire" in element:
                        questionnaire_whitelist = element["questionnaire"]
                        continue
            return person_whitelist, questionnaire_whitelist
        person_whitelist, questionnaire_whitelist = extract_whitelists(whitelist)

        # load orcid information
        if to_bool(os.getenv("ORCID_ACTIVATED")):
            # TODO: does it work??
            orcids = json_content["custom_fields"].get(find_custom_fields_key(json_content["custom_fields"].keys(), "ORCID"), "")
            orcid_pattern = re.compile("\d{4}-\d{4}-\d{4}-\d{4}")
            matched_orcids = orcid_pattern.findall(orcids)
            extended_orcids = load_orcid_information(matched_orcids)
        else:
            extended_orcids = {}

        # load authors and speakers
        persons = []
        authors = json_content["persons"]
        for author in authors:
            person = Person.from_json(person_whitelist, author, extended_orcids)
            if person is not None:
                persons.append(person)
        # load answers to other questions
        questionnaire = Questionnaire.from_json(questionnaire_whitelist, json_content)
        return Contribution(
            id=json_content["id"],
            whitelist=whitelist,
            submission_date=json_content["submitted_dt"],
            acceptance_date=None,
            persons=persons,
            questionnaire=questionnaire,
            contact_email=None,
            title=json_content["title"],
            content=json_content["content"]
        )

    def to_md(self, template=None):
        contribution = self.to_json()

        templateLoader = jinja2.FileSystemLoader(searchpath="./templates")
        templateEnv = jinja2.Environment(loader=templateLoader)
        TEMPLATE_FILE = template
        template = templateEnv.get_template(TEMPLATE_FILE)
        return template.render(contribution=contribution)

    def __repr__(self):
        return f"{self.__class__.__name__}(id='{self.id}', " \
               f"submission_date='{self.submission_date}', " \
               f"acceptance_date='{self.acceptance_date}', persons={self.persons}, " \
               f"questionnaire={self.questionnaire}, " \
               f"contact_email='{self.contact_email}', title='{self.title}', " \
               f"content='{self.content}', " \
               f"contribution_type='{self.contribution_type}')"
