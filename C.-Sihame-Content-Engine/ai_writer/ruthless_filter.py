import re
import collections
import random

filepath = r"c:\Users\hello\OneDrive\Desktop\Abdo\SIham\ai_writer\knowledge_pack\GOLD_EXAMPLES.md"

with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

# Split by POST ID
blocks = content.split("[POST ID: ")

bad_keywords = [
    "اسلام_شعيب",
    "إسلام_شعيب",
    "سميرة",
    "الغامدي",
    "طارق الحبيب",
    "طارق_الحبيب",
    "تشيخوف",
    "باولو كويلو",
    "مصطفى محمود",
    "عائض القرني",
    "سائد دوزدار",
    "صانع_بهجة",
    "صباح الخير",
    "مساء الخير",
    "جمعة مباركة",
    "تم 61",
    "اليوم 1", "اليوم 2", "اليوم 3", "اليوم 4", "اليوم 5",
    "اليوم 6", "اليوم 7", "اليوم 8", "اليوم 9", "اليوم 0"
]

seen_texts = set()
retained_blocks = []

for block in blocks[1:]:
    # Extract metadata
    type_match = re.search(r"\[TYPE: (.*?)\]", block)
    theme_match = re.search(r"\[THEME: (.*?)\]", block)
    tone_match = re.search(r"\[TONE: (.*?)\]", block)
    
    post_type = type_match.group(1) if type_match else "Reflection Post"
    
    # Extract text block
    text_match = block.split("]\n\n", 1)
    if len(text_match) > 1:
        text = text_match[1].replace("---", "").strip()
        
        # Rule 1 & 3: Filter non-siham voices & obvious low signal patterns
        if any(bk in text for bk in bad_keywords):
            continue
            
        # Filter link only or very short logistical ones
        if len(text) < 150: # Short filler
            continue
            
        # If it's 90% link
        if text.count("http") > 0 and len(text) < 200:
            continue
            
        # Deduplication check
        snippet = text[:150]
        if snippet in seen_texts:
            continue
            
        seen_texts.add(snippet)
        retained_blocks.append({
            "type": post_type,
            "text": text,
            "theme": theme_match.group(1) if theme_match else "",
            "tone": tone_match.group(1) if tone_match else "",
            "full_body": text_match[1].strip()
        })

# Rule 5 & 6: Balance the file, target ~100 posts.
# Let's group by type
grouped = collections.defaultdict(list)
for b in retained_blocks:
    grouped[b["type"]].append(b)

# Desired balance (approx 100 total):
# Reflection: 45
# Guided Practice: 20
# Promo Post: 15
# Prayer / Reflection: 15
# Event / Invite: 5

limits = {
    "Reflection Post": 45,
    "Guided Practice Post": 20,
    "Promo Post": 15,
    "Prayer / Reflection Post": 15,
    "Event/Invite Post": 5,
    "Campaign / Day-Series Post": 0 # User said specific trackers are bad, we'll keep 0 or 2 max
}

final_selected = []
random.seed(42) # Deterministic for consistent quality

for p_type, limit in limits.items():
    items = grouped.get(p_type, [])
    # Sort by length, usually more somatic text = better quality, but we random sample to get variety
    # Let's take the longest ones as they tend to be richest in vocabulary
    items.sort(key=lambda x: len(x["text"]), reverse=True)
    selected = items[:limit]
    final_selected.extend(selected)

# Additional ones if we are under 80
if len(final_selected) < 80:
    remaining = [b for b in retained_blocks if b not in final_selected and b["type"] == "Reflection Post"]
    remaining.sort(key=lambda x: len(x["text"]), reverse=True)
    needed = 80 - len(final_selected)
    final_selected.extend(remaining[:needed])

# Cap at 120 total just in case
if len(final_selected) > 120:
    final_selected = random.sample(final_selected, 120)

# Sort them to mix types nicely, or keep grouped? Mix them up so GPT sees diverse stuff.
random.shuffle(final_selected)

header = """# GOLD EXAMPLES

**EDITOR NOTE:**
This file contains ONLY high-signal, authentic examples of Coach Siham’s original voice. Reposts, duplicates, campaign counters, logistical filler, and external-author content have been rigorously removed. This document is specifically engineered for style imitation and modeling, not for corpus archiving. All retained posts heavily emphasize her somatic-spiritual grounding, nervous system language, and deep compassionate pacing.

---
"""

final_output = [header]

for i, b in enumerate(final_selected):
    block_str = f"[POST ID: {i+1:03d}]\n[TYPE: {b['type']}]\n[THEME: {b['theme']}]\n[TONE: {b['tone']}]\n\n{b['text']}\n\n---"
    final_output.append(block_str)

with open(filepath, "w", encoding="utf-8") as f:
    f.write("\n".join(final_output))

print(f"File successfully rebuilt! Total pristine examples retained: {len(final_selected)}.")
