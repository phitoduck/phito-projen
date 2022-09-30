from abc import ABC, abstractmethod
from pathlib import Path
from typing import Union
from projen import Component, Project, TextFile


class CommentableObjectFile(Component, ABC):
    def __init__(self, project: Project, file_path: Union[str, Path]):
        super().__init__(project)
        self.__file = TextFile(self, file_path=str(file_path))

    def pre_synthesize(self):
        """Add all lines to the final text file."""
        contents: str = self.synthesize_contents()
        lines = contents.splitlines()
        projen_marker_comment: str = self.make_single_line_comment(self.__file.marker)

        self.__file.add_line(projen_marker_comment)
        self.__file.add_line("")
        for line in lines:
            self.__file.add_line(line)

    @abstractmethod
    def synthesize_contents(self) -> str:
        """Generate the final contents of the object file."""
        ...

    @abstractmethod
    def set_header_comment(self, comment: str):
        """Set a comment at the beginning of the file."""
        ...

    @abstractmethod
    def set_comment_before_key_at_path(self, path: str, comment: str):
        """Set a comment just before a key or list item in the object."""
        ...

    @abstractmethod
    def set_eol_comment_at_path(self, path: str, comment: str):
        """Set a end-of-line comment in-line after the key or list item at the path."""
        ...

    @abstractmethod
    def make_single_line_comment(comment: str) -> str:
        """
        Return a commented out version of ``comment``.

        For example,

        YAML:        ``hi there`` -> ``# hi there``
        JavaScript:  ``hi there`` -> ``// hi there``

        .. code-block:: yaml

            hi: there

        Yes no?
        """
        ...
