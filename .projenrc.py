from phito_projen import PythonPackage

project = PythonPackage(
    name="phitoduck-projen",
    module_name="phito_projen",
    install_requires=["projen", "jinja2"]
)

project.synth()