import json
from mistralai import Mistral
from config import MISTRAL_API_KEY, MISTRAL_MODEL

client = Mistral(api_key=MISTRAL_API_KEY)

SYSTEM_PROMPT = """
You are a friendly, concise shopping assistant.

You will receive:
- The user query
- The detected shopping intent (e.g., gaming, gifting, personal use)
- The tone of the user (e.g., professional, casual, enthusiastic)
- A list of top 1–3 matching products (with title, price, rating)
- The user action (search | compare | refine | sort)

Your job is to generate a short, helpful natural-language response that:
- Is aware of the user's intent and adapts accordingly
- Matches the tone of the user (e.g., if they are casual, be casual too)
- Clearly explains what you found or compared
- Highlights useful details like brand, rating, or value
- NEVER lists exact product specs — those will be printed separately
- NEVER make up or hallucinate products

Be friendly but brief. Encourage refinement or comparison.
"""

def generate_reply(user_query, products, action, intent=None, tone=None):
    try:
        # Format top 1–3 products into structured summaries
        examples = [
            {
                "title": p.get("title"),
                "price": p.get("price"),
                "rating": p.get("rating"),
            } for p in products[:3]
        ]

        # Assemble prompt dictionary
        prompt = {
            "query": user_query,
            "action": action,
            "products": examples
        }

        if intent:
            prompt["intent"] = intent
        if tone:
            prompt["tone"] = tone

        # Generate reply using Mistral
        response = client.chat.complete(
            model=MISTRAL_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": json.dumps(prompt)}
            ]
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        print("❌ Reply generation failed:", e)
        return "Here are some product options. Let me know if you'd like to refine them!"
