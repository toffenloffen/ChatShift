# ChatShift

**Write your way. Chat with the world.**

**Work in progress — experimental prototype.** The current implementation runs on
Windows. SteamOS / Steam Deck support is a planned development direction and is **not
implemented yet**. Downloading this repository on a Deck gives you the source code,
not a working SteamOS application. See [SteamOS development notes](STEAMOS.md).

ChatShift is an experimental Windows desktop app that translates the message you are
writing directly in a supported chat field. You write in Norwegian, press your chosen
keyboard shortcut, and the app replaces your draft with a translation into your selected
language. It can then send the message automatically, or leave it for you to review.

It is designed for people who want to join a conversation without stopping to translate
every message manually. That includes gamers, people less comfortable writing in another
language, and people with dyslexia or other spelling difficulties. The translator is
instructed to interpret Norwegian spelling mistakes, dialect and gaming terms in context,
so you do not have to write perfect Norwegian first. It can still misunderstand a message.

For example, the intended meaning of a message like **“kan du hile meg, æ e såra”** is
**“Can you heal me? I'm hurt.”** The goal is to translate what you mean, including gaming
slang, rather than turn every misspelled word into a literal translation. This example
illustrates the intended behavior; individual model responses can vary.

## Features

- Translate your outgoing draft in place, without switching to a separate translation window.
- Choose from 26 target languages. The current source language is Norwegian.
- Record your own keyboard shortcut, with separate support for left and right modifier keys.
- Send automatically after translation, or review the translated draft before sending.
- Save your language, shortcut and sending preferences between sessions.
- Reuse recent identical translations to avoid unnecessary model requests.

ChatShift uses GPT-5.6 Luna through the installed Codex app server and your own ChatGPT
sign-in. Internet access and an eligible account are required; no API key is needed for
the current backend. It is an independent project, not an official OpenAI product.

**Compatibility:** most fields need selecting, copying and pasting. An optional experimental
Among Us adapter reads the existing field with local OCR and types the translation in place.
It passed a short local-lobby test at 2560×1440, but later field-detection failures remain.
The user reported successful WoW use; other configurations require individual testing. It translates your outgoing
draft, not other players' messages. See [compatibility findings](COMPATIBILITY.md).

## How it works

1. Open ChatShift and choose your target language. You can also choose **Change shortcut**.
2. Write your message in a supported chat field. The current version accepts Norwegian input;
   support for more input languages is planned.
3. Press your shortcut once, then release the keys. The default is **Right Ctrl + Enter**;
   **Alt + Enter** also works with the default settings.
4. Stay in the same field. ChatShift replaces the text with its translation and sends Enter.

**Press once, then wait about 1–3 seconds.** This is an approximate range from limited
local tests, not a measured average or a guarantee; it can take longer. Avoid typing or
pressing the shortcut or Enter again while waiting. Pressing Enter can send the original
message before translation finishes.

Open ChatShift from the taskbar to choose one of 26 target languages or turn off automatic
sending to review the translation first. Source text is currently Norwegian. Preferences
are saved automatically. The app starts ready in the background after warming up.

Choose **Change shortcut**, hold Ctrl or Alt (optionally Shift), and press your preferred
key. Left and right modifier keys are distinguished. Your saved combination replaces both
default shortcuts. Escape cancels recording; **Restore default** restores the original keys.

## Install

Requirements: Windows, Python 3.11+ with Tcl/Tk, and Codex installed and signed in with ChatGPT.
The account must have access to GPT-5.6 Luna in Codex. Internet access is required.
Tested locally with Windows and Python 3.13. Other Windows configurations are not yet verified.

1. Download or clone this repository.
2. Run `./setup.ps1` in PowerShell from the project directory.
3. Open `norsk engelsk/Start ChatShift.vbs`.

For experimental Among Us support, also run `./setup_ocr.ps1` and restart ChatShift.
Windows OCR support for Norwegian and English (United Kingdom) must be installed.

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
are separated by target language and cleared when the app closes. ChatShift does not write
message contents to its settings or status files. Codex uses ephemeral sessions.

There is no continuous translation or polling of the model. One request warms it up at startup;
then one request is made per uncached translation. Only one translation runs at a time.
Codex adds fixed input context, so a short message can still use several thousand input tokens,
some cached. This is **not** a hard token-budget or spending-cap system. Usage consumes your
Codex allowance; API prices should not be treated as subscription charges.

See [REVIEW.md](REVIEW.md) for measured usage, tests and remaining limitations.

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

The visual preview script needs Pillow (`pip install -r requirements-dev.txt`). Pillow is
not needed for the standard clipboard adapter; the optional OCR adapter does require it. A Windows CI workflow runs only offline tests.

The old local translator and API client are retained as experimental alternatives, but are
not used by the app. The optional local model has separate attribution in
[THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).

## License

ChatShift source code is provided under the MIT license. Dependencies and downloaded models
retain their own licenses. See [LICENSE](LICENSE).
