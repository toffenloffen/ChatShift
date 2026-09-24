# Get started with ChatShift

**Write or speak. Press your shortcut. Chat in another language.**

This is an early Windows release. Setup includes both text and local voice support.
For Steam Deck / SteamOS or other Linux systems, see [platform status](STEAMOS.md);
do not run the Windows installer there.

Using a controller? See [controller setup](CONTROLLERS.md).

## 1. Install

1. [Download ChatShift-Windows.zip](https://github.com/toffenloffen/ChatShift/releases/latest/download/ChatShift-Windows.zip) and choose **Extract all**. Keep the extracted folder in a permanent location.
2. Double-click **Install ChatShift.cmd**. Follow any installer prompts.
   It installs Python 3.13 if needed through Windows Package Manager, installs voice
   dependencies, downloads and checks Whisper small, and creates a desktop shortcut.
   Internet is required. The model is several hundred MB; setup may take several minutes.
   Wait for **Setup complete**. No microphone recording is made during setup.
3. Install [Codex](https://learn.chatgpt.com/docs/windows/windows-app), open it,
   and sign in with your ChatGPT account. No prompt or API key is needed.
   Your account must have access to the model ChatShift uses; usage limits apply.
4. Open **ChatShift** from the desktop. Enable voice in the app if you want to use it.

If setup fails, the window stays open with the error. Fix it and run the same file again.
If Windows Package Manager is unavailable, install Python 3.13 from python.org with
Tcl/Tk and the Python launcher, then rerun setup. Follow your organization's security policy.

This is a guided setup, not a standalone EXE. Codex sign-in is still your own step.
Keep the extracted folder: the desktop shortcut needs it.

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

Want to test the microphone first? Open **Voice → Microphone test → Open test**.
Record a short sentence. The test shows the result without writing into your game.

## Good to know

- Always open a chat field first. ChatShift cannot reliably detect closed game chat;
  it may still process speech and attempt insertion when no chat is open.
- ChatShift translates your outgoing messages, not messages from other players.
- **Run in background** hides the window. **Pause** stops shortcuts. Closing exits the app.
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
