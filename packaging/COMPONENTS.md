# Cloud voice build components

This build includes Python/Tcl/Tk, Pillow, NumPy, sounddevice/PortAudio and their
runtime dependencies. Actual distribution licenses and metadata are included under
licenses; runtime-inventory.txt also records the build tools. Codex is external.

DeepFilterNet, its verified model assets, ONNX Runtime and soxr are included for
optional local noise suppression. The model runs on the CPU. Their licenses and
the soxr source archive are included under licenses. The dynamically loaded soxr
library may be replaced with a compatible modified version under its LGPL terms.

aiortc, PyAV and their WebRTC/FFmpeg dependencies are bundled for streaming audio.
Available package licenses and metadata are included under licenses.
Whisper and CTranslate2 are not bundled. No speech recognition models
download during setup. Old model caches are not deleted.
