import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path
import subprocess


def _import_actions():
    """Import after patching so module-level side effects don't fire."""
    from executor.actions.system import (
        take_screenshot,
        lock_screen,
        sleep_system,
    )

    return take_screenshot, lock_screen, sleep_system


# ---------------------------------------------------------------------------
# take_screenshot
# ---------------------------------------------------------------------------


class TestTakeScreenshot:
    @patch("executor.actions.system.pyautogui.screenshot")
    @patch("executor.actions.system.datetime")
    def test_saves_to_desktop_with_timestamp(self, mock_dt, mock_ss):
        import datetime as dt
        fixed_now = dt.datetime(2024, 6, 15, 10, 30, 0)
        expected_timestamp = "20240615_103000"

        # 2. Tell the mock: "When someone calls datetime.now(), 
        # return this real fixed_now object."
        mock_dt.now.return_value = fixed_now

        # 3. Run the function
        take_screenshot, _, _ = _import_actions()
        result = take_screenshot({})

        # 4. Assertions
        expected_path = str(Path.home() / "Desktop" / f"screenshot_{expected_timestamp}.png")
        mock_ss.assert_called_once_with(expected_path)
        assert f"screenshot_{expected_timestamp}.png" in result
        assert "Desktop" in result

    @patch(
        "executor.actions.system.pyautogui.screenshot",
        side_effect=Exception("display error"),
    )
    def test_propagates_screenshot_error(self, _):
        take_screenshot, _, _ = _import_actions()
        with pytest.raises(Exception, match="display error"):
            take_screenshot({})


# ---------------------------------------------------------------------------
# lock_screen
# ---------------------------------------------------------------------------


class TestLockScreen:
    @patch("executor.actions.system.ctypes.windll")
    def test_calls_lock_workstation(self, mock_windll):
        _, lock_screen, _ = _import_actions()
        result = lock_screen({})
        mock_windll.user32.LockWorkStation.assert_called_once()
        assert "locked" in result.lower()


# ---------------------------------------------------------------------------
# sleep_system
# ---------------------------------------------------------------------------


class TestSleepSystem:
    @patch("executor.actions.system.subprocess.run")
    def test_calls_rundll32_suspend(self, mock_run):
        _, _, sleep_system = _import_actions()
        result = sleep_system({})
        mock_run.assert_called_once_with(
            ["rundll32.exe", "powrprof.dll,SetSuspendState", "0,1,0"],
            check=True,
        )
        assert "sleep" in result.lower()

    @patch(
        "executor.actions.system.subprocess.run",
        side_effect=subprocess.CalledProcessError(1, "rundll32"),
    )
    def test_propagates_subprocess_error(self, _):
        _, _, sleep_system = _import_actions()
        with pytest.raises(subprocess.CalledProcessError):
            sleep_system({})
