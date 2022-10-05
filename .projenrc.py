from phito_projen import PythonPackage
from phito_projen.components.projenrc_py.projenrc_py import ProjenrcPy

project = PythonPackage(
    name="phitoduck-projen",
    module_name="phito_projen",
    install_requires=["projen", "jinja2"],
    version="0.0.2",
)
project.manifest_in.add_recursive_include("src/", "*template*", comment="include template files for rendering components")

project.synth()