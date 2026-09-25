# Optional components

Voice noise suppression now uses deepfilter-stream 0.1.0 (MIT) and its
DeepFilterNet3 torchDF streaming ONNX export, dfn3-512-v1 (MIT/Apache-2.0;
MIT option selected). The model is downloaded by the installed package with
SHA-256 verification. Model and original-author attribution are retained in
third_party_licenses/deepfilter, together with full installed dependency notices.
Sources: https://github.com/wuxuedaifu/deepfilter-stream and
https://github.com/Rikorose/DeepFilterNet.

Runtime dependencies include ONNX Runtime (MIT with bundled third-party notices),
NumPy (BSD-3-Clause with bundled notices), platformdirs (MIT), sounddevice (MIT,
including PortAudio notices), soxr (LGPL-2.1-or-later), cffi (MIT), pycparser
(BSD-3-Clause), flatbuffers (Apache-2.0), protobuf (BSD-3-Clause with bundled
notices), and packaging (Apache-2.0/BSD-2-Clause). These installed packages
remain separate, replaceable components under their own licenses. Do not strip
their bundled licenses. A future frozen executable/Steam distribution needs its
own packaging review, including LGPL source/relinking obligations for soxr.
This dependency audit covers the current local pip installation, not all future
ChatShift distributions. No microphone audio is uploaded by DeepFilterNet.

The online application calls the separately installed OpenAI Codex executable; Codex is
not bundled in this repository. OpenAI services require a user's own account and terms.

The optional `setup_local.py` downloads Argos Norwegian–English 1.9, based on OPUS-MT work
by Jörg Tiedemann and Santhosh Thottingal. The model is CC BY 4.0; its README and attribution
are retained in the downloaded model directory. It is separate from ChatShift's own license.
Model source: https://data.argosopentech.com/argospm/v1/translate-nb_en-1_9.argosmodel
Index: https://github.com/argosopentech/argospm-index

CTranslate2, SentencePiece, NumPy, PyYAML and Pillow are installed separately, if requested,
and retain their respective licenses. Neither model files nor the local Python environment
should be committed to this repository.
