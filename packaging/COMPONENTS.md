# Replaceable native components

The installed `_internal` directory retains native shared libraries separately.
Third-party licenses apply to these components; ChatShift's license does not
limit rights under those licenses, including modification and reverse engineering
for debugging modified LGPL components. Make a backup before replacing libraries.

The soxr Python extension is in `_internal/soxr`; its corresponding source archive
with vendored libsoxr is included in `licenses/sources`. Build for 64-bit Python
3.13 using the source archive's build instructions and replace the matching `.pyd`
file to use a modified version. No signing check restricts replacement.

PyAV is in `_internal/av`; its separately replaceable FFmpeg shared libraries are
in `_internal/av.libs`. PyAV sources and the FFmpeg 8.1.2 source inputs are included
under `licenses/sources`. `native/source-manifest.json` records upstream URLs and
verified SHA-256 hashes. `native/recipe` retains upstream build scripts and patches
at pyav-ffmpeg commit a71bf9279f7a4659154b68ba6783e89be460bcd5. The packaged DLLs'
reported configuration and license are in `native/packaged-ffmpeg-build.json`.

PUBLICATION REVIEW REQUIRED: that upstream recipe's `patches/ffmpeg.patch` moves
x264/x265 out of FFmpeg's GPL list, while the binaries enable those codecs and
report LGPL-3.0-or-later. Do not infer redistribution compatibility from that
reported string. Review the codec licenses and ChatShift's license together, or
replace the wheel with a properly built LGPL-only dependency before publication.
The 16.1.0 and 14.2.0 Windows wheels inspected also enable x264/x265; a casual
downgrade does not resolve this. These findings do not alter the speech engine.

Python, Tcl/Tk, Pillow, NumPy, ONNX Runtime, CTranslate2 and the remaining
dependencies retain their license notices in this directory and `_internal`.
The runtime inventory records exact installed versions. Codex is not bundled.
Whisper small and DeepFilterNet3 models download from their upstream hosts on first
setup and retain their upstream licenses. DeepFilterNet3 uses its original
streaming model, without an added postfilter.
