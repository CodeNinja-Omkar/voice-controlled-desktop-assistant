# This is the single source of truth for supported actions.
# LLM prompt is generated from this — schema and docs stay in sync automatically.

from dataclasses import dataclass
from typing import Callable
from executor.actions import browser, system, notes , media

@dataclass
class ActionSpec:
    name: str
    description: str
    parameters: dict  # param_name -> description


SUPPORTED_ACTIONS: dict[str, ActionSpec] = {
    "open_url": ActionSpec(
        name="open_url",
        description="Open a URL in the default browser",
        parameters={"url": "fully qualified URL including https://"},
    ),
    "search_web": ActionSpec(
        name="search_web",
        description="Search the web for a query",
        parameters={"query": "search query string"},
    ),
    "set_volume": ActionSpec(
        name="set_volume",
        description="Set system volume level",
        parameters={"level": "integer 0-100"},
    ),
    "open_application": ActionSpec(
        name="open_application",
        description="Open an installed application by name",
        parameters={"name": "application name e.g. notepad, calculator, spotify"},
    ),
    "take_note": ActionSpec(
        name="take_note",
        description="Save a text note to a local file",
        parameters={"content": "the note content to save"},
    ),
    "tell_time": ActionSpec(
        name="tell_time",
        description="Tell the current time or date",
        parameters={},
    ),
    "increase_volume": ActionSpec(
        name="increase_volume",
        description="Increase system volume by a relative amount",
        parameters={"amount": "integer 1-50, default 10"},
    ),
    "decrease_volume": ActionSpec(
        name="decrease_volume",
        description="Decrease system volume by a relative amount",
        parameters={"amount": "integer 1-50, default 10"},
    ),
    "close_application": ActionSpec(
        name="close_application",
        description="Close a running application by name",
        parameters={"name": "application name"},
    ),
    "unknown": ActionSpec(
        name="unknown",
        description="Use when the command does not match any supported action",
        parameters={"reason": "brief explanation of why it could not be handled"},
    ),
    "take_screenshot": ActionSpec(
        name="take_screenshot",
        description="Take a screenshot and save it to the Desktop",
        parameters={},
    ),
    "lock_screen": ActionSpec(
        name="lock_screen",
        description="Lock the Windows session",
        parameters={},
    ),
    "sleep_system": ActionSpec(
        name="sleep_system",
        description="Put the computer to sleep",
        parameters={},
    ),
    "play_pause_media": ActionSpec(
        name="play_pause_media",
        description="Play or pause the current media player",
        parameters={},
    ),
    "next_track": ActionSpec(
        name="next_track",
        description="Skip to the next track in the current media player",
        parameters={},
    ),
    "previous_track": ActionSpec(
        name="previous_track",
        description="Go back to the previous track in the current media player",
        parameters={},
    ),
    "mute_toggle": ActionSpec(
        name="mute_toggle",
        description="Toggle system mute on or off",
        parameters={},
    ),
}

ACTION_HANDLERS: dict[str, callable] = {
    "open_url": lambda p: browser.open_url(p.get("url", "")),
    "search_web": lambda p: browser.search_web(p.get("query", "")),
    "set_volume": lambda p: system.set_volume(p.get("level", 50)),
    "increase_volume": lambda p: system.increase_volume(p.get("amount", 10)),
    "decrease_volume": lambda p: system.decrease_volume(p.get("amount", 10)),
    "open_application": lambda p: system.open_application(p.get("name", "")),
    "close_application": lambda p: system.close_application(p.get("name", "")),
    "tell_time": lambda p: system.tell_time(),
    "take_note": lambda p: notes.take_note(p.get("content", "")),
    "take_screenshot": lambda p: system.take_screenshot(p),
    "lock_screen": lambda p: system.lock_screen(p),
    "sleep_system": lambda p: system.sleep_system(p),
    "play_pause_media": lambda p: media.play_pause_media(p),
    "next_track": lambda p: media.next_track(p),
    "previous_track": lambda p: media.previous_track(p),
    "mute_toggle": lambda p: media.mute_toggle(p),
    "unknown": lambda p: p.get("reason", "Unknown command."),
}
