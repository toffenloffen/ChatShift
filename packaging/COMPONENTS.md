# Cloud voice build components

This build includes Python/Tcl/Tk, Pillow, NumPy, sounddevice/PortAudio and their
runtime dependencies. Actual distribution licenses and metadata are included under
licenses; runtime-inventory.txt also records the build tools. Codex is external.

Whisper, DeepFilterNet, ONNX Runtime, CTranslate2, soxr, PyAV and FFmpeg are not bundled.
No speech models download during setup. Legacy source files remain in the repository
for reference but are excluded from this build. Old model caches are not deleted.
