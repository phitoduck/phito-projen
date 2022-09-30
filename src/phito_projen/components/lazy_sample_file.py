from pathlib import Path
from typing import Callable, Optional, Union
from projen import Component, Project

TGetContentsFn = Callable[[], str]
"""A function that will be called during synthesis of a component to get the contents that will be written to the file."""


class LazySampleFile(Component):
    """
    A file that is not tamper-proof.

    This class differs from ``projen.SampleFile`` in that the contents are derived "lazily".
    This is to say, the actual contents of a ``LazySampleFile`` are not decided until
    ``synthesize()`` is called. ``synthesize()`` will execute the provided
    ``get_contents_fn()`` to decide the contents.

    See ``TemplatizedSampleFile`` for an example of why the ability to defer
    the deciding of file contents is useful.

    Sample files are typically meant to

    1. save developers from writing boilerplate
    2. suggest a certain set of practices; for example, you might use sample files
       to structure a FastAPI application in a particular way

    Since sample files are not tamper-proof, they have these two properties:

    1. developers can completely disregard any suggestions within
    2. updates to a library of sample files made by a platform team will not
       automatically propagate to projects that were initialized with an
       older set of sample files; in this case, developers can regenerate
       a newer set of sample files and manually bring any desired changes
       into their existing project if they want certain updates
    """

    def __init__(
        self,
        project: "Project",
        file_path: Union[str, Path],
        get_contents_fn: Optional[TGetContentsFn] = None,
        file_encoding: Optional[str] = None,
    ):
        super().__init__(project)

        self.file_encoding = file_encoding
        self.get_contents_fn = get_contents_fn
        self.file_path: Union[str, Path] = file_path
        """File path relative to ``project.outdir`` where the final sample file will be created."""

    def synthesize(self) -> None:
        """Write the file contents to disk if file is not already present."""
        contents: str = self.get_contents_fn()
        final_fpath = Path(self.project.outdir) / Path(self.file_path)
        write_file_if_not_exists(
            contents=contents, path=final_fpath, encoding=self.file_encoding
        )


def write_file_if_not_exists(path: Path, contents: str, encoding: Optional[str] = None):
    if not path.exists():
        path.parent.mkdir(exist_ok=True, parents=True)
        path.write_text(data=contents, encoding=encoding)
