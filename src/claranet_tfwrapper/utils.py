"""Utility functions for tfwrapper."""


def format_env(env):
    """Format an dict containing environment variables for usage on a shell prompt."""
    return " ".join(["=".join(e) for e in env.items()])
