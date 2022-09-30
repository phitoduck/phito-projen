from pathlib import Path
from typing import Union
from projen import IniFile, Component, Project


class PylintRc(Component):
    def __init__(
        self, project: "Project", file_path: Union[str, Path] = ".pylintrc"
    ) -> None:
        super().__init__(project)
        self.ini_file = IniFile(project=self.project, file_path=str(file_path))
