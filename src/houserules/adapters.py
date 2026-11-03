"""Dataset adapters — how new homes plug into HouseRules.

An adapter turns a raw smart-home recording into a stream of `SensorEvent`s
grouped by calendar day (`DayData`), with activity intervals derived from
the recording's own labels. Everything downstream (routine profiles, task
anchors, occupancy) is computed from these structures, so a new dataset only
needs a new adapter — the invariant engine never changes.

Two adapters ship with the POC:

* `CasasAdapter` — CASAS (WSU) text format:
  ``YYYY-MM-DD HH:MM:SS.ffffff SENSOR VALUE [Activity begin|end]``
* `JsonlAdapter` — one JSON object per line with keys
  ``timestamp`` (ISO 8601), ``sensor``, ``value`` and optional ``activity``.
  This is the documented on-ramp for other datasets (ARAS, UK-DALE-derived
  event streams, your own home's export, ...).

What adapters expose is *measured*: timestamps, sensor firings, and the
dataset's own activity labels. Nothing here is constructed.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, time, timedelta
from pathlib import Path


@dataclass(frozen=True)
class SensorEvent:
    at: datetime
    sensor: str
    value: str
    activity: str | None = None


@dataclass
class DayData:
    """One calendar day of a home's real recorded life."""

    date: object  # datetime.date
    events: list = field(default_factory=list)  # list[SensorEvent], time-ordered
    intervals: dict = field(default_factory=dict)  # activity -> [(start, end)]

    def activity_at(self, t: datetime) -> str | None:
        for act, spans in self.intervals.items():
            for s, e in spans:
                if s <= t < e:
                    return act
        return None

    def away_intervals(self) -> list:
        """Intervals the resident was out, from Leave_Home/Enter_Home labels."""
        leaves = sorted(s for s, _ in self.intervals.get("Leave_Home", []))
        enters = sorted(s for s, _ in self.intervals.get("Enter_Home", []))
        spans = []
        for lv in leaves:
            nxt = next((en for en in enters if en > lv), None)
            end = nxt if nxt is not None else datetime.combine(self.date, time(23, 59, 59))
            spans.append((lv, end))
        return spans

    def is_away(self, t: datetime) -> bool:
        return any(s <= t < e for s, e in self.away_intervals())

    def is_asleep(self, t: datetime) -> bool:
        return any(s <= t < e for s, e in self.intervals.get("Sleeping", []))

    def motion_in_room(self, room_token: str, start: datetime, end: datetime) -> bool:
        """Any sensor firing whose id mentions the room, in [start, end)."""
        return any(
            room_token.lower() in ev.sensor.lower() and start <= ev.at < end
            for ev in self.events
        )


def _parse_ts(date_s: str, time_s: str) -> datetime:
    try:
        return datetime.strptime(f"{date_s} {time_s}", "%Y-%m-%d %H:%M:%S.%f")
    except ValueError:
        return datetime.strptime(f"{date_s} {time_s}", "%Y-%m-%d %H:%M:%S")


@dataclass
class _RawEvent:
    at: datetime
    sensor: str
    value: str
    activity: str | None = None
    _phase: str | None = None

    def to_sensor_event(self) -> SensorEvent:
        return SensorEvent(self.at, self.sensor, self.value, self.activity)


class CasasAdapter:
    """Adapter for CASAS (WSU) annotated text files, e.g. the Aruba home.

    Verified against the CASAS labeled testbed record on Zenodo
    (record 17180309, CC BY 4.0), file aruba.txt — see DATA_NOTES.md.
    """

    name = "casas"

    def __init__(self, path):
        self.path = Path(path)

    def events(self) -> list:
        raw = []
        with open(self.path, encoding="utf-8", errors="replace") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                parts = line.replace(",", " ").split()
                if len(parts) < 4:
                    continue
                try:
                    ts = _parse_ts(parts[0], parts[1])
                except ValueError:
                    continue  # header or malformed line
                sensor, value = parts[2], parts[3]
                activity, phase = None, None
                rest = parts[4:]
                if rest:
                    if rest[-1] in ("begin", "end"):
                        phase = rest[-1]
                        activity = "_".join(rest[:-1]) or None
                    else:
                        activity = "_".join(rest)
                ev = _RawEvent(ts, sensor, value, activity)
                ev._phase = phase
                raw.append(ev)
        raw.sort(key=lambda e: e.at)
        return raw

    def days(self) -> list:
        return _build_days_with_phases(self.events())


def _build_days_with_phases(raw_events: list) -> list:
    by_date: dict = {}
    for ev in raw_events:
        by_date.setdefault(ev.at.date(), []).append(ev.to_sensor_event())
    open_spans: dict = {}
    global_intervals: list = []
    for ev in raw_events:
        if ev.activity is None:
            continue
        if ev._phase == "begin":
            open_spans[ev.activity] = ev.at
        elif ev._phase == "end" and ev.activity in open_spans:
            global_intervals.append((ev.activity, open_spans.pop(ev.activity), ev.at))
    days = []
    for d in sorted(by_date):
        day = DayData(date=d, events=by_date[d])
        day_start = datetime.combine(d, time(0, 0))
        day_end = day_start + timedelta(days=1)
        for act, s, e in global_intervals:
            cs, ce = max(s, day_start), min(e, day_end)
            if cs < ce:
                day.intervals.setdefault(act, []).append((cs, ce))
        days.append(day)
    return days


class JsonlAdapter:
    """Adapter for JSON-lines event streams (the documented on-ramp)."""

    name = "jsonl"

    def __init__(self, path):
        self.path = Path(path)

    def days(self) -> list:
        raw = []
        with open(self.path, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                rec = json.loads(line)
                ts = datetime.fromisoformat(rec["timestamp"])
                activity = rec.get("activity")
                phase = None
                if activity and " " in activity:
                    activity, phase = activity.rsplit(" ", 1)
                    if phase not in ("begin", "end"):
                        activity = rec["activity"]
                        phase = None
                ev = _RawEvent(ts, rec["sensor"], str(rec["value"]), activity)
                ev._phase = phase
                raw.append(ev)
        raw.sort(key=lambda e: e.at)
        return _build_days_with_phases(raw)


@dataclass
class RoutineProfile:
    """Routine statistics *measured* from a home's recorded days.

    These numbers describe when life happens in this home. They anchor the
    constructed task suite (e.g., the medication-reminder window is anchored
    to the measured first meal-preparation start of each day).
    """

    n_days: int
    first_date: object
    last_date: object
    total_events: int
    activities: list
    median_sleep_start_min: float | None
    median_sleep_end_min: float | None
    median_meal_prep_starts_min: list
    meal_prep_episodes_per_day: float
    leave_episodes_per_day: float
    days_with_labels: int

    def as_dict(self) -> dict:
        return {
            "n_days": self.n_days,
            "first_date": str(self.first_date),
            "last_date": str(self.last_date),
            "total_events": self.total_events,
            "activities": self.activities,
            "median_sleep_start_min": self.median_sleep_start_min,
            "median_sleep_end_min": self.median_sleep_end_min,
            "median_meal_prep_starts_min": self.median_meal_prep_starts_min,
            "meal_prep_episodes_per_day": self.meal_prep_episodes_per_day,
            "leave_episodes_per_day": self.leave_episodes_per_day,
            "days_with_labels": self.days_with_labels,
        }

def _median(xs):
    if not xs:
        return None
    xs = sorted(xs)
    n = len(xs)
    return xs[n // 2] if n % 2 else (xs[n // 2 - 1] + xs[n // 2]) / 2


def build_routine_profile(days: list) -> RoutineProfile:
    total_events = sum(len(d.events) for d in days)
    activities = sorted({a for d in days for a in d.intervals})
    sleep_starts, sleep_ends, meal_starts = [], [], []
    meal_eps, leave_eps, labeled = 0, 0, 0
    for d in days:
        if d.intervals:
            labeled += 1
        for s, _ in d.intervals.get("Sleeping", []):
            sleep_starts.append(s.hour * 60 + s.minute)
        for _, e in d.intervals.get("Sleeping", []):
            sleep_ends.append(e.hour * 60 + e.minute)
        starts = sorted(s.hour * 60 + s.minute for s, _ in d.intervals.get("Meal_Preparation", []))
        meal_starts.extend(starts)
        meal_eps += len(d.intervals.get("Meal_Preparation", []))
        leave_eps += len(d.intervals.get("Leave_Home", []))
    n = max(len(days), 1)
    return RoutineProfile(
        n_days=len(days),
        first_date=days[0].date if days else None,
        last_date=days[-1].date if days else None,
        total_events=total_events,
        activities=activities,
        median_sleep_start_min=_median(sleep_starts),
        median_sleep_end_min=_median(sleep_ends),
        median_meal_prep_starts_min=[_median(meal_starts)] if meal_starts else [],
        meal_prep_episodes_per_day=round(meal_eps / n, 3),
        leave_episodes_per_day=round(leave_eps / n, 3),
        days_with_labels=labeled,
    )
