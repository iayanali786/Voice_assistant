# Python Voice Assistant

A voice-controlled assistant built with `speech_recognition` and `pyttsx3`,
covering both the beginner feature set and the advanced tier
(NLU-style intent parsing, email, reminders, weather, Q&A, custom commands).

## Project structure

```
voice_assistant/
├── assistant.py       # entry point / main loop
├── nlu.py              # keyword-scoring intent classifier
├── speech_utils.py      # microphone input + text-to-speech output
├── features.py           # one function per capability
├── config.json             # API keys, email settings, custom commands, knowledge base
└── requirements.txt
```

## Setup

1. Install Python 3.10+.
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
   Note: `PyAudio` sometimes needs a system package first.
   - Windows: `pip install pyaudio` usually works directly.
   - macOS: `brew install portaudio` then `pip install pyaudio`.
   - Linux: `sudo apt install portaudio19-dev` then `pip install pyaudio`.
3. Get a **free** OpenWeatherMap API key at https://openweathermap.org/api
   and put it in `config.json` under `weather.api_key`.
4. For email, use a **test/dummy Gmail account**, turn on 2-step
   verification, and generate an "App Password" (not your real password)
   at https://myaccount.google.com/apppasswords. Put that in
   `config.json` under `email.sender_app_password`.
5. Run it:
   ```
   python assistant.py
   ```

## Feature checklist

**Beginner tier**
- [x] Capture voice input via `speech_recognition`
- [x] Respond to "hello" with a time-of-day greeting
- [x] Tell the current time and date
- [x] Web search on a spoken topic (opens browser)
- [x] Graceful error handling — re-prompts on unrecognized audio
- [x] Text-to-speech feedback via `pyttsx3` for every response

**Advanced tier**
- [x] Keyword-scoring intent parser (`nlu.py`) instead of exact-phrase matching
- [x] Send email via voice command (`smtplib`)
- [x] Timed reminders with an audible spoken alert (`threading.Timer`)
- [x] Live weather via OpenWeatherMap
- [x] General knowledge Q&A — local knowledge base first, Wikipedia summary API as fallback
- [x] Add custom voice commands at runtime, saved to `config.json`
- [x] Privacy documentation (below)

## How the NLU works

Every intent (time, weather, email, etc.) has a small set of trigger
keywords. When a sentence is heard, each intent is scored by how many
of its keywords appear in that sentence, and the highest-scoring intent
wins. This is intentionally lightweight — no extra ML libraries required
— but it means phrasing can vary ("what's the time", "tell me the time")
instead of needing one exact command string. Swapping in `nltk` or a
`transformers` intent model later is possible without touching the rest
of the app, since `parse_intent()` is the only function that changes.

## Privacy: what data is processed and how

- **Audio**: Captured only while actively listening in the main loop; it
  is sent to Google's speech-recognition service (via the
  `speech_recognition` library) to be converted to text, and is not
  stored locally or elsewhere by this project.
- **Recognized text**: Kept only in memory for the duration of a single
  command; nothing is logged to disk.
- **Email content**: Recipient, subject and body are sent directly over
  an authenticated SMTP connection to the mail server configured in
  `config.json`. Use a dummy/test account, not a personal one, while
  developing.
- **Weather queries**: The city name you speak is sent to the
  OpenWeatherMap API to fetch a forecast; no other personal data is sent.
- **Wikipedia lookups**: Only the extracted topic/question text is sent
  to Wikipedia's public summary API.
- **Custom commands & knowledge base**: Stored locally in `config.json`
  in plain text. Don't put real credentials or sensitive personal data
  in there beyond what's needed (e.g. the email app password), and treat
  that file as sensitive/do not commit it to a public repo.
- No data in this project is sold, shared with advertisers, or sent
  anywhere beyond the third-party APIs listed above that are required
  for each feature to work.

## Notes for extending this

- Add a brand-new spoken feature by writing a handler in `features.py`,
  adding its keywords to `INTENT_KEYWORDS` in `nlu.py`, and wiring it up
  in `handle_command()` in `assistant.py`.
- Add a brand-new custom command by voice ("teach you a new command")
  or by editing `custom_commands` in `config.json` directly.
