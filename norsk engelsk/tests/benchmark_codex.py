"""Manual timing and recovery check using the ChatGPT subscription."""
import sys
import time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from codex_translator import CodexTranslator

if __name__ == '__main__':
    start = time.perf_counter()
    translator = CodexTranslator()
    print('Startup:', round(time.perf_counter() - start, 2), flush=True)
    try:
        for text in ['hei kan du hile meg', 'har vi en druid som kan hile ås',
                     'jeg trengr hjelp kan noen hile meig']:
            start = time.perf_counter()
            print(translator.translate(text), round(time.perf_counter() - start, 2), flush=True)
        if '--recovery' in sys.argv:
            old_thread = translator.thread_id
            translator.turn_count = 20
            print('New session:', translator.translate('vent på meg dragen komer'), flush=True)
            assert translator.thread_id != old_thread
            old_process = translator.process
            old_process.terminate()
            old_process.wait(timeout=3)
            print('Reconnected:', translator.translate('kan du hile oss'), flush=True)
            assert translator.process.pid != old_process.pid
    finally:
        process = translator.process
        translator.close()
        assert process is None or process.poll() is not None
