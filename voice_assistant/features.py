"""
features.py
-----------
One function per feature. Keeping these separate from assistant.py
means each capability can be tested or reused on its own.
"""

import json
import re
import smtplib
import threading
import webbrowser
from datetime import datetime
from email.mime.text import MIMEText
from pathlib import Path

import requests

from speech_utils import speak, listen

CONFIG_PATH = Path(__file__).parent / "config.json"


def load_config() -> dict:
    with open(CONFIG_PATH, "r") as f:
        return json.load(f)


def save_config(config: dict) -> None:
    with open(CONFIG_PATH, "w") as f:
        json.dump(config, f, indent=2)


# ---------------------------------------------------------------- greeting
def greet(config: dict) -> None:
    hour = datetime.now().hour
    if hour < 12:
        part_of_day = "morning"
    elif hour < 17:
        part_of_day = "afternoon"
    else:
        part_of_day = "evening"
    speak(f"Good {part_of_day}, {config.get('user_name', 'there')}! How can I help?")


# ---------------------------------------------------------------- time / date
def tell_time() -> None:
    now = datetime.now().strftime("%I:%M %p")
    speak(f"It's currently {now}.")


def tell_date() -> None:
    today = datetime.now().strftime("%A, %B %d, %Y")
    speak(f"Today is {today}.")


# ---------------------------------------------------------------- web search
def web_search(query: str) -> None:
    # strip the trigger words so only the actual topic is left
    topic = re.sub(r"\b(search|google|look up|browse|for)\b", "", query).strip()
    if not topic:
        speak("What would you like me to search for?")
        topic = listen() or ""
    if topic:
        speak(f"Searching the web for {topic}.")
        webbrowser.open(f"https://www.google.com/search?q={topic}")
    else:
        speak("I didn't catch a topic to search for.")


# ---------------------------------------------------------------- email
def send_email(config: dict) -> None:
    email_cfg = config["email"]

    speak("Who is this email for? Please say the email address.")
    recipient = listen()
    if not recipient:
        speak("I couldn't catch the email address, cancelling.")
        return
    # spoken addresses often come back with spaces or "at"/"dot" spelled out
    recipient = recipient.replace(" at ", "@").replace(" dot ", ".").replace(" ", "")

    speak("What should the subject be?")
    subject = listen() or "Voice assistant message"

    speak("What should the email say?")
    body = listen()
    if not body:
        speak("I didn't catch a message, cancelling.")
        return

    try:
        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = email_cfg["sender_address"]
        msg["To"] = recipient

        with smtplib.SMTP(email_cfg["smtp_server"], email_cfg["smtp_port"]) as server:
            server.starttls()
            server.login(email_cfg["sender_address"], email_cfg["sender_app_password"])
            server.send_message(msg)

        speak("Email sent.")
    except Exception as exc:
        speak("Sorry, I couldn't send the email. Please check the email settings in config.json.")
        print(f"[email error] {exc}")


# ---------------------------------------------------------------- reminders
def set_reminder() -> None:
    speak("In how many minutes should I remind you?")
    raw = listen()
    minutes = None
    if raw:
        match = re.search(r"\d+", raw)
        if match:
            minutes = int(match.group())

    if minutes is None:
        speak("I didn't catch a number of minutes, cancelling.")
        return

    speak("What should I remind you about?")
    note = listen() or "your reminder"

    speak(f"Okay, I'll remind you about {note} in {minutes} minutes.")

    def alert():
        speak(f"Reminder: {note}")

    timer = threading.Timer(minutes * 60, alert)
    timer.daemon = True  # so it doesn't block the program from closing
    timer.start()


# ---------------------------------------------------------------- weather
def get_weather(config: dict) -> None:
    weather_cfg = config["weather"]
    api_key = weather_cfg["api_key"]

    if "PUT_YOUR" in api_key:
        speak("Weather isn't set up yet. Add a free OpenWeatherMap API key to config.json.")
        return

    speak("Which city would you like the weather for?")
    city = listen() or weather_cfg.get("default_city", "")
    if not city:
        speak("I didn't catch a city name.")
        return

    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {"q": city, "appid": api_key, "units": "metric"}

    try:
        response = requests.get(url, params=params, timeout=6)
        data = response.json()

        if response.status_code != 200:
            speak(f"I couldn't find weather for {city}.")
            return

        temp = round(data["main"]["temp"])
        description = data["weather"][0]["description"]
        speak(f"It's currently {temp} degrees Celsius with {description} in {city}.")

    except requests.RequestException as exc:
        speak("I couldn't reach the weather service right now.")
        print(f"[weather error] {exc}")


# ---------------------------------------------------------------- knowledge / QA
def answer_question(query: str, config: dict) -> None:
    kb = config.get("knowledge_base", {})

    # 1. try an exact / substring match against the local knowledge base first,
    #    since that's instant and needs no network call
    for question, answer in kb.items():
        if question in query:
            speak(answer)
            return

    # 2. fall back to Wikipedia's free summary API for anything else
    topic = re.sub(r"\b(what|who|is|are|the|a|an)\b", "", query).strip()
    if not topic:
        speak("I'm not sure how to answer that.")
        return

    try:
        url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{topic}"
        response = requests.get(url, timeout=6)
        if response.status_code == 200:
            summary = response.json().get("extract")
            if summary:
                # keep spoken answers short
                speak(summary.split(". ")[0] + ".")
                return
    except requests.RequestException:
        pass

    speak("I'm not sure about that one. You could try rephrasing the question.")


# ---------------------------------------------------------------- custom commands
def run_custom_command(query: str, config: dict) -> bool:
    """Returns True if a matching custom command was found and executed."""
    for phrase, command in config.get("custom_commands", {}).items():
        if phrase in query:
            action = command.get("action")
            value = command.get("value")

            if action == "open_url":
                speak(f"Opening {phrase}.")
                webbrowser.open(value)
                return True

    return False


def add_custom_command(config: dict) -> None:
    speak("What phrase should trigger the new command?")
    phrase = listen()
    if not phrase:
        speak("I didn't catch that, cancelling.")
        return

    speak("What website should that phrase open? Please say the full address.")
    site = listen()
    if not site:
        speak("I didn't catch that, cancelling.")
        return

    site = site.replace(" dot ", ".").replace(" ", "")
    if not site.startswith("http"):
        site = "https://" + site

    config["custom_commands"][phrase] = {"action": "open_url", "value": site}
    save_config(config)
    speak(f"Got it. From now on, saying '{phrase}' will open {site}.")
