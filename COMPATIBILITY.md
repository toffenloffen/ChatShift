# Game compatibility — 2026-09-13

## Among Us: experimental in-place OCR adapter

The installed Steam version was tested in a local lobby at 2560×1440 with free chat open.
The shortcut registers, but Ctrl+A/C does not expose the draft, and Windows accessibility
exposes only a game pane. The optional adapter therefore uses local Windows OCR to read
only the outgoing field and its character counter, then replaces text using paced keys.
No separate composer, game modification or broad background keystroke tracking is used.

Verified live:

- `hei` became `Hi.` in the existing field in review mode: 2.30 seconds.
- A subsequent shortcut with automatic sending enabled sent `Hi.` into the lobby: 2.39 seconds.
  The message was visible in chat and the draft counter returned to 0/100.
- Earlier window-based capture returned stale frames after edits. Capturing the visible
  screen region fixed the observed failure.
- 59 offline tests passed, including changed-draft, failed-clear, incomplete-output,
  review-mode and character-counter rejection cases.

These are short smoke tests, not proof of general OCR accuracy. Longer sentences,
diatrics, alternate resolutions, gameplay meetings and other output languages need testing.
The adapter accepts 16:9 windows at least 1280 pixels wide, but only 2560×1440 was live-tested.
It checks the counter against recognized length; equal-length OCR errors can still pass.
Clipped text, unsupported keys and oversized translations are rejected. Failures after
replacement starts may leave an empty or partial draft; inspect it before retrying.
Do not type, close chat, switch windows or cover the field while a translation runs.

Install optional dependencies with `./setup_ocr.ps1`. Windows OCR languages Norwegian and
English (United Kingdom) are required. Frames exist only in memory, are cropped for local
OCR and are never uploaded. Only recognized outgoing text goes to the translation service.
OCR adds no model request; longer drafts take longer to delete and type.

The [AUnlocker implementation](https://github.com/astra1dev/AUnlocker/blob/main/src/Patches/ChatPatches.cs)
provides supporting evidence that ordinary clipboard shortcuts are insufficient in this
field. No code from it was copied and no mod was installed.
[Windows OCR](https://learn.microsoft.com/en-us/uwp/api/windows.media.ocr.ocrengine)
provides the local recognition service.

## Follow-up reports

The user subsequently reported another Among Us attempt doing nothing. The runtime status
reported that the chat field and character counter could not be identified. The earlier
short successful tests therefore do not establish reliable Among Us support.

## World of Warcraft and other games

The user reported successful translation in WoW with the standard clipboard adapter.
Chat remains open during translation, preventing normal movement using typing keys.
This behavior is intentionally retained. The exact WoW version and configuration were
not recorded; this is a user report, not an independently repeated integration test.
Other games still require individual testing. Universal compatibility is not claimed.
