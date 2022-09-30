from __future__ import annotations

from typing import Any, List, Optional
from pydantic import BaseModel


class PreCommitConfig(BaseModel):
    repos: List[Repo]
    """:param repos2: A list of repository mappings."""
    default_install_hook_types: Any = None
    """(optional: default [pre-commit]) a list of `--hook-types` which will be used by default when running pre-commit install."""
    default_language_version: Any = None
    """
    (optional: default {}) a mapping from language to the default language_version 
    that should be used for that language. 
    This will only override individual hooks that do not set language_version.
    
    For example to use python3.7 for language: python hooks:

    ```yaml
    default_language_version:
        python: python3.7
    ```
    """
    default_stages: Any = None
    """
    (optional: default (all stages)) a configuration-wide default for the stages property of hooks. This will only override individual hooks that do not set stages. For example:

    ```yaml
    default_stages: [commit, push]
    ```
    """
    files: Any = None
    """(optional: default '') global file include pattern. new in 1.21.0."""
    exclude: Any = None
    """(optional: default ^$) global file exclude pattern. new in 1.1.0."""
    fail_fast: Any = None
    """(optional: default false) set to true to have pre-commit stop running hooks after the first failure. new in 1.1.0."""
    minimum_pre_commit_version: Any = None
    """(optional: default '0') require a minimum version of pre-commit. new in 1.15.0."""


class Repo(BaseModel):
    """
    The repository mapping tells pre-commit where to get the code for the hook from.

    A sample repository:

    ```yaml
    repos:
    -   repo: https://github.com/pre-commit/pre-commit-hooks
        rev: v1.2.3
        hooks:
        -   ...
    ```
    """

    repo: str
    """the repository url to git clone from"""
    rev: str
    """the revision or tag to clone at. new in 1.7.0: previously sha"""
    hooks: List[Hook]
    """A list of hook mappings."""


class Hook(BaseModel):

    id: str
    """which hook from the repository to use."""
    alias: Optional[str] = None
    """(Optional) allows the hook to be referenced using an additional id when using pre-commit run <hookid>. new in 1.14.0."""
    name: Optional[str] = None
    """(Optional) override the name of the hook - shown during hook execution."""
    language_version: Optional[str] = None
    """(Optional) override the language version for the hook. See Overriding Language Version."""
    files: Optional[str] = None
    """(Optional) override the default pattern for files to run on."""
    exclude: Optional[str] = None
    """(Optional) file exclude pattern."""
    types: Optional[str] = None
    """(Optional) override the default file types to run on (AND). See Filtering files with types."""
    types_or: Optional[str] = None
    """(Optional) override the default file types to run on (OR). See Filtering files with types. new in 2.9.0."""
    exclude_types: Optional[str] = None
    """(Optional) file types to exclude."""
    args: Optional[List[str]] = None
    """(Optional) list of additional parameters to pass to the hook."""
    stages: Optional[str] = None
    """(Optional) confines the hook to the commit, merge-commit, push, prepare-commit-msg, commit-msg, post-checkout, post-commit, post-merge, post-rewrite, or manual stage. See Confining hooks to run at certain stages."""
    additional_dependencies: Optional[List[str]] = None
    """(Optional) a list of dependencies that will be installed in the environment where this hook gets run. One useful application is to install plugins for hooks such as eslint."""
    always_run: Optional[bool] = False
    """(Optional) if true, this hook will run even if there are no matching files."""
    verbose: Optional[bool] = False
    """(Optional) if true, forces the output of the hook to be printed even when the hook passes. new in 1.6.0."""
    log_file: Optional[str] = None
    """(Optional) if present, the hook output will additionally be written to a file when the hook fails or verbose is true."""


PreCommitConfig.update_forward_refs()
Repo.update_forward_refs()

if __name__ == "__main__":
    PRE_COMMIT_JSON = {
        "exclude": "^docs/conf.py",
        "repos": [
            {
                "repo": "https://github.com/pre-commit/pre-commit-hooks",
                "rev": "v4.1.0",
                "hooks": [
                    {"id": "trailing-whitespace"},
                    {"id": "check-added-large-files"},
                    {"id": "check-ast"},
                    {"id": "check-json"},
                    {"id": "check-merge-conflict"},
                    {"id": "check-xml"},
                    {"id": "check-yaml"},
                    {"id": "debug-statements"},
                    {"id": "end-of-file-fixer"},
                    {"id": "requirements-txt-fixer"},
                    {"id": "mixed-line-ending", "args": ["--fix=auto"]},
                ],
            },
            {
                "repo": "https://github.com/myint/autoflake",
                "rev": "v1.4",
                "hooks": [
                    {
                        "id": "autoflake",
                        "args": [
                            "--in-place",
                            "--remove-all-unused-imports",
                            "--remove-unused-variables",
                        ],
                    }
                ],
            },
            {
                "repo": "https://github.com/pycqa/isort",
                "rev": "5.10.1",
                "hooks": [{"id": "isort"}],
            },
            {
                "repo": "https://github.com/psf/black",
                "rev": "stable",
                "hooks": [{"id": "black", "language_version": "python3"}],
            },
            {
                "repo": "https://github.com/asottile/blacken-docs",
                "rev": "v1.12.0",
                "hooks": [{"id": "blacken-docs", "additional_dependencies": ["black"]}],
            },
            {
                "repo": "https://github.com/PyCQA/flake8",
                "rev": "4.0.1",
                "hooks": [{"id": "flake8"}],
            },
        ],
    }

    from rich import print

    precommit_config = PreCommitConfig.parse_obj(PRE_COMMIT_JSON)
    print(precommit_config.dict(exclude_unset=True))
