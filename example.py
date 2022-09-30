from pathlib import Path
from typing import Any, Callable, Dict
from projen import SampleFile, Component, Project
from jinja2 import Template
from textwrap import dedent

TGetValuesFn = Callable[[], Dict[str, Any]]


class TemplatizedSampleFile(SampleFile):
    """Generate a sample file from a Jinja template."""

    def __init__(
        self,
        project: "Project",
        file_path: str | Path,
        template: str,
        initial_values: Dict[str, Any] | None = None,
    ):
        super().__init__(project)
        self.fpath = str(file_path)
        self.values: Dict[str, Any] = initial_values or {}
        self.template = template
        self.file = SampleFile(project=project, file_path=self.fpath, contents=self.render_template)

    def render_template(self) -> str:
        return Template(source=self.template).render(self.values)


monorepo = Project(
    name="parent-project",
)

sample_file = TemplatizedSampleFile(
    project=monorepo,
    file_path="cool-sample-file.txt",
    template="""\
    Hi, I'm a template.

    Your name is {{ name }},
    but *his* name is {{ other_name }}.
    """,
)
sample_file.values["name"] = "murph"
sample_file.values["other_name"] = "diddle"

monorepo.synth()
