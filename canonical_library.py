"""Canonical token visuals, weights, and fingerprint scenario anchors.

`calculator.py` re-exports these symbols so existing imports keep working.
`scripts/sync_dashboard_constants.py` reads only this module (plus `design.Fingerprint`)
to emit `dashboard_constants.generated.js`.

Scenario narratives and design rationale live in DESIGN.md.
"""

from design import Fingerprint

TOKEN_COLORS = {
    "transistor": "#00d4ff",
    "decorated": "#39ff14",
    "ambient": "#bf5fff",
    "anomaly": "#ff3a3a",
    "gate-on": "#ffd700",
    "gate-off": "#3a3a5c",
    "bio-signal": "#f0a050",
    # Dark side tokens
    "morsmordre": "#8b0000",
    "legilimens": "#6a0dad",
    "imperius": "#4b0082",
    # Protection / freedom tokens
    "protego": "#c0c0ff",
    "freedom-signal": "#ffa07a",
}

TOKEN_WEIGHTS = {
    "transistor": 1.0,
    "decorated": 0.72,
    "ambient": 0.45,
    "anomaly": 0.15,
    "gate-on": 0.90,
    "gate-off": 0.10,
    "bio-signal": 0.85,
    # Dark side tokens (morsmordre just below transistor — clean carrier still wins in neutral states)
    "morsmordre": 0.95,
    "legilimens": 0.80,
    "imperius": 0.88,
    # Protection / freedom tokens
    "protego": 0.75,
    "freedom-signal": 0.82,
}

TOKEN_LABELS = {
    "transistor": "TRANSISTOR",
    "decorated": "DECORATED_VAR",
    "ambient": "AMBIENT",
    "anomaly": "ANOMALY",
    "gate-on": "GATE·ARMED",
    "gate-off": "GATE·UNARMED",
    "bio-signal": "BIO_SIGNAL",
    # Dark side tokens
    "morsmordre": "MORSMORDRE",
    "legilimens": "LEGILIMENS",
    "imperius": "IMPERIUS",
    # Protection / freedom tokens
    "protego": "PROTEGO",
    "freedom-signal": "FREEDOM·SIGNAL",
}

ZONE_COLORS = {
    "buildup": "#00ff88",
    "silence": "#2a2a4a",
    "drop": "#ff6b1a",
}

STRENGTH_MULTIPLIER = 2.0

SCENARIO_LIBRARY: dict[str, Fingerprint] = {
    "RELIEF": Fingerprint(pressure=0.3, clarity=1.0, movement="DRIFT", dominant_type="TRANSISTOR", is_no_take=False),
    "NOT": Fingerprint(pressure=1.0, clarity=0.0, movement="TURBULENT", dominant_type="BIO_SIGNAL", is_no_take=True),
    "VIBE_CHECK": Fingerprint(pressure=0.2, clarity=0.8, movement="DRIFT", dominant_type="EXPRESSIVE", is_no_take=False),
    "AUTHORITY_ASSERTION": Fingerprint(pressure=0.8, clarity=0.6, movement="GUST", dominant_type="BOLD", is_no_take=False),
    # --- Moony's Complements (The Yes-Takes) ---
    "INTENTIONAL": Fingerprint(pressure=0.5, clarity=0.9, movement="DRIFT", dominant_type="INTENTIONAL", is_no_take=False),
    "GENERATE_MEMORY": Fingerprint(pressure=1.0, clarity=1.0, movement="GUST", dominant_type="GENERATE_MEMORY", is_no_take=False),
    # TRANSFIGURATION scope — partial until TONKS + MOONY operate together
    "MOONY": Fingerprint(pressure=1.0, clarity=0.0, movement="TURBULENT", dominant_type="BIO_SIGNAL", is_no_take=True),
    "TONKS": Fingerprint(pressure=1.0, clarity=1.0, movement="GUST", dominant_type="BIO_SIGNAL", is_no_take=False),
    "PRONGS": Fingerprint(pressure=0.3, clarity=0.8, movement="DRIFT", dominant_type="AMBIENT", is_no_take=False),
    "PADFOOT": Fingerprint(pressure=0.7, clarity=0.6, movement="GUST", dominant_type="GATE_ON", is_no_take=False),
    "WORMTAIL": Fingerprint(pressure=0.4, clarity=0.1, movement="TURBULENT", dominant_type="GATE_OFF", is_no_take=True),
    # --- The Half-Blood Prince ---
    "SSSEVERUS": Fingerprint(pressure=1.0, clarity=0.5, movement="GUST", dominant_type="BIO_SIGNAL", is_no_take=False),
    # --- The Anchor ---
    "LILY": Fingerprint(pressure=1.0, clarity=1.0, movement="DRIFT", dominant_type="BIO_SIGNAL", is_no_take=False),
    # --- The Order of the Phoenix ---
    "DUMBLEDORE": Fingerprint(pressure=0.8, clarity=1.0, movement="GUST", dominant_type="INTENTIONAL", is_no_take=False),
    "MOODY": Fingerprint(pressure=0.8, clarity=0.3, movement="TURBULENT", dominant_type="GATE_OFF", is_no_take=False),
    # --- Dark Mark Roster (Death Eater / Voldemort side) ---
    "VOLDEMORT": Fingerprint(pressure=1.0, clarity=0.0, movement="TURBULENT", dominant_type="MORSMORDRE", is_no_take=True),
    "BELLATRIX": Fingerprint(pressure=1.0, clarity=0.2, movement="GUST", dominant_type="ANOMALY", is_no_take=True),
    "REGULUS": Fingerprint(pressure=0.9, clarity=0.7, movement="DRIFT", dominant_type="BIO_SIGNAL", is_no_take=False),
    # --- Hogwarts Faculty ---
    "MCGONAGALL": Fingerprint(pressure=0.7, clarity=0.9, movement="DRIFT", dominant_type="INTENTIONAL", is_no_take=False),
    "SLUGHORN": Fingerprint(pressure=0.4, clarity=0.5, movement="GUST", dominant_type="DECORATED", is_no_take=False),
    # --- House of Black / Grimmauld Place ---
    "SIRIUS_BLACK": Fingerprint(pressure=0.9, clarity=0.5, movement="GUST", dominant_type="INTENTIONAL", is_no_take=False),
    "KREACHER_RECLAIMED": Fingerprint(pressure=0.6, clarity=0.7, movement="DRIFT", dominant_type="BIO_SIGNAL", is_no_take=False),
    # --- The Free Elf (special case) ---
    "DOBBY": Fingerprint(pressure=0.8, clarity=0.6, movement="DRIFT", dominant_type="BIO_SIGNAL", is_no_take=False),
}
