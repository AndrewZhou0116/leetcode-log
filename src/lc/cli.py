from pathlib import Path
import typer
from rich import print as rprint
from lc.db import DEFAULT_DB_PATH, init_db



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

def main():
    app()

if __name__ == "__main__":
    main()
