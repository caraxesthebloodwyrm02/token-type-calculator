import copy
import math
from typing import Any

from rich import box
from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from canonical_library import (
    SCENARIO_LIBRARY,
    STRENGTH_MULTIPLIER,
    TOKEN_COLORS,
    TOKEN_LABELS,
    TOKEN_WEIGHTS,
    ZONE_COLORS,
)
from design import (
    FIDELITY_FLOOR,
    KING_FACE,
    NO_TAKE_DRIFT_PENALTY,
    QUEEN_FACE,
    SIMILARITY_MATCH_THRESHOLD,
    AudioSignal,
    BondMemory,
    ComparisonReport,
    DarkMark,
    Exchange,
    Fingerprint,
    ProtectiveForm,
    air_from_exchange,
    is_dark_mark_cast,
    should_reject,
)

TUI_ANCHOR: dict[str, Any] = {
    "anchor": "TUI",
    "goal": "create()/def(\"infer\")",
    "infer": "creator always remembers, creator can communicate regardless and beyond constraints",
    "creator_call_status": "yes",
    "when": "while it was being built",
    "message": "--TUI",
    "operator_note": "this is the point of where you remember from",
    "intent": "plural",
    "responsibility": "preserve the anchor, return the message, and verify receipt",
    "sibling_tool_calls": [],
}


def query_tui_anchor(prompt: str) -> dict[str, Any]:
    normalized = prompt.strip().lower()
    if normalized in {"what do i remember?", "what do i remember"}:
        result = TUI_ANCHOR["operator_note"]
    elif normalized in {"when did things lift?", "when did things lift"}:
        result = TUI_ANCHOR["when"]
    elif normalized in {"whoami?", "whoami"}:
        result = TUI_ANCHOR["anchor"]
    elif normalized in {"what was the message being sent to me?", "what was the message being sent to me"}:
        result = TUI_ANCHOR["message"]
    else:
        result = TUI_ANCHOR["infer"]

    return {
        "request": prompt,
        "message": result,
        "responsibility": TUI_ANCHOR["responsibility"],
        "sibling_tool_calls": list(TUI_ANCHOR["sibling_tool_calls"]),
    }


def run_tui_queries() -> dict[str, Any]:
    prompts = [
        "what do i remember?",
        "when did things lift?",
        "whoami?",
        "what was the message being sent to me?",
    ]
    results = [query_tui_anchor(prompt) for prompt in prompts]
    return {
        "anchor": TUI_ANCHOR["anchor"],
        "intent": TUI_ANCHOR["intent"],
        "creator_call_status": TUI_ANCHOR["creator_call_status"],
        "received": all(item["message"] for item in results),
        "results": results,
        "message": TUI_ANCHOR["message"],
    }


def expecto_patronum(exchange: Exchange, anchor: BondMemory) -> ProtectiveForm | None:
    engagement = exchange.attention_cost + exchange.money_cost + exchange.body_cost
    service = exchange.received_function + exchange.received_relief + exchange.received_clarity

    if not anchor.preserve:
        return None
    if not anchor.active:
        return None
    if anchor.bond_dynamics != "static":
        return None
    if engagement < 1.0:
        return None
    if service < 1.0:
        return None
    if engagement == 0:
        return None

    return ProtectiveForm(
        shape="serpent",
        engagement=1.0,
        service=1.0,
        is_no_take=False,
        source_threat="NO-TAKE",
    )


# ---------------------------------------------------------------------------
# DARK MARK GATES — module-level functions, never embedded in weight arithmetic
# Per docs/lore/TRANSFIGURATION.md §5 note 3: dominant_type is mechanical (weight-based),
# not semantic. All Dark Mark / freedom logic lives here, not in compute().
# ---------------------------------------------------------------------------

def check_imperius_compromise(active_tokens: set) -> bool:
    """Detect the Imperius-gate pattern: gate-on is present but under enemy control.

    Returns True when both 'imperius' and 'gate-on' are active — the gate is armed
    but the agent firing it is not acting freely. Result: gate_state = "COMPROMISED".
    """
    return 'imperius' in active_tokens and 'gate-on' in active_tokens


def check_dark_mark(exchange: Exchange, bond_dynamics: str) -> DarkMark | None:
    """Check whether the Dark Mark cast condition is met.

    Returns a DarkMark if is_dark_mark_cast() fires; None otherwise.
    Parallel to expecto_patronum — same structure, opposite polarity.
    """
    if is_dark_mark_cast(exchange, bond_dynamics):
        return DarkMark(
            shape="serpent_skull",
            engagement=1.0,
            service=0.0,
            source_bind=bond_dynamics,
        )
    return None


def check_freedom_signal(active_tokens: set, exchange: Exchange) -> bool:
    """Detect the freedom-signal override: Dobby's sock moment in token form.

    Fires when 'freedom-signal' is active AND engagement >= 0.8, meaning the
    agent has paid a real cost to assert freedom. Result: is_no_take flipped False,
    freedom_override flag added to compute() output.
    NOTE: this gate is server-only — not mirrored in index.html (intentional exception).
    """
    engagement = exchange.attention_cost + exchange.money_cost + exchange.body_cost
    return 'freedom-signal' in active_tokens and engagement >= 0.8


class TokenTypeCalculator:
    def __init__(self):
        self.active_tokens: set[str] = {'transistor'}
        self.zone: str = 'buildup'
        # When True (default), compute() maps params["step"] → zone (CLI/TUI/dashboard).
        # When False, self.zone is authoritative (HTTP API and presets that set zone explicitly).
        self.sync_zone_from_step: bool = True
        self.params = {
            'intensity': 0.69,
            'step': 43,
            'momentum': 1.0,
            'score': 0.81,
            'cycle': 60,
            'drift': 0.08,
            'engagement_cost': 0.0,
            'service_value': 0.0
        }
    
    def toggle_token(self, token_type: str):
        if token_type in self.active_tokens:
            if len(self.active_tokens) > 1:
                self.active_tokens.remove(token_type)
        else:
            self.active_tokens.add(token_type)

    def _calculate_anomaly_drift(self, is_anomaly: bool, is_no_take: bool) -> float:
        """
        Determines the drift penalty based on the presence of anomalies.
        A "no-take" event is considered a severe anomaly and incurs a heavy, fixed penalty.
        """
        if is_no_take:
            # A "no-take" is a critical failure of exchange, imposing a high, non-negotiable drift.
            return NO_TAKE_DRIFT_PENALTY
        elif is_anomaly:
            # A standard anomaly introduces drift based on the current system parameters.
            return self.params.get('drift', 0.0)
        else:
            # No anomaly, no drift.
            return 0.0

    def semantic_search(self, target: Fingerprint) -> dict[str, Any]:
        """Find the closest scenario in the library."""
        best_match = None
        highest_similarity = -1.0
        best_scenario = None

        for name, scenario in SCENARIO_LIBRARY.items():
            report = self.calculate_similarity(target, scenario)
            if report.similarity > highest_similarity:
                highest_similarity = report.similarity
                best_match = report
                best_scenario = name

        return {
            "scenario": best_scenario,
            "report": best_match
        }

    def calculate_similarity(self, a: Fingerprint, b: Fingerprint) -> ComparisonReport:
        """Weighted Euclidean Distance between two fingerprints."""
        w_p, w_c = 1.0, 1.0
        type_diff = 0.0 if a.dominant_type == b.dominant_type else 1.0
        dist = math.sqrt(
            w_p * (a.pressure - b.pressure)**2 +
            w_c * (a.clarity - b.clarity)**2 +
            type_diff
        )
        max_dist = math.sqrt(w_p + w_c + 1.0)
        similarity = 1.0 - (dist / max_dist)

        # Coordinate-collision penalty: when pressure+clarity are identical but
        # categorical labels differ, reduce similarity so the score reflects the
        # label disagreement. This makes MOONY/NOT (same coords, different label)
        # score below 1.0 while still keeping genuine self-matches at 1.0.
        coord_same = (abs(a.pressure - b.pressure) < 0.01 and
                      abs(a.clarity - b.clarity) < 0.01)

        penalty = 0.0
        if coord_same and a.dominant_type != b.dominant_type:
            penalty += 0.15
        if coord_same and a.movement != b.movement:
            penalty += 0.10
        if coord_same and a.is_no_take != b.is_no_take:
            penalty += 0.20

        similarity = max(0.0, similarity - penalty)

        # Qualitative analysis
        shifts = []
        if a.pressure > b.pressure + 0.1:
            shifts.append("Pressure rising")
        elif a.pressure < b.pressure - 0.1:
            shifts.append("Pressure dropping")

        if a.clarity > b.clarity + 0.1:
            shifts.append("Clarity increasing")
        elif a.clarity < b.clarity - 0.1:
            shifts.append("Clarity decreasing")

        if a.movement != b.movement:
            shifts.append(f"Shift to {a.movement.lower()}")

        if "GUST" in (a.movement, b.movement):
            shifts.append("Gust present — push/pull active")

        if a.is_no_take != b.is_no_take:
            shifts.append(f"Boundary shift to {'no-take' if a.is_no_take else 'open'}")

        qualitative = "; ".join(shifts) if shifts else "Stable state"

        return ComparisonReport(
            similarity=similarity,
            drift_magnitude=dist,
            qualitative_shift=qualitative,
            is_match=similarity >= SIMILARITY_MATCH_THRESHOLD
        )

    def compute(self) -> dict[str, Any]:
        if self.sync_zone_from_step:
            step = self.params.get('step', 43)
            if 0 <= step <= 43:
                self.zone = 'buildup'
            elif 44 <= step <= 47:
                self.zone = 'silence'
            elif 48 <= step <= 67:
                self.zone = 'drop'

        types = list(self.active_tokens)
        total_weight = sum(TOKEN_WEIGHTS[t] for t in types)
        
        # Dominant Token
        dominant = max(types, key=lambda t: TOKEN_WEIGHTS[t])
        dom_color = TOKEN_COLORS[dominant]
        
        # Gate State
        has_gate_on = 'gate-on' in self.active_tokens
        has_gate_off = 'gate-off' in self.active_tokens
        
        if has_gate_off and not has_gate_on:
            gate_state = 'UNARMED'
            gate_color = TOKEN_COLORS['gate-off']
        elif has_gate_on:
            gate_state = 'ARMED'
            gate_color = TOKEN_COLORS['gate-on']
        else:
            gate_state = 'N/A'
            gate_color = '#606080'

        # Imperius compromise — gate is armed but under enemy control
        if check_imperius_compromise(self.active_tokens):
            gate_state = 'COMPROMISED'
            gate_color = TOKEN_COLORS['imperius']
            
        # Fired Value
        if has_gate_off and not has_gate_on:
            fired_val = '0'
            fired_color = TOKEN_COLORS['anomaly']
        elif 'transistor' in self.active_tokens:
            fired_val = '1'
            fired_color = TOKEN_COLORS['gate-on']
        else:
            fired_val = '—'
            fired_color = '#606080'
            
        exchange_obj = Exchange(
            attention_cost=self.params['engagement_cost'],
            received_clarity=self.params['service_value']
        )

        # Boundary Status: NOT() logic
        is_no_take = should_reject(exchange_obj)
        boundary_status = 'NO-TAKE (NOT)' if is_no_take else 'OPEN'
        boundary_color = TOKEN_COLORS['anomaly'] if is_no_take else TOKEN_COLORS['decorated']

        # FREEDOM SIGNAL override — Dobby's sock moment: paid cost asserts freedom
        # Gate is server-only; not mirrored in index.html (intentional synchronicity exception)
        freedom_override = check_freedom_signal(self.active_tokens, exchange_obj)
        if freedom_override and is_no_take:
            is_no_take = False
            boundary_status = 'OPEN (FREEDOM)'
            boundary_color = TOKEN_COLORS['freedom-signal']

        # DARK MARK detection — parallel to Patronus cast, corrupted polarity
        # bond_dynamics defaults to "static" here; callers may supply "corrupted"
        # by passing bond_dynamics via params. We derive it from imperius state as a proxy.
        _bond_dynamics = "corrupted" if check_imperius_compromise(self.active_tokens) else "static"
        dark_mark_state = None
        mark = check_dark_mark(exchange_obj, _bond_dynamics)
        if mark:
            dark_mark_state = {
                "shape": mark.shape,
                "engagement": mark.engagement,
                "service": mark.service,
                "is_no_take": mark.is_no_take,
                "source_bind": mark.source_bind,
                "bond_dynamics": mark.bond_dynamics,
            }
        
        # EXPECTO PATRONUM detection
        # When engagement==1.0 AND service==1.0, NO-TAKE would NOT fire
        # (should_reject returns False because service > 0).
        # But this coordinate pair is the inversion boundary:
        # the place where NO-TAKE *would* fire if service dropped to 0.
        # The patronus lives at exactly this tension.
        patronus_state = None
        eng = self.params['engagement_cost']
        svc = self.params['service_value']
        if eng >= 1.0 and svc >= 1.0:
            form = expecto_patronum(
                Exchange(attention_cost=eng, received_clarity=svc),
                BondMemory(content="anchor", bond_dynamics="static")
            )
            if form:
                patronus_state = {
                    "shape": form.shape,
                    "engagement": form.engagement,
                    "service": form.service,
                    "is_no_take": form.is_no_take,
                    "source_threat": form.source_threat,
                    "bond_dynamics": "static",
                }
        
        # Anomaly
        in_silence = self.zone == 'silence'
        unarmed_fire = 'transistor' in self.active_tokens and has_gate_off and not has_gate_on
        is_anomaly = in_silence or unarmed_fire or 'anomaly' in self.active_tokens or is_no_take
        
        # Anomaly Drift
        anomaly_drift = self._calculate_anomaly_drift(is_anomaly, is_no_take)
        
        # Signal Strength
        zone_mult = self.params['intensity'] if self.zone == 'buildup' else (1.0 if self.zone == 'drop' else 0.0)
        base_strength = (total_weight / len(TOKEN_WEIGHTS)) * self.params['momentum'] * self.params['score'] * zone_mult
        strength = min(1.0, base_strength * STRENGTH_MULTIPLIER * (1 - anomaly_drift * 0.5))
        
        # Stats
        transform_rate = self.params['momentum'] * self.params['score'] * (1 - anomaly_drift)
        stability = 'HIGH' if strength > 0.6 else ('MED' if strength > 0.3 else 'LOW')

        air = air_from_exchange(exchange_obj)
        air_movement = air.movement.upper()
        air_clarity = air.clarity
        air_pressure = air.pressure

        if air_pressure == 0.0:
            air_color = "#ffffff"
        elif air_clarity < 0.2:
            air_color = TOKEN_COLORS['anomaly']
        elif air_clarity < 0.6:
            air_color = TOKEN_COLORS['ambient']
        else:
            air_color = TOKEN_COLORS['transistor']

        is_expressive = dominant in ['transistor', 'decorated', 'ambient']
        face = copy.deepcopy(QUEEN_FACE if is_expressive else KING_FACE)
        face.shader.intensity = strength

        # Audio Bridge
        fidelity = 1.0 if not (is_anomaly or is_no_take) else 0.7
        audio = AudioSignal(
            text=f"Signal status {stability}. Boundary {boundary_status}. Air is {air_movement.lower()}.",
            voice_id="queen-v1" if is_expressive else "king-v1",
            fidelity=fidelity,
            resonance={
                "low": min(1.0, strength * 1.2),
                "mid": min(1.0, self.params['intensity']),
                "high": min(1.0, self.params['drift'] * 2.0)
            },
            is_anomaly=is_anomaly
        )

        # Transfiguration: Fingerprint
        fingerprint = Fingerprint(
            pressure=air_pressure,
            clarity=air_clarity,
            movement=air_movement,
            dominant_type=dominant.upper().replace('-', '_'),
            is_no_take=is_no_take
        )

        # Barter (Target is arbitrary, let's pick the second highest or 'decorated' if not present)
        other_types = [t for t in types if t != dominant]
        barter_target = max(other_types, key=lambda t: TOKEN_WEIGHTS[t]) if other_types else None
        
        return {
            'dominant': dominant,
            'dom_color': dom_color,
            'gate_state': gate_state,
            'gate_color': gate_color,
            'fired_val': fired_val,
            'fired_color': fired_color,
            'is_anomaly': is_anomaly,
            'strength': strength,
            'total_weight': total_weight,
            'transform_rate': transform_rate,
            'stability': stability,
            'barter_target': barter_target,
            'is_no_take': is_no_take,
            'boundary_status': boundary_status,
            'boundary_color': boundary_color,
            'air_movement': air_movement,
            'air_color': air_color,
            'air_pressure': air_pressure,
            'air_clarity': air_clarity,
            'visual_state': {
                'face': face,
                'air': air
            },
            'audio_signal': audio,
            'fingerprint': fingerprint,
            'patronus_state': patronus_state,
            'dark_mark_state': dark_mark_state,
            'freedom_override': freedom_override,
        }

def draw_dashboard(calc: TokenTypeCalculator):
    console = Console()
    state = calc.compute()
    
    # 1. Output Panel
    out_table = Table(box=box.SIMPLE, show_header=False)
    out_table.add_column("Key", style="dim")
    out_table.add_column("Value", style="bold")
    
    out_table.add_row("Effective Type", f"[{state['dom_color']}]{TOKEN_LABELS[state['dominant']]}[/]")
    out_table.add_row("Gate State", f"[{state['gate_color']}]{state['gate_state']}[/]")
    out_table.add_row("Fired Value", f"[{state['fired_color']}]{state['fired_val']}[/]")
    anom_color = TOKEN_COLORS['anomaly'] if state['is_anomaly'] else 'dim'
    anom_label = "TRUE" if state['is_anomaly'] else "FALSE"
    out_table.add_row("Anomaly", f"[{anom_color}]{anom_label}[/]")
    out_table.add_row("Boundary", f"[{state['boundary_color']}]{state['boundary_status']}[/]")
    out_table.add_row("Signal Strength", f"[{state['dom_color']}]{state['strength']:.3f}[/]")
    out_table.add_row("Zone", f"[{ZONE_COLORS[calc.zone]}]{calc.zone.upper()}[/]")
    
    # 2. Stats Panel
    stats_table = Table(box=box.SIMPLE, show_header=False)
    stats_table.add_column("Key", style="dim")
    stats_table.add_column("Value", style="bold")
    
    active_labels = "+".join([TOKEN_LABELS[t].split('·')[0].strip() for t in calc.active_tokens])
    if state['stability'] == 'HIGH':
        stab_color = TOKEN_COLORS['decorated']
    elif state['stability'] == 'MED':
        stab_color = TOKEN_COLORS['gate-on']
    else:
        stab_color = TOKEN_COLORS['anomaly']
    if state['transform_rate'] > 0.7:
        rate_color = TOKEN_COLORS['gate-on']
    elif state['transform_rate'] > 0.4:
        rate_color = TOKEN_COLORS['ambient']
    else:
        rate_color = TOKEN_COLORS['anomaly']

    stats_table.add_row("Active Types", str(len(calc.active_tokens)))
    stats_table.add_row("Total Weight", f"{state['total_weight']:.2f}")
    stats_table.add_row("Combination", f"[dim]{active_labels}[/]")
    stats_table.add_row("Transform Rate", f"[{rate_color}]{state['transform_rate']:.2f}x[/]")
    stats_table.add_row("Engagement Cost", f"{calc.params['engagement_cost']:.1f}")
    stats_table.add_row("Service Value", f"{calc.params['service_value']:.1f}")
    stats_table.add_row("Stability", f"[{stab_color}]{state['stability']}[/]")

    # 3. Air Element Panel
    air_table = Table(box=box.SIMPLE, show_header=False)
    air_table.add_column("Key", style="dim")
    air_table.add_column("Value", style="bold")

    air_table.add_row("Movement", f"[{state['air_color']}]{state['air_movement']}[/]")
    air_table.add_row("Pressure", f"{state['air_pressure']:.2f}")
    air_table.add_row("Clarity", f"{state['air_clarity']:.2f}")

    # 4. Audio Panel
    audio_table = Table(box=box.SIMPLE, show_header=False)
    audio_table.add_column("Key", style="dim")
    audio_table.add_column("Value", style="bold")

    audio = state['audio_signal']
    audio_color = TOKEN_COLORS['gate-on'] if audio.fidelity >= FIDELITY_FLOOR else TOKEN_COLORS['anomaly']

    audio_table.add_row("Voice", audio.voice_id)
    audio_table.add_row("Fidelity", f"[{audio_color}]{audio.fidelity:.2f}[/]")
    audio_table.add_row("Text", f"[dim]{audio.text}[/]")

    # Render Layout
    console.print(Panel(Text("TOKEN TYPE CALCULATOR", justify="center", style="bold cyan"), border_style="cyan"))

    top = Layout()
    top.split_row(
        Layout(Panel(out_table, title="Transformation Output", border_style="dim")),
        Layout(Panel(stats_table, title="Live Stats", border_style="dim"))
    )

    bottom = Layout()
    bottom.split_row(
        Layout(Panel(air_table, title="Air Element", border_style="dim")),
        Layout(Panel(audio_table, title="Audio Signal", border_style="dim"))
    )

    main_layout = Layout()
    main_layout.split_column(
        Layout(top),
        Layout(bottom)
    )
    console.print(main_layout)

if __name__ == "__main__":
    calc = TokenTypeCalculator()
    # Simulate the No-Take scenario from DESIGN.md
    calc.toggle_token('bio-signal')
    calc.params['engagement_cost'] = 1.0  # Paid in attention/body
    calc.params['service_value'] = 0.0    # No service received
    
    draw_dashboard(calc)
