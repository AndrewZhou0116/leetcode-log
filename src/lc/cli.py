from pathlib import Path
import typer
from rich import print as rprint
from lc.db import DEFAULT_DB_PATH, init_db
from .importer import import_plan


app = typer.Typer(help="LeetCode SRS CLI (Plan+Cursor+SRS)")

@app.callback()
def root():
    """Command group for lc."""
    # 这里可以放全局选项（以后比如 --db-path）
    pass

@app.command()
def version():
    """Show version."""
    rprint("[bold green]lcsrs[/bold green] v0.1.0")

@app.command()
def init(db: Path = typer.Option(DEFAULT_DB_PATH, "--db", help="Path to sqlite db file")):
    """Initialize database schema and default meta."""
    path = init_db(db)
    rprint(f"[bold cyan]OK[/bold cyan] initialized db at: {path}")

@app.command("import")
def import_(plan: Path = typer.Argument(..., help="Path to plan.txt"),
            db: Path = typer.Option(DEFAULT_DB_PATH, "--db", help="Path to sqlite db file")):
    """Import plan.txt into problems table (authoritative plan_order)."""
    n, last_order = import_plan(db, plan)
    rprint(f"[bold cyan]OK[/bold cyan] imported {n} problems (last plan_order={last_order})")

def main():
    app()

if __name__ == "__main__":
    main()
