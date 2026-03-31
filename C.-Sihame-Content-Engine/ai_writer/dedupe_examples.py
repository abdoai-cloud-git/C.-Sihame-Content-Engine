import re

filepath = r"c:\Users\hello\OneDrive\Desktop\Abdo\SIham\ai_writer\knowledge_pack\GOLD_EXAMPLES.md"

with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

header = content.split("---")[0] + "---\n"

# Split by POST ID
blocks = content.split("[POST ID: ")

seen_texts = set()
unique_blocks = []

# Exclude specific posts like the daily campaign tracker mentioned in warnings
exclude_texts = [
    "اربعينية الازدهار"
]

for block in blocks[1:]:
    # Extract text (everything after [TONE: ...])
    text_match = block.split("]\n\n", 1)
    if len(text_match) > 1:
        text = text_match[1].replace("---", "").strip()
        
        if any(ex in text for ex in exclude_texts):
            continue
            
        snippet = text[:150] # Check first 150 chars to be safe
        if snippet not in seen_texts:
            seen_texts.add(snippet)
            unique_blocks.append(block)

# Rewrite with correct sequential IDs
final_output = [header]

for i, block in enumerate(unique_blocks):
    # block still has the old ID at the front, e.g. "010]\n[TYPE: "
    # We want to replace it.
    parts = block.split("]\n[TYPE:", 1)
    if len(parts) == 2:
        new_block = f"\n[POST ID: {i+1:03d}]\n[TYPE:{parts[1].rstrip()}\n\n---"
        final_output.append(new_block)

with open(filepath, "w", encoding="utf-8") as f:
    f.write("\n".join(final_output))

print(f"Deduplication complete. Kept {len(unique_blocks)} unique, high-quality posts.")
