# Technical details and development

[Back to ChatShift](README.md)

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

