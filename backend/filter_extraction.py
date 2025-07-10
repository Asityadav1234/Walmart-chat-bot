import json
import re
from mistralai import Mistral
from config import MISTRAL_API_KEY, MISTRAL_MODEL

client = Mistral(api_key=MISTRAL_API_KEY)

SYSTEM_PROMPT = """
You are a shopping assistant that extracts structured shopping intent from a user query.

Always return ONLY a valid JSON object with these exact keys:
{
  "action": "search" | "compare" | "sort" | "refine",
  "category": string | null,
  "brand": string | list | null,
  "price_min": float | null,
  "price_max": float | null,
  "sort_by": "price" | "rating" | null,
  "features": list of strings | null,
  "products": list of strings | null,
  "intent": "gifting" | "personal use" | "work" | "gaming" | "budget shopping" | "luxury shopping" | null,
  "tone": "casual" | "enthusiastic" | "professional" | "fun" | null
}

Instructions:
- For queries like "only Logitech", set brand = "Logitech".
- If user says "under 2000", set price_max = 2000.
- If user says "highest rated", set sort_by = "rating".
- If user says "show me more" or "more like this", set action = "refine".
- If they say "compare this with Lumsburry", set action = "compare" and products = ["this", "lumsburry"].
- Always extract product names into the "products" list if possible.
- Try to infer the intent (e.g., gifting, gaming, personal use, work).
- Try to infer the tone (e.g., casual, enthusiastic, professional) based on how they express themselves.
- Use "null" if unsure about any field.
- Do not output any explanation or markdown. Just valid JSON.
"""

def extract_filters(user_query: str, context: str = "") -> dict:
    try:
        prompt = f"Previous context:\n{context}\nCurrent query: {user_query}"

        response = client.chat.complete(
            model=MISTRAL_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
        )

        content = response.choices[0].message.content.strip()

        if content.startswith("```"):
            content = re.sub(r"^```(?:json)?\s*|\s*```$", "", content.strip(), flags=re.IGNORECASE)

        parsed = json.loads(content)

        required_keys = [
            "action", "category", "brand", "price_min", "price_max",
            "sort_by", "features", "products", "intent", "tone"
        ]
        for key in required_keys:
            if key not in parsed:
                parsed[key] = None

        return parsed

    except Exception as e:
        print("❌ Filter extraction failed:", e)
        return {
            "action": "search",
            "category": None,
            "brand": None,
            "price_min": None,
            "price_max": None,
            "sort_by": None,
            "features": None,
            "products": None,
            "intent": None,
            "tone": None
        }

# Optional direct test
if __name__ == "__main__":
    while True:
        query = input("🧠 User query: ")
        filters = extract_filters(query)
        print("\n🎯 Extracted filters:\n", json.dumps(filters, indent=2))
