"""
Test helpers for XBlock unit tests: DummyRuntime, DummyScopeIds, DummyFieldData.
"""
from typing import Any, Dict, Optional


class DummyRuntime:
    """A minimal mock XBlock runtime for unit testing."""

    def __init__(self):
        self._user_is_staff = True

    def service(self, block: Any, service_name: str) -> Any:
        class DummyUser:
            def get_current_user(self):
                class DummyUserObj:
                    opt_attrs = {'edx-platform.username': 'testuser'}
                return DummyUserObj()
        if service_name == 'user':
            return DummyUser()
        if service_name == 'i18n':
            class DummyI18n:
                def ugettext(self, text):
                    return text
            return DummyI18n()
        return None

    @property
    def user_is_staff(self) -> bool:
        return self._user_is_staff

    @user_is_staff.setter
    def user_is_staff(self, value: bool):
        self._user_is_staff = value

    @property
    def user_id(self) -> int:
        return 1

    def handler_url(self, block: Any, handler: str) -> str:
        return f"/handler/{handler}"

    def local_resource_url(self, block: Any, url: str) -> str:
        return f"/static/{url}"


class DummyScopeIds:
    """A minimal mock for XBlock scope_ids."""
    def __init__(self):
        self.usage_id = 'dummy_usage_id'
        self.block_type = 'staffgradedxblock'
        self.def_id = 'dummy_def_id'
        self.user_id = 'dummy_user_id'
        self.course_id = 'dummy_course_id'


class DummyFieldData:
    """A minimal mock for XBlock field data."""
    def __init__(self, data: Optional[Dict[str, Any]] = None):
        self._data = data or {}

    def has(self, xblock: Any, name: str) -> bool:
        return name in self._data

    def get(self, xblock: Any, name: str) -> Any:
        return self._data.get(name)

    def set(self, xblock: Any, name: str, value: Any) -> None:
        self._data[name] = value