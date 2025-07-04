"""
Pytest configuration and fixtures for Staff Graded XBlock tests.
Ensures a minimal Django environment and provides reusable mocks and helpers.
"""

import os
import pytest

# Set the Django settings module for all tests
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tests.test_settings")

####### use mock and patch

@pytest.fixture(autouse=True)
def patch_bulk_grades(monkeypatch):
    """
    Automatically mock get_score and set_score from bulk_grades.api for all tests.
    Ensures tests do not hit the real database or grading logic.
    """
    import staff_graded.staff_graded as sg

    def fake_get_score(usage_key, user_id):
        return {
            'score': 5,
            'grade': 5,
            'max_grade': 10,
            'created': None,
            'modified': None,
            'state': None,
            'who_last_graded': 'testuser',
        }

    def fake_set_score(usage_key, student_id, score, max_points, override_user_id=None, **defaults):
        # No-op for tests
        pass

    monkeypatch.setattr(sg, 'get_score', fake_get_score)
    monkeypatch.setattr(sg, 'set_score', fake_set_score)


@pytest.fixture
# rename this
# do thi
def xblock():
    """
    Provides a StaffGradedXBlock instance with dummy runtime and field data.
    Use this fixture in tests that require a basic XBlock setup.
    """
    from staff_graded.staff_graded import StaffGradedXBlock
    from tests.helpers import DummyRuntime, DummyScopeIds, DummyFieldData
    field_data = DummyFieldData({
        'display_name': "Staff Graded Points",
        'instructions': "Your results will be graded offline",
        'weight': 1.0,
    })
    return StaffGradedXBlock(
        runtime=DummyRuntime(),
        field_data=field_data,
        scope_ids=DummyScopeIds()
    )


@pytest.fixture
def mock_score_csv_processor(monkeypatch):
    """
    Monkeypatch ScoreCSVProcessor with a dummy processor for tests that need to bypass
    actual CSV processing logic. Use as a fixture in relevant tests.
    """
    import staff_graded.staff_graded as sg
    import types
    dummy_processor = types.SimpleNamespace(
        process_file=lambda f, autocommit=True: None,
        status=lambda: {"saved": 1, "total": 1, "error_rows": [], "waiting": False},
    )
    monkeypatch.setattr(sg, "ScoreCSVProcessor", lambda **kwargs: dummy_processor)
    yield
    monkeypatch.undo()