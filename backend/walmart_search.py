import os
from dotenv import load_dotenv
from serpapi import GoogleSearch

load_dotenv()
SERPAPI_KEY = os.getenv("SERPAPI_KEY")

def search_walmart_products(query, filters, max_results=10):
    try:
        params = {
            "engine": "walmart",
            "query": query,
            "api_key": SERPAPI_KEY,
            "sort": serpapi_sort(filters.get("sort_by")),
            "min_price": str(filters.get("price_min")) if filters.get("price_min") is not None else None,
            "max_price": str(filters.get("price_max")) if filters.get("price_max") is not None else None,
        }

        # Clean out None values
        params = {k: v for k, v in params.items() if v is not None}

        search = GoogleSearch(params)
        results = search.get_dict()

        products = results.get("organic_results", [])[:max_results]

        parsed = []
        for p in products:
            parsed.append({
                "title": p.get("title"),
                "price": p.get("primary_offer", {}).get("offer_price"),
                "rating": p.get("rating"),
                "reviews": p.get("reviews"),
                "url": p.get("product_page_url"),
                "thumbnail": p.get("thumbnail"),
            })

        return parsed

    except Exception as e:
        print(f"🔴 SerpAPI fetch failed: {e}")
        return []

def serpapi_sort(sort_by):
    if sort_by == "price":
        return "price_low"
    elif sort_by == "rating":
        return "rating_high"
    return "best_match"

# Direct test
if __name__ == "__main__":
    filters = {
        "sort_by": "rating",
        "price_max": 1000,
    }
    results = search_walmart_products("logitech gaming mouse", filters)
    for r in results:
        print(r["title"], r["price"])
