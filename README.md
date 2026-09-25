# ChatShift

**Your words. More worlds.**

Created by **[toffenloffen](https://github.com/toffenloffen)**.

Built for gaming chat, including roleplay. Write or speak in your own language, right where you already chat. ChatShift puts
the translation into your game or app's chat field. Review it before sending, or
enable automatic sending. No separate translation window during normal use.

**[Watch the ChatShift demo on YouTube](https://www.youtube.com/watch?v=0wfThs66Kjs)**
— a hands-on demonstration of Norwegian-to-English text and voice translation in Valheim.

**New here? Follow the [Quick start guide](GET_STARTED.md)** for installation,
text and voice setup, shortcuts and your first message.

**Windows installer:** `ChatShift-Setup.exe` is being reviewed before publication.
The new installer includes the runtime, text and voice dependencies; no Python or
source folder is needed. Follow the [Quick start](GET_STARTED.md).
[Published releases](https://github.com/toffenloffen/ChatShift/releases) may still
contain the older source-based ZIP until the installer is approved.

## Choose your platform

| Your device | Installation and status |
| --- | --- |
| **Windows PC** | [Install the Windows version](GET_STARTED.md). Early version with text, voice and experimental Xbox-compatible controller shortcuts. |
| **Steam Deck / SteamOS (Linux)** | [SteamOS development status](STEAMOS.md). A separate version is being developed; its installer is not published in this repository yet. |
| **Other Linux PCs** | No tested installer yet. SteamOS work does not automatically establish compatibility with every Linux desktop. |

**Work in progress — experimental prototype.** The Windows installer is for Windows
only. Downloading this repository on a Deck currently provides the Windows source,
not the separately developed SteamOS application.

Designed for people who find writing in another language difficult. ChatShift uses
context to interpret spelling mistakes, dialect and gaming terms, but translations
can still be wrong. Start with automatic sending off and check your first messages.

Roleplay dialogue, emotes and descriptive messages are welcome: the translator is
instructed to preserve character voice and detail, not summarize them. The current
limit is 1,000 characters per message; this is a game-chat tool, not a long-document editor.

## What is new

- **Optional local noise suppression:** DeepFilterNet3 cleans microphone audio before
  Whisper. Turn it on in Voice; no strength or threshold tuning is needed.
- **Hear and see the difference:** Mic Test shows actual Input/Output levels, with
  optional headphone listening and an on/off comparison. The separate speech test
  offers original/processed playback plus recognition and translation after Stop.
- **Stay visible at startup:** ChatShift no longer minimizes itself. **Run in background**
  is now at the top, between Help & setup and the status badge.
- **Settings grouped by mode:** Text and Voice each contain their own enable switch,
  shortcut and automatic sending option. Status and Pause stay visible at the bottom.
- **One controller picture:** normal buttons and L4/L5/R4/R5 appear together, with
  green selection highlights. Rear buttons open mapping guidance; they require
  Steam Input or compatible software and are not read independently by this Windows build.
- **Gaming vocabulary:** terms such as heal, DPS, aggro, OOM and interrupt are interpreted
  in context. This is not a complete game-location or character-name dictionary.
- **Guided Windows setup:** installs the text and voice dependencies, downloads the
  speech model and creates a desktop shortcut. Codex installation and sign-in remain your step.
- **Microphone test:** inspect recognized speech and its translation without sending
  a message to a game.

The new Windows Setup.exe installs ChatShift into your user account. Voice models
are downloaded from the welcome window with progress and a retry option.

## Features

- Translate your outgoing draft in place, without switching to a separate translation window.
- Choose both source and target from 26 languages. Matching languages correct typed text; voice provides dictation without translation.
- Context-aware [gaming vocabulary](GAMING_TERMS.md), including heal, DPS, aggro, CC and OOM.
- Gaming spelling hints for local speech recognition, shared by voice input and the microphone test.
- Choose a shortcut in the keyboard or mouse picture, with separate left/right modifier keys.
- Choose automatic sending separately in **Text** and **Voice**, or review before sending.
- Save your language, shortcut and sending preferences between sessions.
- See your shortcut highlighted on a keyboard, including left/right modifier keys or F10 alone.
- Open **Help & setup** for the official Codex setup link, usage instructions and troubleshooting.
- Disable text translation independently when you do not need it.
- Experimental **Controller** tab: choose up to three Xbox-compatible buttons for text
  or voice, with live connection/button status. See [controller setup](CONTROLLERS.md).
- Reuse recent identical translations to avoid unnecessary model requests.

**Experimental local voice:** included by **ChatShift-Setup.exe**. Enable **Voice input**.
In the Voice tab, click the pictured keys or mouse buttons to choose a voice shortcut.
Choose **Hold to talk** or **Press to start · press again to stop**. Wait for voice to load,
open your game's chat field, and speak using the shortcut. The language choices at the top
apply to both text and voice. Voice inserts a draft for review by default; its own checkbox
enables automatic sending after readback verification. Choosing a shortcut already used
by the other mode moves it to the mode you are editing.
Keep the same chat field active until insertion finishes.

Setup downloads and checks Whisper small; recognition runs locally on the CPU without a speech API key.
Audio stays on your PC; recognized text goes to Luna when languages differ.
**Voice → Speech and translation test → Test translation** opens a separate quality test that never sends anything into your game.
Optional DeepFilterNet3 noise suppression runs locally before recognition. Setup downloads
its model as well as Whisper. **Mic Test** shows the raw and filtered signal levels;
enable **Listen (headphones)** to compare with suppression on and off.
The creator has manually tested this version, but background music, singing and other
voices can still get through. This is not speaker identification or guaranteed silence.
Game integration and other hardware still need manual testing. See [voice status](VOICE.md).

ChatShift uses GPT-5.6 Luna through the installed Codex app server and your own ChatGPT
sign-in. Internet access and an eligible account are required; no API key is needed for
the current backend. It is an independent project, not an official OpenAI product.

**Compatibility:** most fields need selecting, copying and pasting. An optional experimental
Among Us adapter reads the existing field with local OCR and types the translation in place.
It passed a short local-lobby test at 2560×1440, but later field-detection failures remain.
Text use has been reported working in WoW and Valheim, and voice insertion was manually
tested in Valheim. Other configurations require individual testing. It translates your outgoing
draft, not other players' messages. See [compatibility findings](COMPATIBILITY.md).

## Use ChatShift

1. Choose **From** (your language) and **To** (the output language).
2. Open **Text**, **Voice** or **Controller** to choose your buttons. Enable Text or
   Voice in its own tab; both can stay on. Changes save automatically.
3. Wait for green **READY**. For speech, also wait for **Voice ready** in Voice.
4. Open a chat field. **Text:** write, press your shortcut once and release.
   **Voice:** hold your shortcut, speak and release, or select the press-to-start/stop option.
5. Stay in that field while ChatShift works. Read and send the result yourself,
   or enable automatic sending in the corresponding tab.

Short typed messages took about 1–3 seconds in limited local tests. Voice may take
longer. This is not a guaranteed timing. Do not type or press Enter while waiting.

**Run in background** hides the window; **Pause** stops shortcuts; closing exits.
For picture selection, combinations and first-use checks, see the [Quick start](GET_STARTED.md).
For rear-button mapping and gamepad limits, see [Controllers](CONTROLLERS.md).

## Install

Open **ChatShift-Setup.exe**, follow the installer, and choose **Prepare voice**
in the welcome window. Install/open Codex and sign in with your own ChatGPT account.
Open ChatShift from Start or the optional desktop shortcut. See [Quick start](GET_STARTED.md).

The installer is currently a review artifact, not a published release. Developers
can reproduce it with [Windows packaging instructions](packaging/README.md).
The legacy CMD/Python scripts are development tools, not the consumer install path.
Experimental Among Us OCR is a source-only feature and is not bundled in this installer.

The standard clipboard adapter uses only the Python standard library. It does not need an API key or a
downloaded local model. You must supply your own eligible ChatGPT/Codex account; this app
does not include an account, subscription or credits.

Official [Codex sign-in documentation](https://learn.chatgpt.com/docs/auth).

## Compatibility and limits

- The standard adapter requires Ctrl+A, Ctrl+C and Ctrl+V. This does **not** work in every game.
- Among Us uses an experimental visual adapter automatically when dependencies are installed.
  Use short, fully visible drafts in the tested 16:9 free-chat layout. The game must stay
  visible and focused. OCR can misread text; long drafts and other layouts are unverified.
  Replacement takes additional time per character, and output must fit 100 characters and
  be typeable with the active keyboard layout. No game files are modified.
- Use the shortcut only in an editable chat field. It translates the whole field, up to 1,000 characters.
- Ordinary Enter is sent. Applications requiring another send shortcut may only insert a newline.
- By default both Alt keys are intercepted with Enter, including an application's fullscreen shortcut.
  A custom shortcut may also conflict with shortcuts in other apps; choose one you do not already use.
- The clipboard is overwritten. Prior clipboard contents are not restored.
- Always open the chat field first. ChatShift cannot reliably detect whether game chat
  is open. Voice may still be processed and insertion attempted without an editable field.
- If focus or text changes, copying fails, the model fails, or pasting cannot be verified, sending stops.
  If a failure occurs after pasting, inspect the field before retrying.
- Translations can still be wrong. Review mode is recommended when accuracy matters.
- Games may restrict third-party input tools. Check the game's rules before using one.

## Privacy and usage

Only text captured by the translation shortcut is sent to OpenAI. In Among Us, a visible
game frame is captured in memory and cropped to the outgoing field and character counter
for local Windows OCR. Images are not saved or uploaded; incoming chat is not translated. Codex manages sign-in; ChatShift does not extract
or copy login tokens. Its app-server connection uses local stdin/stdout pipes, not an open network port.
The OpenAI service processes the text according to your account's data settings.

Recent messages and translations exist in memory: a model session is rotated after five
requests, and up to 64 identical translations are cached for five minutes. Cached results
are separated by source and target language and cleared when the app closes. ChatShift does not write
message contents to its settings or status files. Codex uses ephemeral sessions.

There is no continuous translation or polling of the model. One request warms it up at startup;
then one request is made per uncached translation. Only one translation runs at a time.
Codex adds fixed input context, so a short message can still use several thousand input tokens,
some cached. This is **not** a hard token-budget or spending-cap system. Usage consumes your
Codex allowance; API prices should not be treated as subscription charges.

See [REVIEW.md](REVIEW.md) for measured usage, tests and remaining limitations.

## Language checks

See the [260-case text evaluation and roleplay follow-ups](LANGUAGE_EVALUATION.md)
for actual outputs, targeted improvements and remaining issues. These are synthetic
text checks, not a guarantee for every language pair, speaker or game.

## Development

Close ChatShift before running the offline Windows tests:

```powershell
./.venv/Scripts/python.exe run_tests.py
```

Optional live tests use your Codex allowance and a disposable text field:

```powershell
./.venv/Scripts/python.exe -X utf8 "norsk engelsk/tests/benchmark_codex.py"
./.venv/Scripts/python.exe -X utf8 "norsk engelsk/tests/smoke_desktop.py" --codex --right-ctrl
```

The standard installer includes Pillow for smooth controller rendering. Development
dependencies are in `requirements-dev.txt`. Windows CI runs the offline tests and a
separate installation check that downloads and loads the speech model. These checks
do not replace physical controller and in-game testing.

The old local translator and API client are retained as experimental alternatives, but are
not used by the app. The optional local model has separate attribution in
[THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).

## License

ChatShift is free to use under the [ChatShift Free Use and Attribution License](LICENSE).
You may install and use it free of charge and send feedback or bug reports.
Keep the creator credit and do not claim you created ChatShift. This license does
not permit modification, redistribution, resale or paid access without separate
written permission from toffenloffen. Sharing the official project link, reviews,
demonstrations, and using ChatShift at work or in a monetized stream are allowed.
Contribution forks, changes for proposed contributions and pull requests to
the official project are welcome under the license's contribution exception.
Contributors retain rights in their own work; submitting a pull request does
not transfer ownership. GitHub's own viewing and forking rights still apply.

This is a **source-available license, not an OSI open-source license**. The change
does not revoke the MIT permissions on previously published versions or material;
those permissions still allow commercial reuse. The [previous MIT license](LICENSE-MIT-LEGACY.txt)
is retained for reference. Dependencies and downloaded models retain their own licenses.
