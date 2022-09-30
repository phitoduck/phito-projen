from phito_projen.components.templatized_file import TemplatizedFile
from projen import Component
from projen import Project

SETUP_PY_TEMPLATE_BODY = """\
from setuptools import setup

setup()
"""


class SetupPy(Component):
    def __init__(self, project: "Project") -> None:
        super().__init__(project)

        self.setup_py_file = TemplatizedFile(
            project=project,
            file_path="setup.py",
            is_sample=False,
            template_body=SETUP_PY_TEMPLATE_BODY,
            initial_values={},
        )
