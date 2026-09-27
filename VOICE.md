# Cloud voice in ChatShift

This development version replaces local Whisper and DeepFilterNet with experimental
ChatGPT cloud dictation. The published older installer may still use local voice.
No speech models are downloaded or loaded by the cloud build. Existing model files
are not deleted. The text translation model and instructions are unchanged.

Enable Voice, choose your microphone and shortcut, then speak in your chat field.
Recording stops on release, a second press, or after 30 seconds. Audio is sent to
OpenAI when recording stops; the recognized text is translated when languages differ.
Review the inserted draft before sending. Keep the field focused until it finishes.

The local Mic Test only monitors the microphone. The Speech and translation test
uploads its recording after Stop, shows both texts, and never writes into a game.

## Account and privacy

Uses your ChatGPT sign-in through Codex, without an API key. The internal dictation
endpoint is experimental, not a publicly supported third-party API. Availability
can change. Pro was tested in the demo; Free voice access is unverified. Earlier
free-account word/allowance measurements describe text translation, not dictation.

Microphone audio is converted to mono PCM WAV in memory. ChatShift does not save
recordings or transcripts to disk. Codex supplies a credential in memory, sent only
to the fixed ChatGPT HTTPS host. Redirects are rejected; credentials are not logged
or saved by ChatShift. OpenAI processes uploaded audio under the service/account
settings. An upload already in progress cannot be recalled. Cancellation prevents
later translation and insertion; connections have timeouts and are cleaned up.

On migration from local voice, Voice starts disabled until you enable it again.
There is no background microphone recording and no automatic fallback to local AI.

If your microphone cannot open, choose another input and check Windows permissions.
Access or quota errors are displayed, not bypassed. A successful test on one PC does
not establish the cause of a crash on another PC.
