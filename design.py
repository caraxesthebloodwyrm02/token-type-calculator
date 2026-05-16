# DESCRIPTION
# Right partition: crown on a queen's head — EXPRESSIVE surface, authority worn visibly,
#   adornment as signal. Boundary held by form, not force.
# Left partition: king in bandana follows — INTENTIONAL presence, power worn casually,
#   weight carried without declaration. Movement precedes announcement.
# Together: an exchange where both sides carry sovereign weight. The no-take fires
#   when one side performs regalia without delivering the kingdom.

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from typing import Literal


class TokenType(StrEnum):
    EXPRESSIVE = "EXPRESSIVE"
    INTENTIONAL = "INTENTIONAL"
    BOLD = "BOLD"
    GENERATE_MEMORY = "GENERATE_MEMORY"
    BIO_SIGNAL = "BIO_SIGNAL"
    NOT = "NOT"
    # Dark side tokens — Death Eater / Dark Mark layer
    MORSMORDRE = "MORSMORDRE"      # Dark Mark cast; full pressure, zero clarity
    LEGILIMENS = "LEGILIMENS"      # Invasive clarity — forced, not given
    IMPERIUS = "IMPERIUS"          # Corrupted GATE_ON; armed but controlled by another
    # Protection / freedom tokens
    PROTEGO = "PROTEGO"            # Shield charm; reliable protection at moderate cost
    FREEDOM_SIGNAL = "FREEDOM_SIGNAL"  # Dobby's sock moment; overrides enforced NO-TAKE


ClaimedValue = Literal[
    "attention",
    "presentation",
    "vibe",
    "fit",
    "function",
    "reason",
    "authority",
    "certainty",
    "pressure",
    "trace",
    "note",
    "recall",
    "body-level evidence",
    "boundary protection",
]

BoundaryResult = Literal[
    "observe",
    "continue only if service value appears",
    "inspect",
    "preserve",
    "raise weight",
    "stop exchange",
]


@dataclass
class Exchange:
    engagement_cost: float = 0.0
    service_value: float = 0.0


def should_reject(exchange: Exchange) -> bool:
    return exchange.engagement_cost > 0 and exchange.service_value == 0


def is_dark_mark_cast(exchange: Exchange, bond_dynamics: str) -> bool:
    """Dark Mark boundary — the corrupted inverse of the Patronus cast.

    Fires at (1.0, 0.0) with a corrupted bond: full engagement extracted,
    zero service returned, loyalty turned into servitude.
    Structurally parallel to should_reject but requires bond_dynamics == "corrupted"
    to distinguish Death Eater obedience from ordinary NO-TAKE.
    """
    return exchange.engagement_cost >= 1.0 and exchange.service_value == 0.0 and bond_dynamics == "corrupted"



# ---------------------------------------------------------------------------
# CANVAS — visual layer
# ---------------------------------------------------------------------------

Hex = str  # e.g. "#bf5fff"
Partition = Literal["left", "right", "center", "full"]


@dataclass
class ColorShade:
    name: str
    base: Hex
    light: Hex
    dark: Hex
    muted: Hex


@dataclass
class Shader:
    mode: Literal["flat", "radial", "linear", "rim", "ambient-occlusion"]
    intensity: float          # 0.0–1.0
    direction: float          # degrees; 0 = top, 90 = right
    opacity: float = 1.0


@dataclass
class Stroke:
    weight: float             # px equivalent
    color: Hex
    style: Literal["solid", "dashed", "dotted", "none"]
    cap: Literal["round", "square", "butt"] = "round"
    join: Literal["round", "miter", "bevel"] = "round"


@dataclass
class Accessory:
    name: str
    partition: Partition
    token_type: TokenType
    color: ColorShade
    stroke: Stroke
    layer: int = 0            # z-order; higher = front


@dataclass
class Face:
    partition: Partition
    role: Literal["queen", "king", "neutral"]
    skin_shade: ColorShade
    shader: Shader
    accessories: list[Accessory] = field(default_factory=list)
    outline: Stroke = field(default_factory=lambda: Stroke(weight=1.5, color="#ffffff", style="solid"))


# ---------------------------------------------------------------------------
# Canonical palette derived from TOKEN_COLORS + canvas description
# ---------------------------------------------------------------------------

SHADE_CROWN = ColorShade(
    name="crown",
    base="#ffd700",    # gate-on gold
    light="#ffe566",
    dark="#b8960a",
    muted="#a08030",
)

SHADE_BANDANA = ColorShade(
    name="bandana",
    base="#00d4ff",    # transistor cyan
    light="#66e8ff",
    dark="#0099bb",
    muted="#2a6070",
)

SHADE_SKIN_QUEEN = ColorShade(
    name="skin-queen",
    base="#f0c896",
    light="#f8e0c0",
    dark="#c8905a",
    muted="#a07040",
)

SHADE_SKIN_KING = ColorShade(
    name="skin-king",
    base="#8b5e3c",
    light="#b07850",
    dark="#5a3820",
    muted="#6a4830",
)

SHADE_AMBIENT_BG = ColorShade(
    name="ambient-bg",
    base="#bf5fff",    # ambient deep-purple
    light="#d890ff",
    dark="#7a2fbb",
    muted="#4a1a6a",
)

CROWN_ACCESSORY = Accessory(
    name="crown",
    partition="right",
    token_type=TokenType.EXPRESSIVE,
    color=SHADE_CROWN,
    stroke=Stroke(weight=2.0, color="#ffe566", style="solid"),
    layer=3,
)

BANDANA_ACCESSORY = Accessory(
    name="bandana",
    partition="left",
    token_type=TokenType.INTENTIONAL,
    color=SHADE_BANDANA,
    stroke=Stroke(weight=1.5, color="#66e8ff", style="solid"),
    layer=2,
)

QUEEN_FACE = Face(
    partition="right",
    role="queen",
    skin_shade=SHADE_SKIN_QUEEN,
    shader=Shader(mode="rim", intensity=0.75, direction=315.0),
    accessories=[CROWN_ACCESSORY],
)

KING_FACE = Face(
    partition="left",
    role="king",
    skin_shade=SHADE_SKIN_KING,
    shader=Shader(mode="radial", intensity=0.60, direction=270.0),
    accessories=[BANDANA_ACCESSORY],
)


# ---------------------------------------------------------------------------
# ENVIRONMENT — air element
# Synthesized from: token weights, boundary logic, canvas shader modes,
# bio-signal lived cost, and the no-take exchange pattern.
# ---------------------------------------------------------------------------

@dataclass
class AirElement:
    name: str
    description: str
    pressure: float           # 0.0 low / 1.0 high — maps to engagement_cost weight
    clarity: float            # 0.0 opaque / 1.0 clear — maps to service_value delivery
    movement: Literal["still", "drift", "gust", "turbulent"]
    token_affinity: list[TokenType]
    ambient_color: ColorShade


AIR = AirElement(
    name="air",
    description=(
        "The medium through which exchange signals travel. "
        "Clear air = service value delivered, engagement cost justified. "
        "Turbulent air = BIO_SIGNAL active, NOT() imminent. "
        "Still air = silence zone, anomaly window open."
    ),
    pressure=0.0,             # default: no engagement cost loaded
    clarity=1.0,              # default: full service value assumed
    movement="drift",         # resting state mirrors ambient token drift
    token_affinity=[
        TokenType.EXPRESSIVE,
        TokenType.BIO_SIGNAL,
        TokenType.NOT,
    ],
    ambient_color=SHADE_AMBIENT_BG,
)


def air_from_exchange(exchange: Exchange) -> AirElement:
    clarity = min(1.0, exchange.service_value / exchange.engagement_cost) if exchange.engagement_cost > 0 else 1.0
    pressure = min(1.0, exchange.engagement_cost)
    if pressure == 0.0:
        movement: Literal["still", "drift", "gust", "turbulent"] = "still"
    elif clarity < 0.2:
        movement = "turbulent"
    elif clarity < 0.6:
        movement = "gust"
    else:
        movement = "drift"
    return AirElement(
        name="air",
        description=AIR.description,
        pressure=pressure,
        clarity=clarity,
        movement=movement,
        token_affinity=AIR.token_affinity,
        ambient_color=SHADE_AMBIENT_BG,
    )


# ---------------------------------------------------------------------------
# AUDIO — signal layer
# ---------------------------------------------------------------------------

FIDELITY_FLOOR = 0.8

# Similarity
SIMILARITY_MATCH_THRESHOLD = 0.90   # calculator.py:249 — is_match in ComparisonReport

# Marauder map
MOONY_SCORE_THRESHOLD = 0.8          # marauders_map.py:63, api.py:164
TONKS_SCORE_THRESHOLD = 0.8           # api.py:164
PRONGS_ACCOMPANIMENT_FLOOR = 0.15     # marauders_map.py:63 — PRONGS must clear for accompaniment
PRONGS_PRESENCE_THRESHOLD = 0.7        # api.py:150 — prongs_present annotation

# Anomaly drift
NO_TAKE_DRIFT_PENALTY = 0.8            # calculator.py:172 — fixed drift for no-take events

# SSSEVERUS — Half-Blood Prince
SSSEVERUS_CLARITY_GAP = 0.5            # distance between Snape's doe (0.5) and the perfect cast (1.0)

# ORDER OF THE PHOENIX — scope thresholds
PHOENIX_CORE_SCORE = 0.7               # minimum similarity to register as a phoenix presence

# DARK MARK / DEATH EATER — scope thresholds
DARK_MARK_THRESHOLD = 0.8             # minimum similarity to register as Death Eater proximity
MORSMORDRE_SCOPE_MIN = 0.7            # both VOLDEMORT + BELLATRIX must clear this to open MORSMORDRE scope
REGULUS_REDEMPTION_FLOOR = 0.7        # REGULUS score needed to annotate redemption arc


@dataclass
class AudioSignal:
    text: str                  # The string to be synthesized
    voice_id: str = "neutral"  # 'queen-v1' or 'king-v1'
    fidelity: float = 1.0      # 1.0 = clean, < 0.8 = violation
    resonance: dict[str, float] = field(default_factory=lambda: {"low": 0.5, "mid": 0.5, "high": 0.5})
    is_anomaly: bool = False
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


# ---------------------------------------------------------------------------
# TRANSFIGURATION — semantic similarity layer
# ---------------------------------------------------------------------------

@dataclass
class Fingerprint:
    pressure: float           # derived from engagement cost
    clarity: float            # derived from service value delivery
    movement: str             # quantized state (STILL, DRIFT, GUST, TURBULENT)
    dominant_type: str        # highest weight token
    is_no_take: bool          # boundary status


@dataclass
class ComparisonReport:
    similarity: float         # 0.0 to 1.0 (Euclidean-based)
    drift_magnitude: float    # distance in coordinate space
    qualitative_shift: str    # description of how A differs from B
    is_match: bool            # similarity >= 0.90


# ---------------------------------------------------------------------------
# EXPECTO PATRONUM — NO-TAKE inversion layer
# ---------------------------------------------------------------------------

@dataclass
class BondMemory:
    content: str                  # the load-bearing memory
    bond_dynamics: str = "static" # must be static to cast
    preserve: bool = True         # signature stability check
    active: bool = True           # signature is alive


@dataclass
class ProtectiveForm:
    shape: str                    # recompiled threat — "serpent"
    engagement: float = 1.0       # full cost paid
    service: float = 1.0          # full protection returned
    is_no_take: bool = False      # NOT NO-TAKE — perfect inverse
    source_threat: str = ""       # what would have harmed


# ---------------------------------------------------------------------------
# DARK MARK — corrupted inverse of the Patronus system
# Patronus: threat → light (engagement=1.0, service=1.0, bond=static)
# Dark Mark: loyalty → servitude (engagement=1.0, service=0.0, bond=corrupted)
# The Patronus recompiles the threat-shape outward.
# The Dark Mark brands the caster inward — the mark is permanent, the master takes all.
# ---------------------------------------------------------------------------

@dataclass
class DarkMark:
    """The corrupted cast — full engagement, zero service, bond inverted.

    bond_dynamics must be "corrupted" for the mark to form.
    Shape reflects the mechanism of control:
      serpent_skull   — direct domination (Voldemort's inner circle)
      coercion_bind   — indirect control through fear or blackmail
      fear_anchor     — loyalty held by threat alone, no positive bond
    """
    shape: Literal["serpent_skull", "coercion_bind", "fear_anchor"]
    engagement: float = 1.0       # full cost extracted from the caster
    service: float = 0.0          # master returns nothing
    is_no_take: bool = True       # always a NO-TAKE by structure
    source_bind: str = ""         # what holds the caster — Voldemort, fear, debt
    bond_dynamics: str = "corrupted"  # invariant
