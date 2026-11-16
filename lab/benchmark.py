import json
import pathlib
import resource
import time
import wave

from piper import PiperVoice

sentences = {
    "en": [
        "At Cambridge, a camera watched a coffee pot long before video calls became routine.",
        "In nineteen ninety-one, the image stayed inside the lab. In nineteen ninety-three, it reached the web.",
        "The first number is fifteen, not fifty.",
        "Before you hit play, ask yourself: what changed, and why?",
        "The acronym is not the explanation. The explanation starts with a simple question.",
        "A signal can travel quickly and still arrive too late.",
        "The researchers wanted coffee, not a new medium.",
        "Read this aloud: the archive records a record number of visits.",
        "One pixel, two frames, three seconds. Which would you notice?",
        "It looks ordinary now. Imagine seeing it for the first time."
    ],
    "ar": [
        "في عام ألفٍ وتسعمئةٍ وواحدٍ وتسعين، راقبت كاميرا إبريقَ القهوة.",
        "هل تغيّر الاختراع، أم تغيّرت طريقةُ الوصول إليه؟",
        "تبلغ النسبة ١٥٫٥ بالمئة، لا خمسين بالمئة.",
        "في كامبريدج، بدأ الأمر بسؤالٍ بسيط.",
        "قال الخوارزميُّ: ابدأ بالمسألة، ثم فكّر في خطوات الحلّ.",
        "سنُصدِّر الفيديو بصيغة MP4، لكنّ الصوت سيبقى منفصلاً.",
        "في تشرين الثاني من عام ١٩٩٣، أصبحت الصور متاحةً على الويب.",
        "عَلِمَ الفريقُ أنَّ العَلَمَ يظهر في الصورة.",
        "إذا تأخّر الإرسال ثانيتين، فهل يُلاحظ المشاهدُ الفرق؟",
        "اقرأ الاسمَ أولاً: تيم بيرنرز لي. ثم اشرح ماذا أضاف الويب."
    ],
}
out = pathlib.Path("evidence")
out.mkdir(exist_ok=True)
(out / "voice-prompts.json").write_text(json.dumps(sentences,ensure_ascii=False,indent=2))
start = time.monotonic()
voice = PiperVoice.load("models/en.onnx")
load_s = time.monotonic()-start
rows = []
for index, sentence in enumerate(sentences["en"],1):
    path = out / f"en-{index:02}-TEST_ONLY.wav"
    start = time.monotonic()
    with wave.open(str(path),"wb") as wav:
        voice.synthesize_wav(sentence,wav)
    elapsed = time.monotonic()-start
    with wave.open(str(path),"rb") as wav:
        frames, hz = wav.getnframes(), wav.getframerate()
        assert wav.getnchannels()==1 and hz==22050 and frames>hz
        samples = memoryview(wav.readframes(frames)).cast("h")
    peak = max(abs(s) for s in samples)
    assert peak>0
    rows.append(dict(file=path.name,elapsed_s=round(elapsed,3),duration_s=round(frames/hz,3),
                     clipped_samples=sum(abs(s)>=32767 for s in samples),peak_pcm=peak))
(out / "voice-metrics.json").write_text(json.dumps(dict(load_s=round(load_s,3),
    peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss, samples=rows),indent=2))
