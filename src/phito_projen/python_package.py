from copy import deepcopy
from functools import cached_property
from pathlib import Path
from textwrap import dedent
from typing import Any, Dict, List, Optional, Type
from projen import DependencyType, Project
from phito_projen.components.manifest_in import ManifestIn
from phito_projen.components.pyproject_toml import PyprojectToml
from phito_projen.components.lazy_sample_file import LazySampleFile
from phito_projen.components.setup_py import SetupPy
from projen import TextFile
import re
from phito_projen.components.setup_cfg.setup_cfg import SetupCfg

TStrDict = Dict[str, Any]
TPythonExtras = Dict[str, List[str]]

PYTHON_PROJECT_NAME_REGEX = re.compile(r"^[A-Za-z0-9-_\.]+$")

DEFAULT_EXTRAS_REQUIRE = {
    "test": ["pytest", "pytest-cov", "pytest-xdist"],
}


class PythonPackage(Project):
    def __init__(
        self,
        *,
        name: str,
        module_name: str,
        version: str,
        install_requires: Optional[List[str]] = None,
        additional_extras_require: Optional[TPythonExtras] = None,
        entrypoints: Optional[Dict[str, str]] = None,
        outdir: Optional[str] = None,
        parent: Optional["Project"] = None,
    ) -> None:
        """
        :param module_name: Name of the python package as used in imports and filenames. \
            Must only consist of alphanumeric characters and underscores.
        :param version: semantic version of the package; will be the version in PyPI
        :param install_requires: List of runtime dependencies for this project. \
            Dependencies may use the format: ``<module>@<semver>`` or standard ``pip`` format, e.g. ``pandas>=1, <2`` \
            Additional dependencies can be added via ``project.add_dependency()``.
        :param name: This is the name of your project. Default: $BASEDIR
        :param outdir: The root directory of the project. Relative to this directory, all files are synthesized. If this project has a parent, this directory is relative to the parent directory and it cannot be the same as the parent or any of it's other sub-projects. Default: "."
        :param parent: The parent project, if this project is part of a bigger project.
        """
        super().__init__(
            name=name,
            commit_generated=True,
            logging=None,
            outdir=name if parent and not outdir else outdir,
            parent=parent,
            projen_command=None,
            projenrc_json=None,
            projenrc_json_options=None,
            renovatebot=None,
            renovatebot_options=None,
        )

        validate_python_module_name(module_name)
        self.module_name = module_name
        self.pkg_dir = Path(f"src/{module_name}")

        self.install_requires = install_requires or []
        self.extras_require = union_extras_dicts(
            DEFAULT_EXTRAS_REQUIRE, additional_extras_require or {}
        )

        self.init_py = LazySampleFile(
            self,
            file_path=str(self.pkg_dir / "__init__.py"),
            get_contents_fn=lambda: f'"""Modules for {name}."""\n',
        )
        self.pyproject_toml = PyprojectToml(self, file_path="pyproject.toml")
        self.setup_cfg = SetupCfg(
            self,
            file_path="setup.cfg",
            package_name=name,
            package_version=version,
            extras_require=self.extras_require,
            entrypoints=entrypoints,
            # TODO: have a more elegant way to keep setup_cfg.install_requires up to date with the package install requires
            install_requires=self.install_requires,
        )
        self.setup_py = SetupPy(self)
        self.gitignore.add_patterns("*.env", "*venv", "*.venv", "*pyc*", "dist", "build", "*.whl", "*egg-info")

    @cached_property
    def manifest_in(self) -> ManifestIn:
        """
        Include a ``MANIFEST.in`` for keeping non-code files in the final package.
        
        Use this if you want to include images, templates, binaries, or other assets
        in the ``pip``-installable version of your package.
        """
        return ManifestIn(self)

    # NOTE: pre_synthesize can change state of components, but it should not add or remove components
    # I'm not sure what the behavior would be if you did that
    def pre_synthesize(self) -> None:
        # ultimately, all dependencies go in the shared Dependencies instance
        [
            self.deps.add_dependency(spec=dep, type=DependencyType.RUNTIME)
            for dep in self.install_requires
        ]
        [
            self.deps.add_dependency(spec=dep, type=DependencyType.DEVENV)
            for dep in flatten_extras(self.extras_require)
        ]
        return super().pre_synthesize()


class InvalidPythonModuleNameError(Exception):
    """Raise when an invalid module name is thrown."""

    @staticmethod
    def make_err_msg(invalid_module_name: str) -> str:
        return f"'{invalid_module_name}' is not a valid Python module_name. Must satisfy regex: '{PYTHON_PROJECT_NAME_REGEX}'"

    @classmethod
    def from_invalid_module_name(
        cls: Type["InvalidPythonModuleNameError"], invalid_module_name: str
    ) -> Type["InvalidPythonModuleNameError"]:
        return cls(
            InvalidPythonModuleNameError.make_err_msg(
                invalid_module_name=invalid_module_name
            )
        )


def validate_python_module_name(module_name: str):
    is_exact_match = bool(
        re.fullmatch(pattern=PYTHON_PROJECT_NAME_REGEX, string=module_name)
    )
    if not is_exact_match:
        raise InvalidPythonModuleNameError.from_invalid_module_name(module_name)


def union_extras_dicts(
    extras_a: TPythonExtras, extras_b: TPythonExtras
) -> TPythonExtras:
    result = deepcopy(extras_a)
    for extra_name, reqs in extras_b.items():
        if extra_name in extras_a.keys():
            reqs_a = set(extras_a[extra_name])
            reqs_b = set(reqs)
            result[extra_name] = list(reqs_a | reqs_b)
            continue
        result[extra_name] = reqs
    return result


def flatten_extras(extras: TPythonExtras) -> List[str]:
    return [item for sublist in list(extras.values()) for item in sublist]


if __name__ == "__main__":
    # validate_python_module_name("eric_pkg_ftw")
    # validate_python_module_name("totally tubular-man")

    print(flatten_extras({"1": [2, 3], "a": ["b", "c"]}))
