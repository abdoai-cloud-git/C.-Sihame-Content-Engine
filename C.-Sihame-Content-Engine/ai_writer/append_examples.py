import json
import os
import random

corpus_path = r"c:\Users\hello\OneDrive\Desktop\Abdo\SIham\ai_writer\corpus.json"
examples_path = r"c:\Users\hello\OneDrive\Desktop\Abdo\SIham\ai_writer\knowledge_pack\GOLD_EXAMPLES.md"

with open(corpus_path, "r", encoding="utf-8") as f:
    data = json.load(f)

# Filters to ensure "Gold" quality
bad_keywords = [
    "إسلام_شعيب", 
    "اربعينية الازدهار \n\nسورة طه",
    "Partagé avec l'application",
    "pdf",
    "جمعة طيبة\n \nبسم الله الجامع", 
    "اليوم 1️⃣", "اليوم 2️⃣", "اليوم 3️⃣", "اليوم 4️⃣", "اليوم 5️⃣",
    "اليوم 6️⃣", "اليوم 7️⃣", "اليوم 8️⃣", "اليوم 9️⃣", "اليوم 0️⃣"
]

good_posts = []
for item in data:
    text = item.get("text", "")
    if len(text) < 150 or len(text) > 2000:
        continue
    
    # Check negative filters
    if any(bk in text for bk in bad_keywords):
        continue
        
    good_posts.append(text)

# We want 90 more posts to reach ~100
num_to_add = min(90, len(good_posts))

# For reproducibility and distinctness, we sort by length to spread them, then pick evenly, or just random sample.
random.seed(42)
selected_posts = random.sample(good_posts, num_to_add)

def guess_type_and_theme(text):
    post_type = "Reflection Post"
    theme = "Inner Awareness / Healing"
    tone = "Reflective / Compassionate"
    
    if "تطبيق" in text or "تنفس" in text or "اجلسي" in text:
        post_type = "Guided Practice Post"
        theme = "Somatic Regulation"
        tone = "Calming / Grounding"
    elif "اللهم" in text or "دعاء" in text:
        post_type = "Prayer / Reflection Post"
        theme = "Spiritual Connection"
        tone = "Devotional / Reassuring"
    elif "التواصل" in text or "للاشتراك" in text or "برنامج" in text or "الجلسات" in text:
        post_type = "Promo Post"
        theme = "Healing Programs"
        tone = "Empathetic / Professional"
    elif "امسية" in text or "نلتقي" in text or "موعدنا" in text:
        post_type = "Event/Invite Post"
        theme = "Community Session"
        tone = "Warm / Welcoming"
        
    if "الطفل" in text or "طفولة" in text:
        theme = "Inner Child"
    elif "المايسترو" in text or "النسخ" in text:
        theme = "Inner Maestro / Parts"
    elif "الجسد" in text or "الجهاز العصبي" in text:
        theme = "Nervous System / Somatic"
        
    return post_type, theme, tone

examples_blocks = []
start_id = 11

for i, text in enumerate(selected_posts):
    post_id = start_id + i
    post_type, theme, tone = guess_type_and_theme(text)
    
    block = f"""
[POST ID: {post_id:03d}]
[TYPE: {post_type}]
[THEME: {theme}]
[TONE: {tone}]

{text.strip()}

---"""
    examples_blocks.append(block)

with open(examples_path, "a", encoding="utf-8") as f:
    f.write("\n".join(examples_blocks))

print(f"Appended {len(examples_blocks)} gold examples to GOLD_EXAMPLES.md")
