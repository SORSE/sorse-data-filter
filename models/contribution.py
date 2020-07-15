import re
from dataclasses import dataclass
from typing import List

import jinja2

from models import FilteredModel
from models.person import Person
from models.questionnaire import Questionnaire
from utils import load_orcid_information, find_custom_fields_key


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

        def load_orcid_data(orcid_string):
            orcid_pattern = re.compile("\d{4}-\d{4}-\d{4}-\d{4}")
            matched_orcids = orcid_pattern.findall(orcid_string)
            return load_orcid_information(matched_orcids)
        person_whitelist, questionnaire_whitelist = extract_whitelists(whitelist)
        custum_field_keys = list(json_content["custom_fields"].keys())
        extended_orcids = load_orcid_data(json_content["custom_fields"].get(
            find_custom_fields_key(custum_field_keys, "ORCID"), ""))

        # load answers to other questions
        questionnaire = Questionnaire.from_json(questionnaire_whitelist, json_content)
        # get contact email
        contact_email = json_content["custom_fields"].get("Contact Email", None)
        # load authors and speakers
        persons = []
        authors = json_content["persons"]
        for author in authors:
            person = Person.from_json(
                whitelist=person_whitelist,
                json_content=author,
                orcids=extended_orcids,
                email_agreement=questionnaire.agreement_email_publication,
                contact_email=contact_email)
            if person is not None:
                persons.append(person)
        return Contribution(
            id=json_content["id"],
            whitelist=whitelist,
            submission_date=json_content["submitted_dt"],
            acceptance_date=None,
            persons=persons,
            questionnaire=questionnaire,
            contact_email=contact_email,
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
