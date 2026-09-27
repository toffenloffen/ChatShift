# ChatShift

**Your words. More worlds.**

Write or speak in your own language. ChatShift translates your message directly
into your game or app's chat field, so you can join the conversation without
switching to a translation window.

**Text translation tested with a free ChatGPT account — no API key needed.**
Cloud voice is experimental; free-account voice access has not been verified.

I'm **[toffenloffen](https://github.com/toffenloffen)**. I created ChatShift to make chatting easier
when writing in another language is difficult.

## Watch ChatShift in action

[![Watch the ChatShift video demo on YouTube](https://img.youtube.com/vi/qVZ6KIvjux8/hqdefault.jpg)](https://youtu.be/qVZ6KIvjux8)

**[▶ Watch the demo on YouTube](https://youtu.be/qVZ6KIvjux8)** — see text and voice translation in game chat.

## Download and get started

**[Download ChatShift for Windows](https://github.com/toffenloffen/ChatShift/releases/latest/download/ChatShift-Setup.exe)**

**New: streaming voice, with local noise suppression included.**
No ZIP extraction, Python installation or Whisper download is needed.

1. Open **ChatShift-Setup.exe** and follow the installer.
2. Read the welcome screen and click **Open ChatShift**.
3. Sign in to Codex with your own ChatGPT account, then choose languages in
   **Text**, **Voice**, and **Controller** separately. **⇄** swaps each pair.
4. Enable Voice, choose your microphone and try **Speech and translation test**.

Internet and a ChatGPT account with access to the required Codex models are needed.
**No API key or separate API billing setup. Free-account access to the new voice
feature is not yet verified.** The earlier free-account test below covers text only.

## Why I changed voice recognition

In my tests, streaming recognition handled my Norwegian dialect better than the
previous solution. Audio is processed while I speak, then the transcript goes to
Luna for translation. Choosing the same voice input and output language keeps the
transcript without translation. ChatShift uses the recognized speech, not an AI reply.

This also removes the local Whisper workload and its large speech-model download.
**DeepFilter noise suppression stays local** and cleans the audio before streaming.
Recognition can still make mistakes; speed depends on the connection and account.
The cloud voice integration is experimental. See [voice details](VOICE.md).

[Setup help](GET_STARTED.md)

## How much can you chat on a free account?

In my test on **26 September 2026**, I used a new **free ChatGPT account**
to translate **34 messages — 479 words over about 39 minutes** while chatting
on Twitch and with Google AI. My displayed remaining allowance went from **100% to 99%**.
The message and word counts exclude ChatShift's automatic warmup request.

At that rate, my rough estimate for a full allowance is **48,000 words, 3,400 messages,
or 65 hours at the same writing pace**. These are projections from my test,
not guaranteed limits or a daily allowance. Free-account Codex access and usage limits
depend on OpenAI's current availability and account limits.

## What you can do

- **Choose from 26 languages** for both input and output.
- **Type or speak:** translate written messages or use your microphone.
- **Keep chatting where you play:** use keyboard or mouse shortcuts while ChatShift runs in the background.
- **Review or send automatically:** choose separately for text and voice.
- **Streaming cloud dictation:** no local speech-model download. See [voice help](VOICE.md).
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

While recording, microphone audio is streamed to OpenAI. Translation also uses
OpenAI through your Codex sign-in. ChatShift does not save recordings or transcripts
to disk. The experimental Codex voice connection can change or become unavailable.
ChatShift is an independent project, not an official OpenAI product.

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
