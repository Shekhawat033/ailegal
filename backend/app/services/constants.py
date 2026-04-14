from __future__ import annotations

V1_ISSUE_TYPES = frozenset(
    {
        "account_hacking",
        "payment_fraud",
        "impersonation",
        "cyber_stalking_harassment",
    }
)

V1_CITY_SLUGS = frozenset({"mumbai", "delhi", "bengaluru"})

CITY_ALIASES = {
    "mumbai": "mumbai",
    "bombay": "mumbai",
    "delhi": "delhi",
    "new delhi": "delhi",
    "bengaluru": "bengaluru",
    "bangalore": "bengaluru",
}
