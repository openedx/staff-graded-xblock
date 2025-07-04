"""
Unit tests for StaffGradedXBlock using pytest and industry-standard patterns.
"""

import logging
from staff_graded.staff_graded import StaffGradedXBlock

# The xblock fixture is provided by conftest.py


# class wise tests
# mock the modes_for_course
# docs


def test_default_display_name(xblock):
    """Test that the default display_name is correct."""
    assert xblock.display_name == "Staff Graded Points"


def test_default_instructions(xblock):
    """Test that the default instructions are correct."""
    assert xblock.instructions == "Your results will be graded offline"


def test_default_weight(xblock):
    """Test that the default weight is correct."""
    assert xblock.weight == 1.0


def test_max_score(xblock):
    """Test that max_score returns the correct value."""
    assert xblock.max_score() == 1.0


def test_get_current_username(xblock):
    """Test that _get_current_username returns the dummy username."""
    assert xblock._get_current_username() == "testuser"


def test_get_score(xblock):
    """Test that get_score returns the correct Score object from the global mock."""
    xblock.location = "dummy_location"
    score = xblock.get_score()
    assert score.raw_earned == 5
    assert score.raw_possible == 10


def test_set_score(xblock):
    """Test that set_score does not error with the global mock."""
    xblock.location = "dummy_location"
    from collections import namedtuple

    Score = namedtuple("Score", ["raw_earned", "raw_possible"])
    xblock.set_score(Score(3, 5))
    # No assertion needed; just ensure no error


# use template for student_view
def test_student_view_runs(xblock, monkeypatch):
    """Test that student_view runs and returns a Fragment with correct score string for non-staff."""
    monkeypatch.setattr(xblock.loader, "load_unicode", lambda path: "")
    monkeypatch.setattr(
        xblock.loader,
        "render_django_template",
        lambda template_path, context, i18n_service=None: f"<div>{context.get('score_string')}</div>",
    )
    xblock.location = type(
        "Loc",
        (),
        {
            "html_id": lambda self: "id",
            "course_key": "course",
            "__str__": lambda self: "loc",
        },
    )()
    monkeypatch.setattr(
        type(xblock.runtime), "user_is_staff", property(lambda self: False)
    )
    xblock.runtime.local_resource_url = lambda *a, **kw: ""
    result = xblock.student_view(context={})
    assert hasattr(result, "add_content")
    # Check that the score string is present and correct for non-staff
    assert "points possible" in result.content or "/" in result.content


def test_student_view_staff(xblock, monkeypatch):
    """Test staff-specific logic in student_view, including score string in fragment."""
    monkeypatch.setattr(xblock.loader, "load_unicode", lambda path: "")
    monkeypatch.setattr(
        xblock.loader,
        "render_django_template",
        lambda template_path, context, i18n_service=None: f"<div>{context.get('score_string')}</div>",
    )
    xblock.location = type(
        "Loc",
        (),
        {
            "html_id": lambda self: "id",
            "course_key": "course",
            "__str__": lambda self: "loc",
        },
    )()
    monkeypatch.setattr(
        type(xblock.runtime), "user_is_staff", property(lambda self: True)
    )
    xblock.runtime.local_resource_url = lambda *a, **kw: ""
    xblock.runtime.handler_url = lambda *a, **kw: "/handler"
    import sys
    import types

    crum = types.ModuleType("crum")
    setattr(crum, "get_current_request", lambda: None)
    sys.modules["crum"] = crum
    django_csrf = types.ModuleType("django.middleware.csrf")
    setattr(django_csrf, "get_token", lambda req: "csrf")
    sys.modules["django.middleware.csrf"] = django_csrf
    result = xblock.student_view(context={})
    assert hasattr(result, "add_content")
    # Check that the score string is present and correct for staff
    assert "points possible" in result.content or "/" in result.content


def test_workbench_scenarios():
    """Test that workbench_scenarios returns a list with the correct scenario name."""
    scenarios = StaffGradedXBlock.workbench_scenarios()
    assert isinstance(scenarios, list)
    assert "StaffGradedXBlock" in scenarios[0][0]


def test_get_dummy():
    """Test that get_dummy returns the correct dummy string with the global translation mock."""
    result = StaffGradedXBlock.get_dummy()
    assert result == "Dummy"


def test_csv_import_handler_staff(xblock, mock_score_csv_processor):
    """Test csv_import_handler for staff user with a dummy file."""
    xblock.runtime.user_is_staff = True
    xblock.location = "dummy_location"

    class DummyFile:
        size = 1
        name = "dummy.csv"

    class DummyRequest:
        POST = {"csv": type("F", (), {"file": DummyFile()})()}

    response = xblock.csv_import_handler(DummyRequest())
    assert hasattr(response, "status_code")


def test_csv_import_handler_not_staff(xblock, mock_score_csv_processor):
    """Test csv_import_handler for non-staff user returns 403."""
    xblock.runtime.user_is_staff = False
    xblock.location = "dummy_location"

    class DummyRequest:
        POST = {}

    response = xblock.csv_import_handler(DummyRequest())
    assert response.status_code == 403
