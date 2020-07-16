import json
import os

import click
import yaml
from dotenv import load_dotenv

from models.contribution import Contribution
from utils import flatten_custom_fields

load_dotenv()


@click.group()
def cli():
    pass


@click.command()
@click.argument('input', type=click.File('rb'))
@click.option('--workflow', type=click.Choice(['scheduling'], case_sensitive=False))
def filter_multiple_data(input, workflow):
    if workflow is None:
        workflow = "scheduling"
    click.echo(f"starting process for {workflow}")
    click.echo(f"saving data to Google Drive")

    workflow_data = load_workflow_data(workflow)
    json_data = json.load(input)
    abstracts = json_data["abstracts"]
    workflow_filter = workflow_data["filter"]
    contributions = []
    for abstract in abstracts:
        abstract["custom_fields"] = flatten_custom_fields(abstract["custom_fields"])
        contribution = Contribution.from_json(
            workflow_data["allow_list"]["contribution"], abstract)
        if check_filter(workflow_filter, contribution=contribution):
            contributions.append(contribution)
    Contribution.to_spreadsheet(template=workflow_data["output_template"], contributions=abstracts)


@click.command()
@click.argument('input', type=click.File('rb'))
@click.argument("output_path", type=click.Path())
@click.option('--workflow', type=click.Choice(['website'], case_sensitive=False))
def filter_data(input, workflow, output_path):
    if workflow is None:
        workflow = "website"
    click.echo(f"starting process for {workflow}")
    click.echo(f"saving data to {output_path}")

    workflow_data = load_workflow_data(workflow)
    json_data = json.load(input)
    abstracts = json_data["abstracts"]
    workflow_filter = workflow_data["filter"]
    assert isinstance(workflow_filter, dict)
    for abstract in abstracts:
        abstract["custom_fields"] = flatten_custom_fields(abstract["custom_fields"])
        contribution = Contribution.from_json(
            workflow_data["allow_list"]["contribution"], abstract)
        if check_filter(workflow_filter, contribution=contribution):
            format_parameters = [
                traverse_into(
                    parameter.split("."),
                    contribution=contribution,
                    output_type=workflow_data["output_type"])
                for parameter in workflow_data["output_format_arguments"]]
            output_file = os.path.join(output_path, workflow_data["output_format_string"].format(*format_parameters))
            # prepare output path
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            with open(output_file, "w") as output:
                output.write(contribution.to_md(template=workflow_data["output_template"]))
                click.echo(f"created file at {output_file}")


def check_filter(filter, **namespace):
    key = next(iter(filter.keys()))
    head = namespace[key]
    for key, value in filter[key].items():
        if isinstance(value, dict):
            head = getattr(head, key)
        else:
            return getattr(head, key) == value
    return False


def traverse_into(name, **namespace):
    head = namespace[name[0]]
    for path in name[1:]:
        head = getattr(head, path)
    return head


def load_workflow_data(workflow):
    with open("workflows.yaml", "r") as stream:
        config_data = yaml.safe_load(stream)
    return config_data.get(workflow)


cli.add_command(filter_data)
cli.add_command(filter_multiple_data)


if __name__ == "__main__":
    cli()
