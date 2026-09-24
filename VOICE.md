# Voice input

Voice input into the focused chat field is now **experimental and ready for manual game testing**.
The Voice tab offers an independent shortcut, hold-to-talk or toggle mode, microphone selection,
and optional automatic sending. Source and target languages at the top apply to both text and voice.
Voice is off by default and has no default shortcut. Enable it, choose a shortcut in the picture,
wait for Voice ready, and open a chat field before speaking. Release in hold mode, or press again
in toggle mode. Choosing a shortcut used by the other mode moves it to this mode.
Review before sending is the default.
Focus changes, other input, pause or closing cancel pending delivery. The recorder has a 30-second limit.
Automatic sending requires a verified readback and never sends on a failed verification.

The Voice tab also offers **Microphone test → Open test**. Install `requirements-voice.txt`
first. It downloads the multilingual Whisper small model on first use and runs
on the CPU with four threads; no NVIDIA GPU or speech API key is required.
Recordings begin only after clicking Start recording, stop after at most 30 seconds,
and remain in memory on the PC. The test displays recognized text and, when the
chosen languages differ, sends that text to the existing Luna translator. It never
types or sends anything into another application. Norwegian dialect was manually tested,
with useful results and some mistakes; other speakers and dialects still need testing.
Microphone selection is available; close the test to cancel and release the device.
Dependencies and model loading are optional so text-only users do not need them.
Windows is the current test platform; SteamOS microphone and game integration are untested.

## Intended user experience

- Windows first; SteamOS integration and game testing later.
- Type directly in a game's chat as today, or speak without moving to another composer.
- Enable text and voice independently. Both may be enabled together.
- Voice gets its own customizable shortcut and keyboard diagram, separate from text.
- Choose hold-to-talk or press-once-to-start / press-again-to-stop.
- Select source and destination languages. Matching languages means dictation without translation.
- Voice inserts an **unsent draft** by default, independently of text auto-send preferences.
- The user may opt into automatic sending using the separate voice checkbox.
- Prioritize dialect and gaming terminology, and measure release-to-draft latency.
- Cancel delivery if focus changes or the user edits the field. Never redirect into another window.
- Show clear recording, processing and ready states; bound recording duration and stop on cancellation.
- No API credentials in source, logs or shared settings. No audio recording before an explicit user action.

## Access investigation (24 September 2026)

The installed Codex app-server schema accepts local audio inputs, but a synthetic English
audio probe sent to the existing Luna text backend returned that it could not transcribe
the audio. This is not evidence that every OpenAI model lacks audio support.

The app-server's realtime connection was also tested using synthetic audio only.
Both the default connection and V3 audio mode returned `realtime conversation requires API key auth`.
V3 with text output instead returned `text realtime output modality requires realtime v2`.
No user's microphone was recorded; no playback or game input was used.

The documented desktop dictation feature inserts speech into the desktop app's own composer.
An external-app dictation interface using the existing ChatGPT sign-in has not been established.

- [Desktop dictation documentation](https://learn.chatgpt.com/docs/prompting)
- [App-server integration](https://learn.chatgpt.com/docs/app-server)
- [OpenAI speech-to-text API](https://developers.openai.com/api/docs/guides/speech-to-text)

The user initially declined a local speech recognizer, then explicitly authorized
trying one. Local transcription is now the chosen experiment; Luna still uses the
existing account. Separate paid speech API use has not been agreed.

## Still required for a working release

The user accepted local recognition after testing real Norwegian dialect and gaming terms in
the quality-test window. Synthetic speech and silence were also tested. Automated delivery tests
cover default review mode, explicit auto-send, cancellation, changed input, focus changes and
failed readback; recorder tests cover length limits, overflow and device cleanup.
Hold/toggle lifecycle and clickable voice bindings passed a mocked hidden-window UI check.
Physical voice shortcuts and insertion have also been tested manually in Valheim.
Other games and PC configurations still need testing. The app cannot reliably detect
whether game chat is open: always open the chat first, or it may still process speech
and attempt insertion without a text field.
SteamOS and other Windows hardware are unverified. The microphone selection currently resets
to the Windows default on restart; shortcut, enable state, hold/toggle and send preference persist.
