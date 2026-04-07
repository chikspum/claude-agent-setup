"""
Python skills scaffold.
Add new skills following the SkillInput / SkillOutput pattern.
"""

from dataclasses import dataclass


@dataclass
class SkillInput:
    data: str
    options: dict | None = None


@dataclass
class SkillOutput:
    result: str
    success: bool
    error: str | None = None


def echo(input: SkillInput) -> SkillOutput:
    """Return the input data unchanged. Useful for testing the skill pipeline."""
    return SkillOutput(result=input.data, success=True)


# TODO: add your skills here
