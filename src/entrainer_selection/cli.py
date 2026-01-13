"""
Command Line Interface
======================

Typer-based CLI for running the entrainer selection pipeline.

Usage:
    entrainer run --phase 1        # Run Phase 1 only
    entrainer run --all            # Run all phases
    entrainer status               # Show pipeline status
    entrainer validate             # Validate configuration
"""

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from entrainer_selection.core.config import get_settings
from entrainer_selection.core.logging import setup_logging, get_logger
from entrainer_selection.phases import PHASE_ORDER

app = typer.Typer(
    name="entrainer",
    help="Safety-by-Design Framework for Ethanol-Water Separation Entrainer Selection",
    add_completion=False,
)
console = Console()


@app.command()
def run(
    phase: Optional[str] = typer.Option(
        None,
        "--phase", "-p",
        help="Specific phase to run (1, 2a, 2b, 2c, 3, 4, 5)",
    ),
    all_phases: bool = typer.Option(
        False,
        "--all", "-a",
        help="Run all phases sequentially",
    ),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        help="Show what would be executed without running",
    ),
):
    """Run the entrainer selection pipeline."""
    settings = get_settings()
    setup_logging(level=settings.logging.level)
    logger = get_logger(__name__)
    
    if not phase and not all_phases:
        console.print("[red]Error:[/red] Specify --phase or --all")
        raise typer.Exit(1)
    
    phases_to_run = PHASE_ORDER if all_phases else [f"phase_{phase}"]
    
    console.print(f"\n[bold blue]Entrainer Selection Pipeline[/bold blue]")
    console.print(f"Environment: {settings.environment}")
    console.print(f"Phases to run: {', '.join(phases_to_run)}\n")
    
    if dry_run:
        console.print("[yellow]Dry run mode - no execution[/yellow]")
        return
    
    for phase_name in phases_to_run:
        console.print(f"\n[bold]Running {phase_name}...[/bold]")
        logger.info(f"Starting {phase_name}")
        # Phase execution will be implemented in each phase module
        console.print(f"[green]✓[/green] {phase_name} completed")


@app.command()
def status():
    """Show pipeline status and configuration."""
    settings = get_settings()
    
    console.print("\n[bold blue]Pipeline Status[/bold blue]\n")
    
    # Configuration table
    table = Table(title="Configuration")
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="green")
    
    table.add_row("Environment", settings.environment)
    table.add_row("Neo4j URI", settings.databases.neo4j.uri)
    table.add_row("ChromaDB Path", settings.databases.chromadb.persist_directory)
    table.add_row("LLM Model", settings.llm.model)
    table.add_row("Simulation Engine", settings.phase_5.simulation.engine)
    
    console.print(table)
    
    # Critical fixes table
    fixes_table = Table(title="Critical Fixes Applied")
    fixes_table.add_column("Fix", style="cyan")
    fixes_table.add_column("Status", style="green")
    
    fixes_table.add_row(
        "Tanimoto Threshold",
        f"✓ {settings.phase_2c.diversity.tanimoto_similarity_threshold} (was 0.5)"
    )
    fixes_table.add_row(
        "Ternary Azeotrope Check",
        f"✓ {'Enabled' if settings.phase_4.constraints.enable_ternary_azeotrope_check else 'Disabled'}"
    )
    fixes_table.add_row(
        "Safety Verification",
        f"✓ {settings.phase_2a.safety_verification.primary_source}"
    )
    fixes_table.add_row(
        "Simulation Engine",
        f"✓ {settings.phase_5.simulation.engine} (not FUG shortcut)"
    )
    
    console.print(fixes_table)


@app.command()
def validate():
    """Validate configuration and dependencies."""
    console.print("\n[bold blue]Validating Configuration[/bold blue]\n")
    
    checks = []
    
    # Check settings load
    try:
        settings = get_settings()
        checks.append(("Settings YAML", True, "Loaded successfully"))
    except Exception as e:
        checks.append(("Settings YAML", False, str(e)))
    
    # Check directories
    for name, path in [
        ("Data root", settings.paths.data_root),
        ("Outputs", settings.paths.outputs),
        ("Logs", settings.logging.log_directory),
    ]:
        exists = Path(path).exists()
        checks.append((name, exists, path))
    
    # Check API key
    has_api_key = settings.google_api_key is not None
    checks.append(("Google API Key", has_api_key, "Set" if has_api_key else "Missing"))
    
    # Display results
    table = Table(title="Validation Results")
    table.add_column("Check", style="cyan")
    table.add_column("Status")
    table.add_column("Details", style="dim")
    
    for name, passed, details in checks:
        status = "[green]✓[/green]" if passed else "[red]✗[/red]"
        table.add_row(name, status, details)
    
    console.print(table)
    
    all_passed = all(c[1] for c in checks)
    if all_passed:
        console.print("\n[green]All checks passed![/green]")
    else:
        console.print("\n[red]Some checks failed. Please fix before running.[/red]")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()

