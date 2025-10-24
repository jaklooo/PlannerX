"""PlannerX version information."""

__version__ = "1.0.0"
__author__ = "PlannerX Team"
__license__ = "MIT"
__description__ = "Task and event planner with daily email digest"

# Version history
VERSION_INFO = {
    "major": 1,
    "minor": 0,
    "patch": 0,
    "release": "stable",
}


def get_version():
    """Get current version string."""
    return __version__


def get_version_info():
    """Get detailed version information."""
    return {
        "version": __version__,
        "author": __author__,
        "license": __license__,
        "description": __description__,
        **VERSION_INFO,
    }
