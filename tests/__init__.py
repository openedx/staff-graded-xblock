"""
Test package initialization for StaffGradedXBlock tests.

This file sets up the test environment for all tests in this package:
- Sets DJANGO_SETTINGS_MODULE and runs django.setup()
- Patches sys.modules to mock all Open edX and Django dependencies
- Ensures all XBlock and Django imports work in isolation, without a full LMS
"""

import os
import sys
import types

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "staff_graded.locale.settings")

# Mock Open edX and bulk_grades modules for all tests BEFORE importing django
sys.modules["lms"] = types.ModuleType("lms")
sys.modules["lms.djangoapps"] = types.ModuleType("lms.djangoapps")
sys.modules["lms.djangoapps.grades"] = types.ModuleType("lms.djangoapps.grades")
sys.modules["lms.djangoapps.grades.api"] = types.ModuleType("lms.djangoapps.grades.api")
bulk_grades_api = types.ModuleType("bulk_grades.api")
setattr(  # pylint: disable=literal-used-as-attribute
    bulk_grades_api, "ScoreCSVProcessor", object
)
setattr(  # pylint: disable=literal-used-as-attribute
    bulk_grades_api, "get_score", lambda *a, **kw: None
)
setattr(  # pylint: disable=literal-used-as-attribute
    bulk_grades_api, "set_score", lambda *a, **kw: None
)
sys.modules["bulk_grades"] = types.ModuleType("bulk_grades")
sys.modules["bulk_grades.api"] = bulk_grades_api

# Patch crum module globally for all tests
crum = types.ModuleType("crum")
setattr(  # pylint: disable=literal-used-as-attribute
    crum, "get_current_request", lambda: None
)
sys.modules["crum"] = crum

# Patch django.middleware.csrf globally for all tests
django_csrf = types.ModuleType("django.middleware.csrf")
setattr(  # pylint: disable=literal-used-as-attribute
    django_csrf, "get_token", lambda req: "csrf"
)
sys.modules["django.middleware.csrf"] = django_csrf

import django  # pylint: disable=wrong-import-position

django.setup()
