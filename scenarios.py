"""Preset calculator configurations shared by CLI (`main.py`) and API (`api.py`).

Keeping builders here avoids coupling the HTTP surface to the CLI entry module.
"""

from calculator import TokenTypeCalculator


def run_relief_scenario() -> TokenTypeCalculator:
    """Scenario where service value is delivered, justifying the cost."""
    calc = TokenTypeCalculator()
    calc.toggle_token("transistor")
    calc.toggle_token("gate-on")
    calc.params["engagement_cost"] = 0.5
    calc.params["service_value"] = 0.9
    return calc


def run_not_scenario() -> TokenTypeCalculator:
    """The 'Moonlit' No-Take scenario: cost without service."""
    calc = TokenTypeCalculator()
    calc.toggle_token("bio-signal")
    calc.toggle_token("anomaly")
    calc.params["engagement_cost"] = 1.0
    calc.params["service_value"] = 0.0
    return calc


def run_moony_scenario() -> TokenTypeCalculator:
    """Moony under the moon: canonical no-take per DESIGN.md."""
    calc = TokenTypeCalculator()
    calc.toggle_token("bio-signal")
    calc.toggle_token("anomaly")
    calc.toggle_token("gate-off")
    calc.toggle_token("transistor")
    calc.zone = "silence"
    calc.params["engagement_cost"] = 1.0
    calc.params["service_value"] = 0.0
    calc.params["drift"] = 0.3
    return calc


def run_ssseverus_scenario() -> TokenTypeCalculator:
    """The Half-Blood Prince: full engagement cost, occluded clarity, inherited anchor."""
    calc = TokenTypeCalculator()
    calc.toggle_token("bio-signal")
    calc.toggle_token("decorated")
    calc.toggle_token("ambient")
    calc.toggle_token("transistor")
    calc.params["engagement_cost"] = 1.0
    calc.params["service_value"] = 0.5
    calc.params["drift"] = 0.15
    calc.params["intensity"] = 0.95
    return calc


def run_search_scenario() -> TokenTypeCalculator:
    """Find the closest match for a borderline scenario."""
    calc = TokenTypeCalculator()
    calc.toggle_token("decorated")
    calc.params["engagement_cost"] = 0.4
    calc.params["service_value"] = 0.2
    return calc
