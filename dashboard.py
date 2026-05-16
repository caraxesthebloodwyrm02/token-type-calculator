from __future__ import annotations

from typing import TYPE_CHECKING, Any

from rich import box
from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from canonical_library import TOKEN_COLORS, TOKEN_LABELS, ZONE_COLORS
from design import FIDELITY_FLOOR

if TYPE_CHECKING:
    from calculator import TokenTypeCalculator

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


def draw_dashboard(calc: TokenTypeCalculator) -> None:
    console = Console()
    state = calc.compute()

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

    air_table = Table(box=box.SIMPLE, show_header=False)
    air_table.add_column("Key", style="dim")
    air_table.add_column("Value", style="bold")

    air_table.add_row("Movement", f"[{state['air_color']}]{state['air_movement']}[/]")
    air_table.add_row("Pressure", f"{state['air_pressure']:.2f}")
    air_table.add_row("Clarity", f"{state['air_clarity']:.2f}")

    audio_table = Table(box=box.SIMPLE, show_header=False)
    audio_table.add_column("Key", style="dim")
    audio_table.add_column("Value", style="bold")

    audio = state['audio_signal']
    audio_color = TOKEN_COLORS['gate-on'] if audio.fidelity >= FIDELITY_FLOOR else TOKEN_COLORS['anomaly']

    audio_table.add_row("Voice", audio.voice_id)
    audio_table.add_row("Fidelity", f"[{audio_color}]{audio.fidelity:.2f}[/]")
    audio_table.add_row("Text", f"[dim]{audio.text}[/]")

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
