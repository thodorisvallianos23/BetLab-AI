def calculate_tracker_stats(starting_balance, current_balance, bets):
    profit = current_balance - starting_balance
    roi = (profit / starting_balance) * 100 if starting_balance > 0 else 0

    total_bets = len(bets)
    settled_bets = [bet for bet in bets if bet[8] in ("Won", "Lost", "Push")]
    won_bets = [bet for bet in bets if bet[8] == "Won"]

    win_rate = (len(won_bets) / len(settled_bets)) * 100 if settled_bets else 0
    pending_bets = len([bet for bet in bets if bet[8] == "Pending"])

    total_staked = sum(float(bet[7]) for bet in bets)
    total_profit_loss = sum(float(bet[9]) for bet in bets)

    yield_percent = (total_profit_loss / total_staked) * 100 if total_staked > 0 else 0

    return {
        "profit": profit,
        "roi": roi,
        "total_bets": total_bets,
        "settled_bets": len(settled_bets),
        "pending_bets": pending_bets,
        "win_rate": win_rate,
        "total_staked": total_staked,
        "total_profit_loss": total_profit_loss,
        "yield_percent": yield_percent,
    }