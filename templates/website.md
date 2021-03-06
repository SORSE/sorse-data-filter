---
title: "{{ contribution.title }}"
{%- if contribution.persons|length > 0 %}
authors:
{%- set ns = namespace(speaker=false) -%}
{%- set ns.speaker = None -%}
{%- for person in contribution.persons %}
{%- if ns.speaker is none and person.is_speaker %}
{%- set ns.speaker = person %}
    - &speaker
      name: {{ (person.title | titlefilter + " " + person.first_name + " " + person.last_name) | trim }}
{%- else %}
    - name: {{ (person.title | titlefilter + " " + person.first_name + " " + person.last_name) | trim }}
{%- endif %}
{%- if person.email %}
      email: {{ person.email }}
{%- endif %}
{%- if person.orcid %}
      orcid: {{ person.orcid }} 
{%- endif %}
{%- if person.is_speaker %}
      is_speaker: true
{%- endif %}
{%- if person.affiliation_id is not none %}
      affiliation: {{ person.affiliation_id + 1 }}
{%- endif %}
{%- endfor %}
{%- if contribution.affiliations|length > 0 %}
affiliations:
{%- for affiliation in contribution.affiliations %}
    - name: {{ affiliation.name }}
      index: {{ loop.index }}
{%- endfor %}
{%- endif %}
author: *speaker
{%- endif %}
category: {{ contribution.contribution_type }}
{%- if contribution.questionnaire.language %}
language: {{ contribution.questionnaire.language }}
{%- endif %}
{%- if contribution.questionnaire.prerequisite_knowledge %}
prerequisites: "{{ contribution.questionnaire.prerequisite_knowledge | extendlinks }}"
{%- endif %}
{%- if contribution.questionnaire.contribution_questions.license %}
license: {{ contribution.questionnaire.contribution_questions.license }}
{%- endif %}
{%- if contribution.questionnaire.contribution_questions.installation_instructions %}
instructions: "{{ contribution.questionnaire.contribution_questions.installation_instructions | extendlinks }}"
{%- endif %}
{%- if contribution.questionnaire.contribution_questions.panelists %}
panelists: {{ contribution.questionnaire.contribution_questions.panelists }}
{%- endif %}
date: {{ meta.current_date | datetimeformat("%Y-%m-%d") }}
---
{{ contribution.content }}

