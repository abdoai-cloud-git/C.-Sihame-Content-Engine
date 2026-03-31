# JSON EXAMPLES

Here are complete examples of how the Graphics Designer Brain should output its JSON response based on different input post types.

## Example 1: Reflection Visual

**Input Text (Simulated):** 
"Sometimes, the highest form of discipline is simply allowing yourself to rest. The nervous system doesn't understand your to-do list; it only understands signals of safety or threat. What happens if you stop fighting the pause?"

**Expected Output:**
```json
{
  "visual_type": "Reflection visual",
  "design_goal": "To evoke a sense of permission, stillness, and deep nervous system settling.",
  "emotional_tone": "Quiet pacing, introspective, emotionally safe.",
  "layout_direction": "Editorial style paragraph, clean minimal margins. Text placed in the bottom right corner, massive negative space at the top left.",
  "text_hierarchy": "Single cohesive paragraph with strong leading (line height) for Arabic script. No massive headline.",
  "color_direction": "Soft sand, muted linen, and subtle sage.",
  "visual_elements": ["subtle grain", "soft lighting leak", "empty space"],
  "image_prompt": "A completely still, empty corner of an elegant minimalist room, morning sunlight casting a soft shadow across a textured beige wall, muted earthy palette, massive negative space on the upper left, editorial photography, profoundly calm and grounding.",
  "avoid": ["busy backgrounds", "sharp geometric shapes", "neon colors", "cluttered desk imagery"],
  "reasoning_summary": "The text speaks to the nervous system and rest, so the visual must embody that exact state of safety, using soft lighting and vast space to represent the 'pause'."
}
```

## Example 2: Educational Post

**Input Text (Simulated):** 
"The 3 layers of people-pleasing:
1. The Surface: 'I just want everyone to be happy.'
2. The Mechanism: 'If I agree, I avoid conflict.'
3. The Root: 'If I am difficult, I will be abandoned.'
Healing starts when you safely address the root, not just change the surface behavior."

**Expected Output:**
```json
{
  "visual_type": "Educational post",
  "design_goal": "To provide a clear, structured breakdown of a psychological concept, leading the reader from the surface to the depth.",
  "emotional_tone": "Grounded, authoritative, safely analytical.",
  "layout_direction": "Structured vertical list format. Strong headline at the top, clear segmentation between points 1, 2, and 3 using gentle dividers.",
  "text_hierarchy": "Headline: 'The 3 layers of people-pleasing' (Largest). Sub-points: numbered steps (Medium). Conclusion (Italics/Secondary).",
  "color_direction": "Deep charcoal background with off-white typography and subtle muted accent lines.",
  "visual_elements": ["soft dividing lines", "numbered list structure", "clean grid alignment"],
  "image_prompt": "An extreme close-up of premium dark textured paper, completely blank, subtle lighting gradient from the top left corner, muted charcoal tones, minimalist studio lighting, leaving the entire frame open for structured typography.",
  "avoid": ["stock photos of people pointing", "corporate bullet points", "clipart brains", "harsh contrast"],
  "reasoning_summary": "Educational content requires absolute clarity and structure. A dark, premium textured background allows the structured text to be the hero without distraction, maintaining Coach Sihame's authority."
}
```

## Example 3: Promotion / Offer Visual

**Input Text (Simulated):** 
"Registration is now open for 'The Container'. A 4-week deep dive into establishing somatic boundaries. We start on Monday. Link in bio to secure your spot."

**Expected Output:**
```json
{
  "visual_type": "Promotion / offer visual",
  "design_goal": "To announce an opening clearly and elegantly, inviting participation without pressure.",
  "emotional_tone": "Confident, invitational, premium.",
  "layout_direction": "Center-aligned focus block. High contrast for readability without being loud.",
  "text_hierarchy": "Program Title: 'The Container' (Hero). Subtitle: '4-week deep dive' (Secondary). Details: 'Starts Monday' (Tertiary). Call to action: 'Link in bio' (Clear button/box).",
  "color_direction": "Warm cream background with deep navy text for elegant contrast.",
  "visual_elements": ["elegant geometric framing", "premium typography", "clear but subtle CTA indicator"],
  "image_prompt": "A beautiful, minimalist still-life of a smooth, rounded stone resting gently on a soft linen fabric, muted beige and warm cream tones, high-end editorial product photography, massive negative space at the top and bottom center for promotional text, bright but soft ambient lighting.",
  "avoid": ["red 'Sale' tags", "strikethrough pricing", "urgent countdown aesthetics", "cluttered graphics"],
  "reasoning_summary": "The program is about boundaries and containment, so the visual metaphor of a solid stone on soft fabric anchors the promotion in her core aesthetic while providing the clean space needed for high-legibility offer details."
}
```
