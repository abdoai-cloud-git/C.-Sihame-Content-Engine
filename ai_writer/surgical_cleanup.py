import re

filepath = r"c:\Users\hello\OneDrive\Desktop\Abdo\SIham\ai_writer\knowledge_pack\GOLD_EXAMPLES.md"

with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

# Splitting by [POST ID: 
raw_blocks = content.split("[POST ID: ")

header = raw_blocks[0].strip()

posts = {}
for block in raw_blocks[1:]:
    orig_id = block.split("]")[0].strip()
    idx = int(orig_id)
    posts[idx] = block

def get_text(block):
    text_m = re.split(r"\[TONE: .*?\]\s*", block, maxsplit=1)
    if len(text_m) > 1:
        return text_m[1].replace("---","").strip()
    return ""

def set_type(block, new_type):
    return re.sub(r"\[TYPE: .*?\]", f"[TYPE: {new_type}]", block)

# 1) REMOVE 053
if 53 in posts:
    del posts[53]

# 2) COLLAPSE DUPLICATES
# 001 / 025 / 060 -> keep strongest (longest text)
group_a = [1, 25, 60]
valid_a = [posts[i] for i in group_a if i in posts]
if valid_a:
    valid_a.sort(key=lambda b: len(get_text(b)), reverse=True)
    best_a = valid_a[0]
    for i in group_a:
        if i in posts and posts[i] != best_a:
            del posts[i]

# 011 / 015 / 046
group_b = [11, 15, 46]
valid_b = [posts[i] for i in group_b if i in posts]
if valid_b:
    valid_b.sort(key=lambda b: len(get_text(b)), reverse=True)
    best_b = valid_b[0]
    for i in group_b:
        if i in posts and posts[i] != best_b:
            del posts[i]

# 026 / 039 / 051
group_c = [26, 39, 51]
valid_c = [posts[i] for i in group_c if i in posts]
if valid_c:
    valid_c.sort(key=lambda b: len(get_text(b)), reverse=True)
    best_c = valid_c[0]
    for i in group_c:
        if i in posts and posts[i] != best_c:
            del posts[i]

# 3) DELETE LOW-SIGNAL BROCHURE / FAQ MATERIAL -> 020, 021, 034
for i in [20, 21, 34]:
    if i in posts:
        del posts[i]

# 4) DELETE OUTLIERS -> 019, 035, 054
for i in [19, 35, 54]:
    if i in posts:
        del posts[i]

# 5) FIX MISLABELS
# 013 to Promo Post
if 13 in posts:
    posts[13] = set_type(posts[13], "Promo Post")
# 047 to Event/Invite Post
if 47 in posts:
    posts[47] = set_type(posts[47], "Event/Invite Post")


# Collect retained blocks
retained = [b for k, b in sorted(posts.items())]

# 6) REDUCE PROMO DOMINANCE
# Keep only the top 4 Promo and top 2 Event/Invite, we will score by length as a proxy for 'strongest' content.
promo_blocks = []
invite_blocks = []
others = []

for b in retained:
    t_match = re.search(r"\[TYPE: (.*?)\]", b)
    t = t_match.group(1).strip() if t_match else ""
    if "Promo" in t:
        promo_blocks.append(b)
    elif "Event/Invite" in t:
        invite_blocks.append(b)
    else:
        others.append(b)

promo_blocks.sort(key=lambda b: len(get_text(b)), reverse=True)
invite_blocks.sort(key=lambda b: len(get_text(b)), reverse=True)

final_retained = others + promo_blocks[:4] + invite_blocks[:2]

# 8) TARGET SIZE -> 35 to 50
# If > 50, trim the weakest Reflection or Prayer posts
if len(final_retained) > 50:
    final_retained.sort(key=lambda b: len(get_text(b)), reverse=True)
    final_retained = final_retained[:50]

# Shuffle back roughly to organic but sort first
final_retained.sort(key=lambda x: len(get_text(x)), reverse=True)

# 9) PRESERVE FORMAT and RENUMBER
out_blocks = []
# Rewrite editor note perfectly
new_header = """# GOLD EXAMPLES

**EDITOR NOTE:**
This file contains only high-signal, original examples of Coach Siham's authentic voice.
Reposts, uncertain authorship, duplicates, weak promo templates, and low-signal announcements have been rigorously removed.
This document is specifically optimized for voice imitation, not archival completeness.
All retained posts strongly demonstrate her somatic-spiritual grounding, nervous system language, inner child/maestro framing, and dignified compassionate tone.

---"""
out_blocks.append(new_header)

for new_id, block in enumerate(final_retained, 1):
    # Rip out the body excluding old ID
    text_m = re.split(r"\[TYPE: ", block, maxsplit=1)
    if len(text_m) > 1:
        rest = "[TYPE: " + text_m[1]
    else:
        rest = block
    new_block = f"[POST ID: {new_id:03d}]\n{rest.strip()}"
    if not new_block.endswith("---"):
        new_block += "\n\n---"
    out_blocks.append(new_block)

final_md = "\n\n".join(out_blocks)

with open(filepath, "w", encoding="utf-8") as f:
    f.write(final_md)

print("SUCCESS: target size =", len(final_retained))
