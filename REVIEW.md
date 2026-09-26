# Pre-publication review — 2026-09-14

## Result

Suitable for an **experimental Windows release**, with the limitations in README.md.
No critical issue was identified in the tested paths. This is a local engineering review,
not an independent security audit or a guarantee of compatibility with every application.

## Verification performed

- 59 offline tests passed again on Windows / Python 3.13 on 2026-09-14. Coverage includes shortcut interception,
  duplicate triggers, stale clipboard data, changed drafts, focus changes, cancellation,
  failed model responses, paste verification, response routing, settings validation,
  language-specific caches, cache expiration, connection failure, shortcut recording,
  custom bindings and persistence across restarts.
- The settings window was rendered and visually inspected. Visible controls fit in the
  default window; the language selector, status and review-mode control are in English.
- Live translation switched from English to French, German and back to English. Example:
  `har vi en druid som kan hile ås` → `Est-ce qu’on a un druide qui peut nous soigner ?`
- Full French shortcut → capture → translate → paste → verify → Enter test passed in a
  disposable Windows text field in **1.58 seconds**. This did not publish an external message.
- An instruction-like source sentence was translated as text, not obeyed.
- Custom Ctrl+Shift+T completed a live English translation and send in **3.07 seconds**.
  The previous Right Ctrl+Enter shortcut passed through without triggering translation.
  Some desktop attempts stopped on changed text or failed capture, and one on missing
  external focus; the desktop integration is sensitive to focus, field and input timing.
  Successful runs do not establish reliability in other applications or games.
- A repeated identical message returned the cached translation with no additional model call.
- Source candidates were scanned for common API-key/token/private-key patterns and the
  local absolute home-directory path; no matches were found. Environment, model,
  status and preference files are ignored by Git. Pattern scanning cannot prove absence
  of every possible secret.
- Setup PowerShell syntax validated. GitHub Actions is configured, but has not run on GitHub.

## Token usage

### Local latency changes awaiting joint game testing — 2026-09-14

- Removed a 40 ms caret-repaint pause after the initial clipboard capture. The
  subsequent original-draft, focus and pasted-output checks remain in place.
- Prepare the next five-request session on the delivery worker after successful
  delivery, instead of waiting until the next uncached message. This makes no model
  request and preserves the existing model, prompt, effort, cache and rotation limit.
  If preparation fails, reconnect on the next translation without retrying delivery.
- 62 offline tests pass. Real game latency and reliability have not been remeasured;
  further manual game testing is pending. No large speedup is claimed.

Observed new requests used approximately **3,992–4,707 input tokens**, of which **0–3,840
were reported as cached**, and around **16–30 output tokens**. The fixed Codex context is
much larger than a short chat message. Do not interpret this as a direct dollar charge or
an exact Codex-quota estimate; subscription accounting is controlled by OpenAI.

Controls in this build:

- GPT-5.6 Luna, low reasoning effort, one request at a time.
- One startup warmup; no model calls while idle.
- Maximum 1,000 input characters; successful output checked against a 2,000-character limit.
- Five-request conversation rotation limits history growth.
- Up to 64 identical translations reused in memory for five minutes, separately per target language.
- Thirty-second turn timeout and no automatic retry of a failed translation.
- Reported request and token counts in the local status file, without message content.

These controls limit waste, but **are not a hard spending or daily token cap**. Output
validation happens after generation, and a failed request may still consume allowance.

## Remaining limitations before broad distribution

- The experimental Among Us OCR adapter passed a short in-place replacement test (2.30s)
  and a separate automatic-send test (2.39s) in a 2560×1440 local lobby. All 59 offline
  tests passed. In my later attempt, the app failed to identify the chat field/counter, so
  Among Us support is not yet reliable. WoW worked in my tests, with chat
  remaining focused during translation. Longer messages and other layouts remain unverified; see
  [COMPATIBILITY.md](COMPATIBILITY.md). Do not advertise universal game compatibility.
- Clipboard contents are overwritten. A supported text field is required.
- Checking text/focus and then injecting keys is not an atomic operating-system operation.
  Avoid changing windows or typing while insertion is happening.
- There is no signed installer, packaged executable, automatic updater, or clean-machine
  install test yet. The initial release requires Python and Codex.
- The app-server protocol and model availability can change. No fallback model is silently selected.
- Target-language quality has only been spot-checked; not all 26 listed languages were evaluated.
- Recent message content exists temporarily in process memory and in OpenAI's service,
  subject to account settings; this is not an offline tool.

Publication status is tracked in the repository history; this document records test findings.

## Clipboard delivery optimization — pending game validation

The paste payload now remains in the clipboard during final verification; a fresh
clipboard sequence update is required after Ctrl+C, so the payload alone cannot pass
verification. The fixed post-paste pause was reduced from 160 to 20 ms. Selection timing,
original-draft checks, focus checks and exact output comparison remain in place.
A disposable Tk field measured 0.33 s before and 0.19 s after using an immediate fake
translator (single successful measurements, not averages or model timings). Earlier
attempts failed capture; the app and smoke-test hook were found running concurrently.
After closing the app, the integration test and all 64 offline tests passed. Real games
still need joint testing; these results do not establish unchanged game compatibility.

## End-to-end timing investigation

Two real Luna tests in a disposable Tk field measured 2.091 s and 1.355 s from
worker start to observing the field Return handler. Translation/backend time was
1.812 s and 1.078 s; local input work was approximately 0.28 s in both runs.
The second backend breakdown was: lock 0 ms, session preparation 0 ms, request
acknowledgement 1.7 ms, generation/network 1058.9 ms, completion processing 17.4 ms.
These two runs identify backend response latency as the largest measured component;
they do not isolate network from model computation or reproduce my exact
three-second observation in Codex chat.

The live app now timestamps shortcut interception and records stage offsets and
backend durations in ignored status.json without message contents. The displayed
time includes capture and release waiting and ends at Enter injection. It does not
claim that the receiving chat service has displayed or delivered the message.
All 64 offline tests passed after instrumentation. Model and prompts are unchanged.

## Text and voice preview publication — 24 September 2026

66 selected offline tests passed for voice delivery, recording, microphone choices,
shortcuts, keyboard selection, settings, translation and text transaction handling.
The selected tests mock input delivery and do not type into the user's active game.
The full input-injection suite was not rerun during the active gaming session.
I confirmed manual voice insertion in Valheim in my own testing. This is a limited
preview validation, not a security audit or a guarantee for every PC and game.
