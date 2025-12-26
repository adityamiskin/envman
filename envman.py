import os
import json
import subprocess
from pathlib import Path
import click

STORAGE_DIR = Path.home() / ".envman"
STORAGE_FILE = STORAGE_DIR / "data.json"


def get_storage():
    if not STORAGE_FILE.exists():
        STORAGE_DIR.mkdir(parents=True, exist_ok=True)
        with open(STORAGE_FILE, "w") as f:
            json.dump({"projects": {}}, f)
        return {"projects": {}}

    with open(STORAGE_FILE, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {"projects": {}}


def save_storage(data):
    with open(STORAGE_FILE, "w") as f:
        json.dump(data, f, indent=2)


def detect_project():
    # Try git first
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

    # Fallback to current directory name
    return os.path.basename(os.getcwd())


@click.group()
def cli():
    """EnvMan: Manage your project environment files easily."""
    pass


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
    data = get_storage()

    if project not in data["projects"]:
        data["projects"][project] = {"env_files": {}}

    data["projects"][project]["env_files"][filename] = content
    save_storage(data)
    click.echo(f"Added '{filename}' to project '{project}'.")


@cli.command()
@click.argument("filename", default=".env")
@click.option("--output", "-o", help="Output filename")
def get(filename, output):
    """Retrieve an env file from storage."""
    project = detect_project()
    data = get_storage()

    project_data = data["projects"].get(project)
    if not project_data or filename not in project_data["env_files"]:
        click.echo(f"Error: '{filename}' not found for project '{project}'.")
        return

    content = project_data["env_files"][filename]
    output_path = Path(output if output else filename)
    output_path.write_text(content + "\n")
    click.echo(f"Restored '{filename}' to '{output_path}'.")


@cli.command()
@click.argument("filename", default=".env")
def update(filename):
    """Update stored env file with local content."""
    # Logic is same as add for whole-file replacement
    ctx = click.get_current_context()
    ctx.invoke(add, filename=filename)


@cli.command()
@click.argument("filename", default=".env")
def delete(filename):
    """Delete an env file from storage."""
    project = detect_project()
    data = get_storage()

    project_data = data["projects"].get(project)
    if not project_data or filename not in project_data["env_files"]:
        click.echo(f"Error: '{filename}' not found for project '{project}'.")
        return

    del data["projects"][project]["env_files"][filename]
    save_storage(data)
    click.echo(f"Deleted '{filename}' from project '{project}'.")


@cli.command(name="list")
def list_files():
    """List all stored files for the current project."""
    project = detect_project()
    data = get_storage()

    project_data = data["projects"].get(project)
    if not project_data or not project_data["env_files"]:
        click.echo(f"No files stored for project '{project}'.")
        return

    click.echo(f"Stored files for '{project}':")
    for filename in project_data["env_files"]:
        click.echo(f" - {filename}")


@cli.command()
def projects():
    """List all managed projects."""
    data = get_storage()
    if not data["projects"]:
        click.echo("No projects managed yet.")
        return

    click.echo("Managed projects:")
    for project in data["projects"]:
        click.echo(f" - {project}")


if __name__ == "__main__":
    cli()
