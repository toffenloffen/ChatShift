# Included components and source

ChatShift's frozen Windows build accepts microphone PCM arrays, as the original
application does. It does not offer media-file import. PyAV and FFmpeg are not
included. The build explicitly excludes `av` and rejects FFmpeg DLLs in the output;
the frozen self-test also checks PyAV is absent.

The bundled MIT-licensed faster-whisper 1.2.1 has a small, identified modification:
`audio.py` imports PyAV lazily inside the optional file decoder and its helpers.
NumPy-array transcription, the Whisper model and the recognition parameters are
unchanged. If an unsupported media-file decode is requested, it fails honestly
with missing PyAV; no fake decoder or module masks the failure. The original
complete pure-Python source wheel and verified hash are in `licenses/sources`;
`licenses/faster-whisper-audio.patch` is the exact change. Its upstream license and
metadata are in the faster-whisper license directory. Installed PCM transcription
is tested with a locally synthesized sentence; no microphone is recorded by tests.

This avoids shipping the unused codecs whose upstream PyAV wheel raised an
x264/x265 licensing concern during packaging review. Build-only pip resolution
may install PyAV in the builder, but it is excluded from the delivered application.

The soxr Python extension is a separate, replaceable shared component in
`_internal/soxr`. Its source archive with vendored libsoxr and build instructions
is included in `licenses/sources`. Build for 64-bit Python 3.13 and replace the
matching `.pyd` file to use a modified version. No signing check restricts replacement.
Third-party licenses apply to these components; ChatShift's license does not
limit their rights, including modification and reverse engineering for debugging
modified LGPL components. Make a backup before replacing libraries.

Python, Tcl/Tk, Pillow, NumPy, ONNX Runtime, CTranslate2 and the other included
dependencies retain their license notices here and in `_internal`. The inventory
records the builder's exact distributions (excluding non-shipped PyAV), including
build tools. Codex is external and is not bundled. Whisper small and DeepFilterNet3
download from their upstream hosts on first setup under their own licenses.
DeepFilterNet3 uses its original streaming model, without an added postfilter.
