"""
assistant.py
------------
Entry point. Run this file to start the voice assistant:

    python assistant.py

Loop overview:
  1. listen for a spoken command
  2. classify it into an intent with nlu.parse_intent
  3. hand off to the matching handler in features.py
  4. if nothing matched, check custom commands, then fall back to
     general knowledge Q&A
"""

from nlu import parse_intent
from speech_utils import speak, listen
import features


MAX_RETRIES = 3  # how many times in a row we ask the user to repeat before giving up


def handle_command(text: str, config: dict) -> bool:
    """Returns False when the user wants to exit, True otherwise."""
    intent, cleaned = parse_intent(text)

    if intent == "greet":
        features.greet(config)

    elif intent == "time":
        features.tell_time()

    elif intent == "date":
        features.tell_date()

    elif intent == "search":
        features.web_search(cleaned)

    elif intent == "email":
        features.send_email(config)

    elif intent == "reminder":
        features.set_reminder()

    elif intent == "weather":
        features.get_weather(config)

    elif intent == "add_command":
        features.add_custom_command(config)

    elif intent == "exit":
        speak("Goodbye!")
        return False

    else:
        # not a built-in intent -- check user-defined commands first,
        # then fall back to the knowledge base / Wikipedia lookup
        if not features.run_custom_command(cleaned, config):
            features.answer_question(cleaned, config)

    return True


def main() -> None:
    config = features.load_config()
    speak("Voice assistant ready. Say 'hello' to get started, or 'exit' to quit.")

    misheard_in_a_row = 0

    while True:
        heard = listen()

        if heard is None:
            misheard_in_a_row += 1
            if misheard_in_a_row >= MAX_RETRIES:
                speak("I'm having trouble hearing you. Say something whenever you're ready.")
                misheard_in_a_row = 0
            else:
                speak("Sorry, I didn't catch that. Could you repeat that?")
            continue

        misheard_in_a_row = 0
        should_continue = handle_command(heard, config)
        if not should_continue:
            break


if __name__ == "__main__":
    main()
