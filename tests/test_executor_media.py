"""
tests/test_executor_media.py
pytest — mocks pyautogui.press
"""

from unittest.mock import patch, call
import pytest


class TestMediaActions:
    @patch("executor.actions.media.pyautogui.press")
    def test_play_pause(self, mock_press):
        from executor.actions.media import play_pause_media

        result = play_pause_media({})
        mock_press.assert_called_once_with("playpause")
        assert result

    @patch("executor.actions.media.pyautogui.press")
    def test_next_track(self, mock_press):
        from executor.actions.media import next_track

        result = next_track({})
        mock_press.assert_called_once_with("nexttrack")
        assert result

    @patch("executor.actions.media.pyautogui.press")
    def test_previous_track(self, mock_press):
        from executor.actions.media import previous_track

        result = previous_track({})
        mock_press.assert_called_once_with("prevtrack")
        assert result

    @patch("executor.actions.media.pyautogui.press")
    def test_mute_toggle(self, mock_press):
        from executor.actions.media import mute_toggle

        result = mute_toggle({})
        mock_press.assert_called_once_with("volumemute")
        assert result
