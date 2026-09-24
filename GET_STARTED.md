# Get started with ChatShift

**Write or speak. Press your shortcut. Chat in another language.**

This is an early Windows release for testing and feedback. It is not a standalone
installer, and support for every game or PC is not guaranteed.

## 1. Install

1. Install [Python for Windows](https://www.python.org/downloads/windows/).
   Python 3.13 is the version tested here. Include Tcl/Tk and the Python launcher.
2. Install [Codex](https://learn.chatgpt.com/docs/windows/windows-app).
   Open it, choose ChatGPT sign-in and follow the login steps using your own account.
   You do not need to write a prompt. Your account needs access to GPT-5.6 Luna in Codex.
3. On the ChatShift GitHub page, choose **Code → Download ZIP**, then extract the ZIP.
4. Open PowerShell in the extracted folder and run:

   ```powershell
   ./setup.ps1
   ```

5. If you want voice input, run this in the same folder:

   ```powershell
   ./.venv/Scripts/python.exe -m pip install -r requirements-voice.txt
   ```

6. Open the `norsk engelsk` folder and double-click **Start ChatShift.vbs**.
   Keep the extracted folder; the launcher needs it.

Internet and your own eligible Codex account are required for translation. No API key
is needed. Translation uses your account's Codex allowance. Voice recognition runs
locally and downloads its model on first use; this first startup can take longer.

If PowerShell blocks setup, follow your PC's script policy or report the error for
help. Do not change organization-managed security settings.

## 2. Choose your languages and buttons

Wait for the top-right badge to turn green and show **READY**. The translator is connected.

Choose **From** and **To**. These apply to both text and voice. Enable **Text translation**,
**Voice input**, or both. Select a shortcut in each mode's tab:

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

Read the result and send it yourself, or enable automatic sending separately for text
and voice. AI can misunderstand words, dialect and meaning.

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
| Voice does not start | Install the voice dependencies, enable voice, choose its shortcut and wait for Voice ready. |
| Wrong words | Check From and To. Turn off automatic sending and correct the draft. |
| Wrong microphone | Select your microphone in Voice and try Open test. |
| Works in one game only | Games handle input differently. Include the game and what happened in a bug report. |

[Report a problem](https://github.com/toffenloffen/ChatShift/issues). Include your Windows
version, game or app, text/voice mode, shortcut and what happened. Do not include passwords,
login tokens or private chat messages.

See the [README](README.md) for compatibility, privacy, usage and development details.
