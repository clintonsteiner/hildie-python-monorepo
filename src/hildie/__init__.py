"""Hildie monorepo namespace package."""

from hildie._version import __version__ as __version__

__path__ = __import__("pkgutil").extend_path(__path__, __name__)
