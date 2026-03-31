
import json
import sys
import os
from collections import Counter

# Fix encoding for Windows console
sys.stdout.reconfigure(encoding='utf-8')

# Load raw dataset
raw_path = r"c:\Users\hello\OneDrive\Desktop\Abdo\SIham\resouces\dataset_telegram-channels-scraper_2026-03-24_13-16-12-875.json"
with open(raw_path, "r", encoding="utf-8") as f:
    data = json.load(f)

print(f"Total entries in raw dataset: {len(data)}")
if data:
    print(f"Keys: {list(data[0].keys())}")
    # Print first item's date-related fields
    first = data[0]
    for k, v in first.items():
        if "date" in k.lower() or "time" in k.lower() or "publish" in k.lower():
            print(f"  Date field '{k}': {str(v)[:80]}")

# Find 2023 messages
msgs_2023 = []
date_field_candidates = ["date", "createdAt", "timestamp", "pubDate", "publishedDate", "dateTime"]

for item in data:
    date_str = None
    date_field_used = None
    for field in date_field_candidates:
        if field in item and item[field]:
            date_str = str(item[field])
            date_field_used = field
            break
    
    if date_str and "2023" in date_str:
        text = item.get("text", item.get("message", item.get("content", "")))
        if text and len(text.strip()) > 20:
            msgs_2023.append({
                "date": date_str,
                "text": text.strip()
            })

print(f"\nTotal 2023 messages with meaningful text: {len(msgs_2023)}")

# Sort by date
msgs_2023.sort(key=lambda x: x["date"])

# Monthly distribution
month_counts = Counter()
for m in msgs_2023:
    try:
        month = m["date"][:7]
        month_counts[month] += 1
    except:
        pass

print("\n--- Monthly Distribution ---")
for month in sorted(month_counts.keys()):
    print(f"  {month}: {month_counts[month]} messages")

# Save JSON
out_path = r"c:\Users\hello\OneDrive\Desktop\Abdo\SIham\ai_writer\msgs_2023_raw.json"
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(msgs_2023, f, ensure_ascii=False, indent=2)

print(f"\nSaved {len(msgs_2023)} messages to msgs_2023_raw.json")
