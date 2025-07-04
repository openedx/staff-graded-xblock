"""
Test package initialization: Patch sys.modules for Open edX and Django modules to allow isolated XBlock testing.
"""
import sys
import types

# Mock Open edX and bulk_grades modules for all tests
sys.modules['lms'] = types.ModuleType('lms')
sys.modules['lms.djangoapps'] = types.ModuleType('lms.djangoapps')
sys.modules['lms.djangoapps.grades'] = types.ModuleType('lms.djangoapps.grades')
sys.modules['lms.djangoapps.grades.api'] = types.ModuleType('lms.djangoapps.grades.api')
bulk_grades_api = types.ModuleType('bulk_grades.api')
setattr(bulk_grades_api, 'ScoreCSVProcessor', object)
setattr(bulk_grades_api, 'get_score', lambda *a, **kw: None)
setattr(bulk_grades_api, 'set_score', lambda *a, **kw: None)
sys.modules['bulk_grades'] = types.ModuleType('bulk_grades')
sys.modules['bulk_grades.api'] = bulk_grades_api

# Mock django.utils.translation for XBlock i18n
# translation_mod = types.ModuleType('django.utils.translation')
# setattr(translation_mod, 'gettext_noop', lambda x: x)
# setattr(translation_mod, 'get_language', lambda: 'en')
# setattr(translation_mod, 'gettext_lazy', lambda x: x)
# sys.modules['django.utils.translation'] = translation_mod 