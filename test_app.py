"""Tests for app.py greeting functions."""

from app import hello, greet_team


def test_hello_default():
    assert hello() == "Hello, World!"


def test_hello_with_name():
    assert hello("Alice") == "Hello, Alice!"


def test_greet_team():
    result = greet_team(["Alice", "Bob", "Charlie"])
    assert result == ["Hello, Alice!", "Hello, Bob!", "Hello, Charlie!"]


def test_greet_team_empty():
    assert greet_team([]) == []
