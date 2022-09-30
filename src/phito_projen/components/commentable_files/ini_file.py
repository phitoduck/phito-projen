# from ctypes import Union
# from pathlib import Path
# from projen import Project
# from components.commentable_files.object_file import CommentableObjectFile


# class CommentableIniFile(CommentableObjectFile):
#     def __init__(self, project: Project, file_path: Union[str, Path]):
#         super().__init__(project, file_path)

#         self.__doc = ...


if __name__ == "__main__":
    from configupdater import ConfigUpdater
    from configparser import ConfigParser

    cfg_text = """\
    [metadata]
    name = cool-package
    value = brub

    [options.extras.etc]
    install_requires = 
        package-1
        package-2>=1.0.0, <2.0.0
    """

    updater = ConfigUpdater()
    cfg = updater.read_string(cfg_text)

    data = {
        "metadata": {
            "name": "cool-package",
            "value": "eric",
        },
        "options.extras.etc": {
            "install_requires": [
                "package-1",
                "package-2>=1.0.0, <2.0.0",
                "package-2>=1.0.0, <2.0.0",
                "package-2>=1.0.0, <2.0.0",
                "package-2>=1.0.0, <2.0.0",
                "package-2>=1.0.0, <2.0.0",
                "package-2>=1.0.0, <2.0.0",
                "package-2>=1.0.0, <2.0.0",
                "package-2>=1.0.0, <2.0.0",
                "package-2>=1.0.0, <2.0.0",
                "package-2>=1.0.0, <2.0.0",
                "package-2>=1.0.0, <2.0.0",
                "package-2>=1.0.0, <2.0.0",
                "package-2>=1.0.0, <2.0.0",
                "package-2>=1.0.0, <2.0.0",
                "package-2>=1.0.0, <2.0.0",
                "package-2>=1.0.0, <2.0.0",
            ]
        },
    }

    # b = benedict(
    #     data,
    #     format="ini",
    #     keypath_separator="/",
    # )

    # cfg = updater.read_string(b.to_toml())
    # cfg["options.extras.etc"].add_before.comment("section")

    # cfg["options.extras.etc"]["install_requires"].add_before.comment("key")

    # cfg["options.extras.etc"][
    #     "install_requires"
    # .  #.set_values(values=["1", "2", "3"])
    cfg = ConfigParser()
    cfg.read_string(cfg_text)
    cfg.add_section("sec")
    # cfg["sec"]["yolo.my.bro"] = str(["impart", "wisdom", "on", "the", "bro"])

    from io import StringIO

    s = StringIO()
    cfg.write(fp=s)
    out = s.getvalue()
    print(out)
