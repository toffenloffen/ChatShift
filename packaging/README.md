# Windows Setup.exe

Build on Windows x64 with Python 3.13 (including Tcl/Tk) and Inno Setup 6.7.3.
The build is an allowlist of application modules/assets and installed dependencies;
it never copies `.settings.json`, `.controller.json`, credentials, model caches or
the developer source tree into the product. No code signing certificate is configured.

```powershell
python -m venv .build-env
.build-env/Scripts/python.exe -m pip install -r packaging/requirements-build.txt
.build-env/Scripts/python.exe packaging/prepare_test_assets.py
.build-env/Scripts/python.exe packaging/fetch_sources.py
.build-env/Scripts/python.exe packaging/build_windows.py
.build-env/Scripts/python.exe packaging/test_suite.py
```

Pass the path to `ISCC.exe` as the optional argument to `build_windows.py` if it
is not under Program Files (x86). Output: `dist/ChatShift-Setup.exe`.
The Python runtime, speech-engine dependencies and DeepFilter noise models are bundled.
Optional Whisper models download only when a selected local engine is first used.
Opening the welcome window and self-tests never record audio or contact a speech service.
Codex is external, and installation/sign-in are explicitly guided, never automated.

For an isolated test while another ChatShift is running, compile the same payload
with a distinct registration ID and output filename:

```powershell
ISCC.exe /DAppIdValue=ChatShift.IsolatedInstallerTest /DGroupNameValue=ChatShiftInstallerVerification /FChatShift-Test-Setup packaging/ChatShift.iss
```

Run `packaging/test_installer.ps1` for install, update and uninstall checks in a
disposable workspace. Its distinct Start Menu and desktop shortcut names leave
the regular ChatShift shortcuts alone. The production
installer refuses updates while ChatShift holds its existing single-instance mutex.
Use `CHATSHIFT_DATA_DIR` to put test settings/models inside the workspace. The
installed executable accepts `--self-test` (dependencies, assets, DeepFilter, Tk,
26 languages and the five selectable speech models). It exits without starting
the translator, recording the microphone or installing keyboard hooks. JSON results
and failure logs go to the selected data directory. Normal consumers use no switches.

Test installation, same-path update, uninstall registration, Start Menu shortcuts,
EXE self-test and retention of data outside program files. Inspect the welcome GUI.
The offline suite uses its own actual Windows mutex so the running app is unaffected.
Do not run the regular test suite against an actively used chat field.

The CI workflow uses `test_installer.ps1 -Production` only inside its disposable
Windows VM to verify the exact `ChatShift-Setup.exe` offered for review. These checks
do not establish live speech quality or subscription access.
Use the default isolated identity when testing on a personal development PC.

Settings and model caches live in `%LOCALAPPDATA%/ChatShift`, and uninstall deliberately
leaves them intact. Source-install settings remain where they were; no private data
is searched for or copied. To migrate preferences deliberately, close both versions
and copy only `.settings.json` and `.controller.json` into that data directory.

Publication is a separate, user-authorized step. Review `COMPONENTS.md`, the exact
dependency inventory, retained sources and installer results before uploading.
GitHub Actions creates review artifacts; it does not automatically publish a release.
Do not disable Windows security controls if a device blocks the unsigned installer.
