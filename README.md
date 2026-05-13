## Project Goal
Build a voice-controlled desktop assistant (JARVIS) that accepts natural language
commands and executes them on a Windows PC. Long-term goal: replace mouse/keyboard
for most common OS operations. Eventually support open-ended dynamic task execution.


## Stack
- Python 3.11 (not 3.12 — dependency conflicts with Whisper and openWakeWord)
- Windows 11
- Whisper base model (CPU only — Iris Xe ML support unreliable on Windows)
- openWakeWord (onnx inference framework)
- Gemini 2.0 Flash via google-genai SDK (migrated away from deprecated google-generativeai)
- pyttsx3 for TTS (reinitialized per call — Windows runAndWait bug workaround)
- sounddevice + soundfile + numpy for audio
- pyautogui, pygetwindow for OS automation
- python-dotenv for config

## Architecture

wake word (openWakeWord)
→ Audio Recorder (silence detection)
→ Whisper STT
→ LLM (intent → structured JSON)
→ Action Executor
→ pyttsx3 TTS


## Phase 1 — Complete
Working end-to-end pipeline. Wake word activates, records speech, transcribes,
parses intent, executes action, speaks response, resets and waits for next wake word.

Actions implemented (9 + unknown):
- open_url — opens URL in default browser
- search_web — Google search
- set_volume — absolute level 0-100
- increase_volume — relative increase
- decrease_volume — relative decrease
- open_application — by name, mapped to .exe
- close_application — taskkill by process name
- tell_time — speaks current time and date
- take_note — appends timestamped note to ~/jarvis_notes.txt
- unknown — graceful fallback

## Phase 2 — Next
Goal: expand to 23 actions. No architecture changes needed.

system.py additions:
- take_screenshot — save to Desktop with timestamp filename
- get_clipboard — read clipboard content aloud
- set_clipboard — write text to clipboard
- lock_screen — Windows lock
- sleep_system — system sleep

media.py (new file):
- play_pause_media — global media key
- next_track
- previous_track
- mute_toggle

window.py (new file):
- minimize_window — minimize active window
- maximize_window — maximize active window
- switch_window — focus app by name (alt+tab equivalent)

files.py (new file):
- open_file — open file by name from common locations (Desktop, Documents, Downloads)
- list_notes — read back contents of jarvis_notes.txt

Each new action follows same pattern:
1. Add ActionSpec to SUPPORTED_ACTIONS in registry.py
2. Write handler function in appropriate actions/ file
3. Add lambda to ACTION_HANDLERS in registry.py
4. Write unit test with mocked OS calls
5. Verify in live test before moving to next action

## Phase 3 — Planned
Goal: open-ended dynamic task execution.
LLM generates Python code for tasks not covered by predefined actions.
Code runs in sandboxed subprocess with resource limits and allowlisted imports.
Requires sandbox infrastructure before any implementation.
Risk: without sandbox, LLM hallucination can cause destructive OS actions.
Replaces predefined routing only for unrecognized intents — registered actions still preferred.

## Phase 4 — Planned
Goal: screen awareness.
Periodic or on-demand screenshots fed to Gemini Vision.
Enables: "what's on my screen", "summarize this page", "click the confirm button".
Requires different prompt structure, screenshot timing logic, and coordinate mapping.
Depends on Phase 3 being stable first.