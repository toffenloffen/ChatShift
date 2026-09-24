# Controller shortcuts on Windows

This is experimental XInput controller support. Automated dispatch tests pass;
physical controller and in-game behavior still need testing.

1. Connect an Xbox-compatible controller by USB or Bluetooth.
2. Open **Controller**, enable controller shortcuts, and choose its slot (1–4).
   The status shows whether that slot is connected and which buttons are pressed.
3. Select **Text** or **Voice**, check up to three buttons, and click **Save controller shortcut**.
   Uncheck every button and save to remove it. An overlapping shortcut moves from the other mode.
4. Enable text translation or voice input as usual. Wait for the translator and, for voice,
   the local speech model to be ready. Open the game chat before using the shortcut.
5. Text activates on release. Voice follows the hold/toggle setting in the Voice tab.

Keyboard and mouse shortcuts remain available. Controller choices are saved locally.
Pausing ChatShift disables controller actions too. Reconnection requires releasing all
buttons before a new shortcut can activate. Disconnecting cancels a controller voice message.

**Buttons still reach the game.** ChatShift does not suppress XInput game actions.
Choose an unused combination and test with automatic sending off. D-pad directions,
A/B/X/Y, bumpers, triggers, stick clicks, View and Menu are supported. Stick movement
is not a shortcut. Controller button names follow Xbox labels.

**Rear paddles and Steam Deck back buttons:** Windows XInput does not expose them as
separate buttons here. Use supported controller software or Steam Input to map them to
a keyboard shortcut, then select that shortcut in ChatShift's Text or Voice tab.
Do not assume a rear paddle is independent if it duplicates a normal game button.

## Sharing work with SteamOS

The button-chord state machine in `controller_input.py` can be reused by a Linux input
adapter. `XInput` and the current UI dispatch into Windows input handling are Windows-only.
Compare and integrate the separately developed SteamOS implementation before replacing
its input code. Test Desktop Mode and Gaming Mode independently, including hold/toggle,
focus changes, disconnects and conflicts with game controls.
