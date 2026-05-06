import os
import unittest
from unittest.mock import patch

from start import get_bool_env, get_int_env


class StartConfigTest(unittest.TestCase):
    def test_get_int_env_uses_default_when_missing(self):
        with patch.dict(os.environ, {}, clear=True):
            self.assertEqual(get_int_env('CONTROL_INTERVAL_SECONDS', 120), 120)

    def test_get_int_env_rejects_invalid_value(self):
        with patch.dict(os.environ, {'CONTROL_INTERVAL_SECONDS': 'abc'}, clear=True):
            with self.assertRaises(RuntimeError):
                get_int_env('CONTROL_INTERVAL_SECONDS', 120)

    def test_get_bool_env_parses_supported_values(self):
        with patch.dict(os.environ, {'USE_RAW_FAN_DUTY': 'true'}, clear=True):
            self.assertTrue(get_bool_env('USE_RAW_FAN_DUTY'))

        with patch.dict(os.environ, {'USE_RAW_FAN_DUTY': 'false'}, clear=True):
            self.assertFalse(get_bool_env('USE_RAW_FAN_DUTY'))

    def test_get_bool_env_rejects_invalid_value(self):
        with patch.dict(os.environ, {'USE_RAW_FAN_DUTY': 'maybe'}, clear=True):
            with self.assertRaises(RuntimeError):
                get_bool_env('USE_RAW_FAN_DUTY')


if __name__ == '__main__':
    unittest.main()
