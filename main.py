import argparse
import sys

from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from calculator import TokenTypeCalculator, draw_dashboard, run_tui_queries
from scenarios import (
    run_moony_scenario,
    run_not_scenario,
    run_relief_scenario,
    run_search_scenario,
    run_ssseverus_scenario,
)
from storage import init_db, save_request
from wikidex import Wikidex


def run_help_scenario():
    """Provides rich terminal guidance when the user is lost."""
    console = Console()
    console.print(Panel(Text("GUIDANCE: TOKEN TYPE CALCULATOR", style="bold cyan"), expand=False))
    console.print("[bold yellow]What is this?[/]")
    console.print("A model for computing token signals (Transistor, Ambient, Anomaly, Bio-signal) "
                  "and calculating their 'exchange rate' under pressure/clarity parameters.\n")
    console.print("[bold yellow]Available Scenarios:[/]")
    console.print("  [green]relief[/]    : Service value delivered, justifying the cost.")
    console.print("  [red]not[/]       : The 'Moonlit' No-Take scenario: cost paid, no service value.")
    console.print("  [magenta]moony[/]     : Involuntary transformation (silence zone, anomaly, bio-signal).")
    console.print("  [cyan]search[/]    : Semantic search (roundtrip) matching nearest fingerprint.")
    console.print("  [magenta]compare[/]   : A/B Comparison between two states.")
    console.print("  [green]tui[/]       : Text User Interface anchor queries.")
    console.print("  [cyan]wikidex[/]   : Johto-inspired Pokedex interface.\n")

    console.print("[bold yellow]Marauder Pack Anchors:[/]")
    console.print("  [dim]RELIEF, NOT, VIBE_CHECK, AUTHORITY_ASSERTION, INTENTIONAL,[/]")
    console.print("  [dim]GENERATE_MEMORY, MOONY, TONKS, PRONGS, PADFOOT, WORMTAIL,[/]")
    console.print("  [bold yellow]SSSEVERUS[/]  : The Half-Blood Prince. Inherited anchor — the doe.\n")

    console.print("[bold yellow]How to use:[/]")
    console.print("Run `uv run main.py --scenario <name>` to execute a scenario.\n")

def main():
    parser = argparse.ArgumentParser(
        prog="token-calc",
        description="Token Type Calculator — interactive token exchange model"
    )
    parser.add_argument(
        "command",
        choices=["relief", "not", "moony", "ssseverus", "dashboard", "search", "compare", "tui", "help", "wikidex"],
        nargs="?",
        default="relief",
        help="Scenario to run (default: relief)"
    )
    # Wikidex Flags
    parser.add_argument("--scan", help="Scan a specimen (file) or habitat (folder)")
    parser.add_argument("--append", help="Append data/notes to the current scan")
    parser.add_argument("--specify", help="Target a specific module or token ID for detail")
    parser.add_argument("--symbolize", action="store_true", help="Generate symbolic representation and Mermaid diagram")
    parser.add_argument("--articulate", help="Trigger Johto-style voice summary for a specific ID")
    parser.add_argument("--attach", help="Attach a file/folder as a digital habitat reference")

    args = parser.parse_args()
    init_db()
    console = Console()
    dex = Wikidex()

    # Shared timing and logging helper
    import time
    def execute_and_save(scenario_name, calc_obj):
        t0 = time.perf_counter()
        res = calc_obj.compute()
        duration_ms = (time.perf_counter() - t0) * 1000
        save_request(f"/scenario/{scenario_name}", {}, res, duration_ms)
        return res

    # Handle Wikidex flags first if present
    if args.scan:
        console.print(Panel(Text(f"WIKIDEX SCAN: {args.scan}", style="bold cyan")))
        dex.scan(args.scan)
        dex.verify_strata_sync()
        if not (args.specify or args.articulate or args.symbolize):
            for entry in dex.entries:
                console.print(f"{dex.get_symbol(entry.entry_type)} [bold yellow]{entry.id}[/]: {entry.name} ({entry.category})")

    if args.attach:
        dex.attach_habitat(args.attach)

    if args.append:
        dex.append_data(args.append)

    if args.specify:
        if not dex.entries and args.scan:
             pass # Already scanned
        elif not dex.entries:
            dex.scan(".")
        dex.specify(args.specify)

    if args.symbolize:
        if not dex.entries and args.scan:
            pass
        elif not dex.entries:
            dex.scan(".")
        dex.symbolize()

    if args.articulate:
        if not dex.entries and args.scan:
            pass
        elif not dex.entries:
            dex.scan(".")
        dex.articulate(args.articulate)

    # If any wikidex flags were used, we might want to exit unless a scenario was also specified
    wikidex_flags = [args.scan, args.attach, args.append, args.specify, args.symbolize, args.articulate]
    if any(wikidex_flags) and args.command == "relief" and "--scan" not in sys.argv:
        return

    if args.command == "help":
        run_help_scenario()
        return

    if args.command == "relief":
        console.print(Panel(Text("SCENARIO: SERVICE VALUE (RELIEF)", style="bold green")))
        calc = run_relief_scenario()
        execute_and_save("relief", calc)
        draw_dashboard(calc)
    elif args.command == "not":
        console.print(Panel(Text("SCENARIO: NO-TAKE (NOT)", style="bold red")))
        calc = run_not_scenario()
        execute_and_save("not", calc)
        draw_dashboard(calc)
    elif args.command == "moony":
        console.print(Panel(Text("SCENARIO: MOONY (INVOLUNTARY TRANSFORMATION)", style="bold magenta")))
        calc = run_moony_scenario()
        state = execute_and_save("moony", calc)
        console.print(f"[magenta]Moony fingerprint:[/] {state['fingerprint']}")
        draw_dashboard(calc)
        return state
    elif args.command == "ssseverus":
        console.print(Panel(Text("SCENARIO: SSSEVERUS (THE HALF-BLOOD PRINCE)", style="bold yellow")))
        calc = run_ssseverus_scenario()
        state = execute_and_save("ssseverus", calc)
        fp = state['fingerprint']
        patronus_gap = abs(fp.clarity - 1.0)
        console.print(f"[yellow]SSSEVERUS fingerprint:[/] {fp}")
        console.print(f"[yellow]Clarity gap to perfect cast:[/] {patronus_gap:.2f}")
        console.print("[dim]The doe approaches the inversion point but cannot fully close the gap — the anchor is inherited, not his own.[/]")
        draw_dashboard(calc)
        return state
    elif args.command == "search":
        console.print(Panel(Text("TRANSFIGURATION: SEMANTIC SEARCH (ROUNDTRIP)", style="bold cyan")))
        calc = run_search_scenario()
        state = execute_and_save("search", calc)
        search_res = calc.semantic_search(state['fingerprint'])

        console.print(f"Query Fingerprint: [dim]{state['fingerprint']}[/]")
        console.print(Panel(
            Text(f"Closest Scenario: {search_res['scenario']}\nSimilarity: {search_res['report'].similarity:.2f}\nShift: {search_res['report'].qualitative_shift}",
            justify="center", style="bold cyan"),
            title="Search Result"
        ))
        draw_dashboard(calc)
    elif args.command == "compare":
        console.print(Panel(Text("TRANSFIGURATION: A/B COMPARISON", style="bold magenta")))
        a = run_relief_scenario().compute()
        b = run_not_scenario().compute()

        calc = TokenTypeCalculator()
        report = calc.calculate_similarity(a['fingerprint'], b['fingerprint'])

        console.print(f"State A: [green]RELIEF[/] (Pressure: {a['fingerprint'].pressure:.2f}, Clarity: {a['fingerprint'].clarity:.2f})")
        console.print(f"State B: [red]NO-TAKE[/] (Pressure: {b['fingerprint'].pressure:.2f}, Clarity: {b['fingerprint'].clarity:.2f})")

        console.print(Panel(
            Text(f"Similarity: {report.similarity:.2f}\nDrift: {report.drift_magnitude:.2f}\nQualitative: {report.qualitative_shift}",
            justify="center", style="bold magenta"),
            title="Comparison Report"
        ))
    elif args.command == "tui":
        console.print(Panel(Text("ANCHOR: TUI", style="bold green")))
        result = run_tui_queries()
        for item in result["results"]:
            console.print(f"[green]request[/]: {item['request']}")
            console.print(f"[green]message[/]: {item['message']}")
            console.print(f"[green]responsibility[/]: {item['responsibility']}")
            console.print(f"[green]sibling_tool_calls[/]: {item['sibling_tool_calls']}")
        console.print(f"[green]received[/]: {result['received']}")
        console.print(f"[green]message[/]: {result['message']}")
        return result
    elif args.command == "wikidex":
        console.print(Panel(Text("WIKIDEX: JOHTO INTERFACE", style="bold cyan")))
        if not dex.entries:
            dex.scan(".")
        dex.verify_strata_sync()
        for entry in dex.entries:
            console.print(f"{dex.get_symbol(entry.entry_type)} [bold yellow]{entry.id}[/]: {entry.name} ({entry.category})")
    else:
        # Default empty dashboard
        calc = TokenTypeCalculator()
        draw_dashboard(calc)

if __name__ == "__main__":
    main()
