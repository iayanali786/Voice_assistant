"""
speech_utils.py
----------------
Everything related to turning voice into text and text back into voice
lives here, so the rest of the assistant never has to touch the
microphone or the TTS engine directly.
"""

import speech_recognition as sr
import pyttsx3


# pyttsx3 engines don't like being re-created on every call, so we set
# one up once and reuse it for the whole session.
_engine = pyttsx3.init()
_engine.setProperty("rate", 175)   # a little faster than the default, sounds more natural
_engine.setProperty("volume", 1.0)


def speak(text: str) -> None:
    """Speak text out loud and also print it, so the console doubles as a transcript."""
    print(f"Assistant: {text}")
    _engine.say(text)
    _engine.runAndWait()


def listen(timeout: int = 5, phrase_time_limit: int = 8) -> str | None:
    """
    Capture one utterance from the default microphone and return it as
    lowercase text. Returns None (instead of raising) whenever the audio
    could not be turned into text, so callers can just check for None
    and ask the user to repeat themselves.
    """
    recognizer = sr.Recognizer()

    with sr.Microphone() as source:
        # a short ambient-noise calibration keeps the mic from picking up
        # background hum as if it were speech
        recognizer.adjust_for_ambient_noise(source, duration=0.6)
        print("Listening...")
        try:
            audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
        except sr.WaitTimeoutError:
            # user simply didn't say anything in time
            return None

    try:
        text = recognizer.recognize_google(audio)
        print(f"You: {text}")
        return text.lower()
    except sr.UnknownValueError:
        # audio was captured but couldn't be understood
        return None
    except sr.RequestError:
        speak("I'm having trouble reaching the speech recognition service right now.")
        return None
