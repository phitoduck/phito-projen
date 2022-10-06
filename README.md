# 📣 Welcome to `phito-projen`!

------------

> ⚠️ Warning
>
> This library is in rapid development. Expect breaking API changes.

A library of Python-based `projen` components that can be used in `.projenrc.py`.

## Philosophies

This project is working to implement the ideas proposed in [this RFC](https://github.com/phitoduck/project-generator-cli-poc).

For convenience, here are the philosophies laid out in the RFC:

- #TemplatesAreEvil 
    - Templates get stale over time
    - A process should exist so that projects are always up to date
- ... but they are helpful:
    - In the overwhelming space of Python software development, starting from an opinionated framework helps learn best practices with minimal cognitive load.
- ... but they often lack desirable features, outside the scope of generating code:
    - Writing/releasing production-worthy code requires infrastructure (i.e. GitHub account/repo). These
    tools also have a non-trivial learning curve that should be automated where possible.
- Automation eliminates avoidable errors caused by manual steps
- The average use should not have to learn the entire Python ecosystem--thanks to abstractions.
- The advanced user should be able to extend the abstractions; you should not need to "grow out" of the tool.
- Where possible, we should avoid rebuilding what has already been built/standardized on by the community.
- The iteration cycle should be fast:
    - developers should be able to run builds locally
    - processes that can be run in parallel should be run in parallel (both locally and in CI)
- Released software and docs should be immutable. Once package `v0.0.0` is out there,
  consumers of the software should be able to rely on the fact that it won't disappear and that the behavior
  won't change.
- The tool should be built with both open- and closed-source development in mind.
- The trunk-based development branching model should have first-class support.
- Multi-project repositories (mono-repos) have a place in modern software development, and should be supported to an extent (e.g. `frontend` and `backend` projects, or `src` and `iac` might reside in one repository)
    - ... but the framework should encourage developers to modularize projects in separate repos as much as possible

## Quick start

1. `pip install phitoduck-projen`
2. Create and execute a `.projenrc.py`

### Example: Single-package Repository

```python
# .projenrc.py

from phito_projen import PythonPackage

package = PythonPackage(
    name="phitoduck-projen",
    module_name="phitoduck_projen",
    install_requires=["projen", "jinja2"],
    version="0.1.0",
)
package.manifest_in.add_recursive_include("src/", "*template*", comment="include template files for rendering components")

package.synth()
```

Running `python .projenrc.py` will yield a nicely organized Python project structured like this:

```text
phitoduck-projen/
├── README.md
├── pyproject.toml
├── setup.cfg
├── setup.py
├── MANIFEST.in
└── src/
```

In this case, the `setup.cfg`, `setup.py` and `pyproject.toml` files are set to be read-only.
This is because these config files are meant to be an implementation detail, created by
the `PythonPackage` abstraction.

These read-only files can be modified by calling methods on the `PythonPackage` instance,
or changing the parameters passed in. Calling `python .projenrc.py` again will re-generate
the latest `setup.cfg`, `setup.py` and `pyproject.toml` to reflect the changes.

Future (or alternative) versions of `PythonPackage` might use an entirely different package
build system altogether. For example, we could generate only a `pyproject.toml` for use with `poetry` 
for example, or a `Pipfile`, etc., and keep the build/release process the same.

This is where the power of projen for platform teams comes in!

Because developers can only modify the package via the `PythonPackage` API, we the platform team
can freely swap out the implementation of `PythonPackage` so long as we don't break existing
functionality.

### Example: Sample FastAPI Project

`projen` has a concept of "sample files" and "sample folders". These are files and folders
that are created only if not present.

`phitoduck-projen` provides a number of sample apps (and other components) that
can be used to create boiler projects with best practices. Here, we create
a Python package containing a sample FastAPI app.

```python
# .projenrc.py

from python_package import PythonPackage
from samples.fastapi_app import SampleFastAPIApp

package = PythonPackage(
    name="phitoduck-projen",
    module_name="example_pkg",
    install_requires=["projen", "jinja2"],
    version="0.1.0",
)

SampleFastAPIApp(project=package)

package.synth()
```

Now, running `python .projenrc.py` would yield something like this:

```text
phitoduck-projen
├── pyproject.toml
├── setup.cfg
├── setup.py
└── src
    └── example_pkg
        ├── __init__.py
        ├── config.py
        ├── default_constants.py
        ├── errors.py
        ├── main.py
        ├── types.py
        ├── utilities.py
        └── web/
```

### Example: Multi-package Repository

You may have a use case that requires having multiple Python packages in a single repository.
`projen` makes this easy:

```python
# .projenrc.py

from projen import Project
from phito_projen.python_package import PythonPackage
from phito_projen.samples.fastapi_app import SampleFastAPIApp

repo = Project(name="demo-project", outdir="demo-project")

pkg = PythonPackage(
    parent=repo,
    name="example-python-package",
    module_name="example_pkg",
    install_requires=["pandas", "new-dependency"],
    additional_extras_require={"test": ["pytest"]},
    version="0.0.0",
)

pkg_2 = PythonPackage(
    parent=repo,
    name="another_example-python-package",
    module_name="example_pkg_2",
    install_requires=["pandas", "new-dependency"],
    additional_extras_require={"test": ["pytest"]},
    version="0.0.0",
)

SampleFastAPIApp(project=pkg)

repo.synth()
```

Running `python .projenrc.py` will yield this:

```text
demo-project/
├── another_example-python-package
│   ├── pyproject.toml
│   ├── setup.cfg
│   ├── setup.py
│   └── src/  # sample FastAPI files would be in here
└── example-python-package
    ├── pyproject.toml
    ├── setup.cfg
    ├── setup.py
    └── src/
```

Ta-da! 🎉

## Roadmap

- [ ] Reduce barrier to adoption by writing a CLI wizard that generates and invokes a `.projenrc.py`.
- [ ] Create an abstract `CommentableObjectFile` base from which `YamlFile`, `IniFile`, `TomlFile` and `JsoncFile` derive.
  These will support escape hatches like `projen`'s `ObjectFile`, but will allow for comments as well.
- [ ] Add a `SampleSphinx` (or simply a `Sphinx`) component that can generate docs for multi-package repos.
- [ ] Add a way to orchestrate builds and releases for multi-package repos.
  - [ ] Make these build efficient by parallelizing anything than can be, and skipping any tasks
    if their "input files" have not changed.
- [ ] Use `projen`'s task runner system or write our own to provide a `Makefile`, `Justfile`, or other
  task runner with useful commands for the project and any component add-ons.
- [ ] Add more samples for items like Metaflow training DAGs with MLFlow, BentoML services, CLI tools with Typer, 
  infrastructure as code with AWS CDK/Pulumi etc.
- [ ] Add components for the `pre-commit` framework
- [ ] Add components for config files for code QA tools like `pylint`, `flake8`, `pytest`, `black`, etc.
  - [ ] Add a component for `.vscode/settings.json` that promps you to fix errors from these tools as you code, rather than having to wait to run a linting task.
- [ ] Investigate `commitizen` as a way of automatically bumping package versions and generating changelogs.
