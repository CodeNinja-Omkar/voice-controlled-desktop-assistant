import sounddevice as sd
import numpy as np
import logging

logger = logging.getLogger(__name__)

SAMPLE_RATE = 16000
SILENCE_THRESHOLD = 0.01      # RMS below this is considered silence
SILENCE_DURATION = 1.5        # seconds of silence before stopping
MAX_DURATION = 15             # hard cap to prevent infinite recording


def record_until_silence() -> np.ndarray:
    """
    Records from default mic until silence is detected or max duration hit.
    Returns float32 numpy array at 16kHz mono.
    """
    block_size = int(SAMPLE_RATE * 0.1)  # 100ms blocks
    max_blocks = int(MAX_DURATION / 0.1)
    silence_blocks_needed = int(SILENCE_DURATION / 0.1)

    recorded_blocks = []
    silent_blocks = 0
    recording_started = False

    logger.debug("Recording started")

    with sd.InputStream(
        samplerate=SAMPLE_RATE,
        channels=1,
        dtype="float32",
        blocksize=block_size,
    ) as stream:
        for _ in range(max_blocks):
            block, _ = stream.read(block_size)
            rms = np.sqrt(np.mean(block ** 2))

            if rms > SILENCE_THRESHOLD:
                recording_started = True
                silent_blocks = 0
            elif recording_started:
                silent_blocks += 1

            if recording_started:
                recorded_blocks.append(block.copy())

            if recording_started and silent_blocks >= silence_blocks_needed:
                break

    if not recorded_blocks:
        logger.warning("No audio captured above silence threshold")
        return np.zeros(SAMPLE_RATE, dtype=np.float32)

    audio = np.concatenate(recorded_blocks, axis=0).flatten()
    logger.debug("Recorded %.2f seconds of audio", len(audio) / SAMPLE_RATE)
    return audio