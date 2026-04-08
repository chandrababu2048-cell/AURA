# ============================================================
# core/voice.py — AURA Voice Module (TTS + STT)
# ============================================================
# PURPOSE:
#   Standalone voice module for AURA.
#   TTS  — Moira (Irish) voice + subtle AI shimmer effect
#   STT  — Push to talk via sounddevice + Google Speech Recognition
#   Next — ElevenLabs upgrade (Kerry Condon / FRIDAY quality)
#
# VOICE DESIGN:
#   Based on FRIDAY from Iron Man — voiced by Kerry Condon (Irish).
#   Moira is macOS's Irish English voice: natural lilt, clear, melodic.
#   Ring modulation at 8% adds a barely-there AI shimmer without
#   killing the accent's warmth. Rate 200 keeps her crisp but not rushed.
#
# STT DESIGN:
#   No PyAudio needed — sounddevice records directly.
#   listen() records for max MAX_LISTEN_SEC, sends to Google STT.
#   Push-to-talk: caller presses Enter to trigger, auto-stops on silence.
#
# USAGE (isolation test):
#   python -c "from core.voice import AuraVoice; AuraVoice().test()"
#   python -c "from core.voice import AuraVoice; print(AuraVoice().listen())"
# ============================================================

import tempfile
import os
import numpy as np
import soundfile as sf
import sounddevice as sd
import speech_recognition as sr
import pyttsx3


VOICE_ID        = "com.apple.voice.compact.en-IE.Moira"  # Irish English — FRIDAY-like
RATE            = 200       # wpm — confident, clear, not rushed
VOLUME          = 1.0
ROBOT_MIX       = 0.08      # subtle AI shimmer — preserves Moira's natural warmth
CARRIER_HZ      = 55        # lower = warmer metallic tone, keeps the lilt intact
SAMPLE_RATE     = 16000     # Hz — optimal for Google STT
MAX_LISTEN_SEC  = 8         # max recording duration per push-to-talk


class AuraVoice:
    def __init__(self):
        self.engine = pyttsx3.init()
        self._configure()

    def _configure(self):
        self.engine.setProperty("voice",   VOICE_ID)
        self.engine.setProperty("rate",    RATE)
        self.engine.setProperty("volume",  VOLUME)

    def _apply_shimmer(self, audio: np.ndarray, samplerate: int) -> np.ndarray:
        """
        Subtle ring modulation — AI shimmer effect.
        Blends original + modulated signal at ROBOT_MIX ratio.
        Keeps the Irish accent's melodic quality intact.
        """
        if audio.size == 0:
            return audio

        t = np.arange(len(audio)) / samplerate
        carrier = np.sin(2 * np.pi * CARRIER_HZ * t).astype(np.float32)

        if audio.ndim == 2:
            carrier = carrier[:, np.newaxis]

        modulated = audio * carrier
        result = (1 - ROBOT_MIX) * audio + ROBOT_MIX * modulated

        peak = np.max(np.abs(result))
        if peak > 0:
            result = result / peak * 0.95
        return result

    def speak(self, text: str):
        """Speak text with Moira (Irish) voice + subtle AI shimmer."""
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            tmp_path = f.name

        try:
            self.engine.save_to_file(text, tmp_path)
            self.engine.runAndWait()

            audio, samplerate = sf.read(tmp_path, dtype="float32")
            if audio.size == 0:
                self.engine.say(text)
                self.engine.runAndWait()
                return

            processed = self._apply_shimmer(audio, samplerate)
            sd.play(processed, samplerate)
            sd.wait()
        finally:
            os.unlink(tmp_path)

    def listen(self) -> str | None:
        """
        Push-to-talk STT.
        Records for up to MAX_LISTEN_SEC seconds via sounddevice,
        transcribes with Google Speech Recognition.
        Returns the recognised text, or None if nothing was heard.
        """
        print("\n  [ Listening... speak now ]")
        recording = sd.rec(
            int(MAX_LISTEN_SEC * SAMPLE_RATE),
            samplerate=SAMPLE_RATE,
            channels=1,
            dtype="int16"
        )
        sd.wait()
        print("  [ Got it — processing... ]")

        raw = recording.tobytes()
        audio_data = sr.AudioData(raw, SAMPLE_RATE, 2)
        recognizer = sr.Recognizer()

        try:
            text = recognizer.recognize_google(audio_data)
            return text
        except sr.UnknownValueError:
            return None
        except sr.RequestError:
            return None

    def test(self):
        """Self-test: AURA introduces herself — informal, witty, FRIDAY-style."""
        self.speak(
            "Oh, you're actually here. Brilliant. "
            "I'm AURA — your AI companion, personal assistant, and honestly, "
            "probably the most useful thing in your life right now. "
            "All systems are up. Try not to break anything."
        )
        self.speak(
            "Right, so here's the deal. "
            "I'll talk, you listen — or don't, your call. "
            "Soon you can talk back and I'll actually listen too, which is more than most people manage. "
            "Voice is online. I'm ready. Are you?"
        )
