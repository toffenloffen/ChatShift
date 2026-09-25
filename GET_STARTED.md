# Get started with ChatShift

**Write or speak. Press your shortcut. Chat in another language.**

This is an early Windows release. Setup includes both text and local voice support.
For Steam Deck / SteamOS or other Linux systems, see [platform status](STEAMOS.md);
do not run the Windows installer there.

Using a controller? See [controller setup](CONTROLLERS.md).

## 1. Install

**[Download ChatShift for Windows](https://github.com/toffenloffen/ChatShift/releases/latest/download/ChatShift-Setup.exe)**

1. Double-click **ChatShift-Setup.exe** and follow the Windows installer. It installs
   only for your Windows account, with Start Menu and desktop shortcuts.
   You do not need to install Python, extract a ZIP or keep a source folder.
2. Choose **Set up ChatShift** in the welcome window. Everything is prepared together. Internet is required for the
   Whisper small and DeepFilterNet3 models (about 500 MB). Progress shows the current
   step; downloads can take several minutes. Setup does not record the microphone.
3. If Codex is not ready, use **Setup** in ChatShift to install/open Codex and sign in with your
   own ChatGPT account. ChatShift cannot authenticate you. Your account needs Codex
   access; account usage limits apply. No API key or prompt is needed.
4. ChatShift opens automatically after preparation. Choose your languages and enable text or voice.

If a download fails, check internet access and free disk space, then choose **Try again**.
Diagnostic details are saved in the app data folder as `setup-error.log`. **ChatShift Setup** in Start
reopens preparation for all features.

Updates use the same installer. Close ChatShift first. Settings and model downloads
live in `%LOCALAPPDATA%/ChatShift`, separately from program files, and are preserved
by updates and uninstall. Remove ChatShift through Windows Settings → Apps.
An older source-folder installation is left untouched; its preferences are not
silently copied.

## 2. Choose your languages and buttons

Wait for the top-right badge to turn green and show **READY**. The translator is connected.

Choose **From** and **To**. These apply to both text and voice. Open **Text → Enable text translation** or **Voice → Enable voice input**.
Both can stay enabled. Select a shortcut in the matching tab:

- **One button:** left-click it in the keyboard or mouse picture.
- **A combination:** hold the right mouse button. Left-click the pictured buttons,
  one at a time. Release the right mouse button to save.
- **Remove:** click the selected button again.

Combinations support up to two modifier keys plus one main key or supported mouse button.
Dimmed keys are unavailable. Enter and Num Enter are separate. If the other mode uses
your chosen shortcut, it moves to the mode you are editing. The picture shows your selection.

Leave automatic sending off for your first test.

## 3. Chat

**Text:** open the game's chat, write a message, press your text shortcut once and release it.

**Voice:** wait for **Voice ready**, open the game's chat, hold your voice shortcut,
speak and release it. You can instead choose press once to start and again to stop.

Wait for the result. Stay in the same field and avoid typing or pressing Enter while
waiting. Short typed messages took roughly 1–3 seconds in limited local tests. Voice
may take longer. These are not guaranteed timings.

Read the result and send it yourself, or enable **Send automatically after translating**
in Text or **Send voice messages automatically** in Voice. These settings are independent. AI can misunderstand words, dialect and meaning.

Using a gamepad? Open **Controller** for its clickable diagram and see the
[controller guide](CONTROLLERS.md), including rear-button mapping. Status and Pause
stay visible at the bottom while you browse settings.

Want to check noise suppression? Enable **Voice → Noise suppression (DeepFilterNet3)**,
click **Mic Test**, and optionally enable **Listen (headphones)**. Input shows your
microphone before filtering; Output shows the filtered audio. Switch suppression off
and on while listening to compare. Click **Stop Test** when finished.

For text results, open **Voice → Speech and translation test → Test translation**.
Click **Start recording**, speak, then **Stop recording**. The test displays Whisper's
transcription and the translation, without writing into your game. **Listen: original**
and **Listen: processed** let you compare the same recording. Starting this recording
stops an active Mic Test first. Background voices and singing may still be recognized;
check the words as well as the sound.

## Good to know

- Always open a chat field first. ChatShift cannot reliably detect closed game chat;
  it may still process speech and attempt insertion when no chat is open.
- ChatShift translates your outgoing messages, not messages from other players.
- The window stays open at startup. **Run in background** at the top hides it when you choose.
  **Pause** stops shortcuts. Closing exits the app.
- Audio stays in memory on your PC. Text goes to OpenAI when translation is needed.
- Your clipboard is overwritten during insertion. Check the field before retrying a failure.
- Microphone selection currently resets to the Windows default when you restart.
- SteamOS support is not implemented in this version.

## Something did not work?

| Problem | Try this |
|---|---|
| Not READY | Check internet, open Codex and sign in, then restart ChatShift. |
| Shortcut does nothing | Enable the mode, unpause, check its highlighted shortcut and open the chat field. |
| Voice does not start | Rerun setup if it failed, enable voice, choose its shortcut and wait for Voice ready. |
| Wrong words | Check From and To. Turn off automatic sending and correct the draft. |
| Wrong microphone | Select your microphone in Voice and try Open test. |
| Works in one game only | Games handle input differently. Include the game and what happened in a bug report. |

[Report a problem](https://github.com/toffenloffen/ChatShift/issues). Include your Windows
version, game or app, text/voice mode, shortcut and what happened. Do not include passwords,
login tokens or private chat messages.

See the [README](README.md) for compatibility, privacy, usage and development details.
