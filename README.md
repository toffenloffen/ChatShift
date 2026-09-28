# ChatShift

**Your words. More worlds.**

Write or speak in your own language. ChatShift translates your message directly
into your game or app's chat field, so you can join the conversation without
switching to a translation window.

**Use your ChatGPT sign-in through Codex — no API key to enter.**
Online voice models are experimental. I am looking for Plus-account testers.

I'm **[toffenloffen](https://github.com/toffenloffen)**. I created ChatShift to make chatting easier
when writing in another language is difficult.

## Watch ChatShift in action

[![Watch the ChatShift video demo on YouTube](https://img.youtube.com/vi/qVZ6KIvjux8/hqdefault.jpg)](https://youtu.be/qVZ6KIvjux8)

**[▶ Watch the demo on YouTube](https://youtu.be/qVZ6KIvjux8)** — see text and voice translation in game chat.

## Download and get started

**[Download ChatShift for Windows](https://github.com/toffenloffen/ChatShift/releases/latest/download/ChatShift-Setup.exe)**

**New: choose local or experimental online voice recognition.**
Local noise suppression is included. No ZIP extraction or Python installation is needed.

1. Open **ChatShift-Setup.exe** and follow the installer.
2. Read the welcome screen and click **Open ChatShift**.
3. Sign in to Codex with your own ChatGPT account, then choose languages in
   **Text**, **Voice**, and **Controller** separately. **⇄** swaps each pair.
4. In **Voice → AI models**, choose a model and click **Activate selected model**.
   Enable Voice, choose your microphone and try **Speech and translation test**.

Internet and a ChatGPT account with access to the required Codex models are needed.
The current sign-in path does not require you to enter an API key or configure
separate API billing. Account access and usage limits still apply.

## Voice model choices

| Model | How it works |
|---|---|
| Whisper Small · local | Speech recognition on your CPU; the smallest local option. |
| Whisper Medium · local | Larger local model, with higher memory use. |
| Whisper Large Turbo · local | Large local model; speed depends on your PC. |
| GPT-Live · Experimental | Streams audio while you speak. |
| GPT-Transcribe · Experimental | Sends the recording after you stop. |

Only one speech model is active at a time. Local Whisper files download on first use.
The older **ChatGPT dictation · cloud** option has been removed after repeated access
errors. **DeepFilter noise suppression stays available** before speech recognition.

In my tests, online recognition handled my Norwegian dialect better, but speed and
accuracy vary. The transcript goes to the existing Luna translator. Choosing the
same Voice input and output language keeps the transcript without translation.
Text translation is unchanged. See [voice details](VOICE.md).

**Plus testers wanted:** I have used the online options with my Pro account.
Plus-account access in this integration is still unverified. If you already have
Plus and try it, please report the selected model and whether transcription works,
or the exact error code. You do not need to buy a subscription to help test local voice.

[Setup help](GET_STARTED.md)

## What you can do

- **Choose from 26 languages** for both input and output.
- **Type or speak:** translate written messages or use your microphone.
- **Keep chatting where you play:** use keyboard or mouse shortcuts while ChatShift runs in the background.
- **Review or send automatically:** choose separately for text and voice.
- **Local or online speech recognition:** activate one model in Voice. See [voice help](VOICE.md).
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

Local Whisper keeps speech recognition on your PC. The online models send audio to
OpenAI, while translation uses OpenAI through your Codex sign-in. ChatShift does not
save recordings or transcripts to disk. Experimental online connections can change
or become unavailable; they are not a guarantee of subscription compatibility.
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
