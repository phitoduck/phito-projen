from projen import Project
from python_package import PythonPackage
from samples.fastapi_app.sample import SampleFastAPIApp

repo = Project(name="demo-project", outdir="demo-project")

pkg = PythonPackage(
    parent=repo,
    name="example-python-package",
    module_name="example_pkg",
    install_requires=["pandas", "new-dependency"],
    additional_extras_require={"test": ["pytest"]},
)

pkg_2 = PythonPackage(
    parent=repo,
    name="another_example-python-package",
    module_name="example_pkg_2",
    install_requires=["pandas", "new-dependency"],
    additional_extras_require={"test": ["pytest"]},
)

SampleFastAPIApp(project=pkg)

repo.synth()
