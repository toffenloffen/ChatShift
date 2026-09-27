# Streaming voice

Microphone → optional local DeepFilter noise suppression → OpenAI speech transcript
→ Luna translation → your chat field. Same-language Voice skips translation.
Text, Voice and Controller have independent language pairs; the speech test uses Voice.

Enable Voice, select your microphone and hold the shortcut or use toggle mode.
Audio streams while you record. Release stops the microphone; 0.9 seconds of silence
helps preserve the last words. Warm connections expire after 60 seconds idle and
never open the microphone. Maximum recording: 30 seconds. Speed/accuracy can vary.

## Why I changed it

In my tests, this handled my Norwegian dialect better. Removing local Whisper also
avoids its large model download and CPU/RAM workload. DeepFilter remains local and
still uses resources. The cause of the previous crash on another PC remains unknown.

## Account and privacy

Both voice and Luna use ChatGPT sign-in through Codex, without an API key or separate
API billing setup. Install and sign in to Codex; the ChatGPT app alone is not enough.
**New voice access on a free account has not been verified.** My earlier free-account
text test does not establish voice availability. Account limits apply.

Voice uses gpt-live-1-codex through experimental app-server WebRTC. Only user
transcripts go to Luna; assistant output is ignored. This is not a supported public
third-party dictation API and availability may change. Access errors are not bypassed.

ChatShift holds audio/transcripts in memory and does not save them to disk. The speech
test retains original/filtered audio for playback until the next recording or closing
its window. Diagnostic files contain timings only. Translations have a short-lived
in-memory cache. Codex manages authentication and ephemeral sessions. OpenAI processes
streamed audio/text under its applicable service/account settings; cancellation cannot
recall audio already sent. This does not promise zero retention by OpenAI.

Mic Test is local and does not upload. Speech and translation test streams audio,
shows both texts and never types into a game. Review drafts before sending.
