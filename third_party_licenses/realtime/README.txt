Streaming audio uses aiortc and PyAV, whose licenses are included in the installer.
PyAV includes dynamically linked FFmpeg 8.1.1 libraries (LGPL v3 or later as reported
by avcodec_license and avutil_license) and codec/runtime dependencies.
Upstream sources and build recipes:
https://ffmpeg.org/releases/ffmpeg-8.1.1.tar.xz
https://github.com/PyAV/PyAV
https://github.com/PyAV/FFmpeg-Builds
https://github.com/aiortc/aiortc
The av.libs DLLs are separate files and may be replaced with ABI-compatible builds.
ChatShift's restrictions do not override the rights granted by component licenses,
including modification/relinking and reverse engineering needed to debug modifications
to LGPL components. ChatShift does not claim ownership of these libraries.
