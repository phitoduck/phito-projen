"""
Models for 
"""

from __future__ import annotations
from typing import List, Optional
from pydantic import BaseModel, Field



class PylintRc(BaseModel):
    messages_control: MessagesControlOptions


class PylintRule(BaseModel):
    """
    :param name: name of the pylint rule, e.g. `raw-checker-failed`
    :param reason: reason for the rule being enabled or disabled
    """

    name: str
    reason: Optional[str] = None


class MessagesControlOptions(BaseModel):
    """Settings for the pylint "messages control"."""

    disable: List[PylintRule] = Field(list)
    """Pylint rules to disable"""

    enable: List[PylintRule] = Field(list)
    """Pylint rules to enable"""


class MainOptions(BaseModel):
    ...


class ReportsOptions(BaseModel):
    ...


class LoggingOptions(BaseModel):
    ...


class SpellingOptions(BaseModel):
    ...


class MiscellaneousOptions(BaseModel):
    ...


class TypeCheckOptions(BaseModel):
    ...


class ClassesOptions(BaseModel):
    ...


class VariablesOptions(BaseModel):
    ...


class FormatOptions(BaseModel):
    ...


class ImportsOptions(BaseModel):
    ...


class MethodArgsOptions(BaseModel):
    ...


class ExceptionsOptions(BaseModel):
    ...


class RefactoringOptions(BaseModel):
    ...


class SimilaritiesOptions(BaseModel):
    ...


class DesignOptions(BaseModel):
    ...


class StringOptions(BaseModel):
    ...


class BasicOptions(BaseModel):
    ...
