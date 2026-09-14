"""Offline Norwegian Bokmål -> English using the Argos/OPUS-MT model."""
from pathlib import Path
import re
import threading

MODEL_PATH = Path(__file__).resolve().parents[1] / '.models' / 'translate-nb_en-1_9'


def normalize_chat(text):
    # The dialect phrase "det hær" means "this here", not "the army".
    # Keep the genuine noun "hær" unchanged in all other contexts.
    text = re.sub(r'\b(det)\s+hær\b', lambda match: match[1] + ' her', text, flags=re.IGNORECASE)
    # Norwegian gaming spelling of English "heal". Match whole words only.
    def healing_word(match):
        word = match[0]
        replacement = 'heale'
        if word.isupper():
            return replacement.upper()
        return replacement.capitalize() if word[0].isupper() else replacement
    text = re.sub(r'\bhile\b', healing_word, text, flags=re.IGNORECASE)
    text = re.sub(r'\båss\b', lambda match: 'OSS' if match[0].isupper() else
                  ('Oss' if match[0][0].isupper() else 'oss'), text, flags=re.IGNORECASE)
    # Preserve an inverted question even when chat omits its question mark.
    if re.match(r'^har vi\b', text, flags=re.IGNORECASE) and text[-1:] not in ('.', '!', '?'):
        text += '?'
    return text


class LocalTranslator:
    def __init__(self):
        import ctranslate2
        import sentencepiece
        if not (MODEL_PATH / 'model' / 'model.bin').is_file():
            raise ValueError('Språkmodellen mangler. Kjør oppsettet igjen.')
        self.tokenizer = sentencepiece.SentencePieceProcessor(model_file=str(MODEL_PATH / 'sentencepiece.model'))
        self.engine = ctranslate2.Translator(str(MODEL_PATH / 'model'), device='cpu',
                                            compute_type='int8', intra_threads=2)
        self.lock = threading.Lock()

    def translate(self, text, unused_key=''):
        text = text.strip()
        if not text or len(text) > 1000:
            raise ValueError('Skriv en melding på 1–1000 tegn.')
        if text.startswith('/'):
            raise ValueError('Velg kanal i spillet først. Skriv bare selve meldingen her.')
        with self.lock:
            tokens = self.tokenizer.encode(normalize_chat(text), out_type=str)
            output = self.engine.translate_batch([tokens], beam_size=2, max_input_length=0,
                                                 max_decoding_length=512)[0].hypotheses[0]
            if len(output) >= 512:
                raise ValueError('Oversettelsen ble for lang. Prøv en kortere melding.')
            # Argos 1.9 target vocabulary uses SentencePiece whitespace markers;
            # some target pieces are absent from the source tokenizer vocabulary.
            result = ' '.join(self.tokenizer.decode(output).replace('▁', ' ').split())
        if not result or result.startswith('/') or len(result) > 2000:
            raise ValueError('Ugyldig oversettelse. Ingenting ble sendt.')
        return result
