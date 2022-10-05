from pathlib import Path
from typing import Optional, Union
from projen import Component, TextFile, Project, JsonPatch

class ManifestIn(Component):
    def __init__(
        self,
        project: "Project",
        file_path: Union[str, Path] = "MANIFEST.in",
    ) -> None:
        """
        Generate a ``MANIFEST.in`` file.

        A common frustration when beginners try to create python packages is that
        their non-code files seem to disappear when users go to ``pip install ...``
        their package.

        Assets, resources, binaries, etc. that your code relies upon to run
        do not end up in the zipped version of your package by default. 
        
        For example, this project makes use of many ``*.template.*`` files that are rendered
        using templating engines such as Jinja. These are not code files, but their presence
        is essential for the python ``projen.Component``s that wrap them.

        You must explicitly configure your project to include the assets you wish to include.
        This is done by including a ``MANIFEST.in`` file to the root of your package.

        A ``MANIFEST.in`` file uses directives like

        .. code-block:: text

            include path/to/some-file.txt src/module_name/some-file.json
            recursive-include some-dir/ *.json
            recursive-exclude *__pycache__ *

        A full list of all ``MANIFEST.in`` commands can be found here:
        https://packaging.python.org/en/latest/guides/using-manifest-in/#manifest-in-commands
        """
        super().__init__(project)
        self.__file = TextFile(project=self.project, file_path=str(file_path))
        _add_projen_marker_comment(text_file=self.__file)


    def add_recursive_include(self, dir_glob_pattern: str, *file_glob_patterns: str, comment: Optional[str] = None):
        if comment:
            self.__file.add_line(_make_comment(comment))
        self.__file.add_line(f"recursive-include {dir_glob_pattern} {' '.join(file_glob_patterns)}")

def _add_projen_marker_comment(text_file: TextFile):
    text_file.add_line(_make_comment(text_file.marker))
    text_file.add_line("")

def _make_comment(comment: str) -> str:
    comment_text = comment.strip("#").strip()
    return f"# {comment_text}"
    