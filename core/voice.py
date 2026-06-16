# ============================================================
# core/voice.py — AURA Voice Module
# ============================================================
# TTS: Moira (Irish English) — clean, natural, no effects
# STT: faster-whisper — 100% local, no internet, no rate limits
#
# WHY faster-whisper?
#   Google STT requires internet and gets rate-limited constantly.
#   faster-whisper runs OpenAI's Whisper model locally on your Mac.
#   No API key, no network, no dropped calls. Always works.
#
# UPGRADE PATH:
#   Replace pyttsx3 with ElevenLabs for Kerry Condon quality
# ============================================================

import os
import subprocess
import tempfile
import numpy as np
import sounddevice as sd
import soundfile as sf
from faster_whisper import WhisperModel


VOICE           = "Rocko (English (US))"
RATE            = 200        # wpm — natural pace, Rocko US
SAMPLE_RATE     = 16000
MAX_LISTEN_SEC  = 10         # hard ceiling — stops even if you keep talking
SILENCE_THRESH  = 300        # RMS below this = silence (tune up if noisy room)
SILENCE_CHUNKS  = 25         # ~1.6s of silence after speech → stop listening
CHUNK_SIZE      = 1024       # samples per audio chunk


def _find_mac_mic() -> int | None:
    for i, d in enumerate(sd.query_devices()):
        if d["max_input_channels"] > 0 and "MacBook" in d["name"]:
            return i
    for i, d in enumerate(sd.query_devices()):
        if d["max_input_channels"] > 0:
            return i
    return None


MIC_DEVICE = _find_mac_mic()

# Load Whisper once at startup — "base" model: fast, accurate, ~145MB download
# Runs entirely on CPU. First run downloads the model automatically.
_whisper: WhisperModel | None = None

def _get_whisper() -> WhisperModel:
    global _whisper
    if _whisper is None:
        print("  [ Loading Whisper model... (one-time download ~145MB) ]")
        _whisper = WhisperModel("base", device="cpu", compute_type="int8")
        print("  [ Whisper ready ]")
    return _whisper


class AuraVoice:
    def __init__(self):
        # Pre-load Whisper at startup so first listen isn't slow
        _get_whisper()

    def speak(self, text: str):
        """
        Speak using macOS built-in Moira voice via the 'say' command.
        No Python packages needed — works 100% on any Mac.
        -v Moira = Irish English voice
        -r 220   = fast, sharp pace like FRIDAY (default is 175)
        """
        subprocess.run(["say", "-v", VOICE, "-r", str(RATE), text])

    def listen(self) -> str | None:
        """
        Listen with smart silence detection.
        Starts recording when you speak, stops ~1.6s after you go quiet.
        No fixed wait — responds as soon as you're done talking.
        Uses local Whisper — no internet, no rate limits.
        """
        chunks        = []
        silent_count  = 0
        speech_started = False
        max_chunks    = int(MAX_LISTEN_SEC * SAMPLE_RATE / CHUNK_SIZE)

        print("\n  [ Listening... ]")

        try:
            with sd.InputStream(
                samplerate=SAMPLE_RATE,
                channels=1,
                dtype="int16",
                device=MIC_DEVICE,
                blocksize=CHUNK_SIZE,
            ) as stream:
                while True:
                    data, _ = stream.read(CHUNK_SIZE)
                    rms = np.sqrt(np.mean(data.astype(np.float32) ** 2))

                    if rms > SILENCE_THRESH:
                        # Sound detected — start or continue recording
                        speech_started = True
                        silent_count   = 0
                        chunks.append(data.copy())
                    elif speech_started:
                        # Silence after speech — count down to stop
                        chunks.append(data.copy())
                        silent_count += 1
                        if silent_count >= SILENCE_CHUNKS:
                            break  # you stopped talking — process now
                    # else: silence before speech started — keep waiting

                    # Hard ceiling
                    if len(chunks) >= max_chunks:
                        break

        except Exception as e:
            print(f"  [ Mic error: {e} ]")
            return None

        if not chunks or not speech_started:
            return None

        # Combine chunks → wav file → Whisper
        audio = np.concatenate(chunks, axis=0)

        tmp_path = None
        try:
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
                tmp_path = f.name
            sf.write(tmp_path, audio, SAMPLE_RATE)

            model    = _get_whisper()
            segments, _ = model.transcribe(tmp_path, language="en")
            text     = " ".join(s.text for s in segments).strip()
            return text if text else None

        except Exception as e:
            print(f"  [ Transcription error: {e} ]")
            return None
        finally:
            if tmp_path and os.path.exists(tmp_path):
                os.unlink(tmp_path)
