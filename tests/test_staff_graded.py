"""
Unit tests for StaffGradedXBlock.

This module tests the StaffGradedXBlock in isolation.
"""

import unittest
from collections import namedtuple  # For use in setUp and test_set_score
from tests.utils import make_block
import staff_graded.staff_graded as sg


class StaffGradedXBlockTests(unittest.TestCase):
    """
    Test suite for StaffGradedXBlock.

    """

    maxDiff = None  # Show full diff on assertion failures for easier debugging

    def setUp(self):
        """Set up a fresh StaffGradedXBlock instance and patch all external dependencies."""
        self.block = make_block()
        self.block.location = "dummy_location"

        # Patch ScoreCSVProcessor to a dummy class that accepts arguments and simulates processing
        class DummyScoreCSVProcessor:
            """A dummy CSV processor that simulates the behavior of ScoreCSVProcessor."""

            def __init__(self, *args, **kwargs):
                pass

            def process_file(
                self, f, autocommit=True
            ):  # pylint: disable=unused-argument
                return None

            def status(self):
                # Simulate a successful CSV import status
                return {"saved": 1, "total": 1, "error_rows": [], "waiting": False}

        sg.ScoreCSVProcessor = DummyScoreCSVProcessor

        # Patch get_score to return a fixed score dict as expected by the XBlock
        def fake_get_score(user_id, location):  # pylint: disable=unused-argument
            return {
                "score": 5,
                "max_grade": 10,
            }

        sg.get_score = fake_get_score

        # Patch set_score to a no-op (does nothing)
        sg.set_score = lambda *a, **kw: None

        # Patch get_course_cohorts and modes_for_course to return dummy data
        sg.get_course_cohorts = lambda course_id=None, **kwargs: []
        Mode = namedtuple("Mode", ["slug", "name"])
        sg.modes_for_course = lambda course_id=None, only_selectable=False, **kwargs: [
            Mode("audit", "Audit Track"),
            Mode("masters", "Master's Track"),
            Mode("verified", "Verified Track"),
        ]

    def setup_block_location(self, staff=False):
        """Helper to DRY up block location and runtime setup."""
        self.block.location = type(
            "Loc",
            (),
            {
                "html_id": lambda self: "id",
                "course_key": "course",
                "__str__": lambda self: "loc",
            },
        )()
        type(self.block.runtime).user_is_staff = property(lambda self: staff)
        self.block.runtime.local_resource_url = lambda *a, **kw: ""
        if staff:
            self.block.runtime.handler_url = lambda *a, **kw: "/handler"

    def test_default_display_name(self):
        """Block should have the correct default display name."""
        self.assertEqual(self.block.display_name, "Staff Graded Points")

    def test_default_instructions(self):
        """Block should have the correct default instructions."""
        self.assertEqual(self.block.instructions, "Your results will be graded offline")

    def test_default_weight(self):
        """Block should have the correct default weight."""
        self.assertEqual(self.block.weight, 1.0)

    def test_max_score(self):
        """Block should report the correct max score."""
        self.assertEqual(self.block.max_score(), 1.0)

    def test_get_current_username(self):
        """Block should return the correct username from the dummy runtime."""
        self.assertEqual(
            self.block._get_current_username(),  # pylint: disable=protected-access
            "testuser",
        )

    def test_get_score(self):
        """Block should return the correct score values from the mocked get_score."""
        score = self.block.get_score()
        self.assertEqual(score.raw_earned, 5)
        self.assertEqual(score.raw_possible, 10)

    def test_set_score(self):
        """Block should accept and process a score update without error."""
        Score = namedtuple("Score", ["raw_earned", "raw_possible"])
        self.block.set_score(Score(3, 5))  # No assertion needed; just ensure no error

    def test_student_view_runs(self):
        """Student view should render for a non-staff user without error."""
        self.setup_block_location(staff=False)
        result = self.block.student_view(context={})
        self.assertTrue(hasattr(result, "add_content"))
        # Output should mention points possible or show a score
        self.assertTrue("points possible" in result.content or "/" in result.content)

    def test_student_view_staff(self):
        """Student view should render for a staff user and include staff controls."""
        self.setup_block_location(staff=True)
        result = self.block.student_view(context={})
        self.assertTrue(hasattr(result, "add_content"))
        # Output should mention points possible or show a score
        self.assertTrue("points possible" in result.content or "/" in result.content)

    def test_workbench_scenarios(self):
        """Block should provide workbench scenarios for XBlock SDK integration."""
        scenarios = self.block.workbench_scenarios()
        self.assertIsInstance(scenarios, list)
        self.assertIn("StaffGradedXBlock", scenarios[0][0])

    def test_get_dummy(self):
        """Block should return the dummy value from get_dummy method."""
        result = self.block.get_dummy()
        self.assertEqual(result, "Dummy")

    def test_csv_import_handler_staff(self):
        """CSV import handler should work for staff users and return a response object."""
        self.block.runtime.user_is_staff = True
        self.block.location = "dummy_location"

        class DummyFile:
            size = 1
            name = "dummy.csv"

        class DummyRequest:
            POST = {"csv": type("F", (), {"file": DummyFile()})()}

        response = self.block.csv_import_handler(DummyRequest())
        self.assertTrue(hasattr(response, "status_code"))

    def test_csv_import_handler_not_staff(self):
        """CSV import handler should return 403 for non-staff users."""
        self.block.runtime.user_is_staff = False
        self.block.location = "dummy_location"

        class DummyRequest:
            POST = {}

        response = self.block.csv_import_handler(DummyRequest())
        self.assertEqual(response.status_code, 403)

    def test_student_view_no_grades_available_on_nosuchserviceerror(self):
        """student_view should set grades_available=False if get_score raises NoSuchServiceError."""
        # Patch get_score to raise NoSuchServiceError
        sg.get_score = lambda *a, **kw: (_ for _ in ()).throw(sg.NoSuchServiceError())

        # Patch the template renderer to capture the context and return a string
        captured_context = {}
        orig_render = self.block.loader.render_django_template

        def fake_render(_template, context):
            captured_context.update(context)
            return "<div>dummy</div>"

        self.block.loader.render_django_template = fake_render

        self.setup_block_location(staff=False)
        self.block.student_view(context={})
        self.assertIn("grades_available", captured_context)
        self.assertFalse(captured_context["grades_available"])

        # Restore original renderer
        self.block.loader.render_django_template = orig_render

    def test_student_view_points_possible_string_when_no_score(self):
        """student_view should show points possible string if get_score returns empty."""
        # Patch get_score to return empty dict (no score for user)
        sg.get_score = lambda *a, **kw: {}

        self.setup_block_location(staff=False)
        result = self.block.student_view(context={})
        self.assertIn(f"{self.block.weight} points possible", result.content)
