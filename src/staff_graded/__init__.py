""" Loading Xblock class"""

from importlib.metadata import version

from .staff_graded import StaffGradedXBlock

__version__ = version("staff-graded-xblock")
