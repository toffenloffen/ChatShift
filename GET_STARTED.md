# Get started with ChatShift

**Write or speak. Press your shortcut. Chat in another language.**

Choose local Whisper or experimental online voice recognition. Translation requires
internet and ChatGPT sign-in through Codex. Online voice access with Plus is awaiting testing.
For Steam Deck / SteamOS or other Linux systems, see [platform status](STEAMOS.md);
do not run the Windows installer there.

Using a controller? See [controller setup](CONTROLLERS.md).

## 1. Install

**[Download ChatShift for Windows](https://github.com/toffenloffen/ChatShift/releases/latest/download/ChatShift-Setup.exe)**

1. Double-click **ChatShift-Setup.exe** and follow the Windows installer. It installs
   only for your Windows account, with Start Menu and desktop shortcuts.
   You do not need to install Python, extract a ZIP or keep a source folder.
2. Read the welcome screen and click **Open ChatShift**. Noise suppression is included.
3. Sign in to Codex with your own ChatGPT account, then choose your languages and shortcuts.
4. In **Voice → AI models**, choose a model and click **Activate selected model**.
   Enable **Voice input**. Local Whisper files download on first use; the two online
   options are marked **Experimental** and send audio to OpenAI.

Updates preserve settings and model caches. The removed **ChatGPT dictation · cloud**
option is no longer available. If you previously selected it, choose a remaining model
and enable Voice again. Other saved model selections are retained.

## 2. Choose your languages and buttons

Wait for the top-right badge to turn green and show **READY**. The translator is connected.

Choose **From** and **To** separately in **Text**, **Voice**, and **Controller**. Click the swap arrows to reverse the pair. The speech test uses Voice. Open **Text → Enable text translation** or **Voice → Enable voice input**.
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

Click **Mic Test** to check your microphone levels and optionally listen through headphones.
This monitor does not upload audio. Stop the test when finished.

**Speech and translation test** uses your selected Voice model and language pair.
GPT-Live streams audio while recording; GPT-Transcribe uploads it after Stop;
local Whisper recognizes it on your PC. The test displays the transcript and
translation without typing in your game. Original playback stays in memory until the window closes or you record
again. Closing cancels subsequent translation/insertion; an upload already in
progress cannot be recalled.

## Good to know

- Always open a chat field first. ChatShift cannot reliably detect closed game chat;
  it may still process speech and attempt insertion when no chat is open.
- ChatShift translates your outgoing messages, not messages from other players.
- The window stays open at startup. **Run in background** at the top hides it when you choose.
  **Pause** stops shortcuts. Closing exits the app.
- Online voice sends audio to OpenAI; local voice does not. Text goes to OpenAI when translation is needed.
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
