from pathlib import Path
from typing import Union
from projen import Component, TomlFile, Project, JsonPatch

# docutils is needed if the long_description_... is an rst file (README.rst instead of README.md)
DEFAULT_PYPROJECT_TOML_OBJ = {
    "build-system": {
        "requires": ["setuptools>=46.1.0", "wheel", "build", "docutils"],
        # "build-backend": "setuptools.build-meta",
    }
}


class PyprojectToml(Component):
    def __init__(
        self,
        project: "Project",
        file_path: Union[str, Path] = "pyproject.toml",
    ) -> None:
        super().__init__(project)
        self.toml_file = TomlFile(project=self.project, file_path=str(file_path))
        self.toml_file.patch(JsonPatch.add(path="", value=DEFAULT_PYPROJECT_TOML_OBJ))
