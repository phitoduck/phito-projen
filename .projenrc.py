from projen.python import PythonProject

project = PythonProject(
    author_email="eric.riddoch@bengroup.com",
    author_name="Eric Riddoch",
    module_name="projen_python",
    name="projen-python",
    version="0.1.0",
)

project.synth()