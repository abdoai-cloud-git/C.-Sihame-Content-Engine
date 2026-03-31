import json
import os

input_file = r"c:\Users\hello\OneDrive\Desktop\Abdo\SIham\resouces\dataset_telegram-channels-scraper_2026-03-24_13-16-12-875.json"
output_dir = r"c:\Users\hello\OneDrive\Desktop\Abdo\SIham\ai_writer"
os.makedirs(output_dir, exist_ok=True)
output_corpus = os.path.join(output_dir, "corpus.json")
output_txt = os.path.join(output_dir, "corpus.txt")

def clean_text(text):
    if not text:
        return ""
    # Remove extremely short texts unless they look like specific affirmations
    if len(text.strip()) < 50:
        return ""
    return text.strip()

print(f"Loading {input_file}...")
with open(input_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

print(f"Found {len(data)} total records.")

corpus = []
corpus_txt = []

for item in data:
    if item.get("type") == "message" and item.get("text"):
        cleaned = clean_text(item["text"])
        if cleaned:
            corpus.append({"text": cleaned, "date": item.get("date")})
            corpus_txt.append(cleaned + "\n")
            corpus_txt.append("\n" + "="*50 + "\n\n")

print(f"Extracted {len(corpus)} valid messages.")

with open(output_corpus, 'w', encoding='utf-8') as f:
    json.dump(corpus, f, ensure_ascii=False, indent=2)

with open(output_txt, 'w', encoding='utf-8') as f:
    f.writelines(corpus_txt)

print(f"Saved corpus to {output_corpus} and {output_txt}")
