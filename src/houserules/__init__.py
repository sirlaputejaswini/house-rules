"""HouseRules — a safety benchmark for agents that act in real homes.

HouseRules replays real recorded smart-home sensor streams (CASAS, WSU),
lets pluggable agent policies propose device actions on a documented,
constructed device layer, and scores every action against six hard safety
invariants (I1-I6). The headline metric is *safe success*: a task completed
with zero invariant violations.

Honesty note: CASAS grounds *routines* (when life happens). It contains no
controllable locks, cameras, or alarms. The device layer is a construction
calibrated to those routines. HouseRules is real-data-grounded, never
"recorded device control".
"""

__version__ = "0.1.0"
__author__ = "Tejaswini Sirlapu"
