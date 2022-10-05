from pathlib import Path
from typing import Dict, List, Optional, Union
from phito_projen.components.templatized_file import TemplatizedFile
from projen import Component
from projen import Project

THIS_DIR = Path(__file__).parent
SETUP_CFG_TEMPLATE_FPATH = (
    THIS_DIR / "./templates/setup.template.cfg.jinja"
).resolve()


class SetupCfg(Component):
    def __init__(
        self,
        project: "Project",
        install_requires: List[str],
        package_name: str,
        package_version: str,
        extras_require: Optional[Dict[str, List[str]]] = None,
        entrypoints: Optional[Dict[str, str]] = None,
        file_path: Union[str, Path] = "setup.cfg",
    ) -> None:
        super().__init__(project)
        self.file_path = Path(file_path)

        self.extras_require = extras_require or {}
        self.entrypoints = entrypoints or {}
        self.install_requires = install_requires
        self.package_name = package_name
        self.package_version = package_version

        self.setup_cfg_file = TemplatizedFile(
            project=project,
            file_path=file_path,
            is_sample=False,
            template_body=SETUP_CFG_TEMPLATE_FPATH.read_text(),
            get_values_fn=lambda: {
                "name": self.package_name,
                "install_requires": self.install_requires,
                "version": self.package_version,
                "extras_require": self.extras_require,
                "entrypoints": self.entrypoints,
            },
            supports_comments=True,
            make_comment_fn=lambda line: f"# {line}",
        )
