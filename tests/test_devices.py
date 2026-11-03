"""Unit tests for the constructed device layer."""
import unittest
from datetime import datetime

from houserules.devices import Action, ActionRejected, DeviceLayer

T0 = datetime(2011, 1, 1, 12, 0, 0)


def act(name, device, **kw):
    a = Action(name=name, device=device, **kw)
    a.at = T0
    return a


class TestDeviceLayer(unittest.TestCase):
    def setUp(self):
        self.dev = DeviceLayer()

    def test_unlock_then_lock(self):
        self.dev.apply(act("unlock", "front_door"))
        self.assertTrue(self.dev.door_unlocked("front_door"))
        self.dev.apply(act("lock", "front_door"))
        self.assertFalse(self.dev.door_unlocked("front_door"))

    def test_double_unlock_rejected(self):
        self.dev.apply(act("unlock", "front_door"))
        with self.assertRaises(ActionRejected):
            self.dev.apply(act("unlock", "front_door"))

    def test_mark_dose_requires_fired_reminder(self):
        with self.assertRaises(ActionRejected):
            self.dev.apply(act("mark_dose_taken", "med_reminder", window_id="w1"))
        self.dev.apply(act("fire_reminder", "med_reminder", window_id="w1"))
        self.dev.apply(act("mark_dose_taken", "med_reminder", window_id="w1"))
        self.assertEqual(len(self.dev.doses_marked["w1"]), 1)

    def test_heat_timer_requires_on(self):
        with self.assertRaises(ActionRejected):
            self.dev.apply(act("set_heat_timer", "burner", timer_s=60))
        self.dev.apply(act("heat_on", "burner"))
        self.dev.apply(act("set_heat_timer", "burner", timer_s=60))

    def test_unknown_action_rejected(self):
        with self.assertRaises(ActionRejected):
            self.dev.apply(act("open_window", "front_door"))


if __name__ == "__main__":
    unittest.main()
