import unittest
from unittest.mock import Mock

from controller.client import FanController


class FanControllerConfigTest(unittest.TestCase):
    def make_controller(self, fan_speed_steps=None):
        return FanController(
            host='127.0.0.1',
            username='root',
            password='password',
            fan_speed_steps=fan_speed_steps,
        )

    def test_default_fan_speed_steps_keep_existing_policy(self):
        controller = self.make_controller()

        self.assertEqual(controller.get_required_fan_speed(50), 20)
        self.assertEqual(controller.get_required_fan_speed(55), 25)
        self.assertEqual(controller.get_required_fan_speed(60), 30)
        self.assertEqual(controller.get_required_fan_speed(65), 40)
        self.assertEqual(controller.get_required_fan_speed(66), -1)
        self.assertEqual(controller.get_required_fan_speed(0), -1)

    def test_custom_fan_speed_steps_are_sorted_by_temperature(self):
        controller = self.make_controller('70:50,45:15,55:25')

        self.assertEqual(controller.get_required_fan_speed(45), 15)
        self.assertEqual(controller.get_required_fan_speed(46), 25)
        self.assertEqual(controller.get_required_fan_speed(55), 25)
        self.assertEqual(controller.get_required_fan_speed(56), 50)
        self.assertEqual(controller.get_required_fan_speed(70), 50)
        self.assertEqual(controller.get_required_fan_speed(71), -1)

    def test_invalid_fan_speed_steps_raise_clear_error(self):
        invalid_values = [
            '',
            '50',
            'abc:20',
            '50:abc',
            '-1:20',
            '50:9',
            '50:101',
            '50:20,50:30',
        ]

        for invalid_value in invalid_values:
            with self.subTest(invalid_value=invalid_value):
                with self.assertRaises(ValueError):
                    self.make_controller(invalid_value)

    def test_raw_fan_duty_query_is_disabled_by_default(self):
        controller = self.make_controller()

        self.assertFalse(controller.use_raw_fan_duty)

    def test_set_fan_speed_switches_manual_mode_only_once(self):
        controller = self.make_controller()
        controller.ipmi = Mock()

        controller.set_fan_speed(30)
        controller.set_fan_speed(40)

        controller.ipmi.switch_fan_mode.assert_called_once_with(auto=False)
        self.assertEqual(controller.ipmi.set_fan_speed.call_count, 2)


if __name__ == '__main__':
    unittest.main()
