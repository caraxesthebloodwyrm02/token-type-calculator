import os
from dataclasses import dataclass

from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from design import AudioSignal

# 9 Cognition Patterns
COGNITION_PATTERNS = [
    "Flow", "Spatial", "Rhythm", "Color", "Repetition",
    "Deviation", "Cause", "Time", "Combination"
]

@dataclass
class WikidexEntry:
    id: str
    name: str
    category: str  # One of the 9 cognition patterns
    entry_type: str  # specimen [·], habitat [∴], evolution [~>]
    weight: float
    summary: str
    warning: str = "None"
    path: str = ""

class Wikidex:
    def __init__(self):
        self.entries: list[WikidexEntry] = []
        self.console = Console()
        self.current_scan_path: str | None = None

    def get_symbol(self, entry_type: str) -> str:
        symbols = {
            "specimen": "[·]",
            "habitat": "[∴]",
            "evolution": "[~>]"
        }
        return symbols.get(entry_type.lower(), "[?]")

    def categorize(self, name: str, is_dir: bool) -> str:
        # Special Resonance
        if "waterfall" in name.lower():
            return "Rhythm"
        # Simple heuristic mapping for now
        if is_dir:
            return "Spatial"
        if "calc" in name.lower() or "math" in name.lower():
            return "Cause"
        if "design" in name.lower() or "style" in name.lower():
            return "Color"
        if "main" in name.lower() or "loop" in name.lower():
            return "Flow"
        if "test" in name.lower() or "smoke" in name.lower():
            return "Repetition"
        if "anomaly" in name.lower():
            return "Deviation"
        if "signal" in name.lower() or "audio" in name.lower():
            return "Rhythm"
        if "date" in name.lower() or "time" in name.lower():
            return "Time"
        return "Combination"

    def scan(self, path: str):
        self.current_scan_path = os.path.abspath(path)
        self.entries = []

        self.console.print(f"[bold cyan]Scanning habitat at {path}...[/]")
        self.console.print("[dim italic]Pointing device... Alignment locked.[/]")

        if not os.path.exists(path):
            self.console.print(f"[red]Error: Path {path} does not exist.[/]")
            return

        idx = 1
        if os.path.isfile(path):
            name = os.path.basename(path)
            self.entries.append(WikidexEntry(
                id=str(idx).zfill(3),
                name=name,
                category=self.categorize(name, False),
                entry_type="specimen",
                weight=round(os.path.getsize(path) / 1024, 2),
                summary=f"A digital specimen located at {path}.",
                path=path
            ))
        else:
            for root, dirs, files in os.walk(path):
                # Only top level for now or specific depth?
                # Let's do top level for habitat view
                for d in dirs:
                    if d.startswith('.') or d == "__pycache__":
                        continue
                    self.entries.append(WikidexEntry(
                        id=str(idx).zfill(3),
                        name=d,
                        category=self.categorize(d, True),
                        entry_type="habitat",
                        weight=0.0,
                        summary="A digital habitat containing multiple sub-elements.",
                        path=os.path.join(root, d)
                    ))
                    idx += 1
                for f in files:
                    if f.startswith('.') or f.endswith('.pyc'):
                        continue
                    fpath = os.path.join(root, f)
                    self.entries.append(WikidexEntry(
                        id=str(idx).zfill(3),
                        name=f,
                        category=self.categorize(f, False),
                        entry_type="specimen",
                        weight=round(os.path.getsize(fpath) / 1024, 2),
                        summary="A digital specimen found within the habitat.",
                        path=fpath
                    ))
                    idx += 1
                break # Only top level for habitat scan

    def specify(self, entry_id: str):
        entry = next((e for e in self.entries if e.id == entry_id), None)
        if not entry:
            self.console.print(f"[red]Error: Entry ID {entry_id} not found.[/]")
            return

        self.console.print(Panel(
            Text.assemble(
                (f"{self.get_symbol(entry.entry_type)} ", "bold cyan"),
                (f"ID: {entry.id} | NAME: {entry.name}\n", "bold yellow"),
                (f"CATEGORY: {entry.category} | WEIGHT: {entry.weight} UNITS\n", "dim"),
                (f"SUMMARY: {entry.summary}\n", "italic white"),
                (f"WARNING: {entry.warning}", "bold red")
            ),
            title="Wikidex Detail",
            border_style="cyan"
        ))

    def symbolize(self):
        if not self.entries:
            self.console.print("[yellow]No entries to symbolize. Run --scan first.[/]")
            return

        mermaid = ["graph TD"]
        for entry in self.entries:
            symbol = self.get_symbol(entry.entry_type)
            mermaid.append(f"    E{entry.id}[{symbol} {entry.name}]")
            # For now, just a list. Real lineage would need dependency parsing.

        self.console.print("[bold cyan]Strata Lineage (Mermaid):[/]")
        self.console.print("\n".join(mermaid))

    def articulate(self, entry_id: str):
        entry = next((e for e in self.entries if e.id == entry_id), None)
        if not entry:
            self.console.print(f"[red]Error: Entry ID {entry_id} not found.[/]")
            return

        # Johto Pokedex Voice Template
        template = (
            f"WIKIDEX: {entry.name.upper()}. THE {entry.category.upper()} MODULE. "
            f"DATA ENTRY NUMBER {entry.id}. "
            f"WEIGHT: {entry.weight} UNITS. "
            f"... "
            f"SUMMARY: {entry.summary} "
            f"... "
            f"CONDITION: {entry.warning}. "
            f"THIS DATA HAS BEEN RECORDED IN THE MANGROVE INDEX."
        )

        audio = AudioSignal(
            text=template,
            voice_id="johto-pokedex-v1",
            fidelity=1.0,
            is_anomaly=False
        )

        self.console.print("[bold magenta]Johto Voice Summary:[/]")
        self.console.print(f"[italic]\"{template}\"[/]")
        return audio

    def verify_strata_sync(self):
        claude_md_path = os.environ.get("CLAUDE_MD_PATH", os.path.expanduser("~/CLAUDE.md"))
        if not os.path.exists(claude_md_path):
            self.console.print(f"[red]Error: {claude_md_path} not found.[/]")
            return False

        with open(claude_md_path) as f:
            content = f.read()


        if "token-type-calculator" not in content:
            self.console.print(Panel(
                Text("STRATA SYNC ERROR: DRIFT DETECTED", style="bold white on red"),
                subtitle="Hermes Signature Verification Failed",
                border_style="red"
            ))
            return False
        else:
            self.console.print("[bold green]Hermes Signature: Strata Sync Verified.[/]")
            return True

    def append_data(self, input_text: str):
        if not self.entries:
            self.console.print("[yellow]No active scan to append to.[/]")
            return

        # Append to the last entry for now
        self.entries[-1].summary += f" [Append: {input_text}]"
        self.console.print(f"[green]Appended data to entry {self.entries[-1].id}.[/]")

    def attach_habitat(self, path: str):
        # Alias for scan or adding as an 'evolution'?
        # Let's add it as an evolution if it's external.
        name = os.path.basename(path)
        idx = str(len(self.entries) + 1).zfill(3)
        self.entries.append(WikidexEntry(
            id=idx,
            name=name,
            category=self.categorize(name, os.path.isdir(path)),
            entry_type="evolution",
            weight=0.0,
            summary=f"Attached digital habitat reference at {path}.",
            path=path
        ))
        self.console.print(f"[green]Attached {path} as evolution reference.[/]")

if __name__ == "__main__":
    dex = Wikidex()
    dex.scan(".")
    dex.verify_strata_sync()
    if dex.entries:
        dex.specify("001")
        dex.articulate("001")
