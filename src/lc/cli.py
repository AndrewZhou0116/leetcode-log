import typer
from rich import print as rprint

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

def main():
    app()

if __name__ == "__main__":
    main()
