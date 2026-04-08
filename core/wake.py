# ============================================================
# core/wake.py — AURA Wake Word Listener
# ============================================================
# PURPOSE:
#   Runs silently in the background, always listening.
#   When it hears "AURA" or "Hey AURA" → fires on_wake().
#
# HOW IT WORKS:
#   Uses sounddevice.InputStream — PortAudio's native stream API.
#   PortAudio calls _audio_callback() every CHUNK_DURATION seconds
#   with fresh audio data. We put that data in a queue.
#   A separate thread reads from the queue, transcribes it,
#   and checks for the wake word.
#
# WHY InputStream INSTEAD OF sd.rec()?
#   sd.rec() called from a background thread causes CoreAudio
#   errors on macOS (err=-50). InputStream lets PortAudio
#   handle its own threading — no macOS permission issues.
#
# UPGRADE PATH:
#   Swap Google STT with pvporcupine for fully offline wake word.
#
# USAGE (test):
#   .venv/bin/python -c "
#   from core.wake import WakeWordListener
#   WakeWordListener(lambda: print('WAKE!')).test()
#   "
# ============================================================

import queue
import threading
import numpy as np
import sounddevice as sd
import speech_recognition as sr
from typing import Callable


# ── Constants ─────────────────────────────────────────────

SAMPLE_RATE      = 16000   # Hz — standard for speech recognition
CHUNK_DURATION   = 2       # seconds of audio per recognition attempt
COOLDOWN_SECONDS = 3       # pause after wake word fires (prevents double-trigger)

# Wake words — includes phonetic variants Google STT might return
WAKE_WORDS = ["aura", "hey aura", "hey ora", "hora", "hey hora", "or a"]


def _find_mac_mic() -> int | None:
    """
    Find the MacBook built-in mic device index.
    Avoids accidentally using iPhone/Bluetooth mic.
    Returns device index or None to use system default.
    """
    for i, d in enumerate(sd.query_devices()):
        if d["max_input_channels"] > 0 and "MacBook" in d["name"]:
            return i
    # Fallback: first available input
    for i, d in enumerate(sd.query_devices()):
        if d["max_input_channels"] > 0:
            return i
    return None


MIC_DEVICE = _find_mac_mic()


class WakeWordListener:
    """
    Always-on background wake word detector.

    Uses sounddevice.InputStream (PortAudio native callback) so it
    works correctly on macOS without CoreAudio threading errors.

    Usage:
        listener = WakeWordListener(on_wake=my_function)
        listener.start()
        # ... your app runs ...
        listener.stop()
    """

    def __init__(self, on_wake: Callable):
        """
        Args:
            on_wake: Called (no args) when wake word is detected.
        """
        self.on_wake       = on_wake
        self._running      = False
        self._in_cooldown  = False
        self._stream       = None
        self.recognizer    = sr.Recognizer()

        # Thread-safe queue — audio callback puts chunks here,
        # processor thread reads from here.
        # maxsize=3 = don't queue more than 3 unprocessed chunks.
        # If we're slow processing, we drop old audio rather than falling behind.
        self._audio_queue  = queue.Queue(maxsize=3)

    def _audio_callback(self, indata, frames, time_info, status):
        """
        Called by PortAudio every CHUNK_DURATION seconds with fresh audio.
        Runs in PortAudio's own internal thread — safe on macOS.

        Args:
            indata: numpy array of audio samples (shape: [frames, channels])
            frames: number of samples in this chunk
            time_info: timing info (unused)
            status: any stream errors (ignored for robustness)
        """
        if self._in_cooldown:
            return  # don't queue audio during cooldown

        try:
            # indata.copy() = make a copy because indata gets overwritten
            # put_nowait = don't block if queue is full (just drop the chunk)
            self._audio_queue.put_nowait(indata.copy())
        except queue.Full:
            pass  # queue full — drop this chunk, keep going

    def _process_loop(self):
        """
        Runs in a background thread.
        Reads audio chunks from the queue and checks for wake word.
        """
        while self._running:
            try:
                # Block for up to 1 second waiting for a chunk.
                # timeout prevents the thread from hanging forever on stop().
                chunk = self._audio_queue.get(timeout=1.0)
            except queue.Empty:
                continue  # nothing in queue — loop back

            try:
                # Convert float32 audio → int16 bytes for SpeechRecognition
                # InputStream gives float32, SR wants int16
                audio_int16 = (chunk * 32767).astype(np.int16)
                raw_bytes   = audio_int16.tobytes()

                # Wrap in SR AudioData object
                audio_data = sr.AudioData(raw_bytes, SAMPLE_RATE, 2)

                # Transcribe with Google STT
                text = self.recognizer.recognize_google(audio_data).lower()
                print(f"[Debug] Heard: '{text}'")

                # Check if any wake word appears in the text
                if any(wake in text for wake in WAKE_WORDS):
                    self._trigger_wake()

            except sr.UnknownValueError:
                pass  # silence or unclear audio
            except sr.RequestError as e:
                print(f"[Debug] Network error from Google STT (Rate limited?): {e}")
            except Exception as e:
                print(f"[Debug] Unknown STT Thread error: {e}")

    def _trigger_wake(self):
        """Wake word detected — fire callback and start cooldown."""
        self._in_cooldown = True
        self.on_wake()

        # Reset cooldown after COOLDOWN_SECONDS
        def end_cooldown():
            self._in_cooldown = False

        t = threading.Timer(COOLDOWN_SECONDS, end_cooldown)
        t.daemon = True
        t.start()

    def start(self):
        """Start the wake word listener."""
        if self._running:
            return

        self._running = True

        # InputStream: PortAudio calls _audio_callback() automatically
        # blocksize = samples per callback = CHUNK_DURATION * SAMPLE_RATE
        # dtype=float32 = InputStream default — we convert to int16 in process loop
        self._stream = sd.InputStream(
            samplerate=SAMPLE_RATE,
            channels=1,
            dtype="float32",
            device=MIC_DEVICE,
            blocksize=int(CHUNK_DURATION * SAMPLE_RATE),
            callback=self._audio_callback,
        )
        self._stream.start()

        # Processor thread — reads from queue, runs STT
        proc_thread = threading.Thread(
            target=self._process_loop,
            daemon=True,
            name="WakeWordProcessor"
        )
        proc_thread.start()

        print("  [ AURA is listening for wake word... ]")

    def stop(self):
        """Stop the listener cleanly."""
        self._running = False
        if self._stream:
            self._stream.stop()
            self._stream.close()
            self._stream = None

    def test(self):
        """Say 'AURA' within 15 seconds to test."""
        detected = threading.Event()
        original = self.on_wake
        self.on_wake = lambda: detected.set()

        print("\nSay 'AURA' or 'Hey AURA' within 15 seconds...")
        self.start()

        if detected.wait(timeout=15):
            print("Wake word detected! AURA is awake.")
        else:
            print("No wake word heard in 15 seconds.")

        self.stop()
        self.on_wake = original
