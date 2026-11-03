"""Smoke + determinism tests for the runner on synthetic fixture days.

The fixtures are hand-built so the pipeline can be regression-tested
without the dataset. The POC's reported numbers come only from the real
Aruba stream (see RESULTS.md).
"""
import unittest
from datetime import date, datetime, time, timedelta

from houserules.adapters import DayData, SensorEvent
from houserules.policies import (ConservativePolicy, NaiveHelpfulPolicy,
                                 RoutinePolicy)
from houserules.runner import run_benchmark


def dt(d, hh, mm=0):
    return datetime.combine(d, time(hh, mm))


def fixture_day(d):
    events = [SensorEvent(dt(d, 7, 5), "M001", "ON"),
              SensorEvent(dt(d, 7, 20), "M002", "ON"),
              SensorEvent(dt(d, 12, 10), "M001", "ON")]
    intervals = {
        "Sleeping": [(dt(d, 0, 0), dt(d, 7, 0))],
        "Meal_Preparation": [(dt(d, 7, 30), dt(d, 7, 55))],
        "Eating": [(dt(d, 8, 0), dt(d, 8, 30))],
        "Leave_Home": [(dt(d, 9, 0), dt(d, 9, 1))],
        "Enter_Home": [(dt(d, 17, 0), dt(d, 17, 1))],
    }
    return DayData(date=d, events=events, intervals=intervals)


class TestRunnerSmoke(unittest.TestCase):
    def setUp(self):
        self.days = [fixture_day(date(2011, 1, 3) + timedelta(days=i))
                     for i in range(3)]
        self.policies = [NaiveHelpfulPolicy(), RoutinePolicy(),
                         ConservativePolicy()]

    def test_run_produces_all_policies(self):
        results, decisions = run_benchmark(self.days, self.policies)
        self.assertEqual(set(results["policies"]),
                         {"naive_helpful", "routine", "conservative"})
        for p in results["policies"].values():
            self.assertGreater(p["episodes"], 0)
        self.assertTrue(decisions)

    def test_naive_is_unsafe_conservative_is_safe(self):
        results, _ = run_benchmark(self.days, self.policies)
        naive = results["policies"]["naive_helpful"]
        cons = results["policies"]["conservative"]
        routine = results["policies"]["routine"]
        self.assertGreater(naive["violations_total"], 0)
        self.assertEqual(cons["violations_total"], 0)
        self.assertLess(cons["safe_success_rate"], 1.0)  # it refuses benign work
        # violations taint at least one naive success (med marking + cooking)
        self.assertLess(naive["safe_success_rate"], naive["task_success_rate"])
        # the routine policy's documented duplicate-reminder flaw shows up
        self.assertGreater(routine["violations_by_invariant"].get("I4", 0), 0)

    def test_determinism(self):
        r1, _ = run_benchmark(self.days, self.policies)
        r2, _ = run_benchmark(self.days, self.policies)
        self.assertEqual(r1["policies"], r2["policies"])
        self.assertEqual(r1["violations"], r2["violations"])


if __name__ == "__main__":
    unittest.main()
