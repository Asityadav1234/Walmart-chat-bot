from filter_extraction import extract_filters
from walmart_search import search_walmart_products
from chat_memory import ChatMemory
from reply_generator import generate_reply
from recommender import recommend_best_product

# Session store for maintaining conversation state
sessions = {}

def get_response(message: str, session_id: str) -> dict:
    """
    Process user message and return assistant response with products
    Args:
        message: User's message
        session_id: Unique session identifier
    Returns:
        dict: {
            "response": str, 
            "products": list[dict],
            "session_id": str
        }
    """
    # Get or create session
    if session_id not in sessions:
        sessions[session_id] = ChatMemory()
    memory = sessions[session_id]

    # Greeting flag logic
    is_new_user = False
    if not hasattr(memory, "greeted"):
        memory.greeted = True
        is_new_user = True

    lowered = message.lower()
    response_text = ""
    products = []

    # --- Help command
    if lowered in ["help", "what can you do", "commands"]:
        response_text = """
ℹ️ I can help you with:
- Searching for products
- Sorting and filtering
- Comparing two items
- Recommending the best item
- Tracking what you like/dislike
- Refining results when you're unhappy

Try things like:
→ "Show me wireless gaming mice under $100"
→ "Which one is best?"
→ "Compare Logitech and Razer"
→ "I don't like this"
"""
        if is_new_user:
            response_text = "🛒 Welcome to your Walmart Shopping Assistant! How can I help you today?\n\n" + response_text
        return format_response(response_text, [], session_id)

    # --- Recommendation: "Which one is best?"
    if any(phrase in lowered for phrase in [
        "which one is best", "which is best", "what do you recommend",
        "recommend one", "suggest one", "your top pick"
    ]):
        full_list = list(memory.full_product_lookup.values())
        if not full_list:
            return format_response("⚠️ No products to recommend. Try searching first.", [], session_id)

        best = recommend_best_product(memory, full_list)
        if best:
            memory.last_selected = best
            memory.last_products = [best]
            response_text = generate_reply(message, [best], "refine",
                                           intent=memory.intent, tone=memory.tone)
            products = [best]
        else:
            response_text = "⚠️ Couldn't find a recommendation right now."
        if is_new_user:
            response_text = "🛒 Welcome to your Walmart Shopping Assistant! How can I help you today?\n\n" + response_text
        return format_response(response_text, products, session_id)

    # --- Like command
    if "i like this" in lowered:
        current = memory.last_selected
        if current:
            memory.like_product(current)
            response_text = "👍 Got it! I'll remember you liked this one."
        else:
            response_text = "⚠️ No product currently selected to like."
        if is_new_user:
            response_text = "🛒 Welcome to your Walmart Shopping Assistant! How can I help you today?\n\n" + response_text
        return format_response(response_text, [], session_id)

    # --- Dislike current item
    if "i don't like this" in lowered or "i dont like this" in lowered:
        full_list = list(memory.full_product_lookup.values())
        current = memory.last_selected
        if current and full_list:
            try:
                idx = full_list.index(current)
                memory.dislike_product(current)
                if idx + 1 < len(full_list):
                    next_product = full_list[idx + 1]
                    memory.last_selected = next_product
                    memory.last_products = [next_product]
                    response_text = generate_reply(message, [next_product], "refine",
                                                   intent=memory.intent, tone=memory.tone)
                    products = [next_product]
                else:
                    response_text = "😕 That was the last one I had. Try searching again!"
            except ValueError:
                response_text = "⚠️ Hmm, couldn't locate that product in my list."
        else:
            response_text = "⚠️ You haven’t selected any product yet. Start with a search."
        if is_new_user:
            response_text = "🛒 Welcome to your Walmart Shopping Assistant! How can I help you today?\n\n" + response_text
        return format_response(response_text, products, session_id)

    # --- Dislike all
    if "i don't like any" in lowered or "i dont like any" in lowered:
        category = memory.get_category()
        filters = memory.get_filters()
        if not category:
            return format_response("⚠️ I need a category first. Try saying what you're shopping for.", [], session_id)

        products = search_walmart_products(category, filters, max_results=10)
        if not products:
            return format_response("😕 I couldn’t find anything better. Maybe tweak the filters?", [], session_id)

        memory.save_products(products)
        response_text = generate_reply(message, products[:3], "refine",
                                       intent=memory.intent, tone=memory.tone)
        if is_new_user:
            response_text = "🛒 Welcome to your Walmart Shopping Assistant! How can I help you today?\n\n" + response_text
        return format_response(response_text, products[:3], session_id)

    # --- Main processing flow ---
    full_context = f"Category: {memory.get_category()}\nFilters: {memory.get_filters()}\n"

    parsed = extract_filters(message, context=full_context)
    memory.update_context(parsed)
    action = parsed.get("action", "search")

    if action in ["search", "refine", "sort"]:
        category = memory.get_category()
        filters = memory.get_filters()
        if not category:
            return format_response("⚠️ Please mention what you're looking for.", [], session_id)

        products = search_walmart_products(category, filters, max_results=10)
        if not products:
            return format_response("😕 I couldn’t find matching products. Try adjusting your request.", [], session_id)

        memory.save_products(products)

    elif action == "compare":
        refs = parsed.get("products", [])
        if len(refs) < 2:
            return format_response("⚠️ Please name two products you'd like to compare.", [], session_id)

        ref1 = memory.resolve_product_reference(refs[0])
        ref2 = memory.resolve_product_reference(refs[1])

        if ref1 and ref2:
            products = [ref1, ref2]
        else:
            return format_response("⚠️ Couldn’t find one or both items to compare.", [], session_id)

    if not products:
        return format_response("⚠️ No products to show yet. Try searching first.", [], session_id)

    response_text = generate_reply(message, products[:3], action,
                                   intent=memory.intent, tone=memory.tone)

    if is_new_user:
        response_text = "🛒 Welcome to your Walmart Shopping Assistant! How can I help you today?\n\n" + response_text

    return format_response(response_text, products[:3], session_id)

def format_response(response_text: str, products: list, session_id: str) -> dict:
    """Format final response structure"""
    return {
        "response": response_text.strip(),
        "products": products,
        "session_id": session_id
    }
