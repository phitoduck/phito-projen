from pathlib import Path
from typing import List
from projen import Component, SampleFile
from phito_projen import PythonPackage

THIS_DIR = Path(__file__).parent
FAST_API_SAMPLE_FILE_TEMPLATES_DIR = (THIS_DIR / "./templates/src").resolve().absolute()


class SampleFastAPIApp(Component):

    project: PythonPackage

    def __init__(self, project: PythonPackage) -> None:
        super().__init__(project)
        print(self.project.outdir)

        self.fastapi_sample_files = self.__make_sample_dir()

    def __make_sample_dir(self):
        template_fpaths = self.__get_sample_file_template_fpaths()
        return [
            SampleFile(
                project=self.project,
                file_path=str(
                    self.project.pkg_dir
                    / path.relative_to(FAST_API_SAMPLE_FILE_TEMPLATES_DIR)
                ),
                contents=path.read_text(),
            )
            for path in template_fpaths
        ]

    def __get_sample_file_template_fpaths(self) -> List[Path]:
        template_fpaths = list(FAST_API_SAMPLE_FILE_TEMPLATES_DIR.rglob("*.py"))
        return template_fpaths
