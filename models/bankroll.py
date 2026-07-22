from dataclasses import dataclass


@dataclass
class BankrollResult:
    bankroll: float
    stake_fraction: float

    recommended_stake: float
    final_stake: float

    capped: bool
    skipped: bool

    reason: str


def calculate_stake(
    bankroll: float,
    stake_fraction: float,
    minimum_stake: float = 2.0,
    maximum_fraction: float = 0.03,
) -> BankrollResult:

    recommended_stake = bankroll * stake_fraction
    final_stake = recommended_stake

    capped = False
    skipped = False
    reason = ""

    # Maximum allowed stake
    maximum_stake = bankroll * maximum_fraction

    if final_stake > maximum_stake:
        final_stake = maximum_stake
        capped = True
        reason = "Stake capped to bankroll limit."

    # Minimum allowed stake
    if final_stake < minimum_stake:
        final_stake = 0.0
        skipped = True
        reason = "Recommended stake below minimum stake."

    return BankrollResult(
        bankroll=bankroll,
        stake_fraction=stake_fraction,
        recommended_stake=recommended_stake,
        final_stake=final_stake,
        capped=capped,
        skipped=skipped,
        reason=reason,
    )


def print_bankroll_result(result: BankrollResult) -> None:
    print()
    print("BETLAB AI BANKROLL MANAGEMENT")
    print("=" * 60)

    print(f"Bankroll:           €{result.bankroll:.2f}")
    print(f"Stake fraction:     {result.stake_fraction:.2%}")
    print(f"Recommended stake:  €{result.recommended_stake:.2f}")
    print(f"Final stake:        €{result.final_stake:.2f}")
    print(f"Capped:             {'YES' if result.capped else 'NO'}")
    print(f"Skipped:            {'YES' if result.skipped else 'NO'}")

    if result.reason:
        print(f"Reason:             {result.reason}")


def main() -> None:

    result = calculate_stake(
        bankroll=100.0,
        stake_fraction=0.125,
    )

    print_bankroll_result(result)


if __name__ == "__main__":
    main()