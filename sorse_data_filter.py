import json
import os

import click
import yaml
from dotenv import load_dotenv

from models.contribution import Contribution
from utils import flatten_custom_fields

load_dotenv()


@click.command()
@click.argument('input', type=click.File('rb'))
@click.argument("output_path", type=click.Path())
@click.option('--workflow', type=click.Choice(['website'], case_sensitive=False))
def filter_data(input, workflow, output_path):
    click.echo(f"starting process for {workflow}")
    click.echo(f"saving data to {output_path}")
    if workflow is None:
        workflow = "website"

    workflow_data = None
    with open("workflows.yaml", "r") as stream:
        config_data = yaml.safe_load(stream)
        workflow_data = config_data.get(workflow)
    json_data = json.load(input)
    abstracts = json_data["abstracts"]
    for abstract in abstracts:
        abstract["custom_fields"] = flatten_custom_fields(abstract["custom_fields"])
        contribution = Contribution.from_json(
            workflow_data["whitelist"]["contribution"], abstract)
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


def traverse_into(name, **namespace):
    head = namespace[name[0]]
    for path in name[1:]:
        head = getattr(head, path)
    return head


if __name__ == "__main__":
    filter_data()
