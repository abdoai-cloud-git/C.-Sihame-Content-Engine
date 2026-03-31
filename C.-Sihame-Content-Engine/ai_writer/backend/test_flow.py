import asyncio
import json
from app.services.context_builder import DynamicContextBuilder
from app.services.llm_router import TextModelRouter

async def test_end_to_end():
    print("1. Initializing Context Builder...")
    builder = DynamicContextBuilder()
    
    # Mock voice note from Coach Sihame
    raw_input = "أهلا بك، حابة نحكي اليوم عن أهمية فكرة التنظيم مع التحرير. يعني مستحيل أعمل تحرير لصدمة قوية والجهاز العصبي مش منظم. لازم التنظيم الأول، وبعدها التحرير بيمشي بطريقة متوازية ومريحة جدا. تقنية P.E.A.T تلعب دور كبير هنا. اكتبلي منشور يطمن الناس ويوضحلهم الفكرة بدون تعقيد طبي."
    post_type = "Reflection"
    platform = "telegram"
    
    print("2. Building Context Payload (RAG-Ready)...")
    context_assembly = builder.build_payload(user_raw_input=raw_input, post_type=post_type, platform=platform)
    
    print(f"Payload assembled successfully! Total length: {len(context_assembly.prompt)} characters.")
    
    print("3. Sending Context to LLM Router (Gemini Pro via Kie.ai)...")
    print("Waiting for AI response (this might take 10-20 seconds depending on the prompt size)...")
    router = TextModelRouter()
    
    response = await router.generate_primary_draft(context_assembly.prompt)
    
    print("\n=== AI GENERATED STRUCTURED RESPONSE ===")
    with open("response.json", "w", encoding="utf-8") as f:
        json.dump(response.model_dump(), f, indent=2, ensure_ascii=False)
    print("Successfully saved response to response.json!")
    print("========================================")

if __name__ == "__main__":
    asyncio.run(test_end_to_end())
