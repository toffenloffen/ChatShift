# SteamOS development notes

The published code in this repository is the Windows prototype. A separate SteamOS
version is under development on Steam Deck, with controller bindings reported in its UI.
That code and a tested SteamOS installer have not yet been published here.
No Linux compatibility is claimed for the Windows installer.

Windows now has experimental controller support; see [controller notes](CONTROLLERS.md)
for the portable chord logic and the Windows-specific parts to compare with the Deck work.

## Get the source on Steam Deck

In Desktop Mode, download **Code → Download ZIP** from GitHub and extract it, or clone:

```sh
git clone https://github.com/toffenloffen/ChatShift.git
cd ChatShift
```

The Windows launcher and PowerShell setup scripts do not install a SteamOS version.
Do not expect installing the Python dependencies alone to make the app run on Linux.

## Porting work still needed

- Replace `windows_input.py`: Win32 keyboard hooks, window/focus checks, clipboard,
  synthetic input and single-instance handling are Windows-specific.
- Replace the Among Us Windows OCR/capture implementation. Its current layout-specific
  reader is experimental and has failed field detection in live use.
- Separate platform adapters from the translation transaction and user interface so
  portable modules can load without importing Windows DLLs.
- Implement and test Linux discovery and startup of the translation backend. The current
  executable lookup searches for `codex.exe` and Windows installation paths.
- Evaluate shortcuts, capture and input separately in Desktop Mode and Gaming Mode;
  neither environment has been validated. Preserve focus, cancellation and verification
  checks instead of assuming injected text reached the correct field.
- Add a Linux test suite, install instructions and actual Deck/game integration tests.

## Behaviors to preserve

Write in the original game's chat field, trigger one customizable shortcut, translate,
verify replacement and optionally send. No separate composer. Keep model requests bounded,
do not store chat messages or credentials in the repository, and stop on ambiguous capture
or focus changes. The Windows version already passes the selected source and target languages to the
translator and the source language to local speech recognition. Preserve these choices
in the SteamOS implementation.

See `COMPATIBILITY.md` for observed Windows results and limitations. This document is a
development checklist, not a claim that SteamOS support already works.
