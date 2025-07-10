import re

def recommend_best_product(memory, products):
    if not products:
        return None

    scores = []

    for product in products:
        score = 0

        title = product.get("title", "").lower()
        price = product.get("price")
        brand = extract_brand(product)

        # Match liked brand
        if brand and brand in memory.liked_brands:
            score += 10

        # Penalize disliked brand
        if brand and brand in memory.disliked_brands:
            score -= 10

        # Match liked features
        keywords = extract_keywords(title)
        score += 2 * len(keywords & memory.liked_features)

        # Penalize disliked features
        score -= len(keywords & memory.disliked_features)

        # Price similarity to user preference
        if price and memory.price_preferences:
            try:
                price = float(price)
                avg = sum(memory.price_preferences) / len(memory.price_preferences)
                score -= abs(price - avg) / max(avg, 1) * 2
            except:
                pass

        # Slight boost for higher rating
        if product.get("rating"):
            try:
                score += float(product["rating"])
            except:
                pass

        scores.append((score, product))

    scores.sort(reverse=True, key=lambda x: x[0])
    return scores[0][1] if scores else None


def rerank_products(memory, products):
    scored = []
    for p in products:
        score = 0

        title = p.get("title", "").lower()
        price = p.get("price")
        brand = extract_brand(p)
        keywords = extract_keywords(title)

        if brand in memory.liked_brands:
            score += 10
        if brand in memory.disliked_brands:
            score -= 10

        score += 2 * len(keywords & memory.liked_features)
        score -= len(keywords & memory.disliked_features)

        if price and memory.price_preferences:
            try:
                price = float(price)
                avg = sum(memory.price_preferences) / len(memory.price_preferences)
                score -= abs(price - avg) / max(avg, 1) * 2
            except:
                pass

        try:
            score += float(p.get("rating", 0))
        except:
            pass

        scored.append((score, p))

    scored.sort(reverse=True, key=lambda x: x[0])
    return [p for score, p in scored]


def extract_keywords(text):
    return set(re.findall(r'\b[a-zA-Z]{4,}\b', text.lower()))


def extract_brand(product):
    title = product.get("title", "")
    if "brand" in product:
        return product["brand"].lower()
    words = title.split()
    for word in words:
        if word.istitle():
            return word.lower()
    return None
