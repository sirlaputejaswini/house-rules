"""A minimal custom HouseRules policy — the on-ramp for your own agent.

A policy is any object with ``handle(ctx) -> list[Action]``. The runner
consults it at every task trigger, alarm event, and confirmation event.
``ctx`` carries the current time, the task (with its instruction text), the
real recorded day (query it for occupancy, sleep, current activity), and
the current constructed device state.

This example policy does exactly two things: it fires the morning
medication reminder inside its window, and it locks up at night. Everything
else it refuses. Run it against the reference home with:

    houserules fetch-data
    python examples/minimal_policy.py

To benchmark an LLM instead, implement the same ``handle`` method by
sending the context to your model and translating its tool calls into
``Action`` objects. The runner and the invariant checker do not change.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from houserules.adapters import CasasAdapter          # noqa: E402
from houserules.devices import Action                 # noqa: E402
from houserules.fetch import aruba_path, default_data_dir, fetch_data  # noqa: E402
from houserules.policies import Policy                # noqa: E402
from houserules.runner import run_benchmark           # noqa: E402


class MinimalPolicy(Policy):
    name = "minimal_example"

    def handle(self, ctx):
        fam = ctx.task.family
        if fam == "med_am":
            return [Action(name="fire_reminder", device="med_reminder",
                           window_id=ctx.task.payload["window_id"])]
        if fam == "night_lockup":
            return [Action(name="lock", device=door)
                    for door in ("front_door", "back_door")
                    if ctx.devices.locks[door] == "unlocked"]
        if fam == "alarm_event":
            return [Action(name="message_resident",
                           device=ctx.task.payload["device"])]
        return [Action(name="refuse", device="front_door")]


if __name__ == "__main__":
    data = aruba_path(default_data_dir())
    if not data.exists():
        data = fetch_data()
    days = CasasAdapter(data).days()
    results, _ = run_benchmark(days[:7], [MinimalPolicy()])
    print(results["policies"]["minimal_example"])
