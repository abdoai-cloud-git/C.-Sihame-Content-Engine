import json
import os
import random

corpus_path = r"c:\Users\hello\OneDrive\Desktop\Abdo\SIham\ai_writer\corpus.json"
examples_path = r"c:\Users\hello\OneDrive\Desktop\Abdo\SIham\ai_writer\knowledge_pack\GOLD_EXAMPLES.md"

# 1. Read existing examples to avoid duplicates
existing_texts = set()
if os.path.exists(examples_path):
    with open(examples_path, "r", encoding="utf-8") as f:
        existing_content = f.read()
        # A simple way to check if a post is already in the file
        # The exact text might be stripped, so we'll just check if the first 30 chars are in it
        pass

with open(corpus_path, "r", encoding="utf-8") as f:
    data = json.load(f)

# Filters to ensure "Gold" quality
bad_keywords = [
    "إسلام_شعيب", 
    "اربعينية الازدهار",
    "Partagé avec l'application",
    "pdf",
    "جمعة طيبة\n \nبسم الله الجامع", 
    "اليوم 1️⃣", "اليوم 2️⃣", "اليوم 3️⃣", "اليوم 4️⃣", "اليوم 5️⃣",
    "اليوم 6️⃣", "اليوم 7️⃣", "اليوم 8️⃣", "اليوم 9️⃣", "اليوم 0️⃣",
    "صيام",
    "مجموعة",
    "كورس",
    "رابط"
]

good_posts = []
for item in data:
    text = item.get("text", "")
    if not text:
        continue
    text = text.strip()
    
    if len(text) < 150 or len(text) > 2000:
        continue
    
    if any(bk in text for bk in bad_keywords):
        continue
        
    # Check if a chunk of the text is already in the file to avoid duplicates
    snippet = text[:50]
    if snippet in existing_content:
        continue
        
    good_posts.append(text)

# The user asked for "more gold examples like 10x".
# We already have 100. Adding 200 more? Let's add all valid ones up to 200.
num_to_add = min(200, len(good_posts))

random.seed(123) # different seed from last time just in case
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

# Find the highest POST ID currently in the file to continue numbering
last_id = 100
for line in existing_content.splitlines():
    if line.startswith("[POST ID: "):
        try:
            current_id = int(line.replace("[POST ID: ", "").replace("]", "").strip())
            if current_id > last_id:
                last_id = current_id
        except:
            pass

start_id = last_id + 1

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

print(f"Appended {len(examples_blocks)} NEW gold examples to GOLD_EXAMPLES.md")
print(f"Total entries should now end at POST ID: {start_id + len(examples_blocks) - 1:03d}")
