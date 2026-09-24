# Optional components

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
