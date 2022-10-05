from phito_projen import PythonPackage

project = PythonPackage(
    name="phitoduck-projen",
    module_name="phito_projen",
    install_requires=["projen", "jinja2"],
    version="0.1.0",
)
project.manifest_in.add_recursive_include("src/", "*template*", comment="include template files for rendering components")

project.synth()