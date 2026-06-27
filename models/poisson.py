import math

def poisson_probability(lam, goals):
    return (math.exp(-lam) * lam**goals) / math.factorial(goals)

def over_probability(total_xg, line):
    max_goals = int(line)
    prob_under_or_equal = sum(
        poisson_probability(total_xg, goals)
        for goals in range(max_goals + 1)
    )
    return 1 - prob_under_or_equal

if __name__ == "__main__":
    total_xg = 2.7

    print("⚽ BetLab Poisson Engine")
    print(f"Expected Goals: {total_xg}")
    print(f"Over 0.5: {round(over_probability(total_xg, 0.5) * 100, 2)}%")
    print(f"Over 1.5: {round(over_probability(total_xg, 1.5) * 100, 2)}%")
    print(f"Over 2.5: {round(over_probability(total_xg, 2.5) * 100, 2)}%")
    print(f"Over 3.5: {round(over_probability(total_xg, 3.5) * 100, 2)}%")
    