import os
import sqlite3
import json
import subprocess
from pathlib import Path
import click

STORAGE_DIR = Path.home() / ".envman"
STORAGE_FILE = STORAGE_DIR / "data.db"
LEGACY_JSON_FILE = STORAGE_DIR / "data.json"


def get_db():
    if not STORAGE_DIR.exists():
        STORAGE_DIR.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(STORAGE_FILE)
    conn.row_factory = sqlite3.Row
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS projects (
            name TEXT PRIMARY KEY
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS env_files (
            project_name TEXT,
            filename TEXT,
            content TEXT,
            PRIMARY KEY (project_name, filename),
            FOREIGN KEY (project_name) REFERENCES projects(name) ON DELETE CASCADE
        )
        """
    )
    conn.commit()
    return conn


def migrate_json_to_sqlite():
    if not LEGACY_JSON_FILE.exists():
        return

    with open(LEGACY_JSON_FILE, "r") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            return

    conn = get_db()
    for project_name, project_data in data.get("projects", {}).items():
        conn.execute(
            "INSERT OR IGNORE INTO projects (name) VALUES (?)", (project_name,)
        )
        for filename, content in project_data.get("env_files", {}).items():
            content = content.replace("\\n", "\n")
            conn.execute(
                "INSERT OR REPLACE INTO env_files (project_name, filename, content) VALUES (?, ?, ?)",
                (project_name, filename, content),
            )
    conn.commit()
    conn.close()

    LEGACY_JSON_FILE.rename(LEGACY_JSON_FILE.with_suffix(".json.bak"))
    click.echo("Migrated legacy JSON data to SQLite.")


def detect_project():
    try:
        git_root = subprocess.check_output(
            ["git", "rev-parse", "--show-toplevel"],
            stderr=subprocess.DEVNULL,
            universal_newlines=True,
        ).strip()
        return os.path.basename(git_root)
    except (
        subprocess.CalledProcessError,
        FileNotFoundError,
        subprocess.SubprocessError,
    ):
        pass
    return os.path.basename(os.getcwd())


@click.group()
def cli():
    """EnvMan: Manage your project environment files easily."""
    migrate_json_to_sqlite()


@cli.command()
@click.argument("filename", default=".env")
def add(filename):
    """Add a local env file to storage."""
    project = detect_project()
    path = Path(filename)

    if not path.exists():
        click.echo(f"Error: File '{filename}' not found.")
        return

    content = path.read_text().strip("\n")
    conn = get_db()

    conn.execute("INSERT OR IGNORE INTO projects (name) VALUES (?)", (project,))
    conn.execute(
        "INSERT OR REPLACE INTO env_files (project_name, filename, content) VALUES (?, ?, ?)",
        (project, filename, content),
    )
    conn.commit()
    conn.close()
    click.echo(f"Added '{filename}' to project '{project}'.")


@cli.command()
@click.option("--output", "-o", help="Output filename")
@click.option("--project", "-p", help="Project name (defaults to current directory)")
@click.argument("filename", default=".env", required=False)
def get(filename, output, project):
    """Retrieve an env file from storage."""
    project = project or detect_project()
    conn = get_db()

    cursor = conn.execute(
        "SELECT content FROM env_files WHERE project_name = ? AND filename = ?",
        (project, filename),
    )
    row = cursor.fetchone()
    conn.close()

    if not row:
        click.echo(f"Error: '{filename}' not found for project '{project}'.")
        return

    content = row["content"]
    output_path = Path(output if output else filename)
    output_path.write_text(content + "\n")
    click.echo(f"Restored '{filename}' to '{output_path}'.")


@cli.command()
@click.argument("filename", default=".env")
def update(filename):
    """Update stored env file with local content."""
    ctx = click.get_current_context()
    ctx.invoke(add, filename=filename)


@cli.command()
@click.argument("filename", default=".env")
def delete(filename):
    """Delete an env file from storage."""
    project = detect_project()
    conn = get_db()

    cursor = conn.execute(
        "SELECT 1 FROM env_files WHERE project_name = ? AND filename = ?",
        (project, filename),
    )
    if not cursor.fetchone():
        conn.close()
        click.echo(f"Error: '{filename}' not found for project '{project}'.")
        return

    conn.execute(
        "DELETE FROM env_files WHERE project_name = ? AND filename = ?",
        (project, filename),
    )
    conn.commit()
    conn.close()
    click.echo(f"Deleted '{filename}' from project '{project}'.")


@cli.command(name="list")
@click.option("--project", "-p", help="Project name (defaults to current directory)")
def list_files(project):
    """List all stored files for the current project."""
    project = project or detect_project()
    conn = get_db()

    cursor = conn.execute(
        "SELECT filename FROM env_files WHERE project_name = ?", (project,)
    )
    files = cursor.fetchall()
    conn.close()

    if not files:
        click.echo(f"No files stored for project '{project}'.")
        return

    click.echo(f"Stored files for '{project}':")
    for row in files:
        click.echo(f" - {row['filename']}")


@cli.command()
def projects():
    """List all managed projects."""
    conn = get_db()
    cursor = conn.execute("SELECT name FROM projects ORDER BY name")
    projects = cursor.fetchall()
    conn.close()

    if not projects:
        click.echo("No projects managed yet.")
        return

    click.echo("Managed projects:")
    for row in projects:
        click.echo(f" - {row['name']}")


if __name__ == "__main__":
    cli()
