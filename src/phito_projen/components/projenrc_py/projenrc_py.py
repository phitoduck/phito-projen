from pathlib import Path
from typing import List, Optional, Union
from phito_projen.components.templatized_file import TemplatizedFile
from projen import Component
from projen import Project

from phito_projen.python_package import TPythonExtras

THIS_DIR = Path(__file__).parent
PROJENRC_PY_TEMPLATE_FPATH = (
    THIS_DIR / "./templates/.projenrc.template.py.jinja"
).resolve()


class ProjenrcPy(Component):
    def __init__(
        self,
        project: "Project",
        package_name: str,
        module_name: str,
        package_version: str,
        install_requires: Optional[List[str]] = None,
        additional_extras_require: Optional[TPythonExtras] = None,
        file_path: Union[str, Path] = ".projenrc.py",
    ) -> None:
        super().__init__(project)
        self.file_path = Path(file_path)

        self.install_requires = install_requires
        self.package_name = package_name
        self.package_version = package_version
        self.additional_extras_require = additional_extras_require
        self.module_name = module_name

        self.setup_cfg_file = TemplatizedFile(
            project=project,
            file_path=file_path,
            is_sample=True,
            template_body=PROJENRC_PY_TEMPLATE_FPATH.read_text(),
            supports_comments=True,
            make_comment_fn=lambda line: f"# {line}",
            get_values_fn=lambda: {
                "install_requires": self.install_requires,
                "package_name": self.package_name,
                "package_version": self.package_version,
                "additional_extras_require": self.additional_extras_require,
                "module_name": self.module_name,
            },
        )
