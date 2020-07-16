# sorse-data-filter

This project manages the visibility of data and automatises several
workflows centred around the abstract submission process of [SORSE – A Series of
Online Research Softare Events](http://sorse.github.io). It is our aim to ensure
that no connection between personal data and diversity information can be derived
from data exported from the [Indico](https://getindico.io) event management platform.

Input of the tool is the exported data from the [Indico](https://getindico.io) system.
Via a command line interface a user can pick one of the available workflows. For each
workflow, allowed fields from the import data is specified along with the output format
that is required.

The tool currently supports the following automatised workflows:

* ``website``: export of Markdown-formatted data after acceptance to the website

Further workflows are planned including:

* ``mentoring``: export of data to a google drive to support the mentoring process
* ``scheduling``: export of data to a google drive to support the scheduling process
* ``statistics``: export of statistical data to a google drive

# Configuring workflows

The export of data is centred around the concepts of allowing specific data fields
and providing formatting with the help of the templating engine
[Jinja2](https://jinja.palletsprojects.com/en/2.11.x/).

## Configuring allowed fields

Allowed fields within a workflow are specified in the
[workflows.yaml file](workflows.yaml). For each workflow an entry is created that
holds a section for ``allow_lists``. The entries in this field follow the model
specified in [models](models) and include the ``contribution`` itself, ``person``s
and ``questionnaire``s holding specific information for each contribution type
as well as diversity information.

## Configuring templates

Templates that can be used are contained in the [templates folder](templates).
For example the template for the website workflow is [templates/website.md](templates/website.md).
Available templating constructs can be found in the documentation of Jinja2. In
principle, all different file formats can be configured with this templating engine.

The name of a template for a given workflow is given via the field
``output_template`` in the [configuration file](workflows.yaml).
