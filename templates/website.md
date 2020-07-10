---
title: {{ contribution.title }}
{%- if contribution.persons|length > 0 %}
authors:
{%- for person in contribution.persons %}
    - name: {{ person.title }} {{ person.first_name }} {{ person.last_name }}
{%- if person.affiliation %} 
      bio: {{ person.affiliation }} 
{%- endif %}
{%- if person.orcid %}
      orcid: {{ person.orcid }} 
{%- endif %}
{%- endfor %}
{%- endif %}
category: {{ contribution.contribution_type }}
---
{{ contribution.content }}