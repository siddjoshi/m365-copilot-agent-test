"""Sample application for the coding agent to work with."""


def hello(name=None):
    """Return a greeting, optionally personalized with a name."""
    if name:
        return f"Hello, {name}!"
    return "Hello, World!"


def greet_team(members):
    """Return a list of personalized greetings for a list of team members."""
    return [hello(member) for member in members]


if __name__ == "__main__":
    print(hello())
    print(hello("Alice"))
    print(greet_team(["Alice", "Bob", "Charlie"]))
