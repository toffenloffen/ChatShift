# Replaceable native components

The installed `_internal` directory retains native shared libraries separately.
Third-party licenses apply to these components; ChatShift's license does not
limit rights under those licenses, including modification and reverse engineering
for debugging modified LGPL components. Make a backup before replacing libraries.

The soxr Python extension is in `_internal/soxr`; its corresponding source archive
with vendored libsoxr is included in `licenses/sources`. Build for 64-bit Python
3.13 using the source archive's build instructions and replace the matching `.pyd`
file to use a modified version. No signing check restricts replacement.

PyAV and its FFmpeg shared libraries are in `_internal/av`. PyAV sources are
included; FFmpeg source and build information must accompany public distributions.
This review installer is not approved for public redistribution until that source
bundle has been checked against the packaged wheel.

Python, Tcl/Tk, Pillow, NumPy, ONNX Runtime, CTranslate2 and the remaining
dependencies retain their license notices in this directory and `_internal`.
The runtime inventory records exact installed versions. Codex is not bundled.
Whisper small and DeepFilterNet3 models download from their upstream hosts on first
setup and retain their upstream licenses. DeepFilterNet3 uses its original
streaming model, without an added postfilter.
