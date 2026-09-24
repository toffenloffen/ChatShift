# Voice input

Voice input into the focused chat field is now **experimental and ready for manual game testing**.
The Voice tab offers an independent shortcut, hold-to-talk or toggle mode, microphone selection,
and optional automatic sending. Source and target languages at the top apply to both text and voice.
Voice is off by default and has no default shortcut. Enable it, choose a shortcut in the picture,
wait for Voice ready, and open a chat field before speaking. Release in hold mode, or press again
in toggle mode. Choosing a shortcut used by the other mode moves it to this mode.
Review before sending is the default.
Whisper receives short gaming vocabulary hints, such as healer, DPS and aggro.
These guide recognition without forcing replacements; check ordinary speech and game
names too. Recognition quality still needs testing with your voice and game audio.
Focus changes, other input, pause or closing cancel pending delivery. The recorder has a 30-second limit.
Automatic sending requires a verified readback and never sends on a failed verification.

The Voice tab also offers **Microphone test → Open test**. Run **Install ChatShift.cmd** first. Setup installs dependencies and downloads
the multilingual Whisper small model; it loads on first use and runs
on the CPU with four threads; no NVIDIA GPU or speech API key is required.
Recordings begin only after clicking Start recording, stop after at most 30 seconds,
and remain in memory on the PC. The test displays recognized text and, when the
chosen languages differ, sends that text to the existing Luna translator. It never
types or sends anything into another application. Norwegian dialect was manually tested,
with useful results and some mistakes; other speakers and dialects still need testing.
Microphone selection is available; close the test to cancel and release the device.
Standard setup includes voice dependencies and the model. Recording remains off until enabled.
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

## Testing and remaining limits

Norwegian dialect and gaming terms have been tried in the quality-test window. Synthetic speech and silence were also tested. Automated delivery tests
cover default review mode, explicit auto-send, cancellation, changed input, focus changes and
failed readback; recorder tests cover length limits, overflow and device cleanup.
Hold/toggle lifecycle and clickable voice bindings passed a mocked hidden-window UI check.
Physical voice shortcuts and insertion have also been tested manually in Valheim.
Other games and PC configurations still need testing. The app cannot reliably detect
whether game chat is open: always open the chat first, or it may still process speech
and attempt insertion without a text field.
SteamOS and other Windows hardware are unverified. The microphone selection currently resets
to the Windows default on restart; shortcut, enable state, hold/toggle and send preference persist.
