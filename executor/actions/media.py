import pyautogui


def play_pause_media(parameters: dict) -> str:
    pyautogui.press("playpause")
    return "Toggled play/pause."


def next_track(parameters: dict) -> str:
    pyautogui.press("nexttrack")
    return "Skipped to next track."


def previous_track(parameters: dict) -> str:
    pyautogui.press("prevtrack")
    return "Went back to previous track."


def mute_toggle(parameters: dict) -> str:
    pyautogui.press("volumemute")
    return "Toggled mute."
