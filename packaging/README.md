# Windows Setup.exe

Build on Windows x64 with Python 3.13 (including Tcl/Tk) and Inno Setup 6.7.3.
The build is an allowlist of application modules/assets and installed dependencies;
it never copies `.settings.json`, `.controller.json`, credentials, model caches or
the developer source tree into the product. No code signing certificate is configured.

```powershell
python -m venv .build-env
.build-env/Scripts/python.exe -m pip install -r packaging/requirements-build.txt
.build-env/Scripts/python.exe packaging/fetch_sources.py
.build-env/Scripts/python.exe packaging/fetch_native_sources.py
.build-env/Scripts/python.exe packaging/build_windows.py
.build-env/Scripts/python.exe packaging/test_suite.py
```

Pass the path to `ISCC.exe` as the optional argument to `build_windows.py` if it
is not under Program Files (x86). Output: `dist/ChatShift-Setup.exe`.
The Python runtime and dependencies are bundled; the two voice models download in
the graphical welcome window. The dependency/model preparations never record audio.
Codex is external, and installation/sign-in are explicitly guided, never automated.

For an isolated test while another ChatShift is running, compile the same payload
with a distinct registration ID and output filename:

```powershell
ISCC.exe /DAppIdValue=ChatShift.IsolatedInstallerTest /DGroupNameValue=ChatShiftInstallerVerification /FChatShift-Test-Setup packaging/ChatShift.iss
```

Install that test EXE with `/VERYSILENT /SUPPRESSMSGBOXES /NORESTART /NOICONS`
and an absolute `/DIR=` pointing inside a disposable workspace. The production
installer refuses updates while ChatShift holds its existing single-instance mutex.
Use `CHATSHIFT_DATA_DIR` to put test settings/models inside the workspace. The
installed executable accepts `--self-test` (dependencies, assets, Tk, 26 languages)
and `--test-models` (also downloads/checks both models). They exit without starting
the translator, recording the microphone or installing keyboard hooks. JSON results
and failure logs go to the selected data directory. Normal consumers use no switches.

Test installation, same-path update, uninstall registration, Start Menu shortcuts,
EXE self-test and retention of data outside program files. Inspect the welcome GUI.
The offline suite uses its own actual Windows mutex so the running app is unaffected.
Do not run the regular test suite against an actively used chat field.

Settings and model caches live in `%LOCALAPPDATA%/ChatShift`, and uninstall deliberately
leaves them intact. Source-install settings remain where they were; no private data
is searched for or copied. To migrate preferences deliberately, close both versions
and copy only `.settings.json` and `.controller.json` into that data directory.

Publication is a separate review step. Review `COMPONENTS.md`, exact dependency
inventory and corresponding native-library sources before public redistribution.
This branch does not publish, upload releases or change the existing release URL.
GitHub Actions creates review artifacts on this branch; it does not publish a release.
On the development PC, Windows application control blocked Inno Setup's temporary
executable with error 4551 before installation. Do not disable application control
to test. Use the isolated CI result and resolve release signing before deployment
to a device whose application-control policy requires it.
