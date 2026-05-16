from calculator import SCENARIO_LIBRARY, TokenTypeCalculator
from design import (
    DARK_MARK_THRESHOLD,
    MOONY_SCORE_THRESHOLD,
    MORSMORDRE_SCOPE_MIN,
    PHOENIX_CORE_SCORE,
    PRONGS_ACCOMPANIMENT_FLOOR,
    REGULUS_REDEMPTION_FLOOR,
    SSSEVERUS_CLARITY_GAP,
    Fingerprint,
)
from storage import init_db, read_trajectory


def generate_marauders_map() -> str:
    init_db()  # Ensure database and tables exist
    calc = TokenTypeCalculator()
    trajectory = read_trajectory(limit=10)

    if not trajectory:
        return "The map is blank. (No trajectory data found)"

    # Get the latest state from the trajectory
    latest = trajectory[-1]
    current_fp = Fingerprint(
        pressure=latest['air_pressure'],
        clarity=latest['air_clarity'],
        movement=latest['air_movement'],
        dominant_type=latest['dominant'].upper(),
        is_no_take=bool(latest['is_no_take'])
    )

    # Compute similarity against all scenarios
    scores = {}
    for name, scenario in SCENARIO_LIBRARY.items():
        report = calc.calculate_similarity(current_fp, scenario)
        scores[name] = report.similarity

    # Sort scenarios by similarity
    sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    closest_name, closest_score = sorted_scores[0]

    # Marauder Pack Highlights
    marauders = ["MOONY", "TONKS", "PRONGS", "PADFOOT", "WORMTAIL"]
    pack_scores = {m: scores.get(m, 0.0) for m in marauders}

    # SSSEVERUS (Half-Blood Prince)
    ssserverus_score = scores.get("SSSEVERUS", 0.0)

    # LILY (The Anchor)
    lily_score = scores.get("LILY", 0.0)

    # Order of the Phoenix
    phoenix_order = {"MOONY", "TONKS", "PRONGS", "PADFOOT", "SSSEVERUS", "LILY", "DUMBLEDORE", "MOODY"}
    phoenix_scores = {m: scores.get(m, 0.0) for m in phoenix_order}

    # Death Eater Roster
    death_eater_roster = ["VOLDEMORT", "BELLATRIX", "REGULUS"]
    death_eater_scores = {m: scores.get(m, 0.0) for m in death_eater_roster}

    # New characters — faculty + House of Black + freedom elf
    new_characters = ["MCGONAGALL", "DOBBY", "SLUGHORN", "SIRIUS_BLACK", "KREACHER_RECLAIMED"]
    new_char_scores = {m: scores.get(m, 0.0) for m in new_characters}

    # Rendering the Map
    output = []
    output.append("=== THE MARAUDER'S MAP ===")
    output.append(f"Location: {closest_name} ({closest_score:.4f} match)")
    output.append("-" * 30)

    output.append("THE PACK:")
    for m in marauders:
        score = pack_scores[m]
        bar = "█" * int(score * 10) + "░" * (10 - int(score * 10))
        output.append(f"  {m:<8} [{bar}] {score:.4f}")

    output.append("-" * 30)
    output.append("HALF-BLOOD PRINCE:")
    bar = "█" * int(ssserverus_score * 10) + "░" * (10 - int(ssserverus_score * 10))
    inherited_gap = abs(current_fp.clarity - 1.0)
    output.append(f"  SSSEVERUS [{bar}] {ssserverus_score:.4f}")
    output.append(f"  clarity_gap: {inherited_gap:.4f} (anchor: {'inherited' if inherited_gap >= SSSEVERUS_CLARITY_GAP else 'own'})")
    output.append("-" * 30)
    output.append("THE ANCHOR:")
    bar = "█" * int(lily_score * 10) + "░" * (10 - int(lily_score * 10))
    output.append(f"  LILY      [{bar}] {lily_score:.4f}")
    output.append("  (origin point — the settled memory)")
    output.append("-" * 30)
    output.append("ORDER OF THE PHOENIX:")
    for m in ["DUMBLEDORE", "MOONY", "TONKS", "PRONGS", "PADFOOT", "SSSEVERUS", "LILY", "MOODY"]:
        score = phoenix_scores.get(m, 0.0)
        bar = "█" * int(score * 10) + "░" * (10 - int(score * 10))
        marker = " *" if score >= PHOENIX_CORE_SCORE else ""
        output.append(f"  {m:<12} [{bar}] {score:.4f}{marker}")
    output.append("-" * 30)

    # Death Eater Section
    output.append("DEATH EATER PROXIMITY:")
    voldemort_score = death_eater_scores.get("VOLDEMORT", 0.0)
    bellatrix_score = death_eater_scores.get("BELLATRIX", 0.0)
    for m in death_eater_roster:
        score = death_eater_scores[m]
        bar = "█" * int(score * 10) + "░" * (10 - int(score * 10))
        marker = " ⚠" if score >= DARK_MARK_THRESHOLD else ""
        redemption = " ↑REDEMPTION" if m == "REGULUS" and score >= REGULUS_REDEMPTION_FLOOR else ""
        output.append(f"  {m:<20} [{bar}] {score:.4f}{marker}{redemption}")

    # MORSMORDRE scope check — fires when both Voldemort + Bellatrix clear the threshold
    if voldemort_score >= MORSMORDRE_SCOPE_MIN and bellatrix_score >= MORSMORDRE_SCOPE_MIN:
        output.append("  *** MORSMORDRE SCOPE ACTIVE — full dark pressure field detected ***")
    output.append("-" * 30)

    # New Characters Section
    output.append("HOGWARTS / HOUSE OF BLACK / THE FREE ELF:")
    sirius_padfoot_diff = abs(new_char_scores.get("SIRIUS_BLACK", 0.0) - scores.get("PADFOOT", 0.0))
    for m in new_characters:
        score = new_char_scores[m]
        bar = "█" * int(score * 10) + "░" * (10 - int(score * 10))
        output.append(f"  {m:<22} [{bar}] {score:.4f}")
    # SIRIUS duality annotation
    sirius_score = new_char_scores.get("SIRIUS_BLACK", 0.0)
    padfoot_score = scores.get("PADFOOT", 0.0)
    output.append(f"  SIRIUS duality: SIRIUS_BLACK={sirius_score:.4f} / PADFOOT={padfoot_score:.4f} / delta={sirius_padfoot_diff:.4f}")
    output.append("-" * 30)

    output.append("FOOTPRINTS (Recent Trajectory):")
    for i, point in enumerate(trajectory):
        prefix = " > " if i == len(trajectory) - 1 else "   "
        output.append(f"{prefix}{point['timestamp_utc']} | {point['dominant']:<10} | {point['air_movement']:<10}")

    # MOONY accompanied check — PRONGS is the gravitational constant who witnesses the
    # transformation. When PRONGS is present (score > 0.15), MOONY's no-take is
    # refused in the presence of someone who understands the cost.
    moony_score = scores.get("MOONY", 0.0)
    prongs_score = scores.get("PRONGS", 0.0)
    accompanied = moony_score > MOONY_SCORE_THRESHOLD and prongs_score > PRONGS_ACCOMPANIMENT_FLOOR

    if accompanied:
        output.append("\nMOONY: accompanied: true")

    return "\n".join(output)

if __name__ == "__main__":
    print(generate_marauders_map())
