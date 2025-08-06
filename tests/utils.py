"""
Test helpers and mixins for StaffGradedXBlock unit tests.
"""

from staff_graded.staff_graded import StaffGradedXBlock


class DummyRuntime:
    """A minimal mock XBlock runtime for unit testing StaffGradedXBlock."""

    def __init__(self):
        self._user_is_staff = True

    @property
    def user_is_staff(self):
        return self._user_is_staff

    @user_is_staff.setter
    def user_is_staff(self, value):
        self._user_is_staff = value

    @property
    def user_id(self):
        return 1

    def handler_url(self, block, handler):  # pylint: disable=unused-argument
        return f"/handler/{handler}"

    def local_resource_url(self, block, url):  # pylint: disable=unused-argument
        return f"/static/{url}"

    def service(self, block, service_name):  # pylint: disable=unused-argument
        """Return a dummy user or i18n service, or None for other services."""
        if service_name == "user":

            class DummyUser:
                """Dummy user class for testing user service in DummyRuntime."""

                def get_current_user(self):
                    """Return a dummy user object with opt_attrs for username."""

                    class DummyUserObj:
                        """Dummy user object for testing user service in DummyRuntime."""

                        opt_attrs = {"edx-platform.username": "testuser"}

                    return DummyUserObj()

            return DummyUser()
        if service_name == "i18n":

            class DummyI18n:
                def ugettext(self, text):
                    return text

            return DummyI18n()
        return None


class DummyScopeIds:
    """Dummy scope IDs for XBlock field and user scoping in tests."""

    def __init__(self):
        self.usage_id = "dummy_usage_id"
        self.block_type = "staffgradedxblock"
        self.def_id = "dummy_def_id"
        self.user_id = "dummy_user_id"
        self.course_id = "dummy_course_id"


class DummyFieldData:
    """Dummy field data for XBlock field storage in tests."""

    def __init__(self, data=None):
        self._data = data or {}

    def has(self, xblock, name):  # pylint: disable=unused-argument
        return name in self._data

    def get(self, xblock, name):  # pylint: disable=unused-argument
        return self._data.get(name)

    def set(self, xblock, name, value):  # pylint: disable=unused-argument
        self._data[name] = value


def make_block(field_data=None, runtime=None, scope_ids=None):
    """Helper to create a StaffGradedXBlock with dummy runtime, field data, and scope IDs."""

    field_data = field_data or DummyFieldData(
        {
            "display_name": "Staff Graded Points",
            "instructions": "Your results will be graded offline",
            "weight": 1.0,
        }
    )
    runtime = runtime or DummyRuntime()
    scope_ids = scope_ids or DummyScopeIds()
    return StaffGradedXBlock(
        runtime=runtime, field_data=field_data, scope_ids=scope_ids
    )
