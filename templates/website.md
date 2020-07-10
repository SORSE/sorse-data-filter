---
title: {{ contribution.title }}
{%- if contribution.persons|length > 0 %}
authors:
{%- for person in contribution.persons %}
    - name: {{ person.title }} {{ person.first_name }} {{ person.last_name }}
{%- if person.affiliation %} 
      bio: {{ person.affiliation }} 
{%- endif %}
{%- if person.email %}
      email: {{ person.email }}
{%- endif %}
{%- if person.orcid %}
      orcid: {{ person.orcid }} 
{%- endif %}
{%- endfor %}
{%- endif %}
category: {{ contribution.contribution_type }}
{%- if contribution.questionnaire.language %}
language: {{ contribution.questionnaire.language }}
{%- endif %}
{%- if contribution.questionnaire.prerequisite_knowledge %}
prerequisites: {{ contribution.questionnaire.prerequisite_knowledge }}
{%- endif %}
{%- if contribution.questionnaire.contribution_questions.license %}
license: {{ contribution.questionnaire.contribution_questions.license }}
{%- endif %}
{%- if contribution.questionnaire.contribution_questions.installation_instructions %}
instructions: contribution.questionnaire.contribution_questions.installation_instructions
{%- endif %}
{%- if contribution.questionnaire.contribution_questions.panelists %}
panelists: {{ contribution.questionnaire.contribution_questions.panelists }}
{%- endif %}
---
{{ contribution.content }}