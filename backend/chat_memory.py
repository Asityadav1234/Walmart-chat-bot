import re

class ChatMemory:
    def __init__(self):
        self.reset()

    def reset(self):
        self.category = None
        self.filters = {}  # brand, price_min, price_max, features
        self.sort_by = None
        self.intent = None
        self.tone = None
        self.last_action = None
        self.last_products = []
        self.last_selected = None
        self.product_lookup = {}
        self.full_product_lookup = {}
        self.last_sort_by = None

        # 🆕 Preference tracking
        self.liked_brands = set()
        self.disliked_brands = set()
        self.liked_features = set()
        self.disliked_features = set()
        self.price_preferences = []

    def update_context(self, extraction_result):
        if extraction_result.get("category"):
            self.category = extraction_result["category"].lower()

        if extraction_result.get("brand") is not None:
            self.filters["brand"] = extraction_result["brand"]

        if extraction_result.get("price_min") is not None:
            self.filters["price_min"] = extraction_result["price_min"]

        if extraction_result.get("price_max") is not None:
            self.filters["price_max"] = extraction_result["price_max"]

        if extraction_result.get("features"):
            self.filters["features"] = extraction_result["features"]

        if extraction_result.get("sort_by"):
            self.sort_by = extraction_result["sort_by"]
            self.last_sort_by = extraction_result["sort_by"]

        if extraction_result.get("intent"):
            self.intent = extraction_result["intent"]

        if extraction_result.get("tone"):
            self.tone = extraction_result["tone"]

        self.last_action = extraction_result.get("action", "search")

    def save_products(self, products):
        self.last_products = products
        self.product_lookup = {p["title"].lower(): p for p in products}
        self.full_product_lookup = {p["title"].lower(): p for p in products}
        if products:
            self.last_selected = products[0]

    def resolve_product_reference(self, name_or_ref):
        if not name_or_ref:
            return None

        name_or_ref = name_or_ref.lower()

        if name_or_ref in ["this", "that", "previous", "one"]:
            return self.last_selected

        for title, product in self.product_lookup.items():
            if name_or_ref in title:
                return product

        for title, product in self.full_product_lookup.items():
            if name_or_ref in title:
                return product

        return None

    def like_product(self, product):
        if not product:
            return

        brand = self.extract_brand(product)
        if brand:
            self.liked_brands.add(brand)

        self.liked_features.update(self.extract_keywords(product))
        self.add_price(product)

    def dislike_product(self, product):
        if not product:
            return

        brand = self.extract_brand(product)
        if brand:
            self.disliked_brands.add(brand)

        self.disliked_features.update(self.extract_keywords(product))

    def extract_brand(self, product):
        # Try to infer brand from title, fallback to using filters
        title = product.get("title", "")
        if "brand" in product:
            return product["brand"].lower()
        words = title.split()
        for word in words:
            if word.istitle():
                return word.lower()
        return None

    def extract_keywords(self, product):
        title = product.get("title", "").lower()
        # Extract keywords longer than 3 characters, excluding prices and noise
        words = re.findall(r'\b[a-zA-Z]{4,}\b', title)
        return set(words)

    def add_price(self, product):
        price = product.get("price")
        if price:
            try:
                self.price_preferences.append(float(price))
            except:
                pass

    def get_category(self):
        return self.category

    def get_filters(self):
        return self.filters

    def get_sort_by(self):
        return self.sort_by

    def get_last_sort_by(self):
        return self.last_sort_by

    def get_last_action(self):
        return self.last_action

    def get_last_products(self):
        return self.last_products

    def get_intent(self):
        return self.intent

    def get_tone(self):
        return self.tone
