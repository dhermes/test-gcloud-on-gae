"""GCloud API access in idiomatic Python."""

try:
    from pkg_resources import get_distribution
    __version__ = get_distribution('gcloud').version
except ImportError:
    __version__ = None
