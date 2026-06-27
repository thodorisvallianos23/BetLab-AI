def fair_odds(probability_percent):
    if probability_percent <= 0:
        return None
    return 100 / probability_percent

def implied_probability(bookmaker_odds):
    return 100 / bookmaker_odds

def calculate_edge(model_probability, bookmaker_odds):
    implied = implied_probability(bookmaker_odds)
    edge = model_probability - implied
    return edge

def decision(edge):
    if edge >= 10:
        return "BET"
    elif edge >= 5:
        return "WATCH"
    return "PASS"

if __name__ == "__main__":
    model_probability = 62.5
    bookmaker_odds = 1.90

    fair = fair_odds(model_probability)
    implied = implied_probability(bookmaker_odds)
    edge = calculate_edge(model_probability, bookmaker_odds)

    print("💰 BetLab Value Engine")
    print(f"Model Probability: {model_probability}%")
    print(f"Bookmaker Odds: {bookmaker_odds}")
    print(f"Fair Odds: {round(fair, 2)}")
    print(f"Implied Probability: {round(implied, 2)}%")
    print(f"Edge: {round(edge, 2)}%")
    print(f"Decision: {decision(edge)}")
    