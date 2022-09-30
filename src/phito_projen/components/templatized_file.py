from pathlib import Path
from typing import Any, Callable, Dict, Optional, Text, Union
from projen import Component, Project, TextFile, SampleFile
from phito_projen.components.lazy_sample_file import LazySampleFile
from jinja2 import Template

TGetValuesFn = Callable[[], Dict[str, Any]]
TMakeCommentFn = Callable[[str], str]


class TemplatizedFile(Component):
    def __init__(
        self,
        project: "Project",
        file_path: Union[str, Path],
        template_body: Optional[str] = None,
        template_fpath: Optional[Path] = None,
        initial_values: Optional[Dict[str, Any]] = None,
        get_values_fn: Optional[TGetValuesFn] = None,
        is_sample: bool = False,
        supports_comments: bool = False,
        make_comment_fn: Optional[TMakeCommentFn] = None,
    ) -> None:
        super().__init__(project)

        if template_body and template_fpath:
            raise ValueError(
                "Parameters 'template_string' and 'template_fpath' cannot both be set."
            )

        if initial_values is not None and get_values_fn:
            raise ValueError(
                "Parameters 'initial_values' and 'get_values_fn' cannot both be set."
            )

        self.file_path = file_path
        self.template_body = template_body
        self.template_fpath = template_fpath
        self.values = initial_values or {}
        self.get_values_fn = get_values_fn
        self.supports_comments = supports_comments
        self.make_comment_fn = make_comment_fn

        if is_sample:
            self.__file = LazySampleFile(
                project=self.project,
                file_path=file_path,
                get_contents_fn=self.__render_template,
            )
        else:
            self.__file = TextFile(
                project=project, file_path=file_path, lines=[], marker=True
            )

    def __render_template(self) -> str:
        template_body: str = self.template_body or self.template_fpath.read_text()
        template: Template = Template(source=template_body)
        values: Dict[str, Any] = (
            self.get_values_fn() if self.get_values_fn else self.values
        )
        return template.render(values)

    def pre_synthesize(self) -> None:
        if isinstance(self.__file, TextFile):
            contents: str = self.__render_template()
            if self.supports_comments:
                marker_comment = self.make_comment_fn(self.__file.marker)
                self.__file.add_line(marker_comment)
            [self.__file.add_line(line) for line in contents.splitlines()]
