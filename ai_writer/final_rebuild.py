import re
import json
import collections
import random

examples_path = r"c:\Users\hello\OneDrive\Desktop\Abdo\SIham\ai_writer\knowledge_pack\GOLD_EXAMPLES.md"
corpus_path   = r"c:\Users\hello\OneDrive\Desktop\Abdo\SIham\ai_writer\corpus.json"

# ─── HELPERS ─────────────────────────────────────────────────────────────────

non_siham_kw = [
    "ابراهيم_الدرعان", "ابراهيم الدرعان",
    "سمية_صالحي", "سمية صالحي",
    "منقول للاستفادة", "منقول",
    "اسلام_شعيب", "إسلام_شعيب",
    "سميرة الغامدي", "سميرة_الغامدي",
    "طارق الحبيب", "طارق_الحبيب",
    "تشيخوف", "باولو كويلو",
    "مصطفى محمود", "عائض القرني",
    "سائد دوزدار", "صانع_بهجة",
]
low_signal_kw = [
    "اليوم 1", "اليوم 2", "اليوم 3", "اليوم 4", "اليوم 5",
    "اليوم 6", "اليوم 7", "اليوم 8", "اليوم 9", "اليوم 0",
    "اليوم 1️⃣","اليوم 2️⃣","اليوم 3️⃣","اليوم 4️⃣","اليوم 5️⃣",
    "تم 61", "تم اليوم",
]
family_kw = {
    "inner_child_promo":   ["علاج الطفل الداخلي"],
    "friday_prayer":       ["جمعة طيبة"],
    "istigfar_promo":      ["الاستغفار", "الترميم"],
    "arbainiya_intention": ["اربعينية", "ننوي"],
}

def is_clean(text):
    if not text or len(text) < 200:          return False
    if any(k in text for k in non_siham_kw): return False
    if any(k in text for k in low_signal_kw): return False
    if len(text) > 2800:                      return False   # TOO long → brochure
    return True

def classify(text):
    """Rule-based type classification."""
    if any(w in text for w in ["اللهم","يا رب","جمعة طيبة","جمعة مباركة"]):
        return "Prayer / Reflection Post"
    if any(w in text for w in ["تطبيق","اجلسي","اجلس","تنفسي","تنفس","ضع يدك","ضعي يدك","يا هادي"]):
        return "Guided Practice Post"
    if any(w in text for w in ["نلتقي","موعدنا","امسية","اللقاء القادم","ندوة"]):
        return "Event/Invite Post"
    if any(w in text for w in ["للحجز","للتواصل","مسار","برنامج","الاشتراك","المسار"]):
        return "Promo Post"
    return "Reflection Post"

def guess_theme(text):
    if "الطفل" in text or "طفولة" in text:            return "Inner Child"
    if "المايسترو" in text or "النسخ" in text:        return "Inner Maestro / Parts"
    if "الجهاز العصبي" in text or "الجسد" in text:   return "Nervous System / Somatic"
    if "الازدهار" in text:                             return "Flourishing / Abundance"
    if "الاستغفار" in text or "الترميم" in text:      return "Istighfar / Restoration"
    if "جمعة" in text or "اللهم" in text:             return "Spiritual Connection"
    return "Inner Awareness / Healing"

def guess_tone(post_type, text):
    if post_type == "Prayer / Reflection Post": return "Devotional / Reassuring"
    if post_type == "Guided Practice Post":     return "Calming / Grounding"
    if post_type == "Promo Post":               return "Empathetic / Professional"
    if post_type == "Event/Invite Post":        return "Warm / Welcoming"
    return "Reflective / Compassionate"

# ─── LOAD CORPUS (fresh material) ────────────────────────────────────────────
with open(corpus_path, "r", encoding="utf-8") as f:
    corpus = json.load(f)

all_texts = []
for item in corpus:
    t = item.get("text","").strip()
    if is_clean(t):
        all_texts.append(t)
print(f"Corpus: {len(all_texts)} clean texts.")

# ─── BUILD POST OBJECTS ───────────────────────────────────────────────────────
def make_post(text):
    pt    = classify(text)
    theme = guess_theme(text)
    tone  = guess_tone(pt, text)
    return {"type": pt, "theme": theme, "tone": tone, "text": text}

posts = [make_post(t) for t in all_texts]

# ─── DEDUP ────────────────────────────────────────────────────────────────────
seen = set()
unique_posts = []
for p in posts:
    snip = p["text"][:180]
    if snip not in seen:
        seen.add(snip)
        unique_posts.append(p)
print(f"After dedup: {len(unique_posts)}.")

# ─── CONTENT-FAMILY COLLAPSE ─────────────────────────────────────────────────
family_limits = {
    "inner_child_promo":   2,
    "friday_prayer":       1,
    "istigfar_promo":      1,
    "arbainiya_intention": 1,
}
family_counts = collections.defaultdict(int)

def get_family(text):
    for fam, kws in family_kw.items():
        if all(k in text for k in kws):
            return fam
    return None

collapsed = []
for p in unique_posts:
    fam = get_family(p["text"])
    if fam:
        if family_counts[fam] < family_limits.get(fam, 1):
            family_counts[fam] += 1
            collapsed.append(p)
    else:
        collapsed.append(p)
print(f"After family collapse: {len(collapsed)}.")

# ─── BALANCE: TAKE RICHEST (LONGEST) PER TYPE ────────────────────────────────
grouped = collections.defaultdict(list)
for p in collapsed:
    grouped[p["type"]].append(p)

for t in grouped:
    grouped[t].sort(key=lambda x: len(x["text"]), reverse=True)

allocation = {
    "Reflection Post":           28,
    "Guided Practice Post":      12,
    "Prayer / Reflection Post":   6,
    "Promo Post":                10,
    "Event/Invite Post":          4,
    "Campaign / Day-Series Post": 0,
}

final = []
for t, limit in allocation.items():
    final.extend(grouped.get(t, [])[:limit])

# Pad if short
if len(final) < 45:
    extra_refl = [p for p in collapsed if p not in final and p["type"] == "Reflection Post"]
    extra_refl.sort(key=lambda x: len(x["text"]), reverse=True)
    final.extend(extra_refl[:45-len(final)])

print(f"Final count: {len(final)}.")

# shuffle for organic feel
random.seed(77)
random.shuffle(final)

# ─── WRITE ───────────────────────────────────────────────────────────────────
HEADER = """# GOLD EXAMPLES

**EDITOR NOTE:**
This file contains only high-signal, original examples of Coach Siham Atamnia's authentic writing voice.
Reposts, uncertain authorship, duplicates, weak promo templates, campaign counters, and low-signal announcements have been removed.
This document is optimised for voice imitation, not archival completeness.
Retained posts strongly express her somatic-spiritual framing, nervous system language, inner child/maestro vocabulary, and dignified compassionate pacing.

---"""

blocks = [HEADER]
for i, p in enumerate(final, 1):
    b = (
        f"[POST ID: {i:03d}]\n"
        f"[TYPE: {p['type']}]\n"
        f"[THEME: {p['theme']}]\n"
        f"[TONE: {p['tone']}]\n\n"
        f"{p['text']}\n\n"
        f"---"
    )
    blocks.append(b)

with open(examples_path, "w", encoding="utf-8") as f:
    f.write("\n\n".join(blocks))

print("\nFile rebuilt.")
dist = collections.Counter(p["type"] for p in final)
for t, cnt in dist.most_common():
    print(f"  {t}: {cnt}")
