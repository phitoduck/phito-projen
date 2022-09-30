"""Provide utility methods for use throughout the application."""
from pathlib import Path


def get_project_base() -> Path:
    """Return a path object pointing to the project base."""
    cur_dir = Path(__file__, encoding="utf-8")
    base = cur_dir.parent.parent.parent.absolute()
    return base


def get_fully_qualified_path(relative_path: str) -> Path:
    """Get the fully qualified path by post-pending the relative path to the base path."""
    return Path(get_project_base(), relative_path)


def get_project_version() -> str:
    """Pull the version info from version.txt."""
    return get_fully_qualified_path("version.txt").read_text(encoding="utf-8").strip()[1:]
