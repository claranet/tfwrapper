"""Utility functions for tfwrapper."""


def format_env(env):
    """Format a dict containing environment variables for usage on a shell prompt."""
    return " ".join(["=".join(e) for e in env.items()])


def get_dict_value(dic, *keys, default=None):
    """Retrieve a value recursively from dict with fallback in case any key is missing."""
    d = dict(dic)
    try:
        for k in keys:
            d = d[k]
        return d
    except KeyError:
        return default
