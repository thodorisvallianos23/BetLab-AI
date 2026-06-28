def find_best_bookmaker(bookmakers):
    best_bookmaker = max(bookmakers, key=bookmakers.get)
    best_odds = bookmakers[best_bookmaker]

    return best_bookmaker, best_odds


def calculate_edge(model_probability, bookmaker_odds):
    implied_probability = 1 / bookmaker_odds
    edge = model_probability - implied_probability
    return edge


def value_decision(edge):
    if edge >= 0.10:
        return "✅ BET - Strong value"
    elif edge >= 0.05:
        return "👀 WATCH - Small value"
    return "❌ PASS - No value"


def analyze_market(model_probability, bookmakers):
    best_bookmaker, best_odds = find_best_bookmaker(bookmakers)
    edge = calculate_edge(model_probability, best_odds)

    return {
        "best_bookmaker": best_bookmaker,
        "best_odds": best_odds,
        "edge": edge,
        "decision": value_decision(edge),
    }