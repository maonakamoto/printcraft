"""Command-line interface for PrintCraft.

Usage:
    printcraft project info <path>              # Show project summary
    printcraft project list-scenes <path>       # List scenes defined in project.yaml
    printcraft generate scene <path> <scene-id> [--round NAME]
    printcraft generate mural <path> [--round NAME]
"""
from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from printcraft.project import Project
from printcraft.generators.grok import GrokGenerator, GrokConfig


app = typer.Typer(help="PrintCraft — custom artwork for physical print surfaces")
project_app = typer.Typer(help="Project management commands")
generate_app = typer.Typer(help="Generation commands")
app.add_typer(project_app, name="project")
app.add_typer(generate_app, name="generate")

console = Console()


@project_app.command("info")
def project_info(path: Path = typer.Argument(..., help="Project directory")):
    """Show a project summary."""
    p = Project.load(path)
    console.print(f"[bold cyan]{p.title}[/bold cyan]")
    console.print(f"Client: {p.client}")
    console.print(f"Status: {p.status}")
    console.print(f"Root: {p.root}")
    console.print()
    console.print(f"[bold]Surface:[/bold] {p.surface.name} @ {p.surface.dpi} DPI")
    for panel in p.surface.panels:
        w, h = panel.pixels(p.surface.dpi)
        console.print(f"  {panel.id}: {panel.width_cm}×{panel.height_cm} cm → {w}×{h} px")
    total_w, total_h = p.surface.total_pixels()
    console.print(f"  [dim]Total: {total_w}×{total_h} px[/dim]")
    console.print()
    console.print(f"[bold]Style:[/bold] {p.style.name}")
    console.print(f"[bold]Scene:[/bold] {p.scene_setting}")
    console.print()
    console.print(f"[bold]Characters:[/bold] {len(p.characters)}")
    console.print(f"[bold]Scenes:[/bold] {len(p.scenes)}")


@project_app.command("list-scenes")
def list_scenes(path: Path = typer.Argument(..., help="Project directory")):
    """List all scenes defined in the project."""
    p = Project.load(path)
    table = Table(title=f"Scenes — {p.title}")
    table.add_column("ID", style="cyan")
    table.add_column("Role", style="yellow")
    table.add_column("Description")
    table.add_column("Ref photo", style="dim")
    for s in p.scenes:
        table.add_row(
            s.id,
            s.composition_role,
            s.description[:60] + ("..." if len(s.description) > 60 else ""),
            s.reference_photo or "—",
        )
    console.print(table)


@generate_app.command("scene")
def generate_scene(
    path: Path = typer.Argument(..., help="Project directory"),
    scene_id: str = typer.Argument(..., help="Scene ID from project.yaml"),
    round_name: Optional[str] = typer.Option(None, "--round", "-r"),
    cdp_url: Optional[str] = typer.Option(None, "--cdp"),
):
    """Generate a single scene."""
    p = Project.load(path)
    scene = p.scene(scene_id)

    if not round_name:
        round_name = f"{date.today().isoformat()}-adhoc"
    round_dir = p.round_dir(round_name, create=True)

    prompt = f"{scene.description}\n\n{p.style.prompt}"
    prompt_file = round_dir / "prompts" / f"{scene.id}.txt"
    prompt_file.write_text(prompt)

    ref = p.resolve(scene.reference_photo) if scene.reference_photo else None

    console.print(f"[cyan]Generating[/cyan] {scene.id} → {round_dir}/outputs/")
    console.print(f"[dim]Reference: {ref}[/dim]")
    console.print(f"[dim]Prompt ({len(prompt)} chars): {prompt[:80]}...[/dim]")

    config = GrokConfig(cdp_url=cdp_url)
    with GrokGenerator(config) as gen:
        result = gen.generate(
            scene_id=scene.id,
            prompt=prompt,
            reference_photo=ref,
            output_dir=round_dir / "outputs",
            file_prefix=scene.id,
        )

    if result.success:
        console.print(f"[green]✓ Saved {len(result.outputs)} image(s)[/green]")
        for out in result.outputs:
            console.print(f"  {out}")
    else:
        console.print(f"[red]✗ Failed: {result.error}[/red]")


@generate_app.command("all-scenes")
def generate_all_scenes(
    path: Path = typer.Argument(..., help="Project directory"),
    round_name: Optional[str] = typer.Option(None, "--round", "-r"),
    cdp_url: Optional[str] = typer.Option(None, "--cdp"),
):
    """Generate every scene defined in the project."""
    p = Project.load(path)
    if not round_name:
        round_name = f"{date.today().isoformat()}-all"
    round_dir = p.round_dir(round_name, create=True)

    config = GrokConfig(cdp_url=cdp_url)
    results = []
    with GrokGenerator(config) as gen:
        for scene in p.scenes:
            prompt = f"{scene.description}\n\n{p.style.prompt}"
            (round_dir / "prompts" / f"{scene.id}.txt").write_text(prompt)
            ref = p.resolve(scene.reference_photo) if scene.reference_photo else None
            console.print(f"[cyan]→[/cyan] {scene.id}")
            result = gen.generate(
                scene_id=scene.id,
                prompt=prompt,
                reference_photo=ref,
                output_dir=round_dir / "outputs",
                file_prefix=scene.id,
            )
            results.append(result)
            if result.success:
                console.print(f"  [green]✓[/green] {len(result.outputs)} file(s)")
            else:
                console.print(f"  [red]✗[/red] {result.error}")

    ok = sum(1 for r in results if r.success)
    console.print(f"\n[bold]{ok}/{len(results)} scenes generated successfully[/bold]")


if __name__ == "__main__":
    app()
