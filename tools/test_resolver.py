from services.match_resolver import resolve_match

result = resolve_match(
    "Arsenal FC",
    "Liverpool FC",
    "Premier League",
    "2026/2027",
)

print(result)