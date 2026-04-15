"""Tests for tools/python/skills.py."""

from skills import SkillInput, SkillOutput, echo, reverse


def test_echo_returns_input_unchanged():
    result = echo(SkillInput(data="hello world"))
    assert result.result == "hello world"


def test_echo_handles_empty_string():
    result = echo(SkillInput(data=""))
    assert result.result == ""


def test_echo_contract_success_true_error_none():
    result = echo(SkillInput(data="test"))
    assert isinstance(result, SkillOutput)
    assert result.success is True
    assert result.error is None


def test_reverse_returns_reversed_string():
    result = reverse(SkillInput(data="hello"))
    assert result.result == "olleh"


def test_reverse_handles_empty_string():
    result = reverse(SkillInput(data=""))
    assert result.result == ""


def test_reverse_contract_success_true_error_none():
    result = reverse(SkillInput(data="abc"))
    assert isinstance(result, SkillOutput)
    assert result.success is True
    assert result.error is None
