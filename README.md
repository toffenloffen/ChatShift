# ChatShift

**Your words. More worlds.**

Write or speak in your own language. ChatShift translates your message directly
into your game or app's chat field, so you can join the conversation without
switching to a translation window.

**Tested with a free ChatGPT account — no API key or separate API billing needed.**

Created by **[toffenloffen](https://github.com/toffenloffen)** to make chatting easier
when writing in another language is difficult.

## Watch ChatShift in action

[![Watch the ChatShift video demo on YouTube](https://img.youtube.com/vi/qVZ6KIvjux8/hqdefault.jpg)](https://youtu.be/qVZ6KIvjux8)

**[▶ Watch the demo on YouTube](https://youtu.be/qVZ6KIvjux8)** — see text and voice translation in game chat.

## Download and get started

**[Download ChatShift for Windows](https://github.com/toffenloffen/ChatShift/releases/latest/download/ChatShift-Setup.exe)**

**New: one Windows installer for text, voice and noise suppression.**
No ZIP extraction or separate Python installation is needed.

1. Open **ChatShift-Setup.exe** and follow the installer.
2. Click **Set up ChatShift**. It prepares everything together, including the voice models.
3. Sign in to Codex with your own ChatGPT account if prompted, then choose your
   languages and shortcuts in ChatShift.

First-time setup downloads about **500 MB** of voice models. Translation requires
internet access and a ChatGPT account with Codex access; your account's usage limits
apply. No API key is needed.

[Setup help](GET_STARTED.md)

## How much can you chat on a free account?

In the creator's test on **26 September 2026**, a new **free ChatGPT account**
handled **34 translated messages — 479 words over about 39 minutes** while chatting
on Twitch and with Google AI. The displayed remaining allowance went from **100% to 99%**.
The message and word counts exclude ChatShift's automatic warmup request.

At that rate, a rough estimate for a full allowance is **48,000 words, 3,400 messages,
or 65 hours at the same writing pace**. These are projections from this test,
not guaranteed limits or a daily allowance. Free-account Codex access and usage limits
depend on OpenAI's current availability and account limits.

## What you can do

- **Choose from 26 languages** for both input and output.
- **Type or speak:** translate written messages or use your microphone.
- **Keep chatting where you play:** use keyboard or mouse shortcuts while ChatShift runs in the background.
- **Review or send automatically:** choose separately for text and voice.
- **Reduce microphone background noise** with optional local noise suppression.
- **Use the same language** for spelling correction or voice dictation.

## Using it in a game

Open the chat field. Type your message and press your text shortcut, or use your
voice shortcut to speak. Wait for the translated message, then read and send it.
Your language and shortcut settings are saved automatically.

ChatShift translates **your outgoing messages**. Compatibility depends on the game:
standard text translation needs a chat field that supports selecting, copying and
pasting. Translations and speech recognition can make mistakes.
See [game compatibility](COMPATIBILITY.md) for details.

## Privacy and availability

Speech recognition and noise suppression run on your PC. Microphone audio stays
local; text requiring AI processing is sent to OpenAI through Codex using your
account. ChatShift is an independent project, not an official OpenAI product.

This is an **early Windows release**, free to use. A SteamOS version is in development;
no Linux installer is published here yet. [Platform status](STEAMOS.md).

## Help and feedback

Found a problem? [Report it on GitHub](https://github.com/toffenloffen/ChatShift/issues).
Include your game or app, what you tried, and what happened.

[Quick start](GET_STARTED.md) · [Voice help](VOICE.md) · [Controller setup](CONTROLLERS.md) ·
[Technical details and development](TECHNICAL_DETAILS.md)

## License

Free to install and use under the [ChatShift Free Use and Attribution License](LICENSE).
Modification, redistribution, resale and paid access require separate permission,
except as allowed by the license's contribution provisions. Contributions are welcome.

ChatShift is **source-available, not OSI open source**. Previously published MIT-licensed
material retains its [MIT permissions](LICENSE-MIT-LEGACY.txt). Dependencies and models
retain their own licenses.
