import asyncio
import os
import sys
import traceback
from datetime import datetime
from dotenv import load_dotenv

# Add the 'backend' folder to sys.path so we can import 'app.xyz'
backend_dir = os.path.join(os.path.dirname(__file__), "backend")
sys.path.insert(0, backend_dir)

# Load env variables BEFORE importing anything from app that instantiates Settings
load_dotenv(os.path.join(backend_dir, ".env"))

from app.services.llm_router import TextModelRouter

async def generate_weekly_brief():
    print("1. Gathering Coach Sihame's context files...")
    root_dir = os.path.dirname(__file__)
    kb_dir = os.path.join(root_dir, "knowledge_pack", "core")
    
    # Files needed for a high-level strategic brief
    files_to_read = [
        (kb_dir, "offer_map.md"),
        (kb_dir, "seasonal_calendar.md"),
        (kb_dir, "icp.md"),
        (root_dir, "feedback_log.md")
    ]
    
    context_parts = []
    for directory, filename in files_to_read:
        filepath = os.path.join(directory, filename)
        if os.path.exists(filepath):
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
                context_parts.append(f"--- BEGIN {filename} ---\n{content}\n--- END {filename} ---\n")
        else:
            print(f"[Warning] Could not find {filepath}")

    full_context = "\n".join(context_parts)
    
    print("2. Constructing the brief generation prompt...")
    prompt = f"""
You are the Lead Content Strategist for Coach Sihame Atamnia.

Based on the core knowledge provided below, generate a Weekly Content Brief for the Coach.
The brief should contain EXACTLY 5 post ideas for the upcoming week.
Do NOT write the actual posts. Write the *strategy* and *angle* for the coach.

Consider:
1. Her active offers (offer_map)
2. The current seasonal or spiritual timing (seasonal_calendar)
3. Her Ideal Customer Profile's pain points (icp)
4. Recent feedback on what worked/failed (feedback_log)

Format the output strictly as a JSON object matching this schema:
{{
  "theme_of_the_week": "A one sentence overarching theme",
  "rationale": "Why this theme makes sense right now based on the calendar/feedback",
  "post_ideas": [
    {{
      "day": "Day 1",
      "post_type": "Reflection / Promo / Clinic Story etc.",
      "platform": "Telegram or Instagram or Email",
      "angle": "What the post is about",
      "cta": "What the call to action is (e.g., book a session, reply, none)"
    }},
    ... (5 ideas in total)
  ]
}}

KNOWLEDGE CONTEXT:
{full_context}
"""

    print("3. Calling the AI Strategist...")
    router = TextModelRouter()
    # We can reuse the primary draft generator since we requested JSON
    # It will strip the JSON down to a dictionary
    
    try:
        raw_text = await router.primary_adapter.complete_text(prompt)
        payload = router._extract_json_object(raw_text)
        
        # Save the brief
        date_str = datetime.now().strftime("%Y-%m-%d")
        output_filename = f"weekly_brief_{date_str}.md"
        output_path = os.path.join(root_dir, output_filename)
        
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(f"# Weekly Content Brief ({date_str})\n\n")
            f.write(f"**Theme of the Week:** {payload.get('theme_of_the_week')}\n\n")
            f.write(f"**Rationale:** {payload.get('rationale')}\n\n")
            f.write("## Post Ideas\n\n")
            
            for index, idea in enumerate(payload.get('post_ideas', []), 1):
                f.write(f"### Idea {index}: {idea.get('day')} ({idea.get('platform')})\n")
                f.write(f"- **Type:** {idea.get('post_type')}\n")
                f.write(f"- **Angle:** {idea.get('angle')}\n")
                f.write(f"- **Call to Action:** {idea.get('cta')}\n\n")
                
        print(f"[SUCCESS] Weekly brief generated and saved to {output_filename}")
        
    except Exception as e:
        print(f"[ERROR] Error generating brief: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(generate_weekly_brief())
