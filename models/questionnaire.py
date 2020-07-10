from dataclasses import dataclass
from typing import Sequence,  ClassVar

from models import FilteredModel
from utils import to_bool, find_custom_fields_key, to_str


@dataclass
class Questionnaire(FilteredModel):
    agreement_zenodo_publication: bool
    agreement_recording_publication: bool
    agreement_cc_by_publication: bool
    agreement_email_contact: bool
    agreement_email_publication: bool
    language: str
    topic_bazaar: bool
    prerequisite_knowledge: str
    relevance: str
    earliest_delivery: str
    latest_delivery: str
    multiple_deliveries: bool
    main_author_job_title: str
    diversity_questions: "DiversityQuestions"
    contribution_questions: "ContributionQuestions"

    @classmethod
    def from_json(cls, whitelist: Sequence, json_content):
        custom_fields = json_content["custom_fields"]
        # load contents of diversity  questions
        diversity_questions = DiversityQuestions.from_json(whitelist, custom_fields)
        # load contribution questions
        contribution_questions = contribution_type_map.get(json_content["submitted_contrib_type"]["name"]).from_json(whitelist, custom_fields)
        keys = list(custom_fields.keys())
        return Questionnaire(
            whitelist=whitelist,
            agreement_zenodo_publication=to_bool(custom_fields.get(find_custom_fields_key(keys, "Zenodo"), None)),
            agreement_recording_publication=to_bool(custom_fields.get(find_custom_fields_key(keys, "recording published"), None)),
            agreement_cc_by_publication=to_bool(custom_fields.get(find_custom_fields_key(keys, "CC-BY 4.0"), None)),
            agreement_email_contact=to_bool(custom_fields.get(find_custom_fields_key(keys, "agree to be contacted by email"), None)),
            agreement_email_publication=to_bool(custom_fields.get(find_custom_fields_key(keys, "contact email is published"), None)),
            language=to_str(custom_fields.get("Language", None)),
            topic_bazaar=to_bool(custom_fields.get("Topic Bazaar", None)),
            prerequisite_knowledge=to_str(custom_fields.get("Prerequisite knowledge", None)),
            relevance=to_str(custom_fields.get("Relevance to the community", None)),
            earliest_delivery=custom_fields.get("Earliest delivery date", None),
            latest_delivery=custom_fields.get("Latest delivery date", None),
            multiple_deliveries=to_bool(custom_fields.get("Multiple deliveries", None)),
            main_author_job_title=to_str(custom_fields.get("Main author job title", None)),
            diversity_questions=diversity_questions,
            contribution_questions=contribution_questions,
        )

    def __repr__(self):
        return f"{self.__class__.__name__}(" \
               f"agreement_zenodo_publication='{self.agreement_zenodo_publication}', " \
               f"agreement_recording_publication='{self.agreement_recording_publication}', " \
               f"agreement_cc_by_publication='{self.agreement_cc_by_publication}', " \
               f"agreement_email_contact='{self.agreement_email_contact}', " \
               f"agreement_email_publication='{self.agreement_email_publication}', " \
               f"language='{self.language}', topic_bazaar='{self.topic_bazaar}', " \
               f"prerequisite_knowledge='{self.prerequisite_knowledge}', " \
               f"relevance='{self.relevance}', " \
               f"earliest_delivery='{self.earliest_delivery}', " \
               f"latest_delivery='{self.latest_delivery}', " \
               f"multiple_deliveries='{self.multiple_deliveries}', " \
               f"main_author_job_title='{self.main_author_job_title}', " \
               f"diversity_questions={self.diversity_questions}, " \
               f"contribution_questions={self.contribution_questions})"


@dataclass
class DiversityQuestions(FilteredModel):
    age: str
    under_representation: str
    first_time_presenter: str
    pronouns: str
    gender: str

    @classmethod
    def from_json(cls, whitelist: Sequence, json_content):
        return DiversityQuestions(
            whitelist=whitelist,
            age=to_str(json_content.get("Age", None)),
            under_representation=to_str(json_content.get("Under-representation", None)),
            first_time_presenter=to_str(json_content.get("First time presenter", None)),
            pronouns=to_str(json_content.get("Pronouns", None)),
            gender=to_str(json_content.get("Gender", None)),
        )

    def __repr__(self):
        return f"{self.__class__.__name__}(age='{self.age}', " \
               f"under_representation='{self.under_representation}', " \
               f"first_time_presenter='{self.first_time_presenter}', " \
               f"pronouns='{self.pronouns}', gender='{self.gender}')"


@dataclass
class ContributionQuestions(FilteredModel):
    contribution_type: ClassVar[str]

    def to_json(self):
        result = {}
        for elem in self.whitelist:
            if isinstance(elem, str):
                try:
                    value = self.__getattribute__(elem)
                    if value is not None:
                        result[elem] = value
                except AttributeError:
                    ...
        return result


@dataclass
class TalkContribution(ContributionQuestions):
    length: str
    mentoring: bool
    agreement_streaming: bool
    blog_post: bool
    blog_post_alternative: bool
    contribution_type = "talk"

    @classmethod
    def from_json(cls, whitelist: Sequence, json_content):
        return TalkContribution(
            whitelist=whitelist,
            length=to_str(json_content.get("[TALKS ONLY] Length of talk", None)),
            mentoring=to_bool(json_content.get("[TALKS ONLY] Mentoring", None)),
            agreement_streaming=to_bool(json_content.get("[TALKS ONLY] Streaming", None)),
            blog_post=to_bool(json_content.get("[TALKS ONLY] Blog post", None)),
            blog_post_alternative=to_bool(json_content.get("[TALKS ONLY] Blog post alternative", None)),
        )

    def __repr__(self):
        return f"{self.__class__.__name__}(length='{self.length}', " \
               f"mentoring='{self.mentoring}', " \
               f"agreement_streaming='{self.agreement_streaming}', " \
               f"blog_post='{self.blog_post}', " \
               f"blog_post_alternative='{self.blog_post_alternative}')"


@dataclass
class PanelContribution(ContributionQuestions):
    panelists: str
    advertising: bool
    contribution_type = "panel"

    @classmethod
    def from_json(cls, whitelist: Sequence, json_content):
        return PanelContribution(
            whitelist=whitelist,
            panelists=to_str(json_content.get("[PANELS ONLY] Panelists", None)),
            advertising=to_bool(json_content.get("[PANELS ONLY] Panelist advertising", None)),
        )

    def __repr__(self):
        return f"{self.__class__.__name__}(panelists='{self.panelists}', " \
               f"advertising='{self.advertising}')"


@dataclass
class PosterContribution(ContributionQuestions):
    mentoring: bool
    contribution_type = "poster"

    @classmethod
    def from_json(cls, whitelist: Sequence, json_content):
        return PosterContribution(
            whitelist=whitelist,
            mentoring=to_bool(json_content.get("[POSTERS ONLY] Mentoring", None)),
        )

    def __repr__(self):
        return  f"{self.__class__.__name__}(mentoring='{self.mentoring}')"


@dataclass
class SoftwareContribution(ContributionQuestions):
    installation_instructions: str
    license: str
    contribution_type = "software"

    @classmethod
    def from_json(cls, whitelist: Sequence, json_content):
        return SoftwareContribution(
            whitelist=whitelist,
            installation_instructions=to_str(json_content.get("[SOFTWARE DEMOS ONLY] Installation instructions", None)),
            license=to_str(json_content.get("[SOFTWARE DEMOS ONLY] Software licence", None)),
        )

    def __repr__(self):
        return f"{self.__class__.__name__}(" \
               f"installation_instructions='{self.installation_instructions}', " \
               f"license='{self.license}')"


@dataclass
class WorkshopContriubtion(ContributionQuestions):
    maximum_number_participants: int
    helpers: bool
    delivery: str
    contribution_type = "workshop"

    @classmethod
    def from_json(cls, whitelist: Sequence, json_content):
        return WorkshopContriubtion(
            whitelist=whitelist,
            maximum_number_participants=json_content.get("[WORKSHOPS ONLY] Maximum number of attendees", None),
            helpers=to_bool(json_content.get("[WORKSHOPS ONLY] Helpers", None)),
            delivery=to_str(json_content.get("[WORKSHOPS ONLY] Delivery", None)),
        )

    def __repr__(self):
        return  f"{self.__class__.__name__}(" \
                f"maximum_number_participants='{self.maximum_number_participants}', " \
                f"helpers='{self.helpers}', delivery='{self.delivery}')"


contribution_type_map = {
    "Talk": TalkContribution,
}
