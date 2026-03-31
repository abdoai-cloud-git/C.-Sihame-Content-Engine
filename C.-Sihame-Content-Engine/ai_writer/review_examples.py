import re
import collections

filepath = r"c:\Users\hello\OneDrive\Desktop\Abdo\SIham\ai_writer\knowledge_pack\GOLD_EXAMPLES.md"

with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

# Split by POST ID
blocks = content.split("[POST ID: ")

stats = {
    "total_posts": 0,
    "types": collections.Counter(),
    "themes": collections.Counter(),
    "tones": collections.Counter(),
    "warnings": [],
    "duplicates": 0
}

seen_texts = set()

# skip the first block which is the header
for block in blocks[1:]:
    stats["total_posts"] += 1
    
    # Extract metadata
    post_type = re.search(r"\[TYPE: (.*?)\]", block)
    theme = re.search(r"\[THEME: (.*?)\]", block)
    tone = re.search(r"\[TONE: (.*?)\]", block)
    
    post_id = block.split("]")[0]
    
    if post_type: stats["types"][post_type.group(1)] += 1
    if theme: stats["themes"][theme.group(1)] += 1
    if tone: stats["tones"][tone.group(1)] += 1
        
    # Extract text (everything after [TONE: ...])
    text_match = block.split("]\n\n")
    if len(text_match) > 1:
        text = text_match[1].replace("---", "").strip()
        
        # Check duplicates
        snippet = text[:100]
        if snippet in seen_texts:
            stats["duplicates"] += 1
            stats["warnings"].append(f"Post {post_id} might be a duplicate.")
        else:
            seen_texts.add(snippet)
            
        # Check negative boundaries
        if "إسلام_شعيب" in text:
            stats["warnings"].append(f"Post {post_id} contains Islam Shoaib quote.")
        if "اربعينية الازدهار" in text and "اليوم" in text:
            stats["warnings"].append(f"Post {post_id} might be a daily campaign tracker.")
        if len(text) < 100:
            stats["warnings"].append(f"Post {post_id} is suspiciously short ({len(text)} chars).")

print("--- REVIEW RESULTS ---")
print(f"Total Examples: {stats['total_posts']}")
print(f"Duplicates found: {stats['duplicates']}")
print(f"Warnings ({len(stats['warnings'])}):")
for w in stats['warnings'][:10]:
    print(" -", w)
if len(stats['warnings']) > 10: print(f"   ...and {len(stats['warnings'])-10} more.")

print("\n--- DISTRIBUTIONS ---")
print("Top 5 Types:", stats["types"].most_common(5))
print("Top 5 Themes:", stats["themes"].most_common(5))
print("Top 5 Tones:", stats["tones"].most_common(5))
